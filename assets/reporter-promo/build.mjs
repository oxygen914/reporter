import { writeFileSync } from "node:fs";

const C = {
  bg: [0.027, 0.043, 0.082, 1],
  surface: [0.067, 0.094, 0.157, 1],
  muted: [0.31, 0.38, 0.5, 1],
  white: [0.93, 0.96, 1, 1],
  codex: [0.18, 0.55, 1, 1],
  claude: [0.67, 0.38, 1, 1],
  success: [0.18, 0.83, 0.58, 1],
};

const easeOut = {
  o: { x: [0.2], y: [0.75] },
  i: { x: [0.34], y: [0.94] },
};

const p = (k) => {
  const sid = k === C.bg ? "bgColor"
    : k === C.codex ? "codexColor"
      : k === C.claude ? "claudeColor"
        : k === C.success ? "successColor"
          : undefined;
  return sid ? { a: 0, k, sid } : { a: 0, k };
};
const animated = (frames) => ({ a: 1, k: frames });
const kf = (t, s, e, ease = easeOut) => ({ t, s, e, ...ease });
const end = (t, s) => ({ t, s });

function transform(x, y, scale = [100, 100], opacity = 100) {
  return {
    o: p(opacity), r: p(0), a: p([0, 0, 0]),
    s: p([...scale, 100]), p: p([x, y, 0]),
  };
}

function group(items, x = 0, y = 0, opacity = 100) {
  return {
    ty: "gr",
    it: [
      ...items,
      { ty: "tr", p: p([x, y]), a: p([0, 0]), s: p([100, 100]), r: p(0), o: p(opacity) },
    ],
  };
}

function rect(w, h, radius, color, stroke = null, strokeWidth = 2) {
  const items = [{ ty: "rc", p: p([0, 0]), s: p([w, h]), r: p(radius) }];
  if (color) items.push({ ty: "fl", c: p(color), o: p(100) });
  if (stroke) items.push({ ty: "st", c: p(stroke), o: p(100), w: p(strokeWidth), lc: 2, lj: 2 });
  return items;
}

function ellipse(w, h, color, stroke = null, strokeWidth = 2) {
  const items = [{ ty: "el", p: p([0, 0]), s: p([w, h]) }];
  if (color) items.push({ ty: "fl", c: p(color), o: p(100) });
  if (stroke) items.push({ ty: "st", c: p(stroke), o: p(100), w: p(strokeWidth), lc: 2, lj: 2 });
  return items;
}

function line(x1, y1, x2, y2, color, width = 4, opacity = 100) {
  return group([
    { ty: "sh", ks: p({ i: [[0, 0], [0, 0]], o: [[0, 0], [0, 0]], v: [[x1, y1], [x2, y2]], c: false }) },
    { ty: "st", c: p(color), o: p(opacity), w: p(width), lc: 2, lj: 2 },
  ]);
}

function layer(name, shapes, x = 0, y = 0, ip = 0, op = 180, ks = transform(x, y)) {
  return { ty: 4, nm: name, ip, op, st: 0, ks, shapes };
}

function revealKs(x, y, start, fromX = x, fromY = y + 24) {
  return {
    o: animated([kf(start, [0], [100]), end(start + 14, [100])]),
    r: p(0), a: p([0, 0, 0]), s: p([100, 100, 100]),
    p: animated([kf(start, [fromX, fromY, 0], [x, y, 0]), end(start + 18, [x, y, 0])]),
  };
}

const layers = [];

// Final report cards: daily, weekly, monthly.
[
  { x: 468, accent: C.codex, start: 88, bars: [72, 54, 62] },
  { x: 600, accent: C.success, start: 94, bars: [76, 64, 48] },
  { x: 732, accent: C.claude, start: 100, bars: [58, 74, 61] },
].forEach(({ x, accent, start, bars }, index) => {
  const shapes = [
    group(rect(38, 8, 4, accent), -25, -38),
    ...bars.map((w, i) => group(rect(w, 5, 2.5, i === 0 ? C.white : C.muted), 0, -10 + i * 18)),
    group(ellipse(12, 12, C.success), 36, 39),
    group(rect(108, 116, 14, C.surface, [0.18, 0.23, 0.34, 1], 2)),
  ];
  layers.push(layer(`report-${index + 1}`, shapes, x, 500, 0, 180, revealKs(x, 500, start)));
});

// Central Reporter hub and document/check symbol.
layers.push(layer("reporter-hub", [
  group(rect(38, 6, 3, C.codex), -5, -23),
  group(rect(42, 6, 3, C.muted), -3, -7),
  group(rect(30, 6, 3, C.muted), -9, 9),
  group([
    { ty: "sh", ks: p({ i: [[0, 0], [0, 0], [0, 0]], o: [[0, 0], [0, 0], [0, 0]], v: [[-12, 1], [-2, 11], [17, -13]], c: false }) },
    { ty: "st", c: p(C.success), o: p(100), w: p(7), lc: 2, lj: 2 },
  ], 20, 22),
  group(rect(66, 82, 10, C.white), 0, -4),
  group(ellipse(142, 142, [0.04, 0.07, 0.13, 1], C.success, 4)),
  group(ellipse(190, 190, C.surface, [0.2, 0.29, 0.44, 1], 3)),
], 600, 302, 0, 180, revealKs(600, 302, 44, 600, 338)));

