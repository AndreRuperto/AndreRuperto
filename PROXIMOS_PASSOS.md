# Próximos passos

**Data:** 19/11/2026 · **Branch:** `claude/mais-projetos-completo` (PR 3)

## O que foi feito nesta sessão

Já na `main` (PR 1, mergeado):

- Topo na identidade do portfólio (carvão, laranja Brasa, Sora e Fira Code): cabeçalho "André." com o gráfico do PNCP, botões de contato, números do "Sobre mim", experiência em forma de consulta SQL e painel de skills. Tudo com versão de celular e em inglês, gerado por `.github/scripts/gerar_perfil.py`.
- `README.en.md` com seletor de idioma.
- Cards de estatísticas na mesma paleta, publicados em `stats/` na branch `output`; a `main` só recebe commit quando o conjunto de cards muda.
- `alternador.yml` corrigido; cobra e Pac-Man na paleta. O tema `brasa` do Pac-Man foi criado e mergeado em `svg-pacman-contributions`.
- Descrições, sites e tópicos preenchidos em `turnos`, `genetica-na-gestacao`, `AndreRuperto`, `Portfolio-AndreRuperto`, `whatsapp_gastos_ai`, `2turno`, `mercado-eleicoes`, `leis-rag` e `melhores-restaurantes`.

Do PR 2 (mergeado) e do PR 3:

- Seis destaques: Turnos, Triagegeist, Good Cities, DataBola, A Carta e Cronomapa. Turnos, DataBola, A Carta e Cronomapa têm carrossel próprio em WebP.
- "Mais projetos" em 14 cartões gerados, no lugar da tabela: os cinco que já existiam e mais Cobra o L, 2 Turno, Mercado & Eleições, Capi3D, Mangueira & Peixoto, Blue Mais, documentação da API do Compras.gov.br, simulador de autenticação e leis-rag.
- Modelo do PNCP corrigido: foi feito no estágio no MGI, não no TCC.
- Montador de carrosséis no repositório: `.github/scripts/gerar_carrossel.py`.

## Estado atual

- Conferido na prévia local (desktop e celular, português e inglês). O PR 2 não foi conferido no GitHub.
- No GitHub já rodaram sem erro: o workflow de estatísticas e o Pac-Man no tema `brasa`.
- Não testado no GitHub: a cobra com as cores novas (primeira execução depois de 00:00 UTC de 20/11).
- As animações do README somam cerca de 7,5 MB.

## Próximos passos

- [ ] Conferir a primeira execução da cobra na paleta nova
- [ ] Fixar os repositórios no perfil (manual): `turnos`, `genetica-na-gestacao`, `svg-pacman-contributions`, `whatsapp_gastos_ai`, `Portfolio-AndreRuperto`, `simulador-sistemas-autenticacao`
- [ ] Revisar os textos em inglês e a lista de skills (a contagem veio das dependências dos projetos, não do domínio de cada uma)
- [ ] Decidir se seis destaques é demais; o Good Cities é o candidato a ir para "Mais projetos"
- [ ] Ver se as fotos do TSE carregam para visitantes no `mapa.html` do Turnos
- [ ] Atualizar o README do Cronomapa (fala em globo 3D a partir do ano 1; o site é um mapa a partir de 3000 a.C.)
- [ ] Validação automática do README (links, texto alternativo, peso das imagens)

## Decisões e problemas conhecidos

- O GitHub não carrega fontes externas em SVG, então todo texto das imagens vira contorno a partir de `assets/fontes/`.
- Os carrosséis não se atualizam sozinhos. As capturas de tela ficam fora do repositório; para refazer, capture as telas em 1280x720 e rode o montador.
- Carrosséis e cards de estatísticas têm texto em português também no README em inglês.
- Prancha de design do topo: https://claude.ai/artifact/LYzNB8zYwFmMqEPjeN952k (cores da prancha "Portfólio · Identidade e sistema de design").

## Comandos úteis

```powershell
python .github/scripts/gerar_perfil.py
```

```powershell
python .github/scripts/gerar_carrossel.py saida.webp "site.exemplo" tela1.png="Legenda 1" tela2.png="Legenda 2"
```

```powershell
$env:GITHUB_TOKEN = gh auth token; python .github/scripts/gerar_cards.py; python .github/scripts/atualizar_estatisticas.py
```
