/**
 * FaultTrace L5X Parser — Browser-side
 * Parses Allen-Bradley L5X exports into structured data.
 * Zero network calls. Everything runs in the browser.
 */

const L5XParser = (() => {

  /**
   * Parse an L5X file string into a structured project object.
   * @param {string} xmlString — raw XML content of the L5X file
   * @returns {object} parsed project
   */
  function parse(xmlString) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlString, 'text/xml');

    // Check for parse errors
    const parseError = doc.querySelector('parsererror');
    if (parseError) {
      throw new Error('Invalid XML: ' + parseError.textContent.substring(0, 200));
    }

    const root = doc.documentElement;
    if (root.tagName !== 'RSLogix5000Content') {
      throw new Error('Not an L5X file. Expected RSLogix5000Content, got ' + root.tagName);
    }

    const ctrl = root.querySelector('Controller');
    const targetType = root.getAttribute('TargetType') || '';

    // Handle partial exports (single module, routine, datatype, etc.)
    if (!ctrl) {
      if (targetType === 'Module') {
        // Module-only export — still useful, wrap it
        return parsePartialExport(root, targetType);
      }
      // Try to work with whatever we have
      if (root.querySelector('Program') || root.querySelector('Routine')) {
        return parsePartialExport(root, targetType || 'Component');
      }
      throw new Error(
        'This L5X file doesn\'t contain a full controller export. ' +
        'To get the best analysis, export the entire controller:\n' +
        'Studio 5000 → File → Save As → L5X file (*.L5X)\n\n' +
        'This appears to be a ' + (targetType || 'partial') + ' export.'
      );
    }

    const project = {
      meta: parseMeta(root, ctrl),
      programs: parsePrograms(ctrl),
      tags: parseTags(ctrl),
      modules: parseModules(ctrl),
      aois: parseAOIs(ctrl),
      udts: parseUDTs(ctrl),
      xref: null, // built after parsing
      isPartial: false,
    };

    // Build cross-reference
    project.xref = buildCrossReference(project);

    return project;
  }

  function parseMeta(root, ctrl) {
    return {
      schemaRevision: root.getAttribute('SchemaRevision') || '',
      softwareRevision: root.getAttribute('SoftwareRevision') || '',
      exportDate: root.getAttribute('ExportDate') || '',
      controllerName: ctrl.getAttribute('Name') || '',
      processorType: ctrl.getAttribute('ProcessorType') || '',
      majorRev: ctrl.getAttribute('MajorRev') || '',
      minorRev: ctrl.getAttribute('MinorRev') || '',
      description: getDescription(ctrl),
    };
  }

  function parsePrograms(ctrl) {
    const programs = [];
    ctrl.querySelectorAll(':scope > Programs > Program').forEach(progEl => {
      const prog = {
        name: progEl.getAttribute('Name') || '',
        mainRoutine: progEl.getAttribute('MainRoutineName') || '',
        faultRoutine: progEl.getAttribute('FaultRoutineName') || '',
        disabled: progEl.getAttribute('Disabled') === 'true',
        description: getDescription(progEl),
        tags: parseTagElements(progEl.querySelector(':scope > Tags')),
        routines: [],
      };

      progEl.querySelectorAll(':scope > Routines > Routine').forEach(routEl => {
        prog.routines.push(parseRoutine(routEl, prog.name));
      });

      programs.push(prog);
    });
    return programs;
  }

  function parseRoutine(routEl, programName) {
    const routine = {
      name: routEl.getAttribute('Name') || '',
      type: routEl.getAttribute('Type') || '',
      program: programName,
      description: getDescription(routEl),
      rungs: [],
      stLines: [],
    };

    // RLL (Ladder Logic) rungs
    routEl.querySelectorAll('RLLContent > Rung').forEach(rungEl => {
      const rung = {
        number: parseInt(rungEl.getAttribute('Number') || '0'),
        type: rungEl.getAttribute('Type') || 'N',
        comment: '',
        text: '',
        instructions: [],
        tags: [],
      };

      const commentEl = rungEl.querySelector('Comment');
      if (commentEl) rung.comment = (commentEl.textContent || '').trim();

      const textEl = rungEl.querySelector('Text');
      if (textEl) {
        rung.text = (textEl.textContent || '').trim();
        rung.instructions = parseInstructions(rung.text);
        rung.tags = extractTagsFromRung(rung.text);
      }

      routine.rungs.push(rung);
    });

    // Structured Text content
    const stContent = routEl.querySelector('STContent');
    if (stContent) {
      stContent.querySelectorAll('Line').forEach(lineEl => {
        const text = (lineEl.textContent || '').trim();
        if (text) routine.stLines.push(text);
      });
    }

    // Function Block Diagram content
    const fbdContent = routEl.querySelector('FBDContent');
    if (fbdContent) {
      fbdContent.querySelectorAll('Sheet').forEach((sheetEl, sheetIdx) => {
        const rung = {
          number: parseInt(sheetEl.getAttribute('Number') || String(sheetIdx)),
          type: 'N',
          comment: sheetEl.getAttribute('Description') || '',
          text: '',
          instructions: [],
          tags: [],
          isFBD: true,
        };

        const tagSet = new Set();

        // IRef — input references (reading a tag, equivalent to XIC)
        sheetEl.querySelectorAll('IRef').forEach(el => {
          const operand = el.getAttribute('Operand') || '';
          if (operand) {
            rung.instructions.push({ name: 'IREF', args: [operand], raw: 'IREF(' + operand + ')' });
            tagSet.add(operand);
          }
        });

        // ORef — output references (writing to a tag)
        sheetEl.querySelectorAll('ORef').forEach(el => {
          const operand = el.getAttribute('Operand') || '';
          if (operand) {
            rung.instructions.push({ name: 'OREF', args: [operand], raw: 'OREF(' + operand + ')' });
            tagSet.add(operand);
          }
        });

        // Block — function blocks (OTE, TON, ADD, MOV, etc.)
        sheetEl.querySelectorAll('Block').forEach(el => {
          const blockType = el.getAttribute('Type') || '';
          const operand = el.getAttribute('Operand') || '';
          if (blockType) {
            const args = operand ? [operand] : [];
            rung.instructions.push({ name: blockType, args: args, raw: blockType + '(' + operand + ')' });
            if (operand) tagSet.add(operand);
          }
        });

        // AddOnInstruction — AOI instances in FBD
        sheetEl.querySelectorAll('AddOnInstruction').forEach(el => {
          const aoiName = el.getAttribute('Name') || '';
          const operand = el.getAttribute('Operand') || '';
          if (aoiName || operand) {
            const args = [operand, aoiName].filter(Boolean);
            rung.instructions.push({ name: 'JSR', args: args, raw: 'JSR(' + args.join(',') + ')' });
            if (operand) tagSet.add(operand);
          }
        });

        rung.tags = Array.from(tagSet);

        // Synthetic text for display/reporting
        if (rung.instructions.length > 0) {
          rung.text = rung.instructions.map(function(i) { return i.raw; }).join(' ');
          routine.rungs.push(rung);
        }
      });
    }

    return routine;
  }

  function parseInstructions(rungText) {
    const instructions = [];
    // Match instruction(args) patterns, handling nested brackets for branches
    const re = /([A-Z][A-Z0-9_]{1,10})\(([^)]*)\)/g;
    let match;
    while ((match = re.exec(rungText)) !== null) {
      const name = match[1];
      const args = match[2].split(',').map(a => a.trim()).filter(a => a);
      instructions.push({ name, args, raw: match[0] });
    }
    return instructions;
  }

  function extractTagsFromRung(rungText) {
    const tags = new Set();
    const re = /([A-Z][A-Z0-9_]{1,10})\(([^)]*)\)/g;
    let match;
    while ((match = re.exec(rungText)) !== null) {
      match[2].split(',').forEach(arg => {
        arg = arg.trim();
        // Skip numeric literals, hex, and '?'
        if (!arg || arg === '?' || /^-?\d+(\.\d+)?$/.test(arg) || /^16#/.test(arg)) return;
        tags.add(arg);
      });
    }
    return Array.from(tags);
  }

  function parseTags(ctrl) {
    const allTags = [];

    // Controller-scope tags
    const ctrlTags = ctrl.querySelector(':scope > Tags');
    if (ctrlTags) {
      parseTagElements(ctrlTags).forEach(t => {
        t.scope = 'Controller';
        allTags.push(t);
      });
    }

    // Program-scope tags
    ctrl.querySelectorAll(':scope > Programs > Program').forEach(progEl => {
      const progName = progEl.getAttribute('Name') || '';
      const progTags = progEl.querySelector(':scope > Tags');
      if (progTags) {
        parseTagElements(progTags).forEach(t => {
          t.scope = progName;
          allTags.push(t);
        });
      }
    });

    return allTags;
  }

  function parseTagElements(tagsContainer) {
    const tags = [];
    if (!tagsContainer) return tags;

    tagsContainer.querySelectorAll(':scope > Tag').forEach(tagEl => {
      const tag = {
        name: tagEl.getAttribute('Name') || '',
        dataType: tagEl.getAttribute('DataType') || '',
        tagType: tagEl.getAttribute('TagType') || 'Base',
        constant: tagEl.getAttribute('Constant') === 'true',
        externalAccess: tagEl.getAttribute('ExternalAccess') || '',
        aliasFor: tagEl.getAttribute('AliasFor') || '',
        description: getDescription(tagEl),
        scope: '', // filled in by caller
        // Produced/Consumed metadata
        produceCount: tagEl.getAttribute('ProduceCount') || '',
        remoteTag: '',
        remoteController: '',
        rpi: '',
      };

      // Parse ConsumeInfo for consumed tags
      const consumeInfo = tagEl.querySelector('ConsumeInfo');
      if (consumeInfo) {
        tag.remoteController = consumeInfo.getAttribute('Producer') || '';
        tag.remoteTag = consumeInfo.getAttribute('RemoteTag') || consumeInfo.getAttribute('RemoteElement') || '';
        tag.rpi = consumeInfo.getAttribute('RPI') || '';
      }

      tags.push(tag);
    });
    return tags;
  }

  function parseModules(ctrl) {
    const modules = [];
    ctrl.querySelectorAll('Module').forEach(modEl => {
      const mod = {
        name: modEl.getAttribute('Name') || '',
        catalogNumber: modEl.getAttribute('CatalogNumber') || '',
        vendor: modEl.getAttribute('Vendor') || '',
        productType: modEl.getAttribute('ProductType') || '',
        major: modEl.getAttribute('Major') || '',
        minor: modEl.getAttribute('Minor') || '',
        parentModule: modEl.getAttribute('ParentModule') || '',
        parentModPortId: modEl.getAttribute('ParentModPortId') || '',
        inhibited: modEl.getAttribute('Inhibited') === 'true',
        description: getDescription(modEl),
      };

      // Parse ports for network topology
      mod.ports = [];
      modEl.querySelectorAll('Port').forEach(portEl => {
        mod.ports.push({
          id: portEl.getAttribute('Id') || '',
          address: portEl.getAttribute('Address') || '',
          type: portEl.getAttribute('Type') || '',
          upstream: portEl.getAttribute('Upstream') === 'true',
        });
      });

      modules.push(mod);
    });
    return modules;
  }

  function parseAOIs(ctrl) {
    const aois = [];
    ctrl.querySelectorAll('AddOnInstructionDefinition').forEach(aoiEl => {
      const aoiName = aoiEl.getAttribute('Name') || '';
      const aoi = {
        name: aoiName,
        description: getDescription(aoiEl),
        parameters: [],
        localTags: [],
        routines: [],
      };

      // Parameters
      aoiEl.querySelectorAll('Parameter').forEach(paramEl => {
        aoi.parameters.push({
          name: paramEl.getAttribute('Name') || '',
          usage: paramEl.getAttribute('Usage') || '',
          dataType: paramEl.getAttribute('DataType') || '',
          description: getDescription(paramEl),
        });
      });

      // Local tags (internal to the AOI)
      aoiEl.querySelectorAll('LocalTag').forEach(tagEl => {
        aoi.localTags.push({
          name: tagEl.getAttribute('Name') || '',
          dataType: tagEl.getAttribute('DataType') || '',
          dimension: tagEl.getAttribute('Dimensions') || '0',
          description: getDescription(tagEl),
        });
      });

      // Routines (the actual logic inside the AOI)
      aoiEl.querySelectorAll(':scope > Routines > Routine').forEach(routEl => {
        aoi.routines.push(parseRoutine(routEl, 'AOI:' + aoiName));
      });

      aois.push(aoi);
    });
    return aois;
  }

  function parseUDTs(ctrl) {
    const udts = [];
    ctrl.querySelectorAll('DataType').forEach(dtEl => {
      const name = dtEl.getAttribute('Name') || '';
      // Skip AB internal types
      if (name.startsWith('AB:') || !name) return;
      // Only user-defined
      if (dtEl.getAttribute('Class') !== 'User') return;

      const udt = {
        name,
        family: dtEl.getAttribute('Family') || '',
        description: getDescription(dtEl),
        members: [],
      };
      dtEl.querySelectorAll('Member').forEach(memEl => {
        if (memEl.getAttribute('Hidden') === 'true') return;
        udt.members.push({
          name: memEl.getAttribute('Name') || '',
          dataType: memEl.getAttribute('DataType') || '',
          dimension: memEl.getAttribute('Dimension') || '0',
          description: getDescription(memEl),
        });
      });
      udts.push(udt);
    });
    return udts;
  }

  /**
   * Build cross-reference: maps each tag to every location it's used.
   */
  function buildCrossReference(project) {
    const xref = {}; // tagName -> [{program, routine, rung, instruction, rungText}]

    // Index AOI routines as pseudo-programs for cross-referencing
    project.aois.forEach(aoi => {
      aoi.routines.forEach(routine => {
        routine.rungs.forEach(rung => {
          rung.tags.forEach(tagName => {
            if (!xref[tagName]) xref[tagName] = [];
            const instr = rung.instructions.find(i => i.args.includes(tagName));
            xref[tagName].push({
              program: 'AOI:' + aoi.name,
              routine: routine.name,
              rung: rung.number,
              instruction: instr ? instr.name : '',
              rungText: rung.text,
              comment: rung.comment,
            });
          });
        });
        routine.stLines.forEach((line, idx) => {
          const stTags = line.match(/[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*/g) || [];
          const keywords = new Set(['IF', 'THEN', 'ELSE', 'END_IF', 'FOR', 'TO', 'DO', 'END_FOR',
            'WHILE', 'END_WHILE', 'CASE', 'OF', 'END_CASE', 'RETURN', 'EXIT', 'MOD', 'AND',
            'OR', 'NOT', 'XOR', 'TRUE', 'FALSE', 'ABS', 'SQRT', 'ATAN', 'SIN', 'COS', 'TAN',
            'LN', 'LOG', 'TRUNC', 'REAL', 'DINT', 'INT', 'SINT', 'BOOL', 'STRING']);
          stTags.forEach(tag => {
            if (keywords.has(tag.toUpperCase()) || /^\d/.test(tag)) return;
            if (!xref[tag]) xref[tag] = [];
            xref[tag].push({
              program: 'AOI:' + aoi.name,
              routine: routine.name,
              rung: -1,
              instruction: 'ST',
              rungText: line,
              comment: `ST Line ${idx + 1}`,
            });
          });
        });
      });
    });

    project.programs.forEach(prog => {
      prog.routines.forEach(routine => {
        routine.rungs.forEach(rung => {
          rung.tags.forEach(tagName => {
            if (!xref[tagName]) xref[tagName] = [];
            // Find which instruction uses this tag
            const instr = rung.instructions.find(i => i.args.includes(tagName));
            xref[tagName].push({
              program: prog.name,
              routine: routine.name,
              rung: rung.number,
              instruction: instr ? instr.name : '',
              rungText: rung.text,
              comment: rung.comment,
            });
          });
        });

        // ST cross-reference
        routine.stLines.forEach((line, idx) => {
          // Simple tag extraction from ST
          const stTags = line.match(/[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*/g) || [];
          const keywords = new Set(['IF', 'THEN', 'ELSE', 'END_IF', 'FOR', 'TO', 'DO', 'END_FOR',
            'WHILE', 'END_WHILE', 'CASE', 'OF', 'END_CASE', 'RETURN', 'EXIT', 'MOD', 'AND',
            'OR', 'NOT', 'XOR', 'TRUE', 'FALSE', 'ABS', 'SQRT', 'ATAN', 'SIN', 'COS', 'TAN',
            'LN', 'LOG', 'TRUNC', 'REAL', 'DINT', 'INT', 'SINT', 'BOOL', 'STRING']);
          stTags.forEach(tag => {
            if (keywords.has(tag.toUpperCase()) || /^\d/.test(tag)) return;
            if (!xref[tag]) xref[tag] = [];
            xref[tag].push({
              program: prog.name,
              routine: routine.name,
              rung: -1,
              instruction: 'ST',
              rungText: line,
              comment: `ST Line ${idx + 1}`,
            });
          });
        });
      });
    });

    return xref;
  }

  // Helper: get Description text from an element
  function getDescription(el) {
    const descEl = el.querySelector(':scope > Description');
    return descEl ? (descEl.textContent || '').trim() : '';
  }

  /**
   * Handle partial exports (individual modules, routines, datatypes)
   */
  function parsePartialExport(root, targetType) {
    const project = {
      meta: {
        schemaRevision: root.getAttribute('SchemaRevision') || '',
        softwareRevision: root.getAttribute('SoftwareRevision') || '',
        exportDate: root.getAttribute('ExportDate') || '',
        controllerName: root.getAttribute('TargetName') || 'Partial Export',
        processorType: targetType + ' Export',
        majorRev: '', minorRev: '',
        description: 'Partial export (' + targetType + '). For full analysis, export the entire controller.',
      },
      programs: [],
      tags: [],
      modules: [],
      aois: [],
      udts: [],
      xref: {},
      isPartial: true,
    };

    // Parse whatever elements exist at any level
    root.querySelectorAll('Module').forEach(modEl => {
      project.modules.push({
        name: modEl.getAttribute('Name') || '',
        catalogNumber: modEl.getAttribute('CatalogNumber') || '',
        vendor: modEl.getAttribute('Vendor') || '',
        productType: modEl.getAttribute('ProductType') || '',
        major: modEl.getAttribute('Major') || '',
        minor: modEl.getAttribute('Minor') || '',
        parentModule: modEl.getAttribute('ParentModule') || '',
        parentModPortId: modEl.getAttribute('ParentModPortId') || '',
        inhibited: modEl.getAttribute('Inhibited') === 'true',
        description: getDescription(modEl),
        ports: [],
      });
    });

    root.querySelectorAll('Program').forEach(progEl => {
      const prog = {
        name: progEl.getAttribute('Name') || '',
        mainRoutine: progEl.getAttribute('MainRoutineName') || '',
        faultRoutine: progEl.getAttribute('FaultRoutineName') || '',
        disabled: false,
        description: '',
        tags: parseTagElements(progEl.querySelector('Tags')),
        routines: [],
      };
      progEl.querySelectorAll('Routine').forEach(routEl => {
        prog.routines.push(parseRoutine(routEl, prog.name));
      });
      project.programs.push(prog);
    });

    // Standalone routines (not inside a Program)
    root.querySelectorAll(':scope > Routine').forEach(routEl => {
      const prog = {
        name: 'ImportedRoutine',
        mainRoutine: routEl.getAttribute('Name') || '',
        faultRoutine: '', disabled: false, description: '',
        tags: [], routines: [parseRoutine(routEl, 'ImportedRoutine')],
      };
      project.programs.push(prog);
    });

    root.querySelectorAll('Tag').forEach(tagEl => {
      project.tags.push({
        name: tagEl.getAttribute('Name') || '',
        dataType: tagEl.getAttribute('DataType') || '',
        tagType: tagEl.getAttribute('TagType') || 'Base',
        constant: false, externalAccess: '',
        aliasFor: '', description: getDescription(tagEl),
        scope: 'Imported',
      });
    });

    root.querySelectorAll('AddOnInstructionDefinition').forEach(aoiEl => {
      project.aois.push({
        name: aoiEl.getAttribute('Name') || '',
        description: getDescription(aoiEl),
        parameters: [],
      });
    });

    project.xref = buildCrossReference(project);
    return project;
  }

  // Public API
  return { parse };
})();

// Export for testing in Node.js
if (typeof module !== 'undefined') module.exports = L5XParser;
