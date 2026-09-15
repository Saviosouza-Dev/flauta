"""Todos os exercícios do método, gerados a partir da teoria (notas e graus calculados)."""
import sys
from theory import *
from lyb import Score, COL_HI

Q, H, W, E = "1/4", "1/2", "1", "1/8"
EX = {}


def reg(s):
    EX[s.name] = s
    return s


def letters(n):
    return n.name()


def arp(s, chords, pattern, dur, roman=True, cifra=True, graus=True, hi=None, brk_every=None, symbols=None):
    for ci, c in enumerate(chords):
        if brk_every and ci and ci % brk_every == 0:
            s.brk()
        notes = [c.notes[i] for i in pattern]
        labs = [c.labels()[i] for i in pattern]
        cols = None
        if hi:
            cols = [COL_HI if hi(n) else None for n in notes]
        s.seg(notes, dur,
              roman=c.roman if roman else None,
              cifra=(symbols[ci] if symbols else c.symbol) if cifra else None,
              graus=labs if graus else None, colors=cols)


def scale_score(name, tonic, kind, key=None, desc=True, hi_pcs=(), width=168, brk=False):
    s = reg(Score(name, time="4/4", key=key, width_mm=width, roman=False))
    sc = scale(tonic, kind)
    root = place_root(sc[0]) if sc[0].midi >= 60 else sc[0]
    notes = [root]
    for i in range(1, 8):
        notes.append(place_above(sc[i % 7], notes[-1]))
    seq = [(n, Q) for n in notes]
    if desc:
        seq += [(n, Q) for n in notes[-2:0:-1]] + [(notes[0], H)]
    for idx, (n, d) in enumerate(seq):
        if brk and idx == 8:
            s.brk()
        col = COL_HI if n.pc in hi_pcs else None
        s.note(n, d, cifra=n.name(), grau=interval_label(sc[0], n, chord=False), color=col)
    return s


# ---------------- LIÇÃO 1 ----------------
s = reg(Score("ex1_1", time="4/4", roman=False, width_mm=150))
for nm, pt in zip(["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"], ["Dó", "Ré", "Mi", "Fá", "Sol", "Lá", "Si", "Dó"]):
    s.note(nm, Q, cifra=nm[0], grau=pt)

quiz1 = ["G4", "E5", "A4", "C5", "F4", "D5", "B4", "E4", "A5", "D4", "G5", "F5"]
s = reg(Score("ex1_2", time="4/4", roman=False, graus=False))
s.wide_blank = False
for nm in quiz1:
    s.note(nm, Q, cifra="_")
s = reg(Score("ans1_2", time="4/4", roman=False, graus=False))
for nm in quiz1:
    s.note(nm, Q, cifra=nm[0])

# ---------------- LIÇÃO 2 ----------------
scale_score("ex2_1", "C", "maior", brk=False)

# 1-2-3-1 subindo
s = reg(Score("ex2_2", time="4/4", roman=False))
C = scale("C", "maior")
base = [place_root(C[0])]
for i in range(1, 10):
    base.append(place_above(C[i % 7], base[-1]))
for d in range(7):
    if d == 4:
        s.brk()
    grp = [base[d], base[d + 1], base[d + 2], base[d]]
    for n in grp:
        s.note(n, Q, cifra=n.name(), grau=interval_label(C[0], n, chord=False))
s.note(base[7], W, cifra="C", grau="1")

# pula-uma (terças)
s = reg(Score("ex2_3", time="4/4", roman=False))
for d in range(7):
    if d == 4:
        s.brk()
    for n in [base[d], base[d + 2]]:
        s.note(n, Q, cifra=n.name(), grau=interval_label(C[0], n, chord=False))
s.note(base[7], H, cifra="C", grau="1")

scale_score("ex2_4g", "G", "maior", key="g \\major")
scale_score("ex2_4f", "F", "maior", key="f \\major")
scale_score("ex2_4d", "D", "maior", key="d \\major")

quiz2 = ["D5", "B4", "G4", "F#5", "C5", "A4", "E5", "G5", "D4", "F#4", "B4", "E4"]
G = scale("G", "maior")
s = reg(Score("ex2_5", time="4/4", key="g \\major", roman=False))
for nm in quiz2:
    s.note(nm, Q, cifra=parse(nm).name(), grau="_")
