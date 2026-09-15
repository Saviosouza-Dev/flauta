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

## Gerar tudo

```bash
cd ferramentas
python3 ex.py              # grava as partituras em ../partituras
python3 montar.py --svgo   # otimiza os SVG e gera ../index.html
```

Para gerar só algumas partituras: `python3 ex.py ex4_2 ex4_3`.

## Nova aula

1. Em `ex.py`, crie os exercícios (copie um parecido e troque tom/campo/padrão).
2. Em `src/body.html`, crie a `<section class="chapter" data-chapter="nova-aula">`.
3. Em `src/script.html`, inclua `{id:'nova-aula', label:'Nome curto'}` no array `chapters`.
4. Rode os dois comandos acima e publique.
