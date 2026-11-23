import numpy as np
from PIL import Image
from collections import deque

p = r'd:\Dane\Documents\Trae\temp_20261123_04\_tmp_board.png'
im = Image.open(p).convert('RGB')
a = np.array(im).astype(np.int16)
H, W, _ = a.shape
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]

red_mask = (R - G > 25) & (R - B > 45) & (R > 75) & (G < 105)
dark_mask = (abs(R - G) < 14) & (abs(G - B) < 14) & (R < 135) & (R > 45)

def comps(mask, minpix):
    visited = np.zeros_like(mask, dtype=bool)
    out = []
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        if visited[y, x]:
            continue
        q = deque([(y, x)])
        visited[y, x] = True
        pts = []
        while q:
            cy, cx = q.popleft()
            pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        q.append((ny, nx))
        if len(pts) >= minpix:
            ys2 = np.array([q[0] for q in pts]); xs2 = np.array([q[1] for q in pts])
            out.append(dict(cx=float(xs2.mean()), cy=float(ys2.mean()), n=len(pts),
                            w=int(xs2.max()-xs2.min()), h=int(ys2.max()-ys2.min())))
    return out

for name, mask in (('RED', red_mask), ('DARK', dark_mask)):
    cs = comps(mask, 800)
    cs = [c for c in cs if 25 < c['w'] < 120 and 25 < c['h'] < 120]
    print(name, len(cs))
    for c in sorted(cs, key=lambda t: (round(t['cy']/50), t['cx'])):
        print('  %s cx=%.0f cy=%.0f n=%d w=%d h=%d' % (name, c['cx'], c['cy'], c['n'], c['w'], c['h']))