s = reg(Score("ans2_5", time="4/4", key="g \\major", roman=False))
for nm in quiz2:
    n = parse(nm)
    s.note(n, Q, cifra=n.name(), grau=interval_label(G[0], n, chord=False))

# telefone musical: 5-3-1 | 1-3-5-1
s = reg(Score("ex2_6", time="4/4", roman=False, width_mm=110))
for n in ["G4", "E4", "C4"]:
    s.note(n, Q, cifra=n[0], grau=interval_label(C[0], parse(n), chord=False))
s.rest(Q)
for n in ["C4", "E4", "G4", "C5"]:
    s.note(n, Q, cifra=n[0], grau=interval_label(C[0], parse(n), chord=False))

# ---------------- LIÇÃO 3 ----------------
s = reg(Score("ex3_1", time="3/4", roman=False, width_mm=130))
for q in ["", "m", "°", "(#5)"]:
    c = chord_from("C", q, triad=True)
    s.seg(c.notes, Q, cifra=c.symbol, graus=c.labels())

s = reg(Score("ex3_2", time="4/4", roman=False))
for i, q in enumerate(["7M", "7", "m7", "m7(b5)", "°", "m7M", "7M(#5)"]):
    if i == 4:
        s.brk()
    c = chord_from("C", q)
    s.seg(c.notes, Q, cifra=c.symbol, graus=c.labels())

s = reg(Score("ex3_3", time="4/4", roman=False))
changes = [("7M", None), ("7", 3), ("m7", 1), ("m7(b5)", 2), ("°", 3)]
for i, (q, idx) in enumerate(changes):
    c = chord_from("C", q)
    cols = [COL_HI if k == idx else None for k in range(4)]
    s.seg(c.notes, Q, cifra=c.symbol, graus=c.labels(), colors=cols)

# ---------------- LIÇÃO 4 : campo maior ----------------
Cf = field("C", "maior")
Cf3 = field("C", "maior", size=3)


def with_final(ch):
    """acrescenta o I no fim (uma oitava acima quando cabe)"""
    f = ch + [ch[0]]
    return f


s = reg(Score("ex4_1", time="3/4"))
arp(s, with_final(Cf3), [0, 1, 2], Q, brk_every=4)

s = reg(Score("ex4_2", time="4/4"))
arp(s, with_final(Cf), [0, 1, 2, 3], Q, brk_every=4)

s = reg(Score("ex4_3", time="3/4"))
arp(s, with_final(Cf), [0, 1, 2, 3, 2, 1], E, brk_every=4)

Gf = field("G", "maior")
s = reg(Score("ex4_4", time="4/4", key="g \\major"))
arp(s, with_final(Gf), [3, 2, 1, 0], Q, brk_every=4)

Ff = field("F", "maior")
s = reg(Score("ex4_5", time="4/4", key="f \\major"))
arp(s, with_final(Ff), [0, 2, 1, 3], Q, brk_every=4)

Df = field("D", "maior")
s = reg(Score("ex4_6", time="4/4", key="d \\major", graus=False, ragged_last=False))
for i, c in enumerate(with_final(Df)):
    if i == 4:
        s.brk()
    if i in (2, 4, 6):
        s.mobile_breaks.add(len(s.ev))
    s.space(W, roman=c.roman, cifra=c.symbol)
s = reg(Score("ans4_6", time="4/4", key="d \\major"))
arp(s, with_final(Df), [0, 1, 2, 3], Q, brk_every=4)

Bbf = field("Bb", "maior")
order = [3, 0, 4, 1, 5, 2, 6]
s = reg(Score("ex4_7", time="4/4", key="bf \\major"))
for i, d in enumerate(order):
    if i == 4:
        s.brk()
    c = Bbf[d]
    s.seg(c.notes, Q, roman="_", cifra="_", graus=c.labels())
s = reg(Score("ans4_7", time="4/4", key="bf \\major"))
arp(s, [Bbf[d] for d in order], [0, 1, 2, 3], Q, brk_every=4)

# ---------------- LIÇÃO 5 : progressões ----------------
prog = [Cf[0], Cf[5], Cf[1], Cf[4]]
s = reg(Score("ex5_1", time="4/4"))
for rep in range(2):
    for i, c in enumerate(prog):
        if rep == 1 and i == 0:
            s.brk()
        pat = [0, 1, 2, 3] if i % 2 == 0 else [3, 2, 1, 0]
        s.seg([c.notes[k] for k in pat], Q, roman=c.roman, cifra=c.symbol, graus=[c.labels()[k] for k in pat])
