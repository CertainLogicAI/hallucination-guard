// FaultTrace — Electrical Schematic Generator
// Generates SVG schematics from a parts list / component database

const SYMBOLS = {
  // Grid settings
  GRID: 20,
  PAGE_W: 1100,
  PAGE_H: 850,
  MARGIN: 60,
  WIRE_COLOR: '#e4e4e7',
  SYMBOL_COLOR: '#e4e4e7',
  TEXT_COLOR: '#a1a1aa',
  ACCENT_COLOR: '#f59e0b',
  SAFETY_COLOR: '#ef4444',
  BG_COLOR: '#0a0a0b',
  BORDER_COLOR: '#2a2a2e',
};

// ============ SVG HELPERS ============
function svgHeader(pageNum, title, w = SYMBOLS.PAGE_W, h = SYMBOLS.PAGE_H) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" style="background:${SYMBOLS.BG_COLOR}">
  <style>
    text { font-family: 'Courier New', monospace; fill: ${SYMBOLS.TEXT_COLOR}; }
    .title { font-size: 14px; font-weight: bold; fill: ${SYMBOLS.ACCENT_COLOR}; }
    .subtitle { font-size: 10px; fill: ${SYMBOLS.TEXT_COLOR}; }
    .wire-label { font-size: 8px; fill: ${SYMBOLS.ACCENT_COLOR}; }
    .comp-label { font-size: 9px; fill: ${SYMBOLS.WIRE_COLOR}; font-weight: bold; }
    .desc-label { font-size: 7px; fill: ${SYMBOLS.TEXT_COLOR}; }
    .terminal { font-size: 7px; fill: ${SYMBOLS.TEXT_COLOR}; }
    .wire { stroke: ${SYMBOLS.WIRE_COLOR}; stroke-width: 1.5; fill: none; }
    .wire-thick { stroke: ${SYMBOLS.WIRE_COLOR}; stroke-width: 2.5; fill: none; }
    .symbol { stroke: ${SYMBOLS.SYMBOL_COLOR}; stroke-width: 1.5; fill: none; }
    .symbol-fill { stroke: ${SYMBOLS.SYMBOL_COLOR}; stroke-width: 1.5; fill: ${SYMBOLS.SYMBOL_COLOR}; }
    .safety { stroke: ${SYMBOLS.SAFETY_COLOR}; stroke-width: 1.5; fill: none; }
    .safety-fill { stroke: ${SYMBOLS.SAFETY_COLOR}; stroke-width: 1.5; fill: ${SYMBOLS.SAFETY_COLOR}; }
    .border { stroke: ${SYMBOLS.BORDER_COLOR}; stroke-width: 1; fill: none; }
    .grid-line { stroke: ${SYMBOLS.BORDER_COLOR}; stroke-width: 0.3; opacity: 0.3; }
    .title-block { stroke: ${SYMBOLS.BORDER_COLOR}; stroke-width: 1; fill: rgba(20,20,22,0.9); }
  </style>
  <!-- Border -->
  <rect x="10" y="10" width="${w-20}" height="${h-20}" class="border"/>
  <!-- Title block -->
  <rect x="10" y="${h-70}" width="${w-20}" height="60" class="title-block"/>
  <text x="25" y="${h-48}" class="title">FaultTrace AI — ${title}</text>
  <text x="25" y="${h-33}" class="subtitle">Page ${pageNum} | Generated ${new Date().toLocaleDateString()}</text>
  <text x="${w-200}" y="${h-48}" class="subtitle">Project: Auto-Generated</text>
  <text x="${w-200}" y="${h-33}" class="subtitle">Revision: A (AI Draft)</text>
`;
}

function svgFooter() {
  return '</svg>';
}

function line(x1, y1, x2, y2, cls = 'wire') {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"/>`;
}

function text(x, y, content, cls = '', anchor = 'start') {
  return `<text x="${x}" y="${y}" class="${cls}" text-anchor="${anchor}">${content}</text>`;
}

function circle(cx, cy, r, cls = 'symbol') {
  return `<circle cx="${cx}" cy="${cy}" r="${r}" class="${cls}"/>`;
}

function rect(x, y, w, h, cls = 'symbol') {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" class="${cls}"/>`;
}

// ============ ELECTRICAL SYMBOLS ============

