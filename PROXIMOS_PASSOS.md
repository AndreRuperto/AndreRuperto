# Próximos passos

**Data:** 19/11/2026 · **Branch:** `claude/github-profile-improvements-725406`

## O que foi feito nesta sessão

Melhorias no perfil inspiradas no repositório `anjennlical`:

- `alternador.yml`: mensagem de commit corrigida (saía "Atualiza animação ()"), `::set-output` trocado por `GITHUB_OUTPUT`, `actions/checkout@v4`.
- Cards de estatísticas saíram da `main`: o workflow publica em `stats/` na branch `output` e o README aponta para lá. A `main` só recebe commit quando o conjunto de cards muda.
- Projetos em destaque: Turnos e Triagegeist com captura de tela, PNCP com os números; os outros seis ficaram em "Mais projetos".
- Topo novo na identidade do portfólio (carvão, laranja Brasa, Sora e Fira Code): cabeçalho "André." com o gráfico do PNCP, botões de contato, números do "Sobre mim" e experiência em forma de consulta SQL, cada um com versão de celular. Tudo gerado por `.github/scripts/gerar_perfil.py` a partir de `assets/fontes/`.
- Cards de estatísticas passaram do verde para a mesma paleta.
- Prancha de design do topo: https://claude.ai/artifact/LYzNB8zYwFmMqEPjeN952k

## Estado atual

- Verificado localmente: YAML dos dois workflows, passo da cor da cobra, scripts de estatísticas e caminhos de imagem do README.
- Não testado: os workflows rodando no GitHub Actions (só rodam depois do merge).
- Logo após o merge, os três cards ficam quebrados por cerca de um minuto, até o workflow de estatísticas publicar em `output/stats/` (ele dispara sozinho no push).

## Próximos passos

- [ ] Depois do merge, conferir a execução de "Atualizar estatísticas do README" e os cards no perfil
- [ ] Revisar os textos dos três projetos em destaque (stack do Triagegeist ficou de fora por falta de fonte)
- [ ] Refazer o carrossel (`assets/perfil/projetos.webp` e `assets/projetos/turnos.webp`) quando os sites dos projetos mudarem; foi montado à mão a partir de capturas
- [ ] Versão em inglês (`README.en.md`) com seletor de idioma
- [ ] Trocar os ícones do skillicons por arquivos locais na paleta do portfólio
- [ ] Uma frase de contexto por grupo de skills
- [ ] Validação automática do README (links, âncoras, texto alternativo, peso das imagens)

## Comandos úteis

```powershell
python .github/scripts/gerar_perfil.py
```

```powershell
$env:GITHUB_TOKEN = gh auth token; python .github/scripts/gerar_cards.py; python .github/scripts/atualizar_estatisticas.py
```
