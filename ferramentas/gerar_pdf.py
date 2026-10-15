"""Gera um PDF limpo da cartilha (sem cabeçalho/rodapé do navegador).

A impressão pelo Ctrl+P do aluno sempre vem com data, título, URL e número de
página que o próprio navegador injeta — isso não dá para desligar via CSS.
Este script usa o Chromium headless do Playwright, que aceita
display_header_footer=False de verdade — e, no lugar disso, desenha um
rodapé próprio (nome do método + número de página) via header/footer
template, que é a única forma de personalizar isso: não existe CSS de
página que alcance esse rodapé do PDF.

Requisitos: `pip install playwright` + `playwright install chromium`
(já feito nesta máquina).

Rodar depois de `python montar.py`, sempre que o conteúdo mudar:
    python gerar_pdf.py
"""
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INDEX = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "cartilha-flauta.pdf")

NOME_METODO = "Harmonização aplicada para Flauta"

FOOTER_TEMPLATE = f"""
<div style="width:100%; font-family:'Work Sans', Arial, sans-serif; font-size:8px;
            color:#666; padding:0 12mm; display:grid; grid-template-columns:1fr auto 1fr; align-items:center;">
  <span></span>
  <span style="text-align:center;">{NOME_METODO}</span>
  <span class="pageNumber" style="text-align:right;"></span>
</div>
"""


def main():
    url = "file:///" + INDEX.replace("\\", "/")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1400})
        page.goto(url, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        # emula mídia impressão: dispara o listener matchMedia('print') do
        # script.html, que abre os <details> do FAQ e força as imagens lazy
        page.emulate_media(media="print")
        page.wait_for_function(
            "() => [...document.querySelectorAll('figure.pauta img')].every(img => img.complete)",
            timeout=30000,
        )
        page.pdf(
            path=OUT,
            format="A4",
            margin={"top": "13mm", "bottom": "16mm", "left": "12mm", "right": "12mm"},
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=FOOTER_TEMPLATE,
        )
        browser.close()
    size_kb = os.path.getsize(OUT) / 1024
    print(f"{OUT} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
