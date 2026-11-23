import numpy as np
from PIL import Image, ImageDraw
from collections import deque

p = r'd:\Dane\Documents\Trae\temp_20261123_04\_tmp_board.png'
im = Image.open(p).convert('RGB')
a = np.array(im).astype(np.int16)
H, W, _ = a.shape
R, G, B = a[:,:,0], a[:,:,1], a[:,:,2]

cols = [75, 227, 370, 513, 650, 802, 942, 1088, 1233]
rows = [64, 229, 374, 517, 661, 805, 948, 1093, 1235, 1390]

red_mask = (R - G > 35) & (R - B > 55) & (R > 85) & (R < 215) & (G < 95)
dark_mask = (abs(R - G) < 16) & (abs(G - B) < 18) & (R < 130) & (R > 40) & (G < 130)

def comps(mask, minpix=1500):
    visited = np.zeros_like(mask, dtype=bool)
    out = []
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        if visited[y, x]:
            continue
        q = deque([(y, x)]); visited[y, x] = True; pts = []
        while q:
            cy, cx = q.popleft(); pts.append((cy, cx))
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny, nx = cy+dy, cx+dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True; q.append((ny, nx))
        if len(pts) >= minpix:
            ys2 = np.array([t[0] for t in pts]); xs2 = np.array([t[1] for t in pts])
            w = xs2.max()-xs2.min(); h = ys2.max()-ys2.min()
            if 40 <= w <= 130 and 40 <= h <= 130:
                out.append((float(xs2.mean()), float(ys2.mean()), len(pts), int(w), int(h)))
    return out

def snap(v, arr):
    i = min(range(len(arr)), key=lambda k: abs(arr[k]-v))
    return i, abs(arr[i]-v)

pieces = []
for kind, mask in (('RED', red_mask), ('DARK', dark_mask)):
    for cx, cy, n, w, h in comps(mask):
        ri, dy = snap(cy, rows); ci, dx = snap(cx, cols)
        if dy < 40 and dx < 45:
            pieces.append((ri, ci, kind, cx, cy, n, w, h))

pieces.sort(key=lambda t: (t[0], t[1]))
print('pieces:', len(pieces))
for t in pieces:
    print('r%d c%d %-4s cx=%.0f cy=%.0f w=%d h=%d' % (t[0], t[1], t[2], t[3], t[4], t[6], t[7]))

cell = 150
n_cols = 5
n_rows = (len(pieces)+n_cols-1)//n_cols
sheet = Image.new('RGB', (cell*n_cols, cell*n_rows), (20,20,20))
d = ImageDraw.Draw(sheet)
for i, (ri, ci, kind, cx, cy, n, w, h) in enumerate(pieces):
    box = (int(cx-55), int(cy-55), int(cx+55), int(cy+55))
    pc = im.crop(box).resize((cell-14, cell-14), Image.LANCZOS)
    x = (i % n_cols)*cell + 7
    y = (i // n_cols)*cell + 7
    sheet.paste(pc, (x, y))
    d.text((x, y-3), '%d,%d %s' % (ri, ci, kind), fill=(255,255,0))
sheet = sheet.resize((sheet.width*2, sheet.height*2), Image.LANCZOS)
sheet.save(r'd:\Dane\Documents\Trae\temp_20261123_04\_tmp_montage.png')
print(sheet.size)
