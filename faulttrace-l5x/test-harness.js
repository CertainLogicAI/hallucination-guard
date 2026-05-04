const fs = require('fs');
const jsdom = require('/tmp/node_modules/jsdom');
global.DOMParser = new jsdom.JSDOM('').window.DOMParser;
const L5XParser = require('/data/.openclaw/workspace/projects/plc-analyzer/app/l5x-parser.js');
const RuleEngine = require('/data/.openclaw/workspace/projects/plc-analyzer/app/rule-engine.js');

function makeL5X(opts = {}) {
  const programs = opts.programs || '';
  const tags = opts.tags || '';
  const modules = opts.modules || '';
  const aois = opts.aois || '';
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="36.00" TargetName="TestCtrl" TargetType="Controller" ContainsContext="true" ExportDate="Mon Mar 23 15:00:00 2026" ExportOptions="NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="TestCtrl" ProcessorType="1756-L83E" MajorRev="36" MinorRev="1">
<Tags>${tags}</Tags>
<Programs>${programs}</Programs>
<Modules>${modules}</Modules>
<AddOnInstructionDefinitions>${aois}</AddOnInstructionDefinitions>
</Controller>
</RSLogix5000Content>`;
}

function makeProgram(name, routineName, rungs, opts = {}) {
  const rungXml = rungs.map((text, i) => 
    `<Rung Number="${i}" Type="N"><Text><![CDATA[${text}]]></Text></Rung>`
  ).join('\n');
  const faultAttr = opts.faultRoutine ? ` FaultRoutineName="${opts.faultRoutine}"` : '';
  const extraRoutines = opts.extraRoutines || '';
  return `<Program Name="${name}" MainRoutineName="${routineName}"${faultAttr}>
    <Tags></Tags>
    <Routines>
      <Routine Name="${routineName}" Type="RLL">
        <RLLContent>${rungXml}</RLLContent>
      </Routine>
      ${extraRoutines}
    </Routines>
  </Program>`;
}

function makeTag(name, type) {
  return `<Tag Name="${name}" TagType="Base" DataType="${type}"/>`;
}

function makeModule(name, catalogNum, parentModule, parentPort, slot) {
  return `<Module Name="${name}" CatalogNumber="${catalogNum}" Vendor="1" ProductType="7" ProductCode="55" Major="1" Minor="1" ParentModule="${parentModule}" ParentModPortId="${parentPort}"><EKey State="CompatibleModule"/><Ports><Port Id="1" Address="${slot}" Type="PointIO" Upstream="true"/></Ports></Module>`;
}

const tests = [];
let pass = 0, fail = 0;

function test(name, xml, expectedRule, expectedSeverity, shouldFind = true) {
  tests.push({ name, xml, expectedRule, expectedSeverity, shouldFind });
}

// ═══════ 1. OTE/OTU CONFLICT ═══════
test('OTE/OTU conflict: same tag same rung',
  makeL5X({ programs: makeProgram('Main', 'R', ['[XIC(Start) ][OTE(Motor1) ,OTU(Motor1) ];']) }),
  'OTE_OTU_CONFLICT', 'critical', true);

test('OTE/OTU conflict: separate rungs = OK',
  makeL5X({ programs: makeProgram('Main', 'R', ['XIC(Start)OTE(M);','XIC(Stop)OTU(M);']) }),
  'OTE_OTU_CONFLICT', 'critical', false);

// ═══════ 2. DUPLICATE OTE ═══════
test('Dup OTE: same tag 2 rungs',
  makeL5X({ programs: makeProgram('Main', 'R', ['XIC(S1)OTE(V);','XIC(S2)OTE(V);']) }),
  'DUPLICATE_OTE', 'critical', true);

test('Dup OTE: different tags = OK',
  makeL5X({ programs: makeProgram('Main', 'R', ['XIC(S1)OTE(V1);','XIC(S2)OTE(V2);']) }),
  'DUPLICATE_OTE', 'critical', false);

test('Dup OTE: cross-program',
  makeL5X({ programs: makeProgram('P1','R',['XIC(S)OTE(Out);']) + makeProgram('P2','R',['XIC(S2)OTE(Out);']) }),
  'DUPLICATE_OTE', 'critical', true);

// ═══════ 3. UNCONDITIONAL OUTPUT ═══════
test('Uncond OTE: bare',
  makeL5X({ programs: makeProgram('Main','R',['OTE(X);']) }),
  'UNCONDITIONAL_OUTPUT', 'warning', true);

test('Uncond OTL: bare latch',
  makeL5X({ programs: makeProgram('Main','R',['OTL(X);']) }),
  'UNCONDITIONAL_OUTPUT', 'warning', true);

test('Uncond: MOV literal = OK (init pattern)',
  makeL5X({ programs: makeProgram('Main','R',['MOV(100,X);']) }),
  'UNCONDITIONAL_OUTPUT', 'warning', false);

test('Uncond: conditional OTE = OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(A)OTE(B);']) }),
  'UNCONDITIONAL_OUTPUT', 'warning', false);

// ═══════ 4. UNCONDITIONAL TIMER ═══════
test('Uncond timer: bare TON',
  makeL5X({ programs: makeProgram('Main','R',['TON(T1,1000,0);']) }),
  'UNCONDITIONAL_TIMER', 'warning', true);

test('Uncond timer: conditional = OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(En)TON(T1,5000,0);']) }),
  'UNCONDITIONAL_TIMER', 'warning', false);

// ═══════ 5. TIMER NO RESET ═══════
test('RTO no RES: accumulates forever',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Run)RTO(Tmr,30000,0);']) }),
  'TIMER_NO_RESET', 'warning', true);

test('RTO with RES: OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Run)RTO(Tmr,30000,0);','XIC(Rst)RES(Tmr);']) }),
  'TIMER_NO_RESET', 'warning', false);

// ═══════ 6. COUNTER NO RESET ═══════
test('CTU no RES: forever',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Part)CTU(Cnt,0,1000);']) }),
  'COUNTER_NO_RESET', 'warning', true);

test('CTU with RES: OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Part)CTU(Cnt,0,1000);','XIC(Done)RES(Cnt);']) }),
  'COUNTER_NO_RESET', 'warning', false);

// ═══════ 7. LATCH NO UNLATCH ═══════
test('OTL no OTU: stuck on (non-alarm tag)',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Hi)OTL(StickyBit);']) }),
  'LATCH_NO_UNLATCH', 'warning', true);

test('OTL with OTU: OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Hi)OTL(Latch);','XIC(Rst)OTU(Latch);']) }),
  'LATCH_NO_UNLATCH', 'warning', false);

test('OTL on alarm tag: excluded (intentional pattern)',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Hi)OTL(OverTempAlarm);']) }),
  'LATCH_NO_UNLATCH', 'warning', false);

test('OTL on fault tag: excluded',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Hi)OTL(CommFault);']) }),
  'LATCH_NO_UNLATCH', 'warning', false);

// ═══════ 8. CIRCULAR DEPENDENCY ═══════
test('Circular OTE: A↔B',
  makeL5X({ programs: makeProgram('Main','R',['XIC(B)OTE(A);','XIC(A)OTE(B);']) }),
  'CIRCULAR_DEPENDENCY', 'warning', true);

test('Circular: OTL/OTU interlock = OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(B)OTL(A);','XIC(A)OTU(B);']) }),
  'CIRCULAR_DEPENDENCY', 'warning', false);

// ═══════ 9. MISSING FAULT ROUTINE ═══════
test('No fault routine',
  makeL5X({ programs: makeProgram('Main','R',['XIC(S)OTE(M);']) }),
  'MISSING_FAULT_ROUTINE', 'info', true);

test('Has fault routine assigned: OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(S)OTE(M);'], {
    faultRoutine: 'FaultHandler',
    extraRoutines: '<Routine Name="FaultHandler" Type="RLL"><RLLContent><Rung Number="0" Type="N"><Text><![CDATA[OTE(F);]]></Text></Rung></RLLContent></Routine>'
  }) }),
  'MISSING_FAULT_ROUTINE', 'info', false);

// ═══════ 10. EMPTY ROUTINE ═══════
test('Empty routine: zero rungs',
  makeL5X({ programs: `<Program Name="Main" MainRoutineName="R">
    <Tags></Tags><Routines>
      <Routine Name="R" Type="RLL"><RLLContent></RLLContent></Routine>
      <Routine Name="Dead" Type="RLL"><RLLContent></RLLContent></Routine>
    </Routines></Program>` }),
  'EMPTY_ROUTINE', 'info', true);

// ═══════ 11. REDUNDANT RUNGS ═══════
test('Redundant: 3x NOP',
  makeL5X({ programs: makeProgram('Main','R',['NOP();','NOP();','NOP();']) }),
  'REDUNDANT_RUNGS', 'info', true);

test('Redundant: duplicated real logic',
  makeL5X({ programs: makeProgram('Main','R',['XIC(S)OTE(O);','XIC(S)OTE(O);']) }),
  'REDUNDANT_RUNGS', 'info', true);

test('Redundant: unique rungs = OK',
  makeL5X({ programs: makeProgram('Main','R',['XIC(S1)OTE(O1);','XIC(S2)OTE(O2);']) }),
  'REDUNDANT_RUNGS', 'info', false);

// ═══════ 12. UNUSED TAGS ═══════
test('Unused tags: declared never used',
  makeL5X({ tags: makeTag('Orphan','DINT'), programs: makeProgram('Main','R',['NOP();']) }),
  'UNUSED_TAGS', 'info', true);

// ═══════ 13. I/O MODULE MISMATCH ═══════
test('I/O mismatch: ref nonexistent module',
  makeL5X({ 
    programs: makeProgram('Main','R',['XIC(Fake:1:I.Data.0)OTE(O);']),
    modules: makeModule('Real','1756-IB16','Local','1','1')
  }),
  'IO_MODULE_MISMATCH', 'critical', true);

test('I/O match: ref existing module = OK',
  makeL5X({ 
    programs: makeProgram('Main','R',['XIC(Real:1:I.Data.0)OTE(O);']),
    modules: makeModule('Real','1756-IB16','Local','1','1')
  }),
  'IO_MODULE_MISMATCH', 'critical', false);

test('I/O: no modules (partial) = skip check',
  makeL5X({ programs: makeProgram('Main','R',['XIC(Mod:1:I.Data.0)OTE(O);']) }),
  'IO_MODULE_MISMATCH', 'critical', false);

// ═══════ 14. FBD SUPPORT ═══════

function makeFBDRoutine(name, sheets) {
  const sheetsXml = sheets.map((s, i) => 
    `<Sheet Number="${i}" Description="">${s}</Sheet>`
  ).join('\n');
  return `<Routine Name="${name}" Type="FBD"><FBDContent>${sheetsXml}</FBDContent></Routine>`;
}

function makeProgramWithFBD(name, routineName, fbdSheets, opts = {}) {
  const faultAttr = opts.faultRoutine ? ` FaultRoutineName="${opts.faultRoutine}"` : '';
  return `<Program Name="${name}" MainRoutineName="${routineName}"${faultAttr}>
    <Tags></Tags>
    <Routines>${makeFBDRoutine(routineName, fbdSheets)}</Routines>
  </Program>`;
}

// FBD: Duplicate OTE via Block elements
test('FBD: Duplicate OTE across sheets',
  makeL5X({ programs: makeProgramWithFBD('Main', 'FBD1', [
    '<IRef ID="1" Operand="Start"/><Block ID="2" Type="OTE" Operand="Motor1"/>',
    '<IRef ID="1" Operand="Stop"/><Block ID="2" Type="OTE" Operand="Motor1"/>',
  ]) }),
  'DUPLICATE_OTE', 'critical', true);

// FBD: Unconditional output (Block OTE with no IREF)
test('FBD: Unconditional OTE (no input ref)',
  makeL5X({ programs: makeProgramWithFBD('Main', 'FBD2', [
    '<Block ID="1" Type="OTE" Operand="PumpRun"/>',
  ]) }),
  'UNCONDITIONAL_OUTPUT', 'warning', true);

// FBD: Conditional OTE (has IREF) = OK
test('FBD: Conditional OTE with IREF = OK',
  makeL5X({ programs: makeProgramWithFBD('Main', 'FBD3', [
    '<IRef ID="1" Operand="Enable"/><Block ID="2" Type="OTE" Operand="Output1"/>',
  ]) }),
  'UNCONDITIONAL_OUTPUT', 'warning', false);

// FBD: Unconditional timer
test('FBD: Unconditional TON',
  makeL5X({ programs: makeProgramWithFBD('Main', 'FBD4', [
    '<Block ID="1" Type="TON" Operand="MyTimer"/>',
  ]) }),
  'UNCONDITIONAL_TIMER', 'warning', true);

// FBD: Tags appear in cross-reference (unused tag detection)
test('FBD: Unused tag with FBD routine',
  makeL5X({
    tags: makeTag('Orphan','DINT'),
    programs: makeProgramWithFBD('Main', 'FBD5', [
      '<IRef ID="1" Operand="UsedTag"/><Block ID="2" Type="OTE" Operand="Output"/>',
    ]),
  }),
  'UNUSED_TAGS', 'info', true);

// FBD: OTL without OTU
test('FBD: OTL no OTU (latch stuck)',
  makeL5X({ programs: makeProgramWithFBD('Main', 'FBD6', [
    '<IRef ID="1" Operand="Trigger"/><Block ID="2" Type="OTL" Operand="StickyBit"/>',
  ]) }),
  'LATCH_NO_UNLATCH', 'warning', true);

// ═══════ 15. PRODUCED/CONSUMED TAGS ═══════

// Produced tag never written — stale data broadcasting
test('Produced tag never written in logic',
  makeL5X({
    tags: '<Tag Name="SharedData" TagType="Produced" DataType="DINT"/>',
    programs: makeProgram('Main', 'R', ['XIC(Start)OTE(Motor);']),
  }),
  'PRODUCED_NEVER_WRITTEN', 'warning', true);

// Produced tag that IS written — OK
test('Produced tag written in logic = OK',
  makeL5X({
    tags: '<Tag Name="SharedData" TagType="Produced" DataType="DINT"/>',
    programs: makeProgram('Main', 'R', ['XIC(Start)MOV(1,SharedData);']),
  }),
  'PRODUCED_NEVER_WRITTEN', 'warning', false);

// Consumed tag never read — wasting bandwidth
test('Consumed tag never read in logic',
  makeL5X({
    tags: '<Tag Name="RemoteData" TagType="Consumed" DataType="DINT"/>',
    programs: makeProgram('Main', 'R', ['XIC(Start)OTE(Motor);']),
  }),
  'CONSUMED_NEVER_READ', 'info', true);

// Consumed tag that IS read — OK
test('Consumed tag read in logic = OK',
  makeL5X({
    tags: '<Tag Name="RemoteData" TagType="Consumed" DataType="DINT"/>',
    programs: makeProgram('Main', 'R', ['XIC(RemoteData.0)OTE(Motor);']),
  }),
  'CONSUMED_NEVER_READ', 'info', false);

// Produced/Consumed tags should NOT appear in unused tags
test('Produced tag not flagged as unused',
  makeL5X({
    tags: '<Tag Name="ProdTag" TagType="Produced" DataType="DINT"/>' + makeTag('Orphan','DINT'),
    programs: makeProgram('Main', 'R', ['XIC(Start)OTE(Motor);']),
  }),
  'UNUSED_TAGS', 'info', true);  // Should find Orphan, not ProdTag

// ═══════ 16. SCAN ORDER ANALYSIS ═══════

// Two OTEs in different programs — scan order determines winner
test('Scan order: duplicate OTE cross-program',
  makeL5X({ programs:
    makeProgram('ProgramA', 'R', ['XIC(Start)OTE(Motor);']) +
    makeProgram('ProgramB', 'R2', ['XIC(Stop)OTE(Motor);'])
  }),
  'SCAN_ORDER_CONFLICT', 'warning', true);

// OTL then OTU in scan order — unlatch wins
test('Scan order: OTL before OTU (unlatch wins)',
  makeL5X({ programs:
    makeProgram('Main', 'R', ['XIC(Start)OTL(Valve);', 'XIC(Stop)OTU(Valve);'])
  }),
  'SCAN_ORDER_CONFLICT', 'info', true);

// Mixed OTE + OTL on same tag — critical
test('Scan order: mixed OTE and OTL (critical)',
  makeL5X({ programs:
    makeProgram('Main', 'R', ['XIC(Start)OTL(Pump);', 'XIC(Enable)OTE(Pump);'])
  }),
  'SCAN_ORDER_CONFLICT', 'critical', true);

// Single OTE — no conflict, should NOT flag
test('Scan order: single OTE = OK',
  makeL5X({ programs:
    makeProgram('Main', 'R', ['XIC(Start)OTE(Motor);'])
  }),
  'SCAN_ORDER_CONFLICT', 'warning', false);

// JSR interleave: OTE in subroutine should scan BEFORE OTE in main routine after the JSR
// Main: Rung 0 = JSR(Sub), Rung 1 = OTE(Motor)
// Sub:  Rung 0 = OTE(Motor)
// Real scan: Main/R0 → Sub/R0[OTE] → Main/R1[OTE] — Main/R1 wins
test('Scan order: JSR interleave — main after JSR wins over subroutine',
  makeL5X({ programs:
    makeProgram('Main', 'MainR', ['JSR(SubR,0);', 'XIC(Stop)OTE(Motor);'], {
      extraRoutines: '<Routine Name="SubR" Type="RLL"><RLLContent><Rung Number="0" Type="N"><Text><![CDATA[XIC(Start)OTE(Motor);]]></Text></Rung></RLLContent></Routine>'
    })
  }),
  'SCAN_ORDER_CONFLICT', 'warning', true);

// ═══════ COMBO ═══════
test('Combo: 5 faults in one file',
  makeL5X({ 
    tags: makeTag('Orphan','DINT'),
    programs: makeProgram('Main','R',[
      'OTE(AlwaysOn);', 'XIC(S1)OTE(V);', 'XIC(S2)OTE(V);',
      'XIC(Hi)OTL(StickyBit);', 'XIC(Run)RTO(Tmr,99,0);', 'XIC(P)CTU(Cnt,0,99);',
    ]),
  }),
  'DUPLICATE_OTE', 'critical', true);

// ═══════ RUN ═══════
console.log('═'.repeat(70));
console.log('FAULTTRACE — FAULT INJECTION TEST HARNESS v2');
console.log('═'.repeat(70));
console.log('');

tests.forEach(t => {
  try {
    const project = L5XParser.parse(t.xml);
    const results = RuleEngine.analyze(project);
    const found = results.findings.some(f => f.rule === t.expectedRule);
    const match = results.findings.find(f => f.rule === t.expectedRule);
    
    if (t.shouldFind && found) {
      const sevOk = !t.expectedSeverity || (match && match.severity === t.expectedSeverity);
      if (sevOk) { console.log('  ✅ ' + t.name); pass++; }
      else { console.log('  ❌ ' + t.name + ' — severity: expected ' + t.expectedSeverity + ', got ' + match.severity); fail++; }
    } else if (!t.shouldFind && !found) {
      console.log('  ✅ ' + t.name + ' (correctly NOT flagged)'); pass++;
    } else if (t.shouldFind && !found) {
      console.log('  ❌ ' + t.name + ' — MISSED! Expected ' + t.expectedRule);
      console.log('     Found: ' + results.findings.map(f => f.rule).join(', ')); fail++;
    } else {
      console.log('  ❌ ' + t.name + ' — FALSE POSITIVE!'); fail++;
    }
  } catch(e) { console.log('  💥 ' + t.name + ' — CRASH: ' + e.message.substring(0,80)); fail++; }
});

console.log('\n' + '═'.repeat(70));
console.log('RESULTS: ' + pass + ' passed, ' + fail + ' failed out of ' + tests.length);
console.log('═'.repeat(70));