function drawNOContact(x, y, label, wireNum) {
  // Normally Open contact: two vertical lines with gap
  let svg = '';
  svg += line(x, y, x + 8, y);
  svg += line(x + 8, y - 8, x + 8, y + 8);
  svg += line(x + 22, y - 8, x + 22, y + 8);
  svg += line(x + 22, y, x + 30, y);
  svg += text(x + 15, y - 12, label, 'comp-label', 'middle');
  if (wireNum) svg += text(x + 15, y + 18, wireNum, 'wire-label', 'middle');
  return svg;
}

function drawNCContact(x, y, label, wireNum) {
  // Normally Closed contact: two vertical lines with diagonal
  let svg = '';
  svg += line(x, y, x + 8, y);
  svg += line(x + 8, y - 8, x + 8, y + 8);
  svg += line(x + 22, y - 8, x + 22, y + 8);
  svg += line(x + 22, y, x + 30, y);
  svg += line(x + 6, y + 8, x + 24, y - 8); // diagonal slash
  svg += text(x + 15, y - 12, label, 'comp-label', 'middle');
  if (wireNum) svg += text(x + 15, y + 18, wireNum, 'wire-label', 'middle');
  return svg;
}

function drawCoil(x, y, label) {
  // Relay/output coil: circle with parentheses
  let svg = '';
  svg += line(x, y, x + 8, y);
  svg += circle(x + 20, y, 12);
  svg += line(x + 32, y, x + 40, y);
  svg += text(x + 20, y + 4, label, 'comp-label', 'middle');
  return svg;
}

function drawOverload(x, y, label) {
  // Thermal overload: rectangle with heater symbol
  let svg = '';
  svg += line(x, y, x + 5, y);
  svg += rect(x + 5, y - 10, 20, 20);
  // Heater zigzag inside
  svg += `<polyline points="${x+8},${y-5} ${x+12},${y+5} ${x+16},${y-5} ${x+20},${y+5} ${x+22},${y}" class="symbol"/>`;
  svg += line(x + 25, y, x + 30, y);
  svg += text(x + 15, y - 14, label, 'comp-label', 'middle');
  return svg;
}

function drawMotor(x, y, label, hp) {
  // Motor symbol: circle with M
  let svg = '';
  svg += line(x, y, x + 5, y);
  svg += circle(x + 20, y, 15);
  svg += text(x + 20, y + 4, 'M', 'comp-label', 'middle');
  svg += text(x + 20, y - 20, label, 'comp-label', 'middle');
  if (hp) svg += text(x + 20, y + 24, hp, 'desc-label', 'middle');
  return svg;
}

function drawEStop(x, y, label) {
  // E-Stop: mushroom head symbol (NC contact with special marker)
  let svg = '';
  svg += line(x, y, x + 8, y);
  svg += line(x + 8, y - 8, x + 8, y + 8, 'safety');
  svg += line(x + 22, y - 8, x + 22, y + 8, 'safety');
  svg += line(x + 22, y, x + 30, y);
  svg += line(x + 6, y + 8, x + 24, y - 8, 'safety'); // NC diagonal
  // Mushroom head indicator
  svg += `<path d="M${x+10},${y-10} Q${x+15},${y-18} ${x+20},${y-10}" class="safety"/>`;
  svg += text(x + 15, y - 20, label, 'comp-label', 'middle');
  svg += text(x + 15, y + 18, 'E-STOP', 'wire-label', 'middle');
  return svg;
}

function drawFuse(x, y, label) {
  // Fuse symbol
  let svg = '';
  svg += line(x, y, x + 5, y);
  svg += rect(x + 5, y - 4, 20, 8);
  svg += line(x + 25, y, x + 30, y);
  svg += text(x + 15, y - 8, label, 'comp-label', 'middle');
  return svg;
}

function drawContactor(x, y, label) {
  // Contactor coil (same as coil but with designation)
  let svg = '';
  svg += line(x, y, x + 8, y);
  svg += circle(x + 20, y, 12);
  svg += text(x + 20, y + 4, label, 'comp-label', 'middle');
  svg += line(x + 32, y, x + 40, y);
  return svg;
}

function drawPowerContacts(x, y, label, phases) {
  // 3-phase power contacts (for contactor in power circuit)
  let svg = '';
  const spacing = 40;
  for (let i = 0; i < phases; i++) {
    const px = x + i * spacing;
    svg += line(px, y, px, y + 10);
    svg += line(px - 5, y + 10, px - 5, y + 25);
    // Moving contact (angled line)
    svg += line(px - 5, y + 25, px + 5, y + 12);
    svg += line(px + 5, y + 25, px + 5, y + 35);
    svg += line(px, y + 35, px, y + 45);
    if (i === 1) svg += text(px, y + 52, label, 'comp-label', 'middle');
  }
  return svg;
}

