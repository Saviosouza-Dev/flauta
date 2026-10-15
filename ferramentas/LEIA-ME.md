# Gerador das partituras

As partituras não são desenhadas à mão: são calculadas a partir da teoria
(`theory.py`), gravadas com o LilyPond e montadas no `index.html`. Assim as
notas, cifras e graus nunca saem errados.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `theory.py` | Escalas, campos harmônicos, cifras e graus (soletração correta das notas). |
| `lyb.py` | Transforma um exercício em partitura LilyPond → SVG (versão larga e versão celular). |
| `ex.py` | **A lista de exercícios.** Cada `reg(Score("ex4_2", ...))` é uma partitura. |
| `montar.py` | Junta `src/head.html` + `src/body.html` + `src/script.html` e gera o `index.html`. |
| `src/body.html` | Texto das aulas. `{{FIG ex4_2|Exercício 4.2|Título|Instrução}}` insere uma partitura. |

Outros marcadores aceitos no `body.html`: `{{CHIPS C maior}}` (fichas do campo),
`{{MAPA A}}` (comparação dos quatro campos) e `{{TABELAS}}`.

## Requisitos

- Python 3
- LilyPond 2.24 e `pdftocairo` (poppler)
- Fonte Work Sans instalada no sistema
- Node.js (para `npx svgo`, que reduz o tamanho dos SVG)
- Playwright (`pip install playwright && playwright install chromium`), só
  para gerar o PDF pronto pra download — veja abaixo

## Gerar tudo

```bash
cd ferramentas
python3 ex.py              # grava as partituras em ../partituras
python3 montar.py --svgo   # otimiza os SVG e gera ../index.html
python3 gerar_pdf.py       # gera ../cartilha-flauta.pdf (botão "Baixar PDF")
```

Para gerar só algumas partituras: `python3 ex.py ex4_2 ex4_3`.

## PDF para download (`gerar_pdf.py`)

O botão "Baixar PDF" da barra lateral aponta pro arquivo estático
`cartilha-flauta.pdf`, gerado com Chromium headless (Playwright). Existe
porque o `Ctrl+P` do navegador sempre injeta cabeçalho/rodapé (data, título,
URL, número de página) por cima da página impressa — isso é um comportamento
do navegador, não dá pra desligar por CSS. O `gerar_pdf.py` usa
`display_header_footer=False` de verdade e produz um PDF limpo.

Rode `python3 gerar_pdf.py` **sempre que o conteúdo mudar** (depois do
`montar.py`) e comite o `.pdf` junto — ele precisa estar versionado pro
GitHub Pages servir.

## Nova aula

1. Em `ex.py`, crie os exercícios (copie um parecido e troque tom/campo/padrão).
2. Em `src/body.html`, crie a `<section class="chapter" data-chapter="nova-aula">`.
3. Em `src/script.html`, inclua `{id:'nova-aula', label:'Nome curto'}` no array `chapters`.
4. Rode os dois comandos acima e publique.

## Visual (tema do método)

As cores, fontes e estilos ficam em `src/tema/` — **a mesma pasta em todas as
cartilhas** (flauta, violão, teclado…):

| Arquivo | Para que serve |
|---|---|
| `tema/tokens.json` | A paleta, os tamanhos de letra, espaços e cantos. **Mude cores aqui.** |
| `tema/metodo.css` | Os componentes (barra lateral, partitura, fichas, jogos…), usando só as variáveis dos tokens. |
| `tema/gerar_tokens_css.py` | Transforma `tokens.json` em `tokens.css` (o `montar.py` roda sozinho). |

**Paletas:** o `tokens.json` tem três paletas — Nanquim (padrão), Grafite e
Sálvia —, cada uma com versão clara e escura. O aluno escolhe em “Cores”, na
barra lateral; a escolha fica salva no navegador e vale para todas as cartilhas
do site. Para mudar a padrão, ponha `data-paleta="grafite"` (ou `salvia`) no `<html>`.

As partituras usam a mesma tinta nas três paletas (tokens `pauta-*`). Se mudar
essas cores, rode `python3 recolorir_partituras.py ../partituras` e ajuste
`COL_*` em `lyb.py`.

O instrumento é escolhido em `src/head.html`, no `<html data-instrumento="flauta">`
(`flauta`, `violao`, `teclado`, `canto`, `percussao`). Só a cor de acento muda;
as cores da música (romano, cifra, grau, destaque) são iguais em todas as cartilhas.

Para uma cartilha nova: copie `src/tema/`, troque o `data-instrumento`, o desenho
em `.brand .marca` no `body.html` e rode `python3 montar.py`.
