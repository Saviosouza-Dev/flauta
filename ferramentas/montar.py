"""Monta o index.html da cartilha a partir de src/*.html + partituras geradas em ex.py."""
import html
import json
import os
import re
import subprocess
import sys
from fractions import Fraction

from theory import *
from ex import EX
from transpose import export_all, ORIGIN

ROOT = os.path.dirname(os.path.abspath(__file__))   # ferramentas/
SITE = os.path.dirname(ROOT)                          # raiz do repositório
PART = os.path.join(SITE, "partituras")


def pretty_roman(s):
    return re.sub(r"^b(?=[IV])", "♭", s)


def parse_symbol(sym):
    m = re.match(r"^([A-G](?:#|b)?)(.*)$", sym)
    return m.group(1), m.group(2)


def pad_midis(sym, triads):
    root, q = parse_symbol(sym)
    tetrads = set(TETRAD_Q.values())
    triad = triads or q not in tetrads
    if triad and q not in TRIAD_Q.values():
        return None
    c = chord_from(root, q, triad=triad)
    return [n.midi - 12 for n in c.notes]


def play_data(s):
    n, p = [], []
    t = Fraction(0)
    cur = None  # (start, midis)
    for kind, note, d, r, cif, g, col in s.ev:
        if s.pad and cif and cif != "_":
            ms = pad_midis(cif, s.triads)
            if ms:
                if cur:
                    p.append([float(cur[0] * 4), cur[1], float((t - cur[0]) * 4)])
                cur = (t, ms)
        beats = float(d * 4)
        n.append([note.midi if kind == "n" else 0, beats])
        t += d
    if cur:
        p.append([float(cur[0] * 4), cur[1], float((t - cur[0]) * 4)])
    return {"n": n, "p": p}


def svg_size(path):
    with open(path, encoding="utf-8") as f:
        head = f.read(600)
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    if not m:
        m = re.search(r'width="([\d.]+)(?:pt)?" height="([\d.]+)(?:pt)?"', head)
    return float(m.group(1)), float(m.group(2))


def fig(match):
    parts = match.group(1).split("|")
    name, tag, title = parts[0].strip(), parts[1].strip(), parts[2].strip()
    how = parts[3].strip() if len(parts) > 3 else ""
    s = EX[name]
    w, h = svg_size(os.path.join(PART, name + ".svg"))
    pct = round(min(100, s.width / 168 * 100), 1)
    data = json.dumps(play_data(s), separators=(",", ":"))
    how_html = f'<span class="ex-how">{how}</span>' if how else ""
    alt = html.escape(f"Partitura — {title}")
    ex_attr = f' data-ex="{name}"' if name in ORIGIN else ""
    return f'''<figure class="pauta" data-play='{data}'{ex_attr}>
          <figcaption><span class="ex-tag">{tag}</span><span class="ex-title">{title}</span>{how_html}</figcaption>
          <picture>
            <source media="(max-width:620px)" srcset="partituras/m/{name}.svg">
            <img src="partituras/{name}.svg" width="{w:.0f}" height="{h:.0f}" style="width:{pct}%" alt="{alt}">
          </picture>
        </figure>'''


def chips(match):
    tonic, kind = match.group(1), match.group(2)
    f = field(tonic, kind)
    ref = field(tonic, "natural") if kind in ("harmonica", "melodica") else None
    out = ['<div class="chips">']
    for i, c in enumerate(f):
        changed = ref is not None and ref[i].symbol != c.symbol
        cls = "chip changed" if changed else "chip"
        notes = " ".join(n.name() for n in c.notes)
        out.append(f'<div class="{cls}"><span class="r">{pretty_roman(c.roman)}</span>'
                   f'<span class="c">{c.symbol}</span><span class="g">{notes}</span></div>')
    out.append("</div>")
    return "\n        ".join(out)


KIND_LABEL = {"maior": "maior", "natural": "menor natural", "harmonica": "menor harmônica", "melodica": "menor melódica"}


def mapa(match):
    tonic = match.group(1)
    rows = []
    prev = None
    for kind in ["maior", "natural", "harmonica", "melodica"]:
        f = field(tonic, kind)
        cells = []
        for i, c in enumerate(f):
            hl = prev is not None and prev[i].symbol != c.symbol
            attr = ' class="hl"' if hl else ""
            cells.append(f"<td{attr}>{c.symbol}</td>")
        name = "Lá " + KIND_LABEL[kind] if tonic == "A" else tonic + " " + KIND_LABEL[kind]
        rows.append(f"<tr><th>{name}</th>{''.join(cells)}</tr>")
        prev = f
    head = "".join(f"<th>{g}</th>" for g in ROMAN)
    return f'''<div class="table-scroll">
          <table class="campo">
            <thead><tr><th></th>{head}</tr></thead>
            <tbody>{"".join(rows)}</tbody>
          </table>
        </div>'''


