#!/usr/bin/env python3
"""plot_filter.py <filter.csv> <out.svg>: the known-answer cloud of the launch test on a height axis:
each point sent on /velodyne_points, filled if the node returned it on /velodyne_filtered,
with the pass-through band (-0.3 to 5.0 m) shaded. Standard library only."""
import csv
import sys

rows = [(float(r['z']), r['returned'] == '1') for r in csv.DictReader(open(sys.argv[1]))]
LO, HI = -1.5, 9.0
W, H, X0, X1 = 520, 360, 60, 380


def Y(z):
    return 20 + (HI - z) / (HI - LO) * (H - 60)


el = [f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
      f'<rect x="{X0}" y="{Y(5.0):.1f}" width="{X1 - X0}" height="{Y(-0.3) - Y(5.0):.1f}" fill="#e8f3f5"/>',
      f'<line x1="{X0}" y1="{Y(5.0):.1f}" x2="{X1}" y2="{Y(5.0):.1f}" stroke="#005f73" stroke-dasharray="5 4"/>',
      f'<line x1="{X0}" y1="{Y(-0.3):.1f}" x2="{X1}" y2="{Y(-0.3):.1f}" stroke="#005f73" stroke-dasharray="5 4"/>',
      f'<text x="{X1 + 8}" y="{Y(5.0) + 4:.1f}" fill="#005f73">z = 5.0 m</text>',
      f'<text x="{X1 + 8}" y="{Y(-0.3) + 4:.1f}" fill="#005f73">z = -0.3 m</text>',
      f'<text x="{X1 + 8}" y="{Y(2.35):.1f}" fill="#005f73">kept band</text>',
      f'<line x1="{X0 - 10}" y1="{Y(HI):.1f}" x2="{X0 - 10}" y2="{Y(LO):.1f}" stroke="#9aa5b1"/>']
for z in range(-1, 10, 1):
    el.append(f'<text x="{X0 - 16}" y="{Y(z) + 4:.1f}" text-anchor="end" fill="#6b7785">{z}</text>')
rows.sort()
for i, (z, kept) in enumerate(rows):
    x = X0 + 25 + i * (X1 - X0 - 50) / max(1, len(rows) - 1)
    fill = '#005f73' if kept else '#ffffff'
    el.append(f'<circle cx="{x:.1f}" cy="{Y(z):.1f}" r="6" fill="{fill}" stroke="#005f73" stroke-width="2"/>')
    el.append(f'<text x="{x:.1f}" y="{Y(z) - 10:.1f}" text-anchor="middle" fill="#3f4d58" font-size="11">{z:g}</text>')
n_in, n_out = len(rows), sum(k for _, k in rows)
el.append(f'<text x="8" y="{H - 22}" fill="#3f4d58">{n_in} points sent on /velodyne_points (z, m, sensor frame); '
          f'filled = returned ({n_out}).</text>')
el.append(f'<text x="8" y="{H - 6}" fill="#3f4d58">From the CI launch test: points 0.01 m either side of each limit.</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="Helvetica, Arial, sans-serif" font-size="12">\n' + '\n'.join(el) + '\n</svg>\n')
open(sys.argv[2], 'w').write(svg)
print(f'{sys.argv[2]}: {n_in} in, {n_out} out')
