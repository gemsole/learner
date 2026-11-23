import numpy as np
from PIL import Image

p = r'd:\Dane\Documents\Trae\temp_20261123_04\_tmp_board.png'
im = Image.open(p).convert('RGB')
a = np.array(im).astype(np.int16)
H, W, _ = a.shape
R, G, B = a[:,:,0], a[:,:,1], a[:,:,2]
lum = (R+G+B)/3.0
dark = lum < 115  # thin lines are dark

# restrict to board region: board roughly x 70..1380, y 0..1380
sub = dark[:, :]
colcount = dark.sum(axis=0)
rowcount = dark.sum(axis=1)

def peaks(counts, thresh, min_gap=30):
    idx = [i for i, v in enumerate(counts) if v > thresh]
    groups = []
    cur = []
    for i in idx:
        if cur and i - cur[-1] <= 12:
            cur.append(i)
        else:
            if cur: groups.append(cur)
            cur = [i]
    if cur: groups.append(cur)
    res = []
    for g in groups:
        # weighted center
        w = counts[g]
        res.append(float(np.average(g, weights=w)))
    return res

print('col peaks (thresh=%d)' % int(H*0.25))
for v in peaks(colcount, H*0.25): print('  x=%.0f' % v)
print('row peaks (thresh=%d)' % int(W*0.25))
for v in peaks(rowcount, W*0.25): print('  y=%.0f' % v)
