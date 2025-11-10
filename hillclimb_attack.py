
"""
hillclimb_attack.py
Heuristic hill-climbing attack on DualCipher (Keyword substitution + Playfair).
Usage examples:
  python hillclimb_attack.py --cipher "NWILPEDTVOTSLV" --iter 50000 --restarts 5
  python hillclimb_attack.py --infile cipher.txt --iter 100000 --restarts 10 --known "MYNAMEIS" --known_pos 0
"""

import sys, time, random, argparse
from collections import Counter

# ------------------------
# Simple digraph scoring model (small table but works as a heuristic).
# For best results replace/extend with a full digraph/trigram model from a corpus.
# ------------------------
EN_DIG = {
 'TH': 2.71,'HE': 2.33,'IN': 2.03,'ER': 1.78,'AN': 1.61,'RE': 1.41,'ON': 1.32,'AT': 1.24,
 'EN': 1.13,'ND': 1.07,'TI': 0.99,'ES': 0.99,'OR': 0.98,'TE': 0.97,'OF': 0.97,'ED': 0.94,
 'IS': 0.93,'IT': 0.89,'AL': 0.88,'AR': 0.85,'ST': 0.83,'TO': 0.76,'NT': 0.76,'NG': 0.73
}
# fallback small value for unseen digraphs
FALLBACK = 0.01

# ------------------------
# Playfair helpers (decryption rules)
# ------------------------
def build_grid_from_keystr(keystr25):
    # keystr25: 25-letter string (A-Z excluding J)
    # build 5x5 grid row-major
    grid = [list(keystr25[i*5:(i+1)*5]) for i in range(5)]
    return grid

def find_pos(grid, ch):
    if ch == 'J':
        ch = 'I'
    for r in range(5):
        for c in range(5):
            if grid[r][c] == ch:
                return r,c
    return None

def playfair_decrypt(cipher, grid):
    # cipher must be uppercase letters, even length
    plain = []
    L = len(cipher)
    for i in range(0, L, 2):
        a = cipher[i]; b = cipher[i+1]
        r1,c1 = find_pos(grid,a)
        r2,c2 = find_pos(grid,b)
        if r1 == r2:
            plain.append(grid[r1][(c1-1)%5])
            plain.append(grid[r2][(c2-1)%5])
        elif c1 == c2:
            plain.append(grid[(r1-1)%5][c1])
            plain.append(grid[(r2-1)%5][c2])
        else:
            plain.append(grid[r1][c2])
            plain.append(grid[r2][c1])
    return ''.join(plain)

# ------------------------
# Substitution helpers (keyword mapping)
# ------------------------
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def build_substitution_map_from_alph(alph26):
    # alph26 is 26-letter string representing substitution mapping: A->alph26[0], ...
    # For decryption, we want inverse_map: cipher_letter -> plain_letter
    inv = {}
    for i,ch in enumerate(alph26):
        inv[ch] = ALPHA[i]
    return inv

def apply_sub_inv(stage1, inv_map):
    # stage1 is string of letters (result from Playfair decrypt)
    out = []
    for ch in stage1:
        out.append(inv_map.get(ch, '?'))
    return ''.join(out)

# ------------------------
# Scoring
# ------------------------
def digraph_score(text, known_snippet=None, known_pos=None, known_weight=50.0):
    # compute sum of digraph scores (higher = more English-like)
    s = 0.0
    for i in range(len(text)-1):
        dg = text[i:i+2]
        s += EN_DIG.get(dg, FALLBACK)
    # add bonus if known plaintext snippet matches at known_pos
    if known_snippet and known_pos is not None:
        seg = text[known_pos:known_pos+len(known_snippet)]
        matches = sum(1 for a,b in zip(seg, known_snippet) if a==b)
        # normalized match score times weight
        s += (matches / max(1, len(known_snippet))) * known_weight
    return s

# ------------------------
# Candidate generation / tweak
# ------------------------
def random_alph26():
    letters = list(ALPHA)
    random.shuffle(letters)
    return ''.join(letters)

def random_key25():
    # produce 25-letter ordering excludes 'J' -> Use A..Z excluding J, shuffle
    letters = [c for c in ALPHA if c != 'J']
    random.shuffle(letters)
    return ''.join(letters)