function drawVFD(x, y, label) {
  // VFD: rectangle with ~ and = symbols
  let svg = '';
  svg += rect(x, y, 80, 100);
  svg += text(x + 40, y - 5, label, 'comp-label', 'middle');
  svg += text(x + 40, y + 20, 'VFD', 'comp-label', 'middle');
  // AC input indicator
  svg += text(x + 20, y + 40, '~', 'comp-label', 'middle');
  svg += text(x + 40, y + 40, '→', 'desc-label', 'middle');
  svg += text(x + 60, y + 40, '~', 'comp-label', 'middle');
  // Terminal labels
  svg += text(x + 10, y + 60, 'R/L1', 'terminal');
  svg += text(x + 35, y + 60, 'S/L2', 'terminal');
  svg += text(x + 60, y + 60, 'T/L3', 'terminal');
  svg += text(x + 10, y + 80, 'U/T1', 'terminal');
  svg += text(x + 35, y + 80, 'V/T2', 'terminal');
  svg += text(x + 60, y + 80, 'W/T3', 'terminal');
  // Control terminals
  svg += text(x + 10, y + 95, 'RUN', 'terminal');
  svg += text(x + 35, y + 95, 'FLT', 'terminal');
  svg += text(x + 60, y + 95, 'SPD', 'terminal');
  return svg;
}

function drawPressureTX(x, y, label) {
  // Pressure transmitter: circle with PT
  let svg = '';
  svg += circle(x + 15, y, 12);
  svg += text(x + 15, y + 4, 'PT', 'comp-label', 'middle');
  svg += text(x + 15, y - 16, label, 'comp-label', 'middle');
  svg += line(x + 15, y + 12, x + 15, y + 25); // process connection
  return svg;
}

function drawTempRTD(x, y, label) {
  // RTD/thermocouple: circle with TE
  let svg = '';
  svg += circle(x + 15, y, 12);
  svg += text(x + 15, y + 4, 'TE', 'comp-label', 'middle');
  svg += text(x + 15, y - 16, label, 'comp-label', 'middle');
  svg += line(x + 15, y + 12, x + 15, y + 25);
  return svg;
}

function drawPushbutton(x, y, label, type = 'NO') {
  // Pushbutton: contact with arrow
  let svg = type === 'NC' ? drawNCContact(x, y, label) : drawNOContact(x, y, label);
  // Arrow indicating pushbutton
  svg += line(x + 15, y + 10, x + 15, y + 20);
  svg += `<polygon points="${x+12},${y+12} ${x+18},${y+12} ${x+15},${y+8}" class="symbol-fill"/>`;
  return svg;
}

function drawIndicatorLight(x, y, label, color) {
  // Indicator light: circle with X
  let svg = '';
  svg += line(x, y, x + 8, y);
  svg += circle(x + 20, y, 10);
  svg += line(x + 13, y - 7, x + 27, y + 7);
  svg += line(x + 13, y + 7, x + 27, y - 7);
  svg += line(x + 30, y, x + 38, y);
  svg += text(x + 20, y - 14, label, 'comp-label', 'middle');
  if (color) svg += text(x + 20, y + 20, color, 'desc-label', 'middle');
  return svg;
}

function drawSolenoid(x, y, label) {
  // Solenoid valve: rectangle with diagonal
  let svg = '';
  svg += line(x, y, x + 5, y);
  svg += rect(x + 5, y - 8, 20, 16);
  svg += line(x + 7, y + 6, x + 23, y - 6);
  svg += line(x + 25, y, x + 30, y);
  svg += text(x + 15, y - 12, label, 'comp-label', 'middle');
  return svg;
}

// ============ PAGE GENERATORS ============

