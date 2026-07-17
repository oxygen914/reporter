import { writeFileSync } from "node:fs";

const WIDTH = 1200;
const HEIGHT = 320;
const STROKE_WIDTH = 30;
const APPLE_GRADIENT = [
  { offset: 0, color: "#2997ff", rgb: [0.161, 0.592, 1] },
  { offset: 0.34, color: "#5e5ce6", rgb: [0.369, 0.361, 0.902] },
  { offset: 0.68, color: "#af52de", rgb: [0.686, 0.322, 0.871] },
  { offset: 1, color: "#ff375f", rgb: [1, 0.216, 0.373] },
];

const M = (x, y) => ({ type: "M", x, y });
const L = (x, y) => ({ type: "L", x, y });
const C = (x1, y1, x2, y2, x, y) => ({ type: "C", x1, y1, x2, y2, x, y });
const Z = () => ({ type: "Z" });

// Custom monoline wordmark. Each path is authored in its natural drawing direction.
const paths = [
  { name: "r", letter: 0, commands: [M(72, 226), L(72, 112), L(72, 150), C(93, 119, 128, 111, 157, 130)] },
  { name: "e", letter: 1, commands: [M(292, 198), C(270, 232, 207, 236, 184, 192), C(161, 148, 197, 112, 244, 120), C(280, 126, 297, 151, 288, 171), C(258, 179, 218, 179, 184, 171)] },
  { name: "p", letter: 2, commands: [M(342, 286), L(342, 120), L(342, 151), C(368, 117, 421, 113, 447, 151), C(470, 185, 447, 228, 405, 232), C(376, 235, 353, 218, 342, 198)] },
  { name: "o", letter: 3, commands: [M(527, 176), C(527, 129, 563, 114, 600, 120), C(639, 126, 656, 162, 644, 199), C(632, 236, 580, 244, 546, 216), C(530, 202, 524, 188, 527, 176), Z()] },
  { name: "r-2", letter: 4, commands: [M(696, 226), L(696, 120), L(696, 151), C(716, 121, 748, 112, 777, 130)] },
  { name: "t-stem", letter: 5, commands: [M(836, 76), L(836, 218), C(836, 230, 842, 236, 854, 236)] },
  { name: "t-cross", letter: 5.55, commands: [M(794, 122), L(878, 122)] },
  { name: "e-2", letter: 6, commands: [M(1010, 198), C(988, 232, 925, 236, 902, 192), C(879, 148, 915, 112, 962, 120), C(998, 126, 1015, 151, 1006, 171), C(976, 179, 936, 179, 902, 171)] },
  { name: "r-3", letter: 7, commands: [M(1060, 226), L(1060, 120), L(1060, 151), C(1080, 121, 1115, 112, 1144, 130)] },
];

function svgPath(commands) {
  return commands.map((command) => {
    if (command.type === "M" || command.type === "L") return `${command.type}${command.x} ${command.y}`;
    if (command.type === "C") return `C${command.x1} ${command.y1} ${command.x2} ${command.y2} ${command.x} ${command.y}`;
    return "Z";
  }).join(" ");
}

function lottiePath(commands) {
  const vertices = [];
  const incoming = [];
  const outgoing = [];
  let closed = false;

  for (const command of commands) {
    if (command.type === "M") {
      vertices.push([command.x, command.y]);
      incoming.push([0, 0]);
      outgoing.push([0, 0]);
    } else if (command.type === "L") {
      vertices.push([command.x, command.y]);
      incoming.push([0, 0]);
      outgoing.push([0, 0]);
    } else if (command.type === "C") {
      const previous = vertices.at(-1);
      outgoing[outgoing.length - 1] = [command.x1 - previous[0], command.y1 - previous[1]];
      vertices.push([command.x, command.y]);
      incoming.push([command.x2 - command.x, command.y2 - command.y]);
      outgoing.push([0, 0]);
    } else if (command.type === "Z") {
      closed = true;
    }
  }

  return { i: incoming, o: outgoing, v: vertices, c: closed };
}

const svgStops = APPLE_GRADIENT
  .map(({ offset, color }) => `<stop offset="${offset * 100}%" stop-color="${color}"/>`)
  .join("");
const svgPaths = paths
  .map(({ name, commands }) => `<path id="${name}" d="${svgPath(commands)}"/>`)
  .join("\n    ");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}" fill="none">
  <defs>
    <linearGradient id="apple-gradient" gradientUnits="userSpaceOnUse" x1="56" y1="160" x2="1158" y2="160">
      ${svgStops}
    </linearGradient>
  </defs>
  <g fill="none" stroke="url(#apple-gradient)" stroke-width="${STROKE_WIDTH}" stroke-linecap="round" stroke-linejoin="round">
    ${svgPaths}
  </g>
</svg>\n`;

const gradientColors = APPLE_GRADIENT.flatMap(({ offset, rgb }) => [offset, ...rgb]);
const staticProperty = (value) => ({ a: 0, k: value });
const easeInOut = {
  o: { x: [0.42], y: [0] },
  i: { x: [0.58], y: [1] },
};

function trimEnd(start, duration = 34) {
  return {
    a: 1,
    k: [
      { t: start, s: [0], e: [100], ...easeInOut },
      { t: start + duration, s: [100] },
    ],
  };
}

function layerForPath({ name, letter, commands }, index) {
  const start = Math.round(5 + letter * 11);
  return {
    ty: 4,
    nm: `reporter-${name}`,
    ip: 0,
    op: 150,
    st: 0,
    ks: {
      o: staticProperty(100),
      r: staticProperty(0),
      p: staticProperty([0, 0, 0]),
      a: staticProperty([0, 0, 0]),
      s: staticProperty([100, 100, 100]),
    },
    shapes: [{
      ty: "gr",
      nm: `glyph-${index + 1}`,
      it: [
        { ty: "sh", nm: `${name}-path`, ks: staticProperty(lottiePath(commands)) },
        {
          ty: "gs",
          nm: "Apple gradient stroke",
          o: staticProperty(100),
          w: staticProperty(STROKE_WIDTH),
          lc: 2,
          lj: 2,
          ml: 4,
          g: { p: APPLE_GRADIENT.length, k: staticProperty(gradientColors) },
          s: staticProperty([56, 160]),
          e: staticProperty([1158, 160]),
          t: 1,
        },
        { ty: "tm", nm: "Natural path reveal", s: staticProperty(0), e: trimEnd(start), o: staticProperty(0), m: 1 },
        { ty: "tr", p: staticProperty([0, 0]), a: staticProperty([0, 0]), s: staticProperty([100, 100]), r: staticProperty(0), o: staticProperty(100) },
      ],
    }],
  };
}

const lottie = {
  v: "5.7.0",
  fr: 60,
  ip: 0,
  op: 150,
  w: WIDTH,
  h: HEIGHT,
  nm: "reporter — natural SVG path reveal",
  ddd: 0,
  assets: [],
  layers: paths.map(layerForPath).reverse(),
};

writeFileSync(new URL("./reporter.svg", import.meta.url), svg);
writeFileSync(new URL("./lottie.json", import.meta.url), `${JSON.stringify(lottie, null, 2)}\n`);
