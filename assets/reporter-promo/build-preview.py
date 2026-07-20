#!/usr/bin/env python3
"""Render the reporter SVG-path choreography as a transparent animated WebP preview."""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
SVG_PATH = ROOT / "reporter.svg"
OUTPUT_PATH = ROOT / "reporter.webp"
WIDTH, HEIGHT = 1200, 320
SCALE = 2
FRAME_COUNT = 72
FPS = 24
STROKE_WIDTH = 30
COLORS = [
    (0.00, (41, 151, 255)),
    (0.34, (94, 92, 230)),
    (0.68, (175, 82, 222)),
    (1.00, (255, 55, 95)),
]


def mix(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def gradient_color(x: float) -> tuple[int, int, int, int]:
    position = min(1.0, max(0.0, (x - 56) / (1158 - 56)))
    for (left_pos, left), (right_pos, right) in zip(COLORS, COLORS[1:]):
        if position <= right_pos:
            amount = (position - left_pos) / (right_pos - left_pos)
            return tuple(mix(left[i], right[i], amount) for i in range(3)) + (255,)
    return COLORS[-1][1] + (255,)


def cubic_bezier_y(x: float) -> float:
    # CSS ease-in-out: cubic-bezier(.42, 0, .58, 1).
    lo, hi = 0.0, 1.0
    for _ in range(18):
        t = (lo + hi) / 2
        xt = 3 * (1 - t) ** 2 * t * 0.42 + 3 * (1 - t) * t**2 * 0.58 + t**3
        if xt < x:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return 3 * (1 - t) * t**2 + t**3


TOKEN = re.compile(r"[MLCZ]|-?\d+(?:\.\d+)?")


def sample_svg_path(path_data: str) -> list[tuple[float, float]]:
    tokens = TOKEN.findall(path_data)
    points: list[tuple[float, float]] = []
    cursor = 0
    current = (0.0, 0.0)
    first = (0.0, 0.0)
    while cursor < len(tokens):
        command = tokens[cursor]
        cursor += 1
        if command in {"M", "L"}:
            point = (float(tokens[cursor]), float(tokens[cursor + 1]))
            cursor += 2
            current = point
            if command == "M":
                first = point
            points.append(point)
        elif command == "C":
            c1 = (float(tokens[cursor]), float(tokens[cursor + 1]))
            c2 = (float(tokens[cursor + 2]), float(tokens[cursor + 3]))
            target = (float(tokens[cursor + 4]), float(tokens[cursor + 5]))
            cursor += 6
            start = current
            for step in range(1, 25):
                t = step / 24
                u = 1 - t
                points.append((
                    u**3 * start[0] + 3 * u**2 * t * c1[0] + 3 * u * t**2 * c2[0] + t**3 * target[0],
                    u**3 * start[1] + 3 * u**2 * t * c1[1] + 3 * u * t**2 * c2[1] + t**3 * target[1],
                ))
            current = target
        elif command == "Z":
            points.append(first)
            current = first
    return points


def visible_points(points: list[tuple[float, float]], progress: float) -> list[tuple[float, float]]:
    if progress <= 0 or len(points) < 2:
        return []
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    target = sum(lengths) * min(1.0, progress)
    output = [points[0]]
    travelled = 0.0
    for start, end, length in zip(points, points[1:], lengths):
        if travelled + length <= target:
            output.append(end)
            travelled += length
            continue
        remainder = max(0.0, target - travelled)
        amount = remainder / length if length else 0
        output.append((start[0] + (end[0] - start[0]) * amount, start[1] + (end[1] - start[1]) * amount))
        break
    return output


def draw_path(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], alpha: int) -> None:
    if len(points) < 2:
        return
    scaled = [(x * SCALE, y * SCALE) for x, y in points]
    width = STROKE_WIDTH * SCALE
    radius = width // 2
    for start, end in zip(scaled, scaled[1:]):
        color = gradient_color((start[0] + end[0]) / (2 * SCALE))[:3] + (alpha,)
        draw.line([start, end], fill=color, width=width)
        for x, y in (start, end):
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)


tree = ET.parse(SVG_PATH)
svg_paths = [sample_svg_path(node.attrib["d"]) for node in tree.getroot().iter("{http://www.w3.org/2000/svg}path")]
letter_positions = [0, 1, 2, 3, 4, 5, 5.55, 6, 7]
frames: list[Image.Image] = []

for frame_index in range(FRAME_COUNT):
    lottie_frame = frame_index / (FRAME_COUNT - 1) * 149
    fade = 1.0
    if frame_index >= FRAME_COUNT - 8:
        fade = (FRAME_COUNT - 1 - frame_index) / 7
    canvas = Image.new("RGBA", (WIDTH * SCALE, HEIGHT * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")
    for points, letter in zip(svg_paths, letter_positions):
        start = round(5 + letter * 11)
        raw = min(1.0, max(0.0, (lottie_frame - start) / 34))
        draw_path(draw, visible_points(points, cubic_bezier_y(raw)), round(255 * fade))
    frames.append(canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS))

frames[0].save(
    OUTPUT_PATH,
    save_all=True,
    append_images=frames[1:],
    duration=round(1000 / FPS),
    loop=1,
    lossless=False,
    quality=90,
    method=6,
)