function generatePowerPage(components) {
  const motors = components.filter(c => c.type === 'motor' && c.tag.includes('Contactor'));
  const vfds = components.filter(c => c.tag.includes('VFD'));

  let svg = svgHeader(1, 'Power Distribution & Motor Circuits');

  // L1/L2/L3 bus bars at top
  const busY = 60;
  svg += line(80, busY, SYMBOLS.PAGE_W - 80, busY, 'wire-thick');
  svg += line(80, busY + 20, SYMBOLS.PAGE_W - 80, busY + 20, 'wire-thick');
  svg += line(80, busY + 40, SYMBOLS.PAGE_W - 80, busY + 40, 'wire-thick');
  svg += text(50, busY + 5, 'L1', 'comp-label');
  svg += text(50, busY + 25, 'L2', 'comp-label');
  svg += text(50, busY + 45, 'L3', 'comp-label');

  // Main disconnect
  svg += drawFuse(150, busY, 'FU1');
  svg += drawFuse(150, busY + 20, 'FU2');
  svg += drawFuse(150, busY + 40, 'FU3');
  svg += text(165, busY - 15, 'MAIN FUSES', 'desc-label', 'middle');

  // Motor 1 branch (direct start with contactor)
  const m1x = 200;
  const m1y = 160;
  svg += text(m1x + 60, m1y - 20, 'MOTOR 1 — DIRECT START', 'title');

  // Vertical drops from bus
  for (let i = 0; i < 3; i++) {
    svg += line(m1x + i * 40, busY + i * 20, m1x + i * 40, m1y);
  }

  // Contactor power contacts
  svg += drawPowerContacts(m1x, m1y, 'K1', 3);

  // Overload
  const olY = m1y + 60;
  for (let i = 0; i < 3; i++) {
    svg += drawOverload(m1x + i * 40 - 5, olY, i === 1 ? 'OL1' : '');
  }

  // Motor
  const motY = olY + 40;
  svg += line(m1x, motY, m1x, motY + 20);
  svg += line(m1x + 40, motY, m1x + 40, motY + 20);
  svg += line(m1x + 80, motY, m1x + 80, motY + 20);
  // Connect to motor
  svg += line(m1x, motY + 20, m1x + 80, motY + 20);
  svg += drawMotor(m1x + 25, motY + 50, 'M1', '10 HP');

  // VFD branch
  const vx = 550;
  const vy = 160;
  svg += text(vx + 40, vy - 20, 'MOTOR 2 — VFD', 'title');

  // Vertical drops
  for (let i = 0; i < 3; i++) {
    svg += line(vx + i * 40, busY + i * 20, vx + i * 40, vy);
  }

  // Fuses for VFD
  svg += drawFuse(vx - 5, vy, 'FU4');
  svg += drawFuse(vx + 35, vy, 'FU5');
  svg += drawFuse(vx + 75, vy, 'FU6');

  // VFD
  svg += drawVFD(vx - 10, vy + 30, 'VFD1');

  // Motor from VFD
  svg += drawMotor(vx + 25, vy + 165, 'M2', 'VFD Controlled');

  svg += svgFooter();
  return svg;
}

