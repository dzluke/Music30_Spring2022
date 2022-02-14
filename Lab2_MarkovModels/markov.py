import collections
import numpy as np
import networkx as nx

MAXGEN = 200

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
    def __init__(self, NPREF=4, NONWORD = "\n", MAXGEN = 200):
        # map<Prefix, vector<string>>
        self.statetab = {}
        self.NPREF = NPREF
        #nonword should be starting chord
        self.NONWORD = NONWORD
        self.MAXGEN = MAXGEN
        
        self.prefix = Prefix(self.NPREF, self.NONWORD)

    def add(self, string):
        suf =  self.statetab.get(self.prefix)
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

    def generate(self, first=None, nwords=28, repeatLimit=4):
        chain = []
        last = None
        nodeLast = None
        repeats = 0
        graph = nx.DiGraph()
        #seen = set()
        
        new = Prefix(self.NPREF, self.NONWORD)
        if first is not None:
            new = Prefix(self.NPREF, first)
            graph.add_node(first)
            
        for i in range(0, nwords):
            s = self.statetab.get(new)
            
            if not s:
                return "No state"
            
            s = np.array(s)
            #r = np.random.randint(0, 9999999999) % len(s)
            #word = s[r]
            word = self.randomWord(s)
            
            if word != last:
                nodeLast = last
                last = word
                repeats = 0
                #seen.add(word)
            elif word == last:
                nodeLast = last
                repeats += 1
            if repeats == repeatLimit and repeats % repeatLimit == 0:
                word = self.randomWord(s, word)
            
            if graph.has_node(word) == False:
                graph.add_node(word)
            
            if [nodeLast, word] not in graph.edges and nodeLast != None:
                graph.add_edge(nodeLast, word, label=1, size=5)
            else:
                if nodeLast != None:
                    graph.edges[nodeLast, word]['label'] += 1
            
            chain.append(word)
            new.p.popleft()
            new.p.append(word)
        
        # nx.drawing.nx_agraph.write_dot(graph, 'markov.dot')
        return chain
    
    def randomWord(self, state, word=None):
        unique, counts = np.unique(state, return_counts=True)
        if word != None:
            take = np.where(unique != word)[0]
            unique = unique[take]
            counts = counts[take]
        probs = counts / np.sum(counts)
        return np.random.choice(unique, p=probs)