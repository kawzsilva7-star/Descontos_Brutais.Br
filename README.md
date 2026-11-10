# Bot Rede Sociais

Bot de afiliados. Posta 3 produtos por dia no **Telegram**, no **Facebook** e no **Instagram**, com foto, preço, link de afiliado e aviso de publicidade.

Status: **pronto em modo simulação**. Lê os produtos de uma planilha (`dados/produtos.csv`). Quando a Shopee (ou outra loja) tiver API, entra uma fonte nova em `src/produtos/` e o resto não muda.

## Uso do dia a dia
1. Preencha `dados/produtos.csv` (modelo em `dados/produtos.exemplo.csv`). Colunas: `nome;preco;link;foto;comissao;categoria;video`.
   - `link` = seu link de afiliado. `foto` = endereço público da foto (começa com https://).
   - `comissao` em %. Se ficar em branco, o bot confia que você já conferiu. Abaixo de 10% o produto é ignorado.
   - `video` (opcional) = endereço público de um vídeo. Se tiver, vira Reel no Instagram.
   - Atualize os preços de vez em quando: o bot posta o preço que está na planilha.
2. Veja o que ele postaria: `.venv\Scripts\python.exe -m src.main`
3. Quando aprovar os textos, mude `DRY_RUN=false` no `.env`.

Outros comandos (sempre na pasta do projeto):
- `-m src.main --listar` mostra o próximo produto e por que os outros ficaram de fora
- `-m src.main --testar-conexao` confere as chaves sem postar nada
- `-m src.main --rede telegram` usa só uma rede
- `-m src.main --forcar` ignora o limite de posts do dia
- `-m src.main --atrasados` posta no Facebook e no Instagram (1 por rede, ou `--quantidade N`) o que já saiu só no Telegram, por exemplo depois de uma chave vencida. Roda sozinho às 18:30, depois dos posts normais.
- `scripts\renovar_token_meta.py` troca o token curto do Facebook por um token de Página que não expira e grava no `.env` (copie o token no Explorador da Graph API e aperte Enter).

## Link da bio (página de produtos por categoria)
O bot gera docs/index.html: uma página só sua, com os produtos postados nos últimos 30 dias separados por categoria (Casa, Dia a dia, Carro, Eletrônicos, Gamers, Ferramentas...). A categoria vem da coluna categoria da planilha. A legenda do Instagram manda o público para a seção certa.
- Refazer a página: .venv\Scripts\python.exe -m src.main --gerar-pagina.
- Ela só passa a valer na internet depois de publicada (GitHub Pages). Isso ainda não foi ligado.

## Regras que o bot segue
- Máximo de 3 produtos por dia (`POSTS_POR_DIA`) e 1 post por dia no Instagram (`INSTAGRAM_POSTS_POR_DIA`, a conta é nova).
- Não repete produto por 30 dias (`DIAS_SEM_REPETIR`). Se não souber se postou (rede não respondeu), conta como postado e **não** tenta de novo.
- Se uma rede falha, as outras seguem. Erro de conexão é tentado mais uma vez.
- Todo post tem aviso de publicidade. Nada de desconto ou urgência inventados.
- Registro em `dados/historico.db` e `logs/bot.log`. Chaves nunca aparecem nos logs.

## Em um computador novo
1. Instale o Python (python.org, marque "Add Python to PATH") e o Git.
2. Baixe o projeto do GitHub e entre na pasta.
3. Copie o arquivo `.env` guardado em lugar seguro para dentro da pasta (ele **não** vai para o GitHub). Copie também `dados/produtos.csv`.
4. No PowerShell, na pasta: `.\scripts\instalar.ps1`
5. Teste em simulação. Depois: `.\scripts\agendar.ps1` cria as tarefas diárias: posts às 12:00 e 17:00, e às 18:30 a tarefa dos atrasados. Para outros horários: `.\scripts\agendar.ps1 -Horarios "09:00","15:00" -HorarioAtrasados "22:00"`. Para apagar: `.\scripts\agendar.ps1 -Remover`.

O PC precisa estar ligado e sem suspensão nesses horários.

## Chaves (arquivo `.env`)
Modelo em `.env.example`. As chaves ficam só no `.env`. Nunca no código, nunca no GitHub.
O token da Página do Facebook não expira, mas para de valer se a senha do Facebook mudar ou o app perder a permissão. Nesse caso gere outro no Explorador da Graph API.

## Testes
`.venv\Scripts\python.exe -m unittest discover -s tests -t .`

## Documentos
- `docs/ESPECIFICACAO.md`: regras de negócio e fases do projeto.
