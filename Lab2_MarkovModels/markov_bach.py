import collections
import numpy as np


class Prefix:
    def __init__(self, n, string):
        self.__multiplier = 31
        self.p = collections.deque()

        for i in range(n):
            self.p.append(string)

    def __hash__(self):
        h = 0
        for i in range(len(self.p)):
            h = self.__multiplier * h + hash(self.p[i])
        return h

    def __eq__(self, other):
        for i in range(len(self.p)):
            if (self.p[i] != other.p[i]):
                return False
        return True

    def clone(self, NPREF, NONWORD):
        copyP = self.p.copy()
        copy = Prefix(NPREF, NONWORD)
        copy.p = copyP
        return copy


class Chain:
    def __init__(self, NPREF=4, NONWORD="\n", MAXGEN=200):

        self.statetab = {}
        self.NPREF = NPREF
        # nonword should be starting chord
        self.NONWORD = NONWORD
        self.MAXGEN = MAXGEN

        self.prefix = Prefix(self.NPREF, self.NONWORD)

    def add(self, string):
        suf = self.statetab.get(self.prefix)
        if not suf:
            suf = []
            self.statetab[self.prefix.clone(self.NPREF, self.NONWORD)] = suf

        suf.append(string)
        self.prefix.p.popleft()
        self.prefix.p.append(string)

    def build(self, inStream):
        for i in inStream:
            self.add(i)
        self.add(self.NONWORD)

    def generate(self, first=None, nwords=20, repeatLimit=4):
        chain = []
        last = None
        nodeLast = None
        repeats = 0

        new = Prefix(self.NPREF, self.NONWORD)
        if first is not None:
            new = Prefix(self.NPREF, first)

        for i in range(nwords):
            s = self.statetab.get(new)

            if not s:
                return "No state"

            word = self.randomWord(s)

            if word == '\n':
                word = self.randomWord(s, word='\n')

            if word != last:
                nodeLast = last
                last = word
                repeats = 0
            elif word == last:
                nodeLast = last
                repeats += 1
                if repeats == repeatLimit and repeats % repeatLimit == 0:
                    word = self.randomWord(s, word)
                    last = word
                    nodeLast = word
                    repeate = 0

            chain.append(word)
            new.p.popleft()
            new.p.append(word)

        return chain

    def randomWord(self, state, word=None):
        cts = {}
        total = 0
        for i in state:
            if i == word:
                continue
            elif i not in cts:
                cts[i] = 1
                total += 1
            else:
                cts[i] += 1
                total += 1
        unique = list(cts.keys())
        counts = np.array(list(cts.values()))
        probs = counts / total
        ind = np.random.choice(range(0, len(unique)), p=probs)
        return unique[ind]