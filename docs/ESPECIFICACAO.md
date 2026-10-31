# Bot de afiliados (Mercado Livre)

Documento de instruções para quem for construir o bot. Escrito a partir do que o dono explicou por áudio em 30/10/2026.

## Objetivo
Um bot que roda sozinho, todo dia, e posta produtos do Mercado Livre com o link de afiliado do dono no Facebook, no Instagram e num grupo do Telegram.

## Regras de negócio
- **3 posts por dia**, um produto em cada: manhã, tarde e noite. Horários sugeridos: 08:00, 14:00 e 20:00 (fuso America/Sao_Paulo). Confirmar com o dono.
- **Comissão mínima de 10%.** Produto abaixo disso não entra.
- **Sem limite de preço.** O dono decidiu não limitar o preço. Deixar o limite como opção de configuração, vazia por padrão (vazio = sem limite), caso ele queira usar depois.
- **Não repetir produto** por pelo menos 30 dias. Guardar histórico do que já foi postado.
- **Cada post** tem: foto do produto, descrição curta escrita para vender, preço, e o link de afiliado.
- **Se o produto tiver vídeo**, postar também como Reel. Se não tiver, posta só a imagem. Não gerar vídeo.
- Começar só pelo **Mercado Livre**. Shopee e outros marketplaces ficam para depois.

## Onde posta
Fase 1:
- Página do **Facebook**
- Página do **Instagram** (conta Business ou Creator ligada a uma Página do Facebook)
- Grupo do **Telegram**

Fase 2 (depois):
- **TikTok** (conta nova, a criar)
- **Página de links** ("link na bio") onde o bot adiciona os produtos do dia. O dono pensou em Linktree. Ver pontos a verificar.

## Fluxo de cada execução
1. Buscar produtos candidatos no Mercado Livre.
2. Filtrar: comissão >= 10%, não postado nos últimos 30 dias, tem foto (e preço <= máximo, só se um máximo estiver configurado).
3. Escolher 1 produto.
4. Gerar o link de afiliado.
5. Escrever a descrição.
6. Postar no Telegram, no Facebook e no Instagram.
7. Registrar no histórico: produto, link, horário, onde postou, se deu erro.
8. Em caso de erro numa rede, tentar de novo uma vez e seguir com as outras. Nunca postar duas vezes o mesmo produto por causa de uma nova tentativa.

## Descrição do post
- Fase 1 sem IA: modelos de texto com variações, preenchidos com nome, preço e benefícios do produto.
- Depois, opcional: gerar o texto com a API do Claude (cobrada por uso, separada do plano do claude.ai). Deixar isso atrás de uma configuração, desligado por padrão.
- Sempre avisar que é publicidade (ver Regras).

## Estrutura de pastas sugerida
```
bot-rede-sociais/
  CLAUDE.md              instruções para o Claude
  README.md              como instalar e rodar
  docs/ESPECIFICACAO.md  este arquivo
  .env.example           lista das chaves (sem valores)
  src/
    mercadolivre/        busca, filtro e link de afiliado
    redes/               telegram, facebook, instagram
    texto/               modelos de descrição
    historico/           registro do que já foi postado
    main.py              roda uma publicação
  scripts/
    instalar             prepara um computador novo
    agendar              cria as 3 tarefas diárias
```
Linguagem sugerida: Python. O computador do dono é Windows.

## Como rodar 24 horas
Rodar no PC do dono, sem servidor pago. Em vez de deixar um programa sempre aberto, **agendar 3 tarefas por dia** no Agendador de Tarefas do Windows, cada uma rodando `main.py` uma vez. É mais simples e mais difícil de travar. O PC precisa estar ligado e sem suspensão nesses horários. O script `agendar` cria as tarefas.

## Configuração (.env, nunca vai para o GitHub)
Ver `.env.example`. Em computador novo: clonar o repositório, copiar o `.env` guardado em lugar seguro e rodar `scripts/instalar`.

## Pontos a verificar ANTES de programar
Nada abaixo foi confirmado. Conferir na documentação oficial e com o dono antes de escrever código.

1. **API do Mercado Livre.** O dono vai criar a chave de API. Descobrir: a busca de produtos exige token? A API informa a comissão de cada produto, ou a comissão é por categoria numa tabela do programa de afiliados? Existe forma oficial de gerar o link de afiliado por código, ou só pelo painel do programa? Se não houver, o bot precisa de outro caminho (por exemplo, montar o link com os parâmetros do afiliado).
2. **Instagram e Facebook.** Postar por código exige um app no Meta for Developers, uma conta Instagram Business/Creator ligada a uma Página, e permissões de publicação. Reels por API pedem um endereço público do vídeo. Verificar se o modo de desenvolvimento basta para as contas do próprio dono.
3. **Link na legenda do Instagram não é clicável.** Por isso a página de links na bio faz sentido. No Facebook e no Telegram o link é clicável.
4. **Linktree.** Verificar se existe API para adicionar links por código. Se não existir, alternativa: uma página própria gratuita (por exemplo no GitHub Pages) que o bot atualiza.
5. **Vídeos de produto.** Verificar se a API do Mercado Livre traz vídeo. Se não trouxer, o bot posta só imagem.
6. **Regras das plataformas.** Conferir os termos do programa de afiliados do Mercado Livre e as regras de automação de cada rede. Postar com frequência fixa por contas oficiais é o caminho mais seguro. Não usar automação não oficial.

## Regras que o bot sempre segue
- **Publicidade identificada:** todo post diz que é link de afiliado ou publicidade (por exemplo "#publi" ou "link de afiliado"), como a regulamentação de publicidade no Brasil pede.
- **Não inventar:** preço, desconto, avaliação, estoque ou prazo só aparecem se vieram da API. Nada de "últimas unidades" ou "oferta relâmpago" sem prova.
- **Preço pode mudar:** postar com a data/hora da consulta ou evitar prometer preço fixo.
- **Modo de teste:** `DRY_RUN=true` por padrão. Nesse modo o bot mostra o que postaria, sem postar. O dono liga o modo real depois de aprovar os primeiros exemplos.
- **Chaves e tokens** só no `.env`. Nunca no código, nunca no GitHub, nunca na conversa.

## Fases
1. **Fase 0:** confirmar os pontos a verificar e as decisões pendentes.
2. **Fase 1:** Mercado Livre + Telegram, em modo de teste. Depois ligar de verdade.
3. **Fase 2:** Facebook e Instagram.
4. **Fase 3:** agendamento diário e script de instalação para outro computador.
5. **Fase 4:** página de links e TikTok.
6. **Depois:** Shopee e descrições com IA.

## Decisões pendentes (perguntar ao dono)
- Horários exatos dos 3 posts.
- Categorias de produto preferidas ou proibidas.
- Quer usar a API do Claude para as descrições, aceitando o custo por uso?
- O Instagram e a Página do Facebook já estão ligados e em conta Business/Creator?
- O grupo do Telegram já existe?
