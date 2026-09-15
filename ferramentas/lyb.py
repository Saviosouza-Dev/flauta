"""Gerador de partituras LilyPond -> SVG (via PDF recortado + pdftocairo)."""
import os
import re
import subprocess
from fractions import Fraction
from theory import Note, parse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "partituras")
OUT_M = os.path.join(OUT, "m")
LYDIR = os.path.join(HERE, "build", "ly")
os.makedirs(OUT_M, exist_ok=True)
os.makedirs(LYDIR, exist_ok=True)

def _rgb(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return f"#(rgb-color {r:.3f} {g:.3f} {b:.3f})"


COL_ROMAN = _rgb("#9A6A1C")   # latão escuro  -> grau do campo (I, IIm7...)
COL_CIFRA = _rgb("#3B2A1B")   # tinta         -> cifra
COL_GRAU = _rgb("#2F5A3A")    # sálvia escuro -> graus (1, 3, 5, b7)
COL_HI = _rgb("#B0362A")      # rosa/vermelho -> nota em destaque
COL_BLANK = _rgb("#8A7A66")
COL_INK = _rgb("#2A1E14")


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def mk(text, flat_raise=0.45, flat_size=-2.5):
    """Texto com b/# viram glifos ♭/♯ do LilyPond."""
    parts = []
    buf = ""
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        prev = text[i - 1] if i > 0 else ""
        is_flat = ch == "b" and (nxt.isdigit() or nxt == "b" or nxt in "IV" or (prev in "ABCDEFG" and i == 1))
        if ch == "b" and nxt == "b" and (i + 2 < len(text) and text[i + 2].isdigit()):
            if buf:
                parts.append(f'"{esc(buf)}"')
                buf = ""
            parts.append(f"\\raise #{flat_raise} \\fontsize #{flat_size} \\doubleflat")
            i += 2
            continue
        if is_flat:
            if buf:
                parts.append(f'"{esc(buf)}"')
                buf = ""
            parts.append(f"\\raise #{flat_raise} \\fontsize #{flat_size} \\flat")
        elif ch == "#":
            if buf:
                parts.append(f'"{esc(buf)}"')
                buf = ""
            parts.append(f"\\raise #{flat_raise + 0.25} \\fontsize #{flat_size - 0.5} \\sharp")
        else:
            buf += ch
        i += 1
    if buf:
        parts.append(f'"{esc(buf)}"')
    return "\\concat { " + " ".join(parts) + " }"


def dur_ly(fr):
    fr = Fraction(fr)
    table = {
        Fraction(1): "1", Fraction(3, 4): "2.", Fraction(1, 2): "2", Fraction(3, 8): "4.",
        Fraction(1, 4): "4", Fraction(3, 16): "8.", Fraction(1, 8): "8", Fraction(1, 16): "16",
        Fraction(3, 2): "1.",
    }
    return table[fr]


class Score:
    """Partitura de uma linha melódica com 3 camadas de texto: grau romano, cifra, graus."""

    def __init__(self, name, time="4/4", key=None, width_mm=168, staff_size=19,
                 roman=True, cifra=True, graus=True, tempo=None, ragged_last=True):
        self.name = name
        self.time = time
        self.key = key  # ex: "g \\major"
        self.width = width_mm
        self.staff_size = staff_size
        self.show_roman = roman
        self.show_cifra = cifra
        self.show_graus = graus
        self.tempo = tempo
        self.ev = []  # (kind, ly_pitch or None, dur Fraction, roman, cifra, grau, color)
        self.ragged_last = ragged_last
        self.extra = ""
        self.breaks = set()
        self.wide_blank = True
        self.mobile_width = 92
        self.pad = False
        self.mobile_breaks = set()
        self.triads = False

    def note(self, n, dur, roman=None, cifra=None, grau=None, color=None):
        if isinstance(n, str):
            n = parse(n)
        self.ev.append(("n", n, Fraction(dur), roman, cifra, grau, color))
        return self

    def rest(self, dur, roman=None, cifra=None):
        self.ev.append(("r", None, Fraction(dur), roman, cifra, None, None))
        return self

    def space(self, dur, roman=None, cifra=None):
        self.ev.append(("s", None, Fraction(dur), roman, cifra, None, None))
        return self

    def seg(self, notes, dur, roman=None, cifra=None, graus=None, colors=None):
        durs = dur if isinstance(dur, (list, tuple)) else [dur] * len(notes)
        for i, n in enumerate(notes):
            self.note(n, durs[i],
                      roman if i == 0 else None,
                      cifra if i == 0 else None,
                      graus[i] if graus else None,
                      colors[i] if colors else None)
        return self

    def brk(self):
        """quebra de sistema antes do próximo evento"""
        self.breaks.add(len(self.ev))
        return self

    def build(self, mobile=False):
        mus, rom, cif, gr = [], [], [], []
        for idx, (kind, n, d, r, c, g, col) in enumerate(self.ev):
            if (idx in self.breaks and not mobile) or (mobile and idx in self.mobile_breaks):
                mus.append("\\break")
            dl = dur_ly(d)
            if kind == "n":
                t = f"\\tweak color {col} " if col else ""
                mus.append(f"{t}{n.ly()}{dl}")
            elif kind == "r":
                mus.append(f"r{dl}")
            else:
                mus.append(f"s{dl}")

            def lyr(val, style):
                if val is None:
                    return f"\\skip {dl}"
                if val == "_":
                    return f"\\markup \\with-color {COL_BLANK} \\override #'(box-padding . 0.35) \\override #'(thickness . 1.2) \\box \\transparent \"{style}\" {dl}"
                return f"\\markup {mk(val)} {dl}"

            rom.append(lyr(r, "VIIm7"))
            cif.append(lyr(c, "C7M(b5)" if self.wide_blank else "G#"))
            if g is None:
                gr.append(f"\\skip {dl}")
            elif g == "_":
                gr.append(f"\\markup \\with-color {COL_BLANK} \\override #'(box-padding . 0.35) \\override #'(thickness . 1.2) \\box \\transparent \"b7\" {dl}")
            else:
                colg = col if col else COL_GRAU
                gr.append(f"\\markup \\with-color {colg} {mk(g, 0.35, -3)} {dl}")

        key = f"\\key {self.key}" if self.key else ""
        tempo = f"\\tempo 4 = {self.tempo}" if self.tempo else ""
        roman_ctx = f"""
    \\new Lyrics \\with {{
      \\override VerticalAxisGroup.staff-affinity = #DOWN
      \\override LyricText.self-alignment-X = #LEFT
      \\override LyricText.font-size = #-1.2
      \\override LyricText.color = {COL_ROMAN}
      \\override LyricText.font-series = #'bold
      \\override VerticalAxisGroup.nonstaff-nonstaff-spacing = #'((basic-distance . 0) (padding . 1.1) (stretchability . 0))
      \\override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing = #'((basic-distance . 0) (padding . 2) (stretchability . 1000))
    }} {{ \\lyricmode {{ {' '.join(rom)} }} }}""" if self.show_roman else ""
        cifra_ctx = f"""
    \\new Lyrics \\with {{
      \\override VerticalAxisGroup.staff-affinity = #DOWN
      \\override LyricText.self-alignment-X = #LEFT
      \\override LyricText.font-size = #0.6
      \\override LyricText.font-series = #'bold
      \\override LyricText.color = {COL_CIFRA}
      \\override VerticalAxisGroup.nonstaff-relatedstaff-spacing = #'((basic-distance . 0) (padding . 0.9) (stretchability . 0))
      \\override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing = #'((basic-distance . 0) (padding . 2) (stretchability . 1000))
    }} {{ \\lyricmode {{ {' '.join(cif)} }} }}""" if self.show_cifra else ""
        graus_ctx = f"""
    \\new Lyrics \\with {{
      \\override LyricText.font-size = #-1.5
      \\override LyricText.font-series = #'bold
      \\override VerticalAxisGroup.nonstaff-relatedstaff-spacing = #'((basic-distance . 0) (padding . 1.7) (stretchability . 0))
      \\override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing = #'((basic-distance . 0) (padding . 3) (stretchability . 1000))
    }} {{ \\lyricmode {{ {' '.join(gr)} }} }}""" if self.show_graus else ""

        return f"""\\version "2.24.0"
\\language "english"
#(set-global-staff-size {self.staff_size})
\\paper {{
  indent = 0\\mm
  line-width = {(self.mobile_width if mobile else self.width)}\\mm
  ragged-last = {'##t' if self.ragged_last else '##f'}
  ragged-right = ##f
  tagline = ##f
  print-page-number = ##f
  system-system-spacing = #'((basic-distance . 18) (minimum-distance . 14) (padding . {7 if mobile else 6}) (stretchability . 0))
  #(define fonts (set-global-fonts #:roman "Work Sans" #:sans "Work Sans" #:factor (/ staff-height pt 20)))
}}
\\header {{ tagline = ##f }}
\\score {{
  <<{roman_ctx}{cifra_ctx}
    \\new Staff {{
      \\clef treble {key} {tempo}
      \\numericTimeSignature
      \\time {self.time}
      \\override Score.BarNumber.break-visibility = ##(#f #f #f)
      {' '.join(mus)}
      \\bar "|."
    }}{graus_ctx}
  >>
  \\layout {{
    \\context {{ \\Score \\override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/16) }}
  }}
}}
{self.extra}
"""

    def _render_one(self, mobile):
        suffix = "_m" if mobile else ""
        ly = os.path.join(LYDIR, self.name + suffix + ".ly")
        with open(ly, "w") as f:
            f.write(self.build(mobile))
        base = os.path.join(LYDIR, self.name + suffix)
        r = subprocess.run(["lilypond", "-dcrop", "-dno-point-and-click", "--pdf", "-o", base, ly],
                           capture_output=True, text=True)
        cropped = base + ".cropped.pdf"
        if not os.path.exists(cropped):
            print(r.stderr[-3000:])
            raise RuntimeError("lilypond falhou: " + self.name)
        if "error" in r.stderr.lower() or "warning" in r.stderr.lower():
            print(self.name + suffix, r.stderr[-800:])
        svg = os.path.join(OUT_M if mobile else OUT, self.name + ".svg")
        subprocess.run(["pdftocairo", "-svg", cropped, svg], check=True)
        return svg

    def render(self):
        a = self._render_one(False)
        self._render_one(True)
        return a
