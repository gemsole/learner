import sys
from functools import lru_cache

RED, BLK = 'r', 'b'
TYPES = 'KAEHRCP'

start = {}
# red
start[(1,1)] = (RED,'R')
start[(4,3)] = (RED,'H')
start[(5,5)] = (RED,'R')
start[(4,7)] = (RED,'E')
start[(3,9)] = (RED,'A')
start[(4,9)] = (RED,'K')
# black
start[(3,0)] = (BLK,'A')
start[(4,0)] = (BLK,'K')
start[(5,0)] = (BLK,'A')
start[(4,2)] = (BLK,'E')
start[(2,6)] = (BLK,'R')
start[(3,8)] = (BLK,'R')

PALACE = {RED: [(c,r) for c in (3,4,5) for r in (7,8,9)],
          BLK: [(c,r) for c in (3,4,5) for r in (0,1,2)]}

def inside(c,r): return 0<=c<=8 and 0<=r<=9

def gen_moves(board, side):
    moves = []
    for (c,r),(s,t) in board.items():
        if s != side: continue
        if t == 'K':
            for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
                nc,nr = c+dc, r+dr
                if (nc,nr) in PALACE[side] and board.get((nc,nr), (None,))[0] != side:
                    moves.append(((c,r),(nc,nr)))
        elif t == 'A':
            for dc,dr in ((1,1),(1,-1),(-1,1),(-1,-1)):
                nc,nr = c+dc, r+dr
                if (nc,nr) in PALACE[side] and board.get((nc,nr),(None,))[0] != side:
                    moves.append(((c,r),(nc,nr)))
        elif t == 'E':
            for dc,dr in ((2,2),(2,-2),(-2,2),(-2,-2)):
                nc,nr = c+dc, r+dr
                if not inside(nc,nr): continue
                if side==RED and nr<5: continue
                if side==BLK and nr>4: continue
                if board.get((c+dc//2, r+dr//2)) is not None: continue
                if board.get((nc,nr),(None,))[0] != side:
                    moves.append(((c,r),(nc,nr)))
        elif t == 'H':
            for dc,dr in ((1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)):
                nc,nr = c+dc, r+dr
                if not inside(nc,nr): continue
                lc,lr = (c + (1 if dc==2 else -1 if dc==-2 else 0), r + (1 if dr==2 else -1 if dr==-2 else 0))
                if board.get((lc,lr)) is not None: continue
                if board.get((nc,nr),(None,))[0] != side:
                    moves.append(((c,r),(nc,nr)))
        elif t == 'R':
            for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
                nc,nr = c+dc, r+dr
                while inside(nc,nr):
                    occ = board.get((nc,nr))
                    if occ is None:
                        moves.append(((c,r),(nc,nr)))
                    else:
                        if occ[0] != side: moves.append(((c,r),(nc,nr)))
                        break
                    nc += dc; nr += dr
        elif t == 'C':
            for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
                nc,nr = c+dc, r+dr
                while inside(nc,nr) and board.get((nc,nr)) is None:
                    moves.append(((c,r),(nc,nr)))
                    nc += dc; nr += dr
                # screen found or edge
                nc += dc; nr += dr
                while inside(nc,nr):
                    occ = board.get((nc,nr))
                    if occ is not None:
                        if occ[0] != side: moves.append(((c,r),(nc,nr)))
                        break
                    nc += dc; nr += dr
        elif t == 'P':
            dirs = [(0,-1)] if side==RED else [(0,1)]
            if side==RED and r<=4: dirs += [(1,0),(-1,0)]
            if side==BLK and r>=5: dirs += [(1,0),(-1,0)]
            for dc,dr in dirs:
                nc,nr = c+dc, r+dr
                if inside(nc,nr) and board.get((nc,nr),(None,))[0] != side:
                    moves.append(((c,r),(nc,nr)))
    return moves

KNIGHT = ((1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1))

def attacked(board, sq, by_side):
    """is square sq attacked by pieces of by_side"""
    c,r = sq
    for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
        nc,nr = c+dc, r+dr
        screen = 0
        while inside(nc,nr):
            occ = board.get((nc,nr))
            if occ is not None:
                s,t = occ
                if s == by_side:
                    if t == 'R' and screen == 0: return True
                    if t == 'C' and screen == 1: return True
                    if t == 'K' and screen == 0:
                        if dr == 0 and abs(nc-c) == 1: return True
                        if dc == 0 and abs(nr-r) == 1: return True
                screen += 1
            nc += dc; nr += dr
    # horses
    for dc,dr in KNIGHT:
        nc,nr = c+dc, r+dr
        if inside(nc,nr):
            occ = board.get((nc,nr))
            if occ and occ[0]==by_side and occ[1]=='H':
                lc = nc + (1 if dc==2 else -1 if dc==-2 else 0)
                lr = nr + (1 if dr==2 else -1 if dr==-2 else 0)
                if board.get((lc,lr)) is None: return True
    return False

def kings_face(board):
    rk = bk = None
    for sq,(s,t) in board.items():
        if t=='K':
            if s==RED: rk=sq
            else: bk=sq
    if rk is None or bk is None: return False
    if rk[0] != bk[0]: return False
    c = rk[0]
    lo,hi = sorted((rk[1], bk[1]))
    for r in range(lo+1, hi):
        if board.get((c,r)) is not None: return False
    return True

def in_check(board, side):
    ksq = None
    for sq,(s,t) in board.items():
        if s==side and t=='K': ksq = sq
    if ksq is None: return True
    opp = BLK if side==RED else RED
    if attacked(board, ksq, opp): return True
    if kings_face(board): return True
    return False

def apply(board, mv):
    a,b = mv
    nb = dict(board)
    piece = nb.pop(a)
    nb[b] = piece
    return nb

def legal_moves(board, side):
    res = []
    for mv in gen_moves(board, side):
        nb = apply(board, mv)
        if not in_check(nb, side):
            res.append((mv, nb))
    return res

nodes = 0

def search(board, side, depth, alpha, beta, ply):
    """negamax-ish: returns score from red's perspective; mate = +MATE-ply for red winning"""
    global nodes
    nodes += 1
    moves = legal_moves(board, side)
    if not moves:
        # side to move loses (checkmate or stalemate)
        return -10000 + ply if side==RED else 10000 - ply
    if depth == 0:
        return 0
    if side == RED:
        best = -100000
        for mv, nb in moves:
            sc = search(nb, BLK, depth-1, alpha, beta, ply+1)
            if sc > best: best = sc
            if best > alpha: alpha = best
            if alpha >= beta: break
        return best
    else:
        best = 100000
        for mv, nb in moves:
            sc = search(nb, RED, depth-1, alpha, beta, ply+1)
            if sc < best: best = sc
            if best < beta: beta = best
            if alpha >= beta: break
        return best

def find_mate(max_depth=6):
    for d in range(2, max_depth+1, 2):
        global nodes
        nodes = 0
        res = []
        for mv, nb in legal_moves(start, RED):
            sc = search(nb, BLK, d-1, -100000, 100000, 1)
            if sc >= 10000 - 20:
                res.append((mv, sc))
        if res:
            print('depth', d, 'mates found', len(res), 'nodes', nodes)
            for mv, sc in res:
                print('  ', mv, sc)
            return d, res
    return None, []

print('start check red?', in_check(start, RED))
print('legal red moves:', len(legal_moves(start, RED)))
d, res = find_mate(8)
