# Harmonização aplicada para Flauta — Cartilha do Aluno

Material de apoio para aulas de flauta transversal: escalas, graus e campos
harmônicos maiores e menores, com exercícios em partitura, cifras e graus.
Feito para o aluno abrir no celular ou no computador, sem instalar nada.

**Acesse aqui:** https://saviosouza-dev.github.io/flauta/

## O que tem dentro

- Aula 1 — O nome das notas e as cifras
- Aula 2 — A escala maior e os graus
- Aula 3 — Como nasce um acorde (tríades e tétrades)
- Aula 4 — O campo harmônico maior
- Aula 5 — Progressões e cadências (notas-guia)
- Aula 6 — Campo harmônico menor natural
- Aula 7 — Campo harmônico menor harmônico
- Aula 8 — Campo harmônico menor melódico
- Aula 9 — Jogos e desafios (telefone musical, dado harmônico, detetive do ouvido)
- Consulta: tabelas dos campos nos 12 tons, respostas e dúvidas frequentes

Cada aula traz ideia-chave, exercícios em partitura com botão **▶ Ouvir**,
teste rápido e um checklist que o aluno marca antes de avançar.

## Como funciona

`index.html` tem todo o texto, o estilo e o script — sem dependências além
das fontes do Google Fonts. As partituras ficam em `partituras/` (uma versão
para tela larga e outra, em `partituras/m/`, para celular). O botão “Baixar
PDF” baixa `cartilha-flauta.pdf`, um PDF já pronto com a cartilha inteira,
uma aula por página — gerado sem o cabeçalho/rodapé que o `Ctrl+P` do
navegador injeta por conta própria (veja `ferramentas/LEIA-ME.md`).

O áudio dos exercícios é gerado pela própria página (Web Audio), sem arquivos
de som.

## Para editar

Textos pequenos podem ser corrigidos direto no `index.html`. Salve e publique:

```bash
git add .
git commit -m "Descreva a alteração"
git push
```

O GitHub Pages atualiza o site em cerca de um minuto.

Para criar ou alterar **partituras** (e novas aulas), use o gerador em
`ferramentas/` — veja `ferramentas/LEIA-ME.md`. Nesse caso edite o texto em
`ferramentas/src/`, porque o gerador reescreve o `index.html`.

## Visual (Design System)

As cores, fontes e componentes de todas as cartilhas estão descritos em
`design-system/` — abra `design-system/index.html` no navegador para ver o guia
e os exemplos. O aluno pode escolher entre três paletas (Nanquim, Grafite e
Sálvia) no botão **Cores** da barra lateral.

---

Sávio Souza — material didático para aulas de flauta.
Base teórica inspirada em *Acordes Horizontais* (Daniel Rebel e Carvalho, UFRJ, 2021).
Cartilhas irmãs: [violão](https://saviosouza-dev.github.io/violao/) ·
[teclado](https://saviosouza-dev.github.io/teclado/)
