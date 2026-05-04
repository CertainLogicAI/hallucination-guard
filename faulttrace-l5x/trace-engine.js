// ═══════════════════════════════════════════════════════════
// FaultTrace — Logic Trace Engine
// Traces any tag to its root causes (permissive chain)
// Shows what turns it ON, what turns it OFF, and single points of failure
// ═══════════════════════════════════════════════════════════

(function(exports) {

  // Build write map: which rungs control which tags
  function buildWriteMap(project) {
    const writeMap = {};
    const allContainers = [...project.programs, ...(project.aois || [])];

    allContainers.forEach(prog => {
      prog.routines.forEach(routine => {
        routine.rungs.forEach(rung => {
          const inputs = [];
          const outputs = [];

          rung.instructions.forEach(instr => {
            if (['XIC', 'XIO'].includes(instr.name) && instr.args[0]) {
              inputs.push({
                tag: instr.args[0],
                type: instr.name === 'XIC' ? 'NO' : 'NC',
              });
            }
            if (['EQU','NEQ','GRT','GEQ','LES','LEQ','LIM'].includes(instr.name)) {
              const desc = instr.args.join(` ${instr.name} `);
              inputs.push({ tag: desc, type: 'compare', raw: instr });
            }
            if (['OTE','OTL','OTU'].includes(instr.name) && instr.args[0]) {
              outputs.push({ tag: instr.args[0], type: instr.name });
            }
          });

          outputs.forEach(out => {
            if (!writeMap[out.tag]) writeMap[out.tag] = [];
            writeMap[out.tag].push({
              prog: prog.name,
              routine: routine.name,
              rungNum: rung.number,
              outputType: out.type,
              conditions: inputs,
              text: rung.text,
            });
          });
        });
      });
    });

    return writeMap;
  }

  // ─── Permissive Chain ─────────────────────────────────────
  // "What does this output NEED to turn on?"
  // Returns a flat checklist, not a tree
  function getPermissiveChain(writeMap, targetTag) {
    const chain = [];
    const visited = new Set();

    function walk(tag, depth, path) {
      if (depth > 8 || visited.has(tag)) return;
      visited.add(tag);

      const writes = writeMap[tag] || [];

      if (writes.length === 0) {
        // Terminal — physical input or HMI
        chain.push({
          tag: tag,
          type: 'physical',
          depth: depth,
          path: [...path, tag],
        });
        return;
      }

      // Find the OTE or OTL that ENABLES this tag (not OTU which clears it)
      const enableWriters = writes.filter(w => w.outputType === 'OTE' || w.outputType === 'OTL');

      enableWriters.forEach(writer => {
        writer.conditions.forEach(cond => {
          if (cond.type === 'compare') {
            chain.push({
              tag: cond.tag,
              type: 'compare',
              depth: depth,
              location: `${writer.prog}/${writer.routine} R${writer.rungNum}`,
              path: [...path, tag],
            });
          } else {
            const condTag = cond.tag;
            const condWrites = writeMap[condTag] || [];
            if (condWrites.length === 0) {
              // Physical input
              chain.push({
                tag: condTag,
                type: cond.type === 'NC' ? 'physical_nc' : 'physical',
                depth: depth,
                location: `${writer.prog}/${writer.routine} R${writer.rungNum}`,
                path: [...path, tag],
                mustBeOff: cond.type === 'NC',
              });
            } else {
              // Intermediate — recurse
              chain.push({
                tag: condTag,
                type: cond.type === 'NC' ? 'intermediate_nc' : 'intermediate',
                depth: depth,
                location: `${writer.prog}/${writer.routine} R${writer.rungNum}`,
                path: [...path, tag],
                mustBeOff: cond.type === 'NC',
              });
              walk(condTag, depth + 1, [...path, tag]);
            }
          }
        });
      });
    }

    walk(targetTag, 0, []);
    return chain;
  }

  // ─── Kill Conditions ──────────────────────────────────────
  // "What would turn this output OFF?"
  function getKillConditions(writeMap, targetTag) {
    const kills = [];
    const writes = writeMap[targetTag] || [];

    // OTU rungs — explicit unlatch
    const otuWriters = writes.filter(w => w.outputType === 'OTU');
    otuWriters.forEach(writer => {
      kills.push({
        type: 'unlatch',
        location: `${writer.prog}/${writer.routine} R${writer.rungNum}`,
        conditions: writer.conditions.map(c => ({
          tag: c.tag,
          needsToBeTrue: c.type !== 'NC',
        })),
        text: writer.text,
      });
    });

    // For OTE tags, losing any input condition turns it off
    const oteWriters = writes.filter(w => w.outputType === 'OTE');
    oteWriters.forEach(writer => {
      if (writer.conditions.length > 0) {
        kills.push({
          type: 'lost_input',
          location: `${writer.prog}/${writer.routine} R${writer.rungNum}`,
          conditions: writer.conditions.map(c => ({
            tag: c.tag,
            description: c.type === 'NC'
              ? `${c.tag} turns ON (XIO goes false)`
              : `${c.tag} turns OFF (XIC goes false)`,
          })),
          text: writer.text,
        });
      }
    });

    return kills;
  }

  // ─── Single Points of Failure ─────────────────────────────
  // Inputs that appear exactly once in the permissive chain
  // If they fail, the whole output dies with no backup
  function getSinglePoints(chain) {
    const inputCounts = {};
    chain.filter(c => c.type === 'physical' || c.type === 'physical_nc').forEach(c => {
      inputCounts[c.tag] = (inputCounts[c.tag] || 0) + 1;
    });

    return Object.entries(inputCounts)
      .filter(([tag, count]) => count === 1)
      .map(([tag]) => {
        const entry = chain.find(c => c.tag === tag);
        return {
          tag,
          mustBeOff: entry.mustBeOff || false,
          location: entry.location,
        };
      });
  }

  // ─── Format for UI ────────────────────────────────────────
  function formatTraceReport(writeMap, targetTag) {
    const chain = getPermissiveChain(writeMap, targetTag);
    const kills = getKillConditions(writeMap, targetTag);
    const spofs = getSinglePoints(chain);

    return {
      target: targetTag,
      permissiveChain: chain,
      killConditions: kills,
      singlePointsOfFailure: spofs,
      summary: {
        totalConditions: chain.length,
        physicalInputs: chain.filter(c => c.type === 'physical' || c.type === 'physical_nc').length,
        intermediateLogic: chain.filter(c => c.type === 'intermediate' || c.type === 'intermediate_nc').length,
        comparisons: chain.filter(c => c.type === 'compare').length,
        singlePointsOfFailure: spofs.length,
        killPaths: kills.length,
      },
    };
  }

  exports.buildWriteMap = buildWriteMap;
  exports.getPermissiveChain = getPermissiveChain;
  exports.getKillConditions = getKillConditions;
  exports.getSinglePoints = getSinglePoints;
  exports.formatTraceReport = formatTraceReport;

})(typeof module !== 'undefined' ? module.exports : (window.TraceEngine = {}));
