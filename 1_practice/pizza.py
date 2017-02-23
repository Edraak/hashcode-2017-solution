from termcolor import colored

import sys
import math


class Part(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Pizza(object):
    """The pizza matrix."""

    def __init__(self, r, c, h, s):
        self.R = r
        self.C = c
        self.H = h
        self.S = s
        self.grid = []
        self.parts = []
        print self.R, self.C, self.H, self.S

    def to_string(self):
        """Display the pizza matrix."""
        for r in self.grid:
            for c in r:
                if c == 'T':
                    sys.stdout.write(colored(c, 'red'))
                elif c == 'M':
                    sys.stdout.write(colored(c, 'yellow'))
                else:
                    sys.stdout.write(colored(c, 'white'))
            print
        print

    def create(self):
        for y in range(self.R):
            num_M = 0
            x1 = -1
            x = 0
            while x < self.C:
                print("x,y = %d,%d" % (x, y))
                if self.grid[y][x] == 'M':
                    if num_M == 0:
                        x1 = x
                    num_M += 1
                    if num_M == self.H:
                        xl = x1
                        xr = x
                        size = x - x1 + 1
                        if size <= self.S:
                            # left
                            if x1 > 0:
                                while (xl > 0) and (size < self.S) and \
                                        (self.grid[y][xl - 1] in ('TH')):
                                    xl -= 1
                                    size += 1
                            # right
                            if x < self.C - 1:
                                while (xr < self.C - 1) and (size < self.S) and \
                                        (self.grid[y][xr + 1] in ('TH')):
                                    xr += 1
                                    size += 1
                            print("xl = %d, xr = %d" % (xl, xr))
                            self.parts.append(Part(xl, y, xr, y))
                            for xx in range(xl, xr + 1):
                                self.grid[y][xx] = 'T'
                        x = xr + 1
                        print("set x : %d" % x)
                        num_M = 0
                        continue
                x += 1

    def get_score_rc(self, c, r, width, height):
        # print("get score %d %d ==> %d %d" % (c, r, width, height))
        if width * height > self.S:
            return 9999
        if c + width - 1 >= self.C:
            return 9999
        if r + height - 1 >= self.R:
            return 9999
        num_M = 0
        for j in range(r, r + height):
            for i in range(c, c + width):
                if self.grid[j][i] == 'M':
                    num_M += 1
                elif 'T' != self.grid[j][i]:
                    return 9999
        if num_M < self.H or num_M > width * height - self.H:
            return 9999
        return num_M

    def create_combs(self):
        combs = tuple()
        partnum = 0
        for num in range(self.H*2, self.S+1):
            combs += tuple([(x, num/x) for x in range(1, num+1) if num % x == 0])
        combs = tuple(reversed(combs))
        print combs
        for r in range(self.R):
            for c in range(self.C):
                scores = []
                for comb in combs:
                    scores.append(self.get_score_rc(c, r, comb[0], comb[1]))
                # print scores
                best = scores.index(min(scores))
                # print best
                if scores[best] < 9000:
                    self.parts.append(
                        Part(c, r,
                             c + combs[best][0] - 1, r + combs[best][1] - 1))
                    for yy in range(r, r + combs[best][1]):
                        for xx in range(c, c + combs[best][0]):
                            self.grid[yy][xx] = partnum
                    partnum += 1

    def get_score(self):
        return sum([(p.x2 - p.x1 + 1) * (p.y2 - p.y1 + 1)
                    for p in self.parts])


def read_matrix(filename):
    """Read the input file."""
    with open(filename, 'r') as fin:
        _pizza = Pizza(*[int(num) for num in fin.readline().split()])
        # read matrix
        for i in range(_pizza.R):
            str_line = fin.readline().strip()
            line = []
            for c in str_line:
                line.append(c)
            _pizza.grid.append(line)

    return _pizza


def write_matrix(pizza, filename):
    """Write output file."""
    with open(filename, 'w') as fout:
        fout.write('%d\n' % len(pizza.parts))
        for p in pizza.parts:
            fout.write('%d %d %d %d\n' % (p.y1, p.x1, p.y2, p.x2))


def main():
    """Main function."""

    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    # read data and initialize the matrix
    pizza = read_matrix(sys.argv[1])

    pizza.create_combs()

    print pizza.to_string()
    print('score: %d' % pizza.get_score())

    # write output file
    write_matrix(pizza, sys.argv[2])


if __name__ == '__main__':
    main()