c = Cf[0]
s.note(c.notes[0], W, roman=c.roman, cifra=c.symbol, grau="1")

s = reg(Score("ex5_2", time="4/4", key="g \\major", width_mm=168))
for i, c in enumerate([Gf[0], Gf[3], Gf[4], Gf[0]]):
    pat = [0, 1, 2, 3] if i % 2 == 0 else [3, 2, 1, 0]
    s.seg([c.notes[k] for k in pat], Q, roman=c.roman, cifra=c.symbol, graus=[c.labels()[k] for k in pat])
s.note(Gf[0].notes[0], W, roman="I7M", cifra="G7M", grau="1")

# frase II-V-I com notas-guia
s = reg(Score("ex5_3", time="4/4", width_mm=150))
Dm7, G7, C7M = Cf[1], Cf[4], Cf[0]
hi = COL_HI


def lab(ch, n):
    return interval_label(ch.root, parse(n))


s.seg(["D4", "F4", "A4", "C5"], Q, roman="IIm7", cifra="Dm7", graus=[lab(Dm7, x) for x in ["D4", "F4", "A4", "C5"]],
      colors=[None, None, None, hi])
s.seg(["B4", "G4", "D4", "F4"], Q, roman="V7", cifra="G7", graus=[lab(G7, x) for x in ["B4", "G4", "D4", "F4"]],
      colors=[hi, None, None, hi])
s.seg(["E4", "G4", "B4"], [Q, Q, H], roman="I7M", cifra="C7M", graus=[lab(C7M, x) for x in ["E4", "G4", "B4"]],
      colors=[hi, None, None])
s.note("C5", W, grau="1")

# improviso de 3 notas (exemplo)
s = reg(Score("ex5_4", time="4/4"))
plan = [(Cf[0], ["E4", "G4"]), (Cf[5], ["A4", "C5"]), (Cf[1], ["D5", "A4"]), (Cf[4], ["B4", "D5"])]
for c, ns in plan:
    s.seg(ns, H, roman=c.roman, cifra=c.symbol, graus=[lab(c, x) for x in ns])
s.note("C5", W, roman="I7M", cifra="C7M", grau="1")

s = reg(Score("ex5_5", time="4/4", graus=False, ragged_last=False))
for rep in range(2):
    for i, c in enumerate(prog):
        if rep == 1 and i == 0:
            s.brk()
        if (rep, i) in ((0, 2), (1, 0), (1, 2)):
            s.mobile_breaks.add(len(s.ev))
        s.space(W, roman=c.roman, cifra=c.symbol)

# ---------------- LIÇÃO 6 : menor natural ----------------
scale_score("ex6_1", "A", "natural")
Af = field("A", "natural")
Af3 = field("A", "natural", size=3)
s = reg(Score("ex6_2", time="3/4"))
arp(s, with_final(Af3), [0, 1, 2], Q, brk_every=4)
s = reg(Score("ex6_3", time="4/4"))
arp(s, with_final(Af), [0, 1, 2, 3], Q, brk_every=4)
Ef = field("E", "natural")
s = reg(Score("ex6_4", time="3/4", key="e \\minor"))
arp(s, with_final(Ef), [0, 1, 2, 3, 2, 1], E, brk_every=4)
Dnf = field("D", "natural")
s = reg(Score("ex6_5", time="4/4", key="d \\minor"))
arp(s, with_final(Dnf), [3, 2, 1, 0], Q, brk_every=4)

s = reg(Score("ex6_6", time="4/4"))
seqA = [Af3[0], Af3[5], Af3[6], Af3[0], Af3[0], Af3[3], Af3[4], Af3[0]]
for i, c in enumerate(seqA):
    if i == 4:
        s.brk()
    pat = [0, 1, 2, 1]
    s.seg([c.notes[k] for k in pat], Q, roman=c.roman, cifra=c.symbol, graus=[c.labels()[k] for k in pat])

# ---------------- LIÇÃO 7 : menor harmônica ----------------
scale_score("ex7_1", "A", "harmonica", hi_pcs=(8,))
Ah = field("A", "harmonica")
s = reg(Score("ex7_2", time="4/4"))
arp(s, with_final(Ah), [0, 1, 2, 3], Q, brk_every=4, hi=lambda n: n.pc == 8)

