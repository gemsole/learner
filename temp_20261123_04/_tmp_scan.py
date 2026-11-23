import numpy as np
from PIL import Image, ImageDraw

p = r'd:\Dane\Documents\Trae\temp_20261123_04\_tmp_board.png'
im = Image.open(p).convert('RGB')
a = np.array(im).astype(np.int16)
H, W, _ = a.shape
R, G, B = a[:,:,0], a[:,:,1], a[:,:,2]

cols = [73, 226, 370, 514, 653, 801, 937, 1091, 1244]
rows = [32, 156, 305, 449, 593, 736, 881, 1025, 1168, 1309]

def area_stats(cx, cy, rad=48):
    y0, y1 = max(0, cy-rad), min(H, cy+rad)
    x0, x1 = max(0, cx-rad), min(W, cx+rad)
    rr = R[y0:y1, x0:x1]; gg = G[y0:y1, x0:x1]; bb = B[y0:y1, x0:x1]
    lum = (rr+gg+bb)/3.0
    red = ((rr-gg > 25) & (rr-bb > 45) & (rr > 75)).mean()
    neutral = ((abs(rr-gg) < 14) & (abs(gg-bb) < 14) & (rr < 135)).mean()
    return red, neutral, float(lum.mean())

found = []
for ri, ry in enumerate(rows):
    for ci, cx in enumerate(cols):
        red, neutral, lum = area_stats(cx, ry)
        if max(red, neutral) > 0.18:
            kind = 'RED' if red > neutral else 'DARK'
            found.append((ri, ci, cx, ry, kind, round(red,2), round(neutral,2)))

print('found', len(found))
for f in found:
    print('r%d c%d %s red=%.2f neutral=%.2f' % (f[0], f[1], f[4], f[5], f[6]))

# montage
cell = 128
cols_n = 5
rows_n = (len(found)+cols_n-1)//cols_n
sheet = Image.new('RGB', (cell*cols_n, cell*rows_n), (30,30,30))
d = ImageDraw.Draw(sheet)
for i, (ri, ci, cx, cy, kind, red, neutral) in enumerate(found):
    box = (max(0,cx-52), max(0,cy-52), min(W,cx+52), min(H,cy+52))
    piece = im.crop(box).resize((cell-8, cell-8), Image.LANCZOS)
    x = (i % cols_n)*cell + 4
    y = (i // cols_n)*cell + 4
    sheet.paste(piece, (x, y))
    d.text((x+2, y+2), '%d,%d' % (ri, ci), fill=(255,255,0))
    d.text((x+2, y+4+96), kind, fill=(0,255,0) if kind=='RED' else (255,255,255))
sheet = sheet.resize((sheet.width*2, sheet.height*2), Image.LANCZOS)
sheet.save(r'd:\Dane\Documents\Trae\temp_20261123_04\_tmp_montage.png')
print('montage', sheet.size)
