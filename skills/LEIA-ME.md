# Skills

Skills (instruções prontas) copiadas do repositório privado `Pensamento-critico` em 10/11/2026.
No GitHub público do bot vão **só 3 skills de autoria do dono**: `banca-de-avaliadores`, `rodada-de-tubaroes` e `video-de-produto`. As de Remotion (material de terceiros, licença não confirmada) ficam **só no PC**.
Nunca coloque chaves, tokens, senhas ou dados pessoais aqui: esta pasta é pública.

## Regra de uso (economizar tokens) — vale para o Claude
O dono pediu: **não carregar skill à toa**. Cada skill gasta tokens.
1. **Só use uma skill quando a tarefa for de decisão, criação de código ou raciocínio** que ela cobre. Para ações simples (rodar o bot, ler log, ajustar um texto, responder pergunta curta), **não use nenhuma**.
2. **Use só a skill da função certa** (tabela abaixo). Nunca carregue o grupo inteiro nem as de Remotion "por garantia".
3. **Remotion: comece pela necessária.** Só abra `remotion-best-practices` (que indica qual das outras ler) quando for fazer vídeo. Leia só o `SKILL.md` e **só os arquivos de apoio que a tarefa pedir**, não a pasta toda.
4. Se a tarefa não está na tabela, **não force uma skill**: faça direto.
5. Ao usar uma skill, diga ao dono qual e por quê, em uma linha.
6. Skill nova só vai para o GitHub com autorização do dono, depois de conferir a licença e de procurar chaves ou dados pessoais nos arquivos.

## Qual skill para qual função
| Função | Skill | Quando usar |
|---|---|---|
| Vídeo curto do produto (Reels/Instagram) | `video-de-produto` | Quando o dono pedir vídeo de produto |
| Vídeo explicando a página (o vídeo fixado) | `video-de-produto` (+ `remotion-create`) | Só depois de existir roteiro |
| Criar um vídeo novo em código | `remotion-create` | Início de um vídeo novo |
| Legendas no vídeo | `remotion-captions` | Só se o vídeo tiver legenda |
| Mostrar o vídeo antes de exportar | `remotion-studio` | Ao pré-visualizar |
| Exportar o vídeo final | `remotion-render` | Ao gerar o arquivo final |
| Animação, efeitos, layout do vídeo | `remotion-markup` | Só ao desenhar cenas |
| Dúvida de como o Remotion funciona | `remotion-docs` | Só para pesquisar na documentação |
| Não sei qual do Remotion usar | `remotion-best-practices` | Porta de entrada (indica a certa) |
| Mapas, áudio/vídeo (mediabunny), app, interatividade, atualizar versão | `remotion-maps`, `remotion-multimedia`, `remotion-saas`, `remotion-interactivity`, `remotion-upgrade` | Raramente; só se o vídeo realmente precisar |
| Testar uma ideia de negócio com "investidores" | `rodada-de-tubaroes` | Só se o dono pedir |
| Revisar currículo | `banca-de-avaliadores` | Só se o dono pedir (não tem a ver com o bot) |

## Para o Claude usar sozinho
Para o Claude Code carregar uma skill automaticamente neste projeto, ela precisa estar em `.claude/skills/<nome>/SKILL.md`. Por enquanto estão só guardadas aqui. Copiar apenas as necessárias quando o dono mandar ativar.