function generateControlPage(components) {
  const safetyDevices = components.filter(c => c.type === 'safety');
  const buttons = components.filter(c => c.tag.includes('PB') || c.tag.includes('Start') || c.tag.includes('Stop'));

  let svg = svgHeader(2, 'Control Circuit — Motor Start/Stop & Safety');

  // Control power rails
  const railL = 60;
  const railR = SYMBOLS.PAGE_W - 60;
  const topY = 70;

  svg += line(railL, topY, railL, 650, 'wire-thick');
  svg += line(railR, topY, railR, 650, 'wire-thick');
  svg += text(railL - 5, topY - 5, 'L1', 'comp-label', 'end');
  svg += text(railR + 5, topY - 5, 'L2', 'comp-label', 'start');
  svg += text(railL - 5, topY + 15, '120VAC', 'desc-label', 'end');

  // Rung 1: E-Stop + Safety
  let rungY = 100;
  svg += text(railL + 10, rungY - 10, 'RUNG 1 — SAFETY CIRCUIT', 'wire-label');
  svg += line(railL, rungY, railL + 30, rungY);
  svg += drawEStop(railL + 30, rungY, 'S3');
  svg += line(railL + 60, rungY, railL + 100, rungY);
  svg += drawNCContact(railL + 100, rungY, 'OL1', '3');
  svg += line(railL + 130, rungY, railL + 170, rungY);
  svg += drawNCContact(railL + 170, rungY, 'S4', '4');
  svg += text(railL + 185, rungY + 26, 'GUARD', 'desc-label', 'middle');
  svg += line(railL + 200, rungY, railR - 50, rungY);
  svg += drawCoil(railR - 50, rungY, 'CR1');
  svg += line(railR - 10, rungY, railR, rungY);
  svg += text(railR + 5, rungY + 4, '1', 'wire-label');

  // Rung 2: Start/Stop
  rungY = 180;
  svg += text(railL + 10, rungY - 10, 'RUNG 2 — MOTOR START/STOP', 'wire-label');
  svg += line(railL, rungY, railL + 30, rungY);
  svg += drawNOContact(railL + 30, rungY, 'CR1', '5');
  svg += line(railL + 60, rungY, railL + 100, rungY);
  svg += drawNCContact(railL + 100, rungY, 'S2', '6');
  svg += text(railL + 115, rungY + 26, 'STOP', 'desc-label', 'middle');
  svg += line(railL + 130, rungY, railL + 170, rungY);
  svg += drawPushbutton(railL + 170, rungY, 'S1', 'NO');
  svg += text(railL + 185, rungY + 34, 'START', 'desc-label', 'middle');
  svg += line(railL + 200, rungY, railR - 50, rungY);
  svg += drawContactor(railR - 50, rungY, 'K1');
  svg += line(railR - 10, rungY, railR, rungY);
  svg += text(railR + 5, rungY + 4, '2', 'wire-label');

  // Seal-in contact (parallel to start button)
  const sealY = rungY + 35;
  svg += line(railL + 170, rungY, railL + 170, sealY);
  svg += line(railL + 170, sealY, railL + 210, sealY);
  svg += drawNOContact(railL + 210, sealY, 'K1', '7');
  svg += line(railL + 240, sealY, railR - 50, sealY);
  svg += line(railR - 50, sealY, railR - 50, rungY);
  svg += text(railL + 225, sealY + 26, 'SEAL', 'desc-label', 'middle');

  // Rung 3: Run indicator
  rungY = 290;
  svg += text(railL + 10, rungY - 10, 'RUNG 3 — RUN INDICATOR', 'wire-label');
  svg += line(railL, rungY, railL + 30, rungY);
  svg += drawNOContact(railL + 30, rungY, 'K1', '8');
  svg += line(railL + 60, rungY, railR - 50, rungY);
  svg += drawIndicatorLight(railR - 50, rungY, 'H1', 'GREEN');
  svg += line(railR - 12, rungY, railR, rungY);
  svg += text(railR + 5, rungY + 4, '3', 'wire-label');

  // Rung 4: Fault indicator
  rungY = 360;
  svg += text(railL + 10, rungY - 10, 'RUNG 4 — FAULT INDICATOR', 'wire-label');
  svg += line(railL, rungY, railL + 30, rungY);
  svg += drawNCContact(railL + 30, rungY, 'CR1', '9');
  svg += line(railL + 60, rungY, railR - 50, rungY);
  svg += drawIndicatorLight(railR - 50, rungY, 'H2', 'RED');
  svg += line(railR - 12, rungY, railR, rungY);
  svg += text(railR + 5, rungY + 4, '4', 'wire-label');

  // Rung 5: VFD Run command (to PLC)
  rungY = 430;
  svg += text(railL + 10, rungY - 10, 'RUNG 5 — VFD RUN COMMAND', 'wire-label');
  svg += line(railL, rungY, railL + 30, rungY);
  svg += drawNOContact(railL + 30, rungY, 'K1', '10');
  svg += line(railL + 60, rungY, railL + 100, rungY);
  svg += drawNOContact(railL + 100, rungY, 'CR1', '11');
  svg += line(railL + 130, rungY, railR - 50, rungY);
  svg += drawSolenoid(railR - 50, rungY, 'Y1');
  svg += text(railR - 35, rungY + 20, 'SOL VALVE', 'desc-label', 'middle');
  svg += line(railR - 20, rungY, railR, rungY);
  svg += text(railR + 5, rungY + 4, '5', 'wire-label');

  // Rung numbers on left
  svg += line(40, topY, 40, 650);
  for (let i = 1; i <= 5; i++) {
    svg += text(35, 80 + i * 70, String(i), 'wire-label', 'end');
  }

  svg += svgFooter();
  return svg;
}

