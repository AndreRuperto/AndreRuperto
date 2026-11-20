# Próximos passos

**Data:** 20/11/2026 · **Branch:** `claude/acabamento-perfil`

## O que foi feito

Na `main` (PRs 1, 2 e 3, mergeados):

- Topo na identidade do portfólio (carvão, laranja Brasa, Sora e Fira Code): cabeçalho "André." com o gráfico do PNCP, botões de contato, números do "Sobre mim", experiência em forma de consulta SQL e painel de skills. Tudo com versão de celular e em inglês, gerado por `.github/scripts/gerar_perfil.py`.
- `README.en.md` com seletor de idioma.
- Seis destaques (Turnos, Triagegeist, Good Cities, DataBola, A Carta e Cronomapa) e "Mais projetos" em 14 cartões gerados.
- Cards de estatísticas na mesma paleta, publicados em `stats/` na branch `output`; a `main` só recebe commit quando o conjunto de cards muda.
- Cobra e Pac-Man na paleta (tema `brasa` em `svg-pacman-contributions`).
- Descrições, sites e tópicos preenchidos nos repositórios dos projetos.

Nesta branch (acabamento):

- Carrosséis do Turnos e do Cronomapa recomprimidos: de 2,4 e 2,3 MB para 1,6 e 1,5 MB, na mesma resolução.
- Cards de estatísticas também em inglês (`*-en.svg`), usados pelo `README.en.md`.
- Validação automática: `.github/workflows/validar.yml` confere imagens, texto alternativo e peso a cada mudança, e os links toda segunda-feira.
- `LICENSE` (MIT para scripts e workflows) e tópicos no repositório.

## Estado atual

- Conferido no GitHub depois do PR 3: 33 imagens carregam em desktop e celular, 14 cartões, links funcionando.
- Workflows de estatísticas e de animação rodando sem erro; a cobra já saiu na paleta nova.
- O `README.en.md` só passa a apontar para os cards em inglês depois que o workflow de estatísticas rodar na `main` (ele roda sozinho após o merge).
- As legendas dos carrosséis continuam em português também no README em inglês.

## Próximos passos

- [ ] Fixar os repositórios no perfil (manual): trocar `AndreRuperto` e `Capi3D` por `turnos` e `genetica-na-gestacao`
- [ ] Encurtar as descrições de `svg-pacman-contributions`, `whatsapp_gastos_ai` e `simulador-sistemas-autenticacao` (são cortadas no cartão fixado) e descrever `Capi3D` e `paradigma_orientado_a_eventos`
- [ ] Revisar os textos em inglês e a lista de skills (a contagem veio das dependências dos projetos, não do domínio de cada uma)
- [ ] Confirmar os textos de Blue Mais, Mangueira & Peixoto e Capi3D nos cartões
- [ ] Decidir se seis destaques é demais; o Good Cities é o candidato a ir para "Mais projetos"
- [ ] Legendas dos carrosséis em inglês (exige recapturar as telas)
- [ ] Ver se as fotos do TSE carregam para visitantes no `mapa.html` do Turnos
- [ ] Atualizar o README do Cronomapa (fala em globo 3D a partir do ano 1; o site é um mapa a partir de 3000 a.C.)

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