def tweak_alph26(alph):
    a = list(alph)
    i,j = random.sample(range(26),2)
    a[i],a[j] = a[j],a[i]
    return ''.join(a)

def tweak_key25(k25):
    a = list(k25)
    i,j = random.sample(range(25),2)
    a[i],a[j] = a[j],a[i]
    return ''.join(a)

# ------------------------
# Hill climbing main
# ------------------------
def hillclimb_attack(ciphertext, iterations=50000, restarts=5, known_snip=None, known_pos=None):
    best_overall = ("", -1.0, None, None)  # (plaintext, score, alph26, key25)
    start_time = time.time()
    n = len(ciphertext)
    if n % 2 == 1:
        raise ValueError("Ciphertext length must be even for Playfair.")

    for r in range(restarts):
        # initialize candidate
        curr_alph = random_alph26()
        curr_key = random_key25()
        curr_grid = build_grid_from_keystr(curr_key)
        # evaluate
        stage1 = playfair_decrypt(ciphertext, curr_grid)
        inv_map = build_substitution_map_from_alph(curr_alph)
        cand_plain = apply_sub_inv(stage1, inv_map)
        curr_score = digraph_score(cand_plain, known_snip, known_pos)
        best_local = (cand_plain, curr_score, curr_alph, curr_key)

        # simulated annealing parameters
        for it in range(iterations):
            if random.random() < 0.6:
                cand_alph = tweak_alph26(curr_alph)
                cand_grid = curr_grid
            else:
                cand_alph = curr_alph
                cand_key = tweak_key25(curr_key)
                cand_grid = build_grid_from_keystr(cand_key)
            # decrypt with candidate
            stage1 = playfair_decrypt(ciphertext, cand_grid)
            inv_map = build_substitution_map_from_alph(cand_alph)
            cand_plain = apply_sub_inv(stage1, inv_map)
            cand_score = digraph_score(cand_plain, known_snip, known_pos)
            # acceptance rule (hill-climb with occasional uphill moves)
            if cand_score > curr_score or random.random() < 0.001:
                curr_alph, curr_key, curr_grid, curr_score = cand_alph, (cand_key if 'cand_key' in locals() else curr_key), cand_grid, cand_score
                if cand_score > best_local[1]:
                    best_local = (cand_plain, cand_score, curr_alph, curr_key)
            # update best overall
        if best_local[1] > best_overall[1]:
            best_overall = best_local
        elapsed = time.time() - start_time
        print(f"[restart {r+1}/{restarts}] best_local_score={best_local[1]:.3f} elapsed={elapsed:.1f}s")

    total_time = time.time() - start_time
    print(f"\nBest overall score: {best_overall[1]:.3f} Time: {total_time:.1f}s")
    return best_overall

# ------------------------
# Command line
# ------------------------
def main():
    parser = argparse.ArgumentParser(description="Hill-climb attack on DualCipher (Keyword+Playfair)")
    parser.add_argument("--cipher", help="ciphertext (letters only, even length)")
    parser.add_argument("--infile", help="read ciphertext from file")
    parser.add_argument("--iter", type=int, default=50000, help="iterations per restart")
    parser.add_argument("--restarts", type=int, default=5, help="number of restarts")
    parser.add_argument("--known", help="known plaintext snippet (optional)")
    parser.add_argument("--known_pos", type=int, default=0, help="start position of known snippet in plaintext (optional)")
    args = parser.parse_args()

    if args.infile:
        with open(args.infile, "r") as f:
            cipher = "".join([c for c in f.read().strip().upper() if c.isalpha()])
    elif args.cipher:
        cipher = "".join([c for c in args.cipher.strip().upper() if c.isalpha()])
    else:
        print("Provide --cipher or --infile")
        return

    if len(cipher) % 2 == 1:
        print("Ciphertext length must be even (Playfair).")
        return

    known = None
    if args.known:
        known = "".join([c for c in args.known.strip().upper() if c.isalpha()])

    best_plain, best_score, best_alph, best_key = hillclimb_attack(cipher, iterations=args.iter, restarts=args.restarts, known_snip=known, known_pos=args.known_pos)
    print("\n=== RESULT ===")
    print("Best plaintext guess:\n", best_plain)
    print("Score:", best_score)
    print("Best substitution alphabet (A->...):", best_alph)
    print("Best playfair key25 (row-major):", best_key)
    print("================")

if __name__ == "__main__":
    main()
