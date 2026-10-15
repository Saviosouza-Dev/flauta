# Graus e Campos — Design System

O sistema visual de todas as cartilhas (flauta, violão, teclado…).

- **Ver tudo:** abra `index.html` desta pasta no navegador (dê dois cliques). No topo dá para trocar paleta, tema claro/escuro e instrumento.
- **Fonte de verdade:** as cores e tamanhos ficam em `../ferramentas/src/tema/tokens.json`, e o estilo dos componentes em `../ferramentas/src/tema/metodo.css`. A galeria lê esses mesmos arquivos, então qualquer mudança lá aparece aqui.
- `marcas/`: a marca da flauta em SVG, para usar fora do site (favicon, redes, impressos).

---

Graus e Campos é o sistema visual das cartilhas de harmonia do professor Sávio Souza — uma por instrumento (flauta, violão, teclado e as que vierem), todas com o mesmo método: escalas, graus e campos harmônicos, com partitura, áudio, teste rápido e checklist. A ideia visual é **papel e tinta de partitura**: fundo de papel limpo, tinta escura, latão para os graus romanos e verde para os graus das notas. O aluno escolhe entre **três paletas** — Nanquim, Grafite e Sálvia —, cada uma com versão clara e escura. Cada instrumento tem **uma** cor de identidade; o resto é igual em todas as cartilhas.

## A regra das três camadas

1. **Camada do instrumento — muda.** Só o token `acento` muda de uma cartilha para outra. Escolha com `data-instrumento` no `<html>`:
   `flauta` → `inst-flauta` (cobalto no Nanquim, verde-azulado no Grafite, anil na Sálvia) · `violao` → `inst-violao` (jacarandá) · `teclado` → `inst-teclado` (ameixa) · `canto` → `inst-canto` (petróleo) · `percussao` → `inst-percussao` (grafite).
   Componentes nunca usam `inst-*` direto; usam `acento` e `sobre-acento`.
2. **Camada da paleta — o aluno escolhe.** Nanquim (azul-marinho, padrão), Grafite (neutro) e Sálvia (verde calmo) trocam o papel, a tinta, o bloco da Ideia-chave e o tom do instrumento. No site, `data-paleta="nanquim|grafite|salvia"` no `<html>`; no design system, os temas `<paleta>` e `<paleta>-escuro`. O seletor “Cores” fica na barra lateral e a escolha vale para todas as cartilhas do site.
3. **Camada da música — nunca muda.** `musica-romano`, `musica-cifra`, `musica-grau` e `musica-destaque` significam a mesma coisa em todos os instrumentos e em todas as aulas. O aluno que muda da flauta para o violão, ou de paleta, lê as cores do mesmo jeito.

Não invente uma terceira cor de destaque. Se algo precisa chamar atenção e não é música, use `acento`.

## Conteúdo e voz

- Fale com o aluno por **você**, no presente, em frases curtas e imperativas: “Toque devagar”, “Diga a cifra em voz alta”, “Só avance quando marcar todos os itens”.
- Português do Brasil, nomes de nota em português (Dó, Ré, Mi) e cifras em letra (C, Dm7, Bm7(♭5)). Use os símbolos reais ♭ e ♯ em texto corrido.
- Títulos de aula são frases simples em caixa de frase: “O campo harmônico maior”, “Como nasce um acorde”. Nada de CAIXA ALTA em títulos — caixa alta só no estilo `rotulo` (AULA 4, IDEIA-CHAVE, CONSULTA).
- Cada aula segue a mesma ordem: sobrancelha (`AULA N`) → título → lead → Ideia-chave → fichas/legenda → exercícios em partitura → Teste rápido → Checklist para avançar.
- Exemplo de lead: “Agora juntamos as duas aulas anteriores: aplicamos o ‘pula-uma’ em cada grau da escala maior, usando só as notas da escala.”
- Exemplo de Ideia-chave: “Em qualquer tom maior, a sequência é sempre a mesma: **7M · m7 · m7 · 7M · 7 · m7 · m7(b5)**. Decore como um número de telefone.”
- Sem emoji como enfeite. Os únicos glifos de interface são ▶ (ouvir), ■ (parar), ← → (navegar) e o “+ / –” das dúvidas. *Observação:* o botão “Rolar” do Dado harmônico ainda usa 🎲 — troque por texto quando mexer nele.

## Cor

- Fundo da página: `papel`. Barra lateral, rodapé e cabeçalhos de tabela: `papel-fundo`. Tudo que “pousa” sobre o papel (cartão, ficha, partitura, jogo): `folha` com borda `linha` e sombra `sombra-folha`.
- Texto: `tinta` para corpo e títulos; `tinta-suave` para lead, instruções e descrições; `tinta-fraca` só para metadados curtos sobre `papel` ou `folha`.
- Bordas de controles (botão contornado, select, número da aula): `linha-forte`. Divisórias: `linha`.
- **Ideia-chave** é o único bloco invertido: `bloco` com texto `bloco-tinta` e negritos em `bloco-realce`. Um por aula, no máximo.
- **Dica** usa `musica-grau` e **Atenção** usa `musica-destaque` — sempre com o ícone (i / !) e a palavra em negrito no começo (“**Como usar:**”, “**Atenção a uma diferença de nomenclatura:**”). Nunca só a cor.
- `musica-destaque` marca *o que mudou* (nota alterada, acorde que difere entre campos, resposta errada) e vem sempre com sublinhado ou riscado, para quem não distingue vermelho e verde.
- Todas as combinações de texto passam 4,5:1 nos dois temas; `musica-romano` é o mais justo (4,6:1 sobre `papel-fundo` no claro).

