"""Check an exported CSV using only the grid decomposition, independently of its generator."""
import gzip
import hashlib
import itertools
import sys


def ensure(ok, msg):
    if not ok:
        raise ValueError(msg)


def support(table):
    return [[sum(1 << n for n, row in enumerate(table) if row[k] == value)
             for value in range(6)] for k in range(103)]


def main(path):
    p = 103
    projections = [bytes(f(*divmod(j,p)) % p for j in range(p*p)) for f in (
        lambda a,b: a, lambda a,b: b, lambda a,b: a+b, lambda a,b: 2*a+b)]
    tables = [[] for _ in range(4)]
    constants = set()
    digest = hashlib.sha256()
    count = 0
    with gzip.open(path,'rb') as input_csv:
        for seq, line in enumerate(input_csv):
            count += 1
            data = line.rstrip(b'\r\n')
            ensure(len(data) == 2*p*p-1 and data[1::2] == b','*(p*p-1), 'bad CSV width or delimiter')
            digits = data[::2]
            ensure(set(digits) <= set(b'012345'), 'symbol outside 0 through 5')
            row = digits.translate(bytes.maketrans(b'012345', bytes(range(6))))
            digest.update(row)
            if seq < 6:
                ensure(len(set(row)) == 1, 'one of the first six rows is not constant')
                constants.add(row[0])
                continue
            g = min((seq-6)//618, 3)
            signature = row[::p] if g == 0 else row[:p]
            ensure(row == projections[g].translate(signature.ljust(256,b'\0')),
                   f'row {seq+1} is not constant on its projected fibers')
            tables[g].append(signature)
    ensure(count == 2340 and len(constants) == 6,'wrong number of rows or missing constants')
    # Reuse a check only when the numeric tables from the actual CSV coincide.
    verified = set()
    for table in tables[:3]:
        signature = tuple(table)
        if signature in verified: continue
        masks = support(table + [bytes([a])*p for a in range(6)])
        for i,j,k in itertools.combinations(range(p),3):
            for a in masks[i]:
                for b in masks[j]:
                    if not all(a & b & c for c in masks[k]):
                        raise ValueError(f'incomplete ordinary triple {i,j,k}')
        verified.add(signature)
    masks = support(tables[3])
    rainbow = list(itertools.permutations(range(6),3))
    # Each unordered AP checked in both directions.
    for x in range(p):
        for d in range(1,p):
            y,z = (x+d)%p,(x+2*d)%p
            for a,b,c in rainbow:
                if not masks[x][a] & masks[y][b] & masks[z][c]:
                    raise ValueError(f'incomplete exceptional triple {x,y,z,a,b,c}')
    print('PASS: 2,340 rows, 10,609 columns, six constant tests, four valid projected blocks.')
    print('PASS: each ordinary 103-column table covers every triple; correction covers each rainbow AP.')
    print('Raw row-major SHA-256:',digest.hexdigest())


if __name__ == '__main__':
    if len(sys.argv) != 2: raise SystemExit('Usage: python verify_csv.py test-plan.csv.gz')
    main(sys.argv[1])
