"""Teoria musical mínima: soletração de notas, escalas, campos harmônicos, cifras e graus."""

LETTERS = "CDEFGAB"
NAT = [0, 2, 4, 5, 7, 9, 11]

SCALES = {
    "maior": [0, 2, 4, 5, 7, 9, 11],
    "natural": [0, 2, 3, 5, 7, 8, 10],
    "harmonica": [0, 2, 3, 5, 7, 8, 11],
    "melodica": [0, 2, 3, 5, 7, 9, 11],
}

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]


class Note:
    def __init__(self, letter, acc=0, octave=4):
        self.l = letter if isinstance(letter, int) else LETTERS.index(letter)
        self.acc = acc
        self.oct = octave

    @property
    def midi(self):
        return 12 * (self.oct + 1) + NAT[self.l] + self.acc

    @property
    def pc(self):
        return (NAT[self.l] + self.acc) % 12

    def name(self):  # "Bb", "F#"
        return LETTERS[self.l] + {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}[self.acc]

    def ly(self):  # lilypond english names, absolute octave
        s = LETTERS[self.l].lower() + {-2: "ff", -1: "f", 0: "", 1: "s", 2: "ss"}[self.acc]
        d = self.oct - 3
        return s + ("'" * d if d > 0 else "," * (-d))

    def pt(self):
        base = ["Dó", "Ré", "Mi", "Fá", "Sol", "Lá", "Si"][self.l]
        return base + {-2: "𝄫", -1: "♭", 0: "", 1: "♯", 2: "𝄪"}[self.acc]

    def copy(self, octave=None):
        return Note(self.l, self.acc, self.oct if octave is None else octave)

    def __repr__(self):
        return f"{self.name()}{self.oct}"


def parse(s):
    """'Bb4' -> Note ; 'F#' -> Note octave 4"""
    l = s[0]
    rest = s[1:]
    acc = 0
    while rest and rest[0] in "b#":
        acc += -1 if rest[0] == "b" else 1
        rest = rest[1:]
    return Note(l, acc, int(rest) if rest else 4)


def scale(tonic, kind):
    """Lista de 7 Notes (classe, oitava 4 provisória) soletradas corretamente."""
    t = parse(tonic) if isinstance(tonic, str) else tonic
    out = []
    for i, iv in enumerate(SCALES[kind]):
        l = (t.l + i) % 7
        target = (t.pc + iv) % 12
        acc = (target - NAT[l]) % 12
        if acc > 6:
            acc -= 12
        out.append(Note(l, acc, 4))
    return out


def place_above(n, prev):
    """Coloca a classe de nota n na oitava mais baixa acima de prev."""
    x = n.copy(prev.oct)
    while x.midi <= prev.midi:
        x.oct += 1
    return x


def place_root(n, low=60, high=71):
    x = n.copy(4)
    while x.midi < low:
        x.oct += 1
    while x.midi > high:
        x.oct -= 1
    return x


def interval_label(root, note, chord=True):
    """Grau de 'note' em relação a 'root' (1, b3, 5, b7, bb7, 9...)."""
    ld = (note.l - root.l) % 7
    semis = (note.pc - root.pc) % 12
    expected = [0, 2, 4, 5, 7, 9, 11][ld]
    diff = semis - expected
    if diff > 6:
        diff -= 12
    if diff < -6:
        diff += 12
    if chord:
        num = ["1", "9", "3", "11", "5", "13", "7"][ld]
    else:
        num = ["1", "2", "3", "4", "5", "6", "7"][ld]
    # 3ª e 5ª e 7ª usam referência maior/justa/maior
    pre = {-2: "bb", -1: "b", 0: "", 1: "#", 2: "##"}[diff]
    return pre + num


TETRAD_Q = {
    (4, 7, 11): "7M",
    (4, 7, 10): "7",
    (3, 7, 10): "m7",
    (3, 6, 10): "m7(b5)",
    (3, 6, 9): "°",
    (3, 7, 11): "m7M",
    (4, 8, 11): "7M(#5)",
    (4, 8, 10): "7(#5)",
}
TRIAD_Q = {(4, 7): "", (3, 7): "m", (3, 6): "°", (4, 8): "(#5)"}


class Chord:
    def __init__(self, notes, degree=None, roman=None):
        self.notes = notes  # list of Note (root first, ascending)
        self.root = notes[0]
        self.degree = degree
        self.roman_base = roman

    @property
    def quality(self):
        ints = tuple((n.pc - self.root.pc) % 12 for n in self.notes[1:])
        q = TETRAD_Q if len(self.notes) == 4 else TRIAD_Q
        return q[ints]

    @property
    def symbol(self):
        return self.root.name() + self.quality

    @property
    def roman(self):
        return (self.roman_base or "") + self.quality

    def labels(self):
        return [interval_label(self.root, n) for n in self.notes]


def field(tonic, kind, size=4, low=60, high=71):
    """Campo harmônico: lista de 7 Chords, raízes entre C4 e B4 (região confortável)."""
    sc = scale(tonic, kind)
    maj = scale(sc[0].name(), "maior")
    chords = []
    for d in range(7):
        root = place_root(sc[d], low, high)
        notes = [root]
        for k in range(1, size):
            notes.append(place_above(sc[(d + 2 * k) % 7], notes[-1]))
        # prefixo b no numeral romano se o grau for rebaixado em relação ao maior
        diff = (sc[d].pc - maj[d].pc) % 12
        pre = "b" if diff == 11 else ("#" if diff == 1 else "")
        c = Chord(notes, d, pre + ROMAN[d])
        chords.append(c)
    return chords


def chord_from(root_str, quality, octave=None, triad=False):
    """Monta um acorde a partir de fundamental e qualidade (soletrado por terças)."""
    r = parse(root_str)
    if octave is None:
        r = place_root(r)
    rev = {v: k for k, v in TETRAD_Q.items()}
    rev3 = {v: k for k, v in TRIAD_Q.items()}
    ints = rev3[quality] if (triad or quality not in rev) else rev[quality]
    notes = [r]
    for k, iv in enumerate(ints, start=1):
        l = (r.l + 2 * k) % 7
        target = (r.pc + iv) % 12
        acc = (target - NAT[l]) % 12
        if acc > 6:
            acc -= 12
        notes.append(place_above(Note(l, acc, 4), notes[-1]))
    return Chord(notes)


if __name__ == "__main__":
    for k in SCALES:
        for t in ["C", "A"]:
            f = field(t, k)
            print(k, t, [c.symbol for c in f], [c.roman for c in f])
