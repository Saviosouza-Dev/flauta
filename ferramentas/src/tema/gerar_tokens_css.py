"""Gera tokens.css a partir de tokens.json.

Os temas do tokens.json vêm em pares por paleta: "<paleta>" (claro) e
"<paleta>-escuro". A primeira paleta é a padrão. No site:
  <html data-paleta="grafite">   escolhe a paleta (nanquim | grafite | salvia)
  <html data-tema="escuro">      força claro/escuro (sem o atributo, segue o sistema)

Uso: python3 gerar_tokens_css.py tokens.json > tokens.css
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = json.load(open(sys.argv[1], encoding="utf-8"))
ids = [th["id"] for th in t["color"]["themes"]]
first = ids[0]
paletas = [i for i in ids if not i.endswith("-escuro")]
PULAR = {"acento"}  # definido uma vez em :root e trocado por data-instrumento


def css_val(v):
    m = re.fullmatch(r"\{(.+)\}", v)
    return f"var(--{m.group(1)})" if m else v


def valor(tok, tema):
    v = tok["value"]
    if isinstance(v, str):
        return v
    return v.get(tema, v.get(first))


def bloco(seletor, tema):
    linhas = []
    for fam in ("color", "shadow"):
        for tok in t.get(fam, {}).get("tokens", []):
            if tok["name"] in PULAR:
                continue
            linhas.append(f"  --{tok['name']}: {css_val(valor(tok, tema))};")
    return seletor + "{\n" + "\n".join(linhas) + "\n}"


saida = [f"/* {t['name']} — gerado de tokens.json (não edite à mão) */"]

raiz = []
for fam in ("spacing", "radius"):
    for tok in t[fam]["tokens"]:
        raiz.append(f"  --{tok['name']}: {tok['value']};")
for k, v in t["type"]["families"].items():
    raiz.append(f"  --font-{k}: {v};")
acento = next(x for x in t["color"]["tokens"] if x["name"] == "acento")
raiz.append(f"  --acento: {css_val(valor(acento, first))};")
saida.append(":root{\n" + "\n".join(raiz) + "\n}")

# claro
for p in paletas:
    sel = f':root, [data-paleta="{p}"]' if p == first else f'[data-paleta="{p}"]'
    saida.append(bloco(sel, p))
# escuro automático
escuros = []
for p in paletas:
    sel = (f':root:not([data-tema="claro"]), [data-paleta="{p}"]:not([data-tema="claro"])'
           if p == first else f'[data-paleta="{p}"]:not([data-tema="claro"])')
    escuros.append(bloco(sel, p + "-escuro"))
saida.append("@media (prefers-color-scheme: dark){\n" + "\n".join(escuros) + "\n}")
# escuro forçado
for p in paletas:
    sel = (f':root[data-tema="escuro"], [data-paleta="{p}"][data-tema="escuro"]'
           if p == first else f'[data-paleta="{p}"][data-tema="escuro"]')
    saida.append(bloco(sel, p + "-escuro"))

print("\n".join(saida))