PT = {"C": "Dó", "D": "Ré", "E": "Mi", "F": "Fá", "G": "Sol", "A": "Lá", "B": "Si"}


def pt_name(t):
    s = PT[t[0]]
    if t[1:] == "#":
        s += "♯"
    elif t[1:] == "b":
        s += "♭"
    return s


def tabelas(_):
    majors = ["C", "G", "D", "A", "E", "B", "F#", "F", "Bb", "Eb", "Ab", "Db"]
    minors = ["A", "E", "B", "F#", "C#", "G#", "D", "G", "C", "F", "Bb", "Eb"]
    easy_maj = {"C", "G", "D", "F", "Bb"}
    easy_min = {"A", "E", "B", "D", "G"}
    out = []
    for kind, keys, easy, h in [("maior", majors, easy_maj, "Campo harmônico maior"),
                                 ("natural", minors, easy_min, "Campo harmônico menor natural"),
                                 ("harmonica", minors, easy_min, "Campo harmônico menor harmônico"),
                                 ("melodica", minors, easy_min, "Campo harmônico menor melódico")]:
        f0 = field("C" if kind == "maior" else "A", kind)
        head = "".join(f"<th>{pretty_roman(c.roman)}</th>" for c in f0)
        rows = []
        for k in keys:
            f = field(k, kind)
            label = f"{k}{'' if kind == 'maior' else 'm'}"
            cls = ' class="easy"' if k in easy else ""
            rows.append(f"<tr{cls}><th>{label}</th>" + "".join(f"<td>{c.symbol}</td>" for c in f) + "</tr>")
        out.append(f'''<h3>{h}</h3>
        <div class="table-scroll">
          <table class="campo">
            <thead><tr><th>Tom</th>{head}</tr></thead>
            <tbody>
              {"".join(rows)}
            </tbody>
          </table>
        </div>''')
    return "\n        ".join(out)


def write_transpose_data():
    """Dados dos 12 tons (pauta em formato VexFlow + áudio já transposto),
    calculados em cima da teoria (transpose.py) — não depende do LilyPond."""
    data = export_all(EX)
    js = "window.TRANSPOSE_DATA = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n"
    path = os.path.join(PART, "transpose_data.js")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    print("transpose_data.js", len(js))


def tema():
    """Folha de estilo do método: tokens.css (gerado de tokens.json) + metodo.css.
    A pasta src/tema/ é igual em todas as cartilhas; o instrumento é escolhido
    em src/head.html, no atributo data-instrumento do <html>."""
    d = os.path.join(ROOT, "src", "tema")
    tokens_css = subprocess.run([sys.executable, os.path.join(d, "gerar_tokens_css.py"), os.path.join(d, "tokens.json")],
                                check=True, capture_output=True, text=True, encoding="utf-8").stdout
    with open(os.path.join(d, "tokens.css"), "w", encoding="utf-8", newline="\n") as f:
        f.write(tokens_css)
    metodo = open(os.path.join(d, "metodo.css"), encoding="utf-8").read()
    return "<style>\n" + tokens_css + "\n" + metodo + "</style>"


def build():
    write_transpose_data()
    head = open(os.path.join(ROOT, "src", "head.html"), encoding="utf-8").read()
    head = head.replace("{{TEMA}}", tema())
    body = open(os.path.join(ROOT, "src", "body.html"), encoding="utf-8").read()
    script = open(os.path.join(ROOT, "src", "script.html"), encoding="utf-8").read()
    body = re.sub(r"\{\{FIG ([^}]*)\}\}", fig, body)
    body = re.sub(r"\{\{CHIPS (\S+) (\S+)\}\}", chips, body)
    body = re.sub(r"\{\{MAPA (\S+)\}\}", mapa, body)
    body = re.sub(r"\{\{TABELAS\}\}", tabelas, body)
    left = re.findall(r"\{\{[^}]*\}\}", body)
    if left:
        raise SystemExit(f"placeholders não resolvidos: {left}")
    out = head + body + script
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("index.html", len(out))


def optimize_svgs():
    ink = "rgb(8.627451%, 10.588235%, 14.901961%)"  # #161B26 (token pauta-tinta)
    files = []
    for d in [PART, os.path.join(PART, "m")]:
        for fn in os.listdir(d):
            if fn.endswith(".svg"):
                p = os.path.join(d, fn)
                s = open(p, encoding="utf-8").read()
                s = s.replace('fill="rgb(0%, 0%, 0%)"', f'fill="{ink}"').replace('stroke="rgb(0%, 0%, 0%)"', f'stroke="{ink}"')
                open(p, "w", encoding="utf-8", newline="\n").write(s)
                files.append(p)
    for d in [PART, os.path.join(PART, "m")]:
        subprocess.run(["npx", "svgo", "--multipass", "-p", "2", "-q", "-f", d], cwd=ROOT, check=True)


if __name__ == "__main__":
    if "--svgo" in sys.argv:
        optimize_svgs()
    build()