s = reg(Score("ex7_3", time="4/4", width_mm=150))
Em7 = Af[4]
E7 = Ah[4]
s.seg(Em7.notes, Q, roman="Vm7 (natural)", cifra=Em7.symbol, graus=Em7.labels())
s.seg(E7.notes, Q, roman="V7 (harmônica)", cifra=E7.symbol, graus=E7.labels(),
      colors=[None, COL_HI, None, None])
am = chord_from("A", "m", triad=True)
s.seg(["A4", "C5", "E5"], [Q, Q, H], roman="Im", cifra="Am", graus=["1", "b3", "5"], colors=[COL_HI, None, None])

s = reg(Score("ex7_4", time="4/4", width_mm=150))
B7b5 = Ah[1]
s.seg(["B4", "D5", "F5", "A5"], Q, roman=B7b5.roman, cifra=B7b5.symbol,
      graus=[lab(B7b5, x) for x in ["B4", "D5", "F5", "A5"]], colors=[None, None, None, COL_HI])
s.seg(["G#5", "E5", "B4", "D5"], Q, roman="V7", cifra="E7", graus=[lab(E7, x) for x in ["G#5", "E5", "B4", "D5"]],
      colors=[COL_HI, None, None, COL_HI])
amc = Chord([parse("A4"), parse("C5"), parse("E5")])
s.seg(["C5", "E5", "A4"], [Q, Q, H], roman="Im", cifra="Am", graus=[lab(amc, x) for x in ["C5", "E5", "A4"]],
      colors=[COL_HI, None, None])

Dh = field("D", "harmonica")
s = reg(Score("ex7_5", time="4/4", key="d \\minor"))
arp(s, with_final(Dh), [0, 1, 2, 3], Q, brk_every=4, hi=lambda n: n.pc == 1)

# ---------------- LIÇÃO 8 : menor melódica ----------------
scale_score("ex8_1", "A", "melodica", hi_pcs=(6, 8))
Am_ = field("A", "melodica")
s = reg(Score("ex8_2", time="4/4"))
arp(s, with_final(Am_), [0, 1, 2, 3], Q, brk_every=4, hi=lambda n: n.pc in (6, 8))

s = reg(Score("ex8_3", time="4/4"))
A = parse("A4")
for kind, label, his in [("natural", "Natural", ()), ("harmonica", "Harmônica", (8,)), ("melodica", "Melódica", (6, 8))]:
    if kind != "natural":
        s.brk()
    sc = scale("A", kind)
    notes = [place_root(sc[0])]
    for i in range(1, 8):
        notes.append(place_above(sc[i % 7], notes[-1]))
    for j, n in enumerate(notes):
        s.note(n, Q, roman=label if j == 0 else None, cifra=n.name(), grau=interval_label(sc[0], n, chord=False),
               color=COL_HI if n.pc in his else None)

s = reg(Score("ex8_4", time="4/4"))
D7, E7m, Am7M = Am_[3], Am_[4], Am_[0]
s.seg(D7.notes, Q, roman=D7.roman, cifra=D7.symbol, graus=D7.labels(), colors=[None, COL_HI, None, None])
s.seg(E7m.notes[::-1], Q, roman=E7m.roman, cifra=E7m.symbol, graus=E7m.labels()[::-1],
      colors=[None, None, COL_HI, None])
s.seg(Am7M.notes, Q, roman=Am7M.roman, cifra=Am7M.symbol, graus=Am7M.labels(), colors=[None, None, None, COL_HI])
s.note("A5", W, grau="1")


PAD = ["ex3_2", "ex3_3", "ex4_2", "ex4_3", "ex4_4", "ex4_5", "ex4_6", "ex4_7", "ans4_6", "ans4_7",
       "ex5_1", "ex5_2", "ex5_3", "ex5_4", "ex5_5", "ex6_3", "ex6_4", "ex6_5", "ex7_2", "ex7_3", "ex7_4", "ex7_5",
       "ex8_2", "ex8_4", "ex3_1", "ex4_1", "ex6_2", "ex6_6"]
TRIADS = ["ex3_1", "ex4_1", "ex6_2", "ex6_6"]
for n in PAD:
    EX[n].pad = True
for n in TRIADS:
    EX[n].triads = True

if __name__ == "__main__":
    names = sys.argv[1:] or list(EX)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as pool:
        for r in pool.map(lambda n: EX[n].render(), names):
            print(r)
