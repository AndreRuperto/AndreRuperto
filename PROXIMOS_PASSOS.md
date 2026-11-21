# Próximos passos

**Data:** 21/11/2026 · **Branch:** `main`

## O que foi feito

Na `main` (PRs 1, 2, 3, 4 e 5 mergeados):

- Topo na identidade do portfólio (carvão, laranja Brasa, Sora e Fira Code): cabeçalho "André." com o gráfico do PNCP, botões de contato, números do "Sobre mim", experiência em forma de consulta SQL e painel de skills. Tudo com versão de celular e em inglês, gerado por `.github/scripts/gerar_perfil.py`.
- `README.en.md` com seletor de idioma.
- Seis destaques (Turnos, Triagegeist, Good Cities, DataBola, A Carta e Cronomapa) e "Mais projetos" em 14 cartões gerados.
- Cards de estatísticas na mesma paleta, publicados em `stats/` na branch `output`; a `main` só recebe commit quando o conjunto de cards muda.
- Cobra e Pac-Man na paleta (tema `brasa` em `svg-pacman-contributions`).
- Descrições, sites e tópicos preenchidos nos repositórios dos projetos.

Acabamento concluído na `main` (PRs 4 e 5):

- Carrosséis do Turnos e do Cronomapa recomprimidos: de 2,4 e 2,3 MB para 1,6 e 1,5 MB, na mesma resolução.
- Cards de estatísticas também em inglês (`*-en.svg`), usados pelo `README.en.md`.
- Validação automática: `.github/workflows/validar.yml` confere imagens, texto alternativo e peso a cada mudança, e os links toda segunda-feira.
- `LICENSE` (MIT para scripts e workflows) e tópicos no repositório.

## Estado atual

- Conferido no GitHub depois do PR 3: 33 imagens carregam em desktop e celular, 14 cartões, links funcionando.
- Workflows de estatísticas e de animação rodando sem erro; a cobra já saiu na paleta nova.
- PR 5 (Capi3D) mergeado na `main` em 21/11/2026; validação do README e atualização de estatísticas concluíram com sucesso após o merge.
- As cinco descrições dos repositórios foram conferidas no GitHub. O PNCP está identificado como trabalho de estágio no MGI em ambos os READMEs.
- PR 6 mergeado na `main` em 21/11/2026: textos revisados, tecnologias adicionadas, cartões regenerados e carrosséis EN. Após o merge, os workflows de regeneração, validação do README e estatísticas terminaram com sucesso.
- O `README.en.md` já aponta para os cards em inglês; o workflow de estatísticas após o PR 5 concluiu com sucesso.
- O README em inglês usa cinco carrosséis com legendas traduzidas; a interface capturada nas imagens permanece em português.

## Próximos passos

- [ ] Fixar os repositórios no perfil (manual): trocar `AndreRuperto` e `Capi3D` por `turnos` e `genetica-na-gestacao`
- [x] Encurtar as descrições de `svg-pacman-contributions`, `whatsapp_gastos_ai` e `simulador-sistemas-autenticacao`, e descrever `Capi3D` e `paradigma_orientado_a_eventos` (cinco metadados conferidos em 21/11/2026)
- [x] Revisar textos e skills do perfil: frase do topo em inglês, descrições PT/EN, C# e React Native (Expo) incluídos; nota editorial adicionada sobre níveis variados de experiência
- [x] Confirmar e atualizar Blue Mais (site de natação) e Mangueira & Peixoto (advocacia previdenciária) nos cartões PT/EN; Capi3D já corrigido
- [x] Manter seis destaques neste ciclo: o Good Cities agrega visualização geográfica e diversidade ao portfólio; reavaliar só com dados de navegação
- [x] Gerar legendas em inglês para Turnos, DataBola, A Carta, Cronomapa e Genética usando os WebP existentes; as capturas das interfaces continuam em português
- [ ] Validar em navegador de visitante as fotos do TSE no `mapa.html`: duas URLs públicas retornaram 403 em consulta automatizada; fallback com iniciais foi implementado no Turnos (`25df1e6`), mas falta conferir visualmente
- [x] Atualizar README do Cronomapa para o mapa plano 2D desde 3000 a.C., D3.js, governantes, personalidades e limitações (commit `1c292e4` em `AndreRuperto/cronomapa`)

## Decisões e problemas conhecidos

- O GitHub não carrega fontes externas em SVG, então todo texto das imagens vira contorno a partir de `assets/fontes/`.
- Os carrosséis não se atualizam sozinhos. As capturas de tela ficam fora do repositório; para refazer, capture as telas em 1280x720 e rode o montador (qualidade 50).
- O validador falha se uma imagem passar de 2 MB ou se as imagens de um README somarem mais de 8 MB.
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

```powershell
python .github/scripts/validar_readme.py --links
```
