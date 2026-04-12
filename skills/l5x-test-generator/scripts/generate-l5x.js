#!/usr/bin/env node
/**
 * L5X Test File Generator
 * 
 * Generates realistic Allen-Bradley L5X files from a JSON scenario definition.
 * Usage: node generate-l5x.js <scenario.json> [output.L5X]
 * 
 * Scenario JSON format:
 * {
 *   "controller": { "name": "...", "processor": "1756-L83E", "majorRev": "34", "minorRev": "11" },
 *   "modules": [{ "name": "...", "catalog": "1756-IB16", "slot": "1" }],
 *   "tags": [{ "name": "...", "type": "BOOL", "value": true/false/number, "scope": "Controller", "description": "..." }],
 *   "programs": [{
 *     "name": "...",
 *     "routines": [{
 *       "name": "...",
 *       "type": "RLL",
 *       "rungs": [{ "comment": "...", "logic": "XIC(Tag1)OTE(Tag2);" }]
 *     }]
 *   }]
 * }
 */

const fs = require('fs');
const path = require('path');

function generateL5X(scenario) {
  const ctrl = scenario.controller || {};
  const name = ctrl.name || 'Test_Controller';
  const proc = ctrl.processor || '1756-L83E';
  const major = ctrl.majorRev || '34';
  const minor = ctrl.minorRev || '11';

  let xml = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="${major}.00" TargetName="${esc(name)}" TargetType="Controller" ContainsContext="true" ExportDate="${new Date().toString().slice(0,24)}" ExportOptions="References NoRawData L5KData DecoratedData Context Dependencies ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="${esc(name)}" ProcessorType="${esc(proc)}" MajorRev="${major}" MinorRev="${minor}">
<DataTypes Use="Context"></DataTypes>
`;

  // Modules
  xml += '<Modules>\n';
  xml += `<Module Name="Local" CatalogNumber="${esc(proc)}" Vendor="1" ProductType="14" Major="${major}" Minor="${minor}">\n`;
  xml += '<Ports><Port Id="1" Address="0" Type="ICP" Upstream="true"/></Ports>\n';
  xml += '</Module>\n';
  for (const mod of (scenario.modules || [])) {
    xml += `<Module Name="${esc(mod.name)}" CatalogNumber="${esc(mod.catalog)}" Vendor="1" ProductType="7" Major="3" Minor="1" ParentModule="Local" ParentModPortId="1">\n`;
    xml += `<Ports><Port Id="1" Address="${mod.slot || '1'}" Type="ICP"/></Ports>\n`;
    xml += '</Module>\n';
  }
  xml += '</Modules>\n';

  // Controller-scope tags
  const ctrlTags = (scenario.tags || []).filter(t => !t.scope || t.scope === 'Controller');
  if (ctrlTags.length > 0) {
    xml += '<Tags>\n';
    for (const tag of ctrlTags) {
      xml += renderTag(tag);
    }
    xml += '</Tags>\n';
  }

  // Programs
  xml += '<Programs>\n';
  for (const prog of (scenario.programs || [])) {
    xml += `<Program Name="${esc(prog.name)}" MainRoutineName="${esc(prog.mainRoutine || prog.routines?.[0]?.name || 'Main')}" FaultRoutineName="">\n`;
    
    // Program-scope tags
    const progTags = (scenario.tags || []).filter(t => t.scope === prog.name);
    if (progTags.length > 0) {
      xml += '<Tags>\n';
      for (const tag of progTags) {
        xml += renderTag(tag);
      }
      xml += '</Tags>\n';
    } else {
      xml += '<Tags></Tags>\n';
    }

    xml += '<Routines>\n';
    for (const routine of (prog.routines || [])) {
      const type = routine.type || 'RLL';
      xml += `<Routine Name="${esc(routine.name)}" Type="${type}">\n`;
      
      if (type === 'RLL') {
        xml += '<RLLContent>\n';
        for (let i = 0; i < (routine.rungs || []).length; i++) {
          const rung = routine.rungs[i];
          xml += `<Rung Number="${i}" Type="N">\n`;
          if (rung.comment) {
            xml += `<Comment><![CDATA[${rung.comment}]]></Comment>\n`;
          }
          xml += `<Text><![CDATA[${rung.logic}]]></Text>\n`;
          xml += '</Rung>\n';
        }
        xml += '</RLLContent>\n';
      } else if (type === 'ST') {
        xml += '<STContent>\n';
        for (let i = 0; i < (routine.lines || []).length; i++) {
          xml += `<Line Number="${i}"><![CDATA[${routine.lines[i]}]]></Line>\n`;
        }
        xml += '</STContent>\n';
      }
      
      xml += '</Routine>\n';
    }
    xml += '</Routines>\n';
    xml += '</Program>\n';
  }
  xml += '</Programs>\n';

  xml += '</Controller>\n';
  xml += '</RSLogix5000Content>\n';

  return xml;
}

function renderTag(tag) {
  const name = tag.name;
  const type = tag.type || 'BOOL';
  const desc = tag.description || '';
  const value = tag.value;

  // Handle structure types
  if (type === 'TIMER' || type === 'COUNTER') {
    return renderStructTag(tag);
  }

  let xml = `<Tag Name="${esc(name)}" TagType="${tag.tagType || 'Base'}" DataType="${type}"`;
  if (type === 'BOOL' || type === 'DINT' || type === 'SINT' || type === 'INT') {
    xml += ` Radix="Decimal"`;
  } else if (type === 'REAL') {
    xml += ` Radix="Float"`;
  }
  xml += ` Constant="false" ExternalAccess="Read/Write">\n`;

  if (desc) {
    xml += `<Description><![CDATA[${desc}]]></Description>\n`;
  }

  if (value !== undefined && value !== null) {
    const rawVal = type === 'BOOL' ? (value ? '1' : '0') : String(value);
    xml += `<Data Format="L5K"><![CDATA[${rawVal}]]></Data>\n`;
    xml += `<Data Format="Decorated"><DataValue DataType="${type}"`;
    if (type === 'BOOL' || type === 'DINT' || type === 'SINT' || type === 'INT') {
      xml += ` Radix="Decimal"`;
    } else if (type === 'REAL') {
      xml += ` Radix="Float"`;
    }
    xml += ` Value="${rawVal}"/></Data>\n`;
  }

  xml += '</Tag>\n';
  return xml;
}

function renderStructTag(tag) {
  const type = tag.type;
  const members = tag.members || {};

  let defaults;
  if (type === 'TIMER') {
    defaults = { PRE: { type: 'DINT', val: 0 }, ACC: { type: 'DINT', val: 0 }, EN: { type: 'BOOL', val: 0 }, TT: { type: 'BOOL', val: 0 }, DN: { type: 'BOOL', val: 0 } };
  } else if (type === 'COUNTER') {
    defaults = { PRE: { type: 'DINT', val: 0 }, ACC: { type: 'DINT', val: 0 }, CU: { type: 'BOOL', val: 0 }, CD: { type: 'BOOL', val: 0 }, DN: { type: 'BOOL', val: 0 }, OV: { type: 'BOOL', val: 0 }, UN: { type: 'BOOL', val: 0 } };
  }

  let xml = `<Tag Name="${esc(tag.name)}" TagType="Base" DataType="${type}" Constant="false" ExternalAccess="Read/Write">\n`;
  if (tag.description) {
    xml += `<Description><![CDATA[${tag.description}]]></Description>\n`;
  }

  xml += `<Data Format="Decorated">\n<Structure DataType="${type}">\n`;
  for (const [mName, mDef] of Object.entries(defaults)) {
    const val = members[mName] !== undefined ? members[mName] : mDef.val;
    const radix = mDef.type === 'BOOL' ? '' : ' Radix="Decimal"';
    const displayVal = mDef.type === 'BOOL' ? (val ? '1' : '0') : String(val);
    xml += `<DataValueMember Name="${mName}" DataType="${mDef.type}"${radix} Value="${displayVal}"/>\n`;
  }
  xml += `</Structure>\n</Data>\n</Tag>\n`;
  return xml;
}

function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// CLI mode
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node generate-l5x.js <scenario.json> [output.L5X]');
    console.log('  Generates a realistic L5X test file from a scenario definition.');
    process.exit(0);
  }

  const scenario = JSON.parse(fs.readFileSync(args[0], 'utf8'));
  const output = args[1] || args[0].replace(/\.json$/, '.L5X');
  const xml = generateL5X(scenario);
  fs.writeFileSync(output, xml);
  console.log(`Generated: ${output} (${(xml.length / 1024).toFixed(1)} KB)`);
}

module.exports = { generateL5X };
