"""Independent verifier for the supplied 2,340 by 10,609 compressed array."""

import argparse
import gzip
import hashlib
from itertools import combinations, permutations, product
from pathlib import Path


P = 103
V = 6
WIDTH = P * P
EXPECTED = "1eb464f4a6eab128f8176ff052727759ff69b090666301d2fce09017c594dc3a"


def require(value, error):
    if not value:
        raise ValueError(error)


def read_blocks(csv_path):
    masks = [bytes(f(a, b) for a, b in product(range(P), repeat=2)) for f in (
        lambda a, b: a, lambda a, b: b,
        lambda a, b: (a+b) % P, lambda a, b: (2*a+b) % P)]
    representatives = [[m.index(x) for x in range(P)] for m in masks]
    blocks = [[] for _ in masks]
    constants = []
    digest = hashlib.sha256()
    line_count = 0
    with gzip.open(csv_path, "rb") as data:
        for line_count, line in enumerate(data, 1):
            raw = line.rstrip(b"\r\n")
            digits = raw[::2]
            require(len(digits) == WIDTH and raw[1::2] == b"," * (WIDTH-1)
                    and min(digits) >= 48 and max(digits) <= 53, "CSV row format")
            row = digits.translate(bytes.maketrans(b"012345", bytes(range(V))))
            digest.update(row)
            if line_count <= V:
                require(min(row) == max(row), "Incomplete constant row")
                constants.append(row[0])
                continue
            i = min((line_count - V - 1) // 618, 3)
            keys = bytes(row[pos] for pos in representatives[i])
            require(masks[i].translate(keys.ljust(256, b"\0")) == row, "Projection mismatch")
            blocks[i].append(keys)
    require(line_count == 2340 and set(constants) == set(range(V)), "Dimensions/constants")
    require(digest.hexdigest() == EXPECTED, "CSV digest mismatch")
    require(blocks[0] == blocks[1] == blocks[2], "Seed blocks differ")
    return [bytes([c]) * P for c in constants] + blocks[0], blocks[3]


def symbol_masks(rows):
    index = [[0] * V for _ in range(P)]
    for r, row in enumerate(rows):
        for x, v in enumerate(row):
            index[x][v] |= 1 << r
    return index


def verify_projections(seed, correction):
    index = symbol_masks(seed)
    for i, j, k in combinations(range(P), 3):
        for mi, mj in product(index[i], index[j]):
            hit = mi & mj
            require(all(hit & mk for mk in index[k]), "Uncovered seed interaction")
    print("PASS: every one of 176,851 seed triples covers 216 assignments.")
    index = symbol_masks(correction)
    rainbow = tuple(permutations(range(V), 3))
    progressions = {tuple(sorted(((x-d) % P, x, (x+d) % P)))
                    for x in range(P) for d in range(1, P)}
    for i, j, k in progressions:
        require(all(index[i][a] & index[j][b] & index[k][c] for a,b,c in rainbow),
                "Uncovered correction interaction")
    print(f"PASS: every one of {len(progressions):,} progressions covers 120 distinct-symbol assignments.")


def verify_geometry():
    # Translate the first point to zero. Scale both coordinates by the inverse
    # of the second point's first nonzero coordinate. Equality of projections
    # and the arithmetic-progression property survive both normalizations.
    count = residual = 0
    for u, v in [(1,s) for s in range(P)] + [(0,1)]:
        for a, b in product(range(P), repeat=2):
            if (a,b) in ((0,0),(u,v)):
                continue
            count += 1
            first = ((u,a), (v,b), ((u+v) % P,(a+b) % P))
            if any(x and y and x != y for x,y in first):
                continue
            # Each of the three projections must identify a different pair.
            equal = {(0 == x, 0 == y, x == y) for x,y in first}
            require(equal == {(True,False,False),(False,True,False),(False,False,True)},
                    "Invalid collision case")
            x, y = (2*u+v) % P, (2*a+b) % P
            require(x and y and x != y and (0 in ((2*x-y) % P, (2*y-x) % P, (x+y) % P)),
                    "Residual triple is not an arithmetic progression")
            residual += 1
    print(f"PASS: all {count:,} normalized ordered grid triples; {residual} residual cases.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_gz", type=Path)
    args = parser.parse_args()
    verify_projections(*read_blocks(args.csv_gz))
    verify_geometry()
    print("PASS: the supplied matrix has strength three on all 10,609 columns.")
