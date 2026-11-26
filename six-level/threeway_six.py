"""Construct and check a six-symbol strength-three covering array on 103² columns."""
import argparse
import gzip
import hashlib
import itertools
import math
from pathlib import Path


P = 103
V = 6
MULTIPLIERS = (102, 68, 57, 54)


def cyclotomic_rows():
    # C. J. Colbourn's cyclotomy construction, using 5 as primitive root.
    log = [0] * P
    residues = {pow(5, j, P) for j in range(P - 1)}
    assert len(residues) == P - 1
    for j in range(P - 1):
        log[pow(5, j, P)] = j % V
    for symbol in range(V):
        for shift in range(P):
            yield bytes((log[(x - shift) % P] + symbol) % V for x in range(P))
        yield bytes([symbol]) * P


def projective_permutations():
    # Represent infinity by 5. A zero denominator also yields infinity.
    group = set()
    for a, b, c, d in itertools.product(range(5), repeat=4):
        if (a * d - b * c) % 5 == 0:
            continue
        perm = []
        for x in range(6):
            num, den = (a, c) if x == 5 else (a * x + b, c * x + d)
            perm.append(num * pow(den, -1, 5) % 5 if den % 5 else 5)
        group.add(bytes(perm))
    assert len(group) == 120
    return sorted(group)


def progression_rows():
    for c in MULTIPLIERS:
        colours = [(c * x % P) % V for x in range(P)]
        for perm in projective_permutations():
            yield bytes(perm[x] for x in colours)


def coordinate_maps():
    keys = list(itertools.product(range(P), repeat=2))
    return tuple(bytes(proj(a, b) for a, b in keys) for proj in (
        lambda a, b: a, lambda a, b: b, lambda a, b: (a + b) % P,
        lambda a, b: (2 * a + b) % P))


def full_rows():
    maps = coordinate_maps()
    for s in range(V):
        yield bytes([s]) * (P * P)
    for coordinate in maps[:3]:
        for row in cyclotomic_rows():
            if len(set(row)) > 1:
                yield coordinate.translate(row.ljust(256, b'\0'))
    for row in progression_rows():
        yield maps[3].translate(row.ljust(256, b'\0'))


def index_rows(rows):
    rows = list(rows)
    return [[sum(1 << j for j, row in enumerate(rows) if row[x] == value)
             for value in range(V)] for x in range(P)]


def verify():
    # Projected triples that are separated in a seed block realize any values.
    bits = index_rows(cyclotomic_rows())
    for i, j, k in itertools.combinations(range(P), 3):
        for a, b in itertools.product(range(V), repeat=2):
            pair = bits[i][a] & bits[j][b]
            if not all(pair & mask for mask in bits[k]):
                raise ValueError(f'Cyclotomic seed fails at {i,j,k,a,b}')
    print(f'PASS: {math.comb(P,3):,} seed triples, all {V**3} ordered assignments.')
    # Directly check actual correction rows, independently of group or hash claims.
    bits = index_rows(progression_rows())
    rainbow = list(itertools.permutations(range(V), 3))
    progressions = {tuple(sorted((x, (x + d) % P, (x + 2*d) % P)))
                    for x in range(P) for d in range(1, P)}
    for i, j, k in progressions:
        for a, b, c in rainbow:
            if not bits[i][a] & bits[j][b] & bits[k][c]:
                raise ValueError(f'Progression rows fail at {i,j,k,a,b,c}')
    print(f'PASS: {len(progressions):,} distinct progressions, all {len(rainbow)} rainbow assignments.')
    # Verify multiplicative hashing separately, without recourse to PGL(2,5).
    for i, j, k in progressions:
        if not any(len({((c*x) % P) % V for x in (i,j,k)}) == 3 for c in MULTIPLIERS):
            raise ValueError(f'No separating hash for {i,j,k}')
    # Because each symbolic row is repeated over the full grid, validate and hash
    # the complete array. The streamed digest is over raw row-major bytes 0..5.
    digest = hashlib.sha256()
    n = 0
    for row in full_rows():
        assert len(row) == P**2 and max(row) < V
        n += 1
        digest.update(row)
    assert n == 2340
    print(f'PASS: generated {n:,} x {P**2:,}; raw SHA-256 {digest.hexdigest()}')


def write_array(path):
    if path.exists():
        raise FileExistsError(path)
    # ASCII digits separated by commas, no header; make gzip output reproducible.
    with path.open('xb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw,
                                               mtime=0, compresslevel=6) as output:
        digit = bytes.maketrans(bytes(range(V)), b'012345')
        for row in full_rows():
            data = bytearray(b',' * (2 * len(row)))
            data[::2] = row.translate(digit)
            data[-1] = 10
            output.write(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv-gz', type=Path, help='Write the complete compressed CSV to a new file.')
    args = parser.parse_args()
    verify()
    if args.csv_gz is not None:
        write_array(args.csv_gz)