// Flow traces.
[
  { name: "codex-flow", vertices: [[352, 252], [430, 252], [482, 302], [505, 302]], color: C.codex, start: 24 },
  { name: "claude-flow", vertices: [[848, 252], [770, 252], [718, 302], [695, 302]], color: C.claude, start: 30 },
  { name: "report-flow", vertices: [[600, 397], [600, 431]], color: C.success, start: 72 },
].forEach(({ name, vertices, color, start }) => {
  layers.push(layer(name, [group([
    { ty: "sh", ks: p({ i: vertices.map(() => [0, 0]), o: vertices.map(() => [0, 0]), v: vertices, c: false }) },
    { ty: "st", c: p(color), o: p(90), w: p(5), lc: 2, lj: 2 },
    { ty: "tm", s: p(0), e: animated([kf(start, [0], [100]), end(start + 25, [100])]), o: p(0), m: 1 },
  ])]));
});

// Moving evidence particles.
[
  { name: "codex-particle", color: C.codex, start: [352, 252, 0], mid: [482, 302, 0], finish: [540, 302, 0], t: 26 },
  { name: "claude-particle", color: C.claude, start: [848, 252, 0], mid: [718, 302, 0], finish: [660, 302, 0], t: 32 },
].forEach(({ name, color, start, mid, finish, t }) => {
  const ks = transform(0, 0);
  ks.p = animated([kf(t, start, mid), kf(t + 18, mid, finish), end(t + 28, finish)]);
  ks.o = animated([kf(t, [0], [100]), kf(t + 8, [100], [100]), kf(t + 22, [100], [0]), end(t + 28, [0])]);
  layers.push(layer(name, [group(ellipse(16, 16, color))], 0, 0, 0, 180, ks));
});

// Codex source panel.
layers.push(layer("codex-source", [
  group(ellipse(16, 16, C.codex), -88, -65),
  group(rect(70, 8, 4, C.white), -34, -65),
  group(rect(166, 7, 3.5, C.muted), -20, -28),
  group(rect(128, 7, 3.5, C.codex), -39, -5),
  group(rect(152, 7, 3.5, C.muted), -27, 18),
  group(rect(98, 7, 3.5, C.muted), -54, 41),
  group(rect(7, 22, 3.5, C.codex), 16, 41),
  group(rect(236, 184, 20, C.surface, [0.12, 0.36, 0.7, 1], 3)),
], 234, 252, 0, 180, revealKs(234, 252, 8, 194, 252)));

// Claude source panel.
layers.push(layer("claude-source", [
  group(ellipse(16, 16, C.claude), -88, -65),
  group(rect(78, 8, 4, C.white), -29, -65),
  group(rect(142, 7, 3.5, C.muted), -32, -28),
  group(rect(164, 7, 3.5, C.claude), -21, -5),
  group(rect(118, 7, 3.5, C.muted), -44, 18),
  group(rect(150, 7, 3.5, C.muted), -28, 41),
  group(rect(236, 184, 20, C.surface, [0.45, 0.24, 0.7, 1], 3)),
], 966, 252, 0, 180, revealKs(966, 252, 14, 1006, 252)));

// Header mark: three compact report tabs, no font dependency.
layers.push(layer("header-mark", [
  group(rect(62, 12, 6, C.codex), -78, 0),
  group(rect(62, 12, 6, C.success), 0, 0),
  group(rect(62, 12, 6, C.claude), 78, 0),
], 600, 108, 0, 180, revealKs(600, 108, 2, 600, 84)));

// Quiet grid and full-frame background.
const grid = [];
for (let x = 80; x < 1200; x += 80) grid.push(line(x, 0, x, 630, [0.12, 0.16, 0.24, 1], 1, 35));
for (let y = 70; y < 630; y += 70) grid.push(line(0, y, 1200, y, [0.12, 0.16, 0.24, 1], 1, 35));
layers.push(layer("grid", grid));
layers.push(layer("background", [group([
  { ty: "rc", p: p([0, 0]), s: p([1200, 630]), r: p(0) },
  { ty: "fl", c: { a: 0, k: C.bg, sid: "bgColor" }, o: p(100) },
])], 600, 315));

const lottie = {
  v: "5.7.0", fr: 60, ip: 0, op: 180, w: 1200, h: 630,
  nm: "Reporter — Codex + Claude Code to Work Reports",
  assets: [],
  slots: {
    bgColor: { p: { a: 0, k: C.bg } },
    codexColor: { p: { a: 0, k: C.codex } },
    claudeColor: { p: { a: 0, k: C.claude } },
    successColor: { p: { a: 0, k: C.success } },
  },
  layers,
};

const controls = {
  controls: [
    { sid: "bgColor", label: "Background" },
    { sid: "codexColor", label: "Codex accent" },
    { sid: "claudeColor", label: "Claude accent" },
    { sid: "successColor", label: "Report accent" },
  ],
};

writeFileSync(new URL("./lottie.json", import.meta.url), `${JSON.stringify(lottie, null, 2)}\n`);
writeFileSync(new URL("./controls.json", import.meta.url), `${JSON.stringify(controls, null, 2)}\n`);