function generateIOPage(components) {
  let svg = svgHeader(3, 'PLC I/O Wiring');

  const diComps = components.filter(c => c.io && c.io.startsWith('DI'));
  const doComps = components.filter(c => c.io && c.io.startsWith('DO'));
  const aiComps = components.filter(c => c.io && c.io.startsWith('AI'));
  const aoComps = components.filter(c => c.io && c.io.startsWith('AO'));

  // PLC rack drawing
  const rackX = 400;
  const rackY = 60;
  const slotW = 60;
  const slotH = 120;

  // Draw rack
  svg += rect(rackX, rackY, slotW * 6, slotH);
  svg += text(rackX + slotW * 3, rackY - 8, 'PLC RACK — 1756 CHASSIS', 'title', 'middle');

  // Slots
  const slots = ['CPU\n1756-L83E', 'ENET\n1756-EN2T', 'DI\n1756-IB32', 'DO\n1756-OB32', 'AI\n1756-IF8', 'AO\n1756-OF8'];
  slots.forEach((label, i) => {
    const sx = rackX + i * slotW;
    svg += rect(sx, rackY, slotW, slotH);
    svg += text(sx + slotW / 2, rackY + 30, `Slot ${i}`, 'desc-label', 'middle');
    const lines = label.split('\n');
    svg += text(sx + slotW / 2, rackY + 50, lines[0], 'comp-label', 'middle');
    if (lines[1]) svg += text(sx + slotW / 2, rackY + 65, lines[1], 'desc-label', 'middle');
  });

  // DI wiring
  const diX = 60;
  let diY = 220;
  svg += text(diX, diY - 10, 'DIGITAL INPUTS — Slot 2 (1756-IB32)', 'title');
  diComps.forEach((c, i) => {
    const y = diY + i * 28;
    svg += text(diX, y + 4, c.tag, 'comp-label');
    svg += text(diX + 140, y + 4, c.desc, 'desc-label');
    svg += line(diX + 340, y, rackX + slotW * 2 + 30, y, 'wire');
    svg += text(rackX + slotW * 2 + 35, y + 4, `IN${i}`, 'terminal');
    svg += text(diX + 330, y - 4, `W${100 + i}`, 'wire-label', 'end');
    // Terminal circle
    svg += circle(diX + 340, y, 3, 'symbol-fill');
    svg += circle(rackX + slotW * 2 + 30, y, 3, 'symbol-fill');
  });

  // DO wiring
  const doX = 60;
  let doY = diY + diComps.length * 28 + 40;
  svg += text(doX, doY - 10, 'DIGITAL OUTPUTS — Slot 3 (1756-OB32)', 'title');
  doComps.forEach((c, i) => {
    const y = doY + i * 28;
    svg += text(doX, y + 4, c.tag, 'comp-label');
    svg += text(doX + 140, y + 4, c.desc, 'desc-label');
    svg += line(rackX + slotW * 3 + 30, y, diX + 340, y, 'wire');
    svg += text(rackX + slotW * 3 + 35, y + 4, `OUT${i}`, 'terminal');
    svg += text(diX + 330, y - 4, `W${200 + i}`, 'wire-label', 'end');
    svg += circle(diX + 340, y, 3, 'symbol-fill');
    svg += circle(rackX + slotW * 3 + 30, y, 3, 'symbol-fill');
  });

  // AI wiring
  let aiY = doY + doComps.length * 28 + 40;
  svg += text(doX, aiY - 10, 'ANALOG INPUTS — Slot 4 (1756-IF8)', 'title');
  aiComps.forEach((c, i) => {
    const y = aiY + i * 28;
    svg += text(doX, y + 4, c.tag, 'comp-label');
    svg += text(doX + 140, y + 4, c.desc, 'desc-label');
    svg += line(rackX + slotW * 4 + 30, y, diX + 340, y, 'wire');
    svg += text(rackX + slotW * 4 + 35, y + 4, `CH${i}+`, 'terminal');
    svg += text(diX + 330, y - 4, `W${300 + i}`, 'wire-label', 'end');
    svg += circle(diX + 340, y, 3, 'symbol-fill');
    svg += circle(rackX + slotW * 4 + 30, y, 3, 'symbol-fill');
  });

  svg += svgFooter();
  return svg;
}

// ============ MAIN GENERATOR ============

function generateSchematics(components) {
  const pages = [];

  // Page 1: Power distribution
  pages.push({
    title: 'Power Distribution & Motor Circuits',
    svg: generatePowerPage(components)
  });

  // Page 2: Control circuit
  pages.push({
    title: 'Control Circuit — Start/Stop & Safety',
    svg: generateControlPage(components)
  });

  // Page 3: I/O Wiring
  pages.push({
    title: 'PLC I/O Wiring',
    svg: generateIOPage(components)
  });

  return pages;
}

// Export for use in main app
if (typeof module !== 'undefined') module.exports = { generateSchematics };