## Partituras

As partituras são SVG gerados pelo LilyPond (e desenhadas pelo VexFlow quando o aluno troca de tom), com tinta fixa. Por isso:

- O **cartão** da partitura segue a paleta e o tema (`folha`), mas a **folha da partitura** dentro dele é sempre `pauta-papel` (branco), com tinta `pauta-tinta` azul-quase-preto — igual nas três paletas, porque a partitura é uma imagem fixa.
- Dentro da partitura use só os tokens `pauta-*`: `pauta-tinta` (notas), `pauta-romano` (I, IIm7…), `pauta-cifra` (C7M), `pauta-grau` (1, 3, 5, 7), `pauta-destaque` (nota em destaque). São os mesmos valores do gerador (`lyb.py`) e do VexFlow (`COL_ROMAN`, `COL_CIFRA`, `COL_GRAU`).
- Ordem de leitura de cima para baixo, igual em todo o material: **romano → cifra → pauta → graus**.

## Tipografia

- Duas famílias: `display` (Fraunces, com eixo óptico) para títulos, cifras e a frase da Ideia-chave; `texto` (Work Sans) para todo o resto. Work Sans também é a fonte das letras dentro das partituras — não troque.
- Estilos: `capa` só no título da capa; `titulo-aula` no h2 de cada aula; `secao` nos h3; `subtitulo` em títulos de exercício, cartão, jogo e dúvida; `ideia` na Ideia-chave; `cifra` nas fichas; `lead`, `corpo`, `pequeno`, `botao`, `rotulo` e `grau` no texto.
- Algarismos tabulares (`font-variant-numeric: tabular-nums`) em graus, contadores e tabelas.
- Linhas de texto com no máximo 64 caracteres (`--largura-texto`).

## Espaço, cantos e sombra

- Escala de 4 em 4 até 24 e depois 32/48/64: `space-1` … `space-8`. Cartões e partituras usam `space-5` de respiro; seções (h3) abrem com `space-6`.
- Cantos: `radius-sm` em fichas e selects, `radius-md` em cartões, partituras, avisos e itens da navegação, `radius-lg` na Ideia-chave e nos jogos, `radius-pill` em todos os botões e etiquetas.
- Uma única sombra, `sombra-folha`, macia e baixa. Sem sombras duras deslocadas.

## Layout

- Computador: barra lateral fixa de 272px + conteúdo com no máximo 944px e 64px de margem lateral.
- Celular (até 860px): a navegação vira uma fileira rolável no topo, a margem lateral cai para `space-4` (16px) e o rodapé com Anterior/Próximo fica grudado embaixo.
- Impressão: a cartilha inteira, uma aula por página, fundos viram branco com borda, controles somem.

## Temas e acessibilidade

- Claro e escuro seguem o sistema do aluno (`prefers-color-scheme`), em qualquer paleta; dá para forçar com `data-tema="claro"` ou `"escuro"` no `<html>`.
- As três paletas passam no mesmo contraste: `tinta` ≥12:1, `tinta-suave` ≥6:1, cores da música ≥4,5:1, nos claros e nos escuros.
- No escuro, os acentos clareiam e o texto sobre eles fica escuro: use sempre `sobre-acento`, nunca branco fixo.
- Anel de foco: 2px sólido em `foco`, afastado 2px.
- Animação só na troca de aula (fade de 0,35s), desligada com `prefers-reduced-motion`.

## Iconografia

- A marca de cada cartilha é um disco `acento` com o desenho do instrumento em traço `sobre-acento` (veja **Marcas**). Hoje só existe a flauta; violão e teclado devem seguir o mesmo traço de 1,6px num círculo de 44px.
- Ícones de interface são traços simples de 1,4px em `currentColor` (como o da impressora). Nada de bibliotecas de ícones ou emoji.

## Como começar a cartilha de outro instrumento

1. Copie a pasta `ferramentas/src/tema/` da flauta (tokens.json, metodo.css, gerar_tokens_css.py) sem mudar nada.
2. Em `src/head.html`, troque `data-instrumento="flauta"` pelo instrumento (`violao`, `teclado`…).
3. Troque o desenho dentro de `.brand .marca` em `src/body.html` e o texto “Cartilha do aluno · Flauta”.
4. Rode `python3 montar.py`. Para mudar uma cor do método inteiro, edite `tokens.json` uma vez e copie para todas as cartilhas.
