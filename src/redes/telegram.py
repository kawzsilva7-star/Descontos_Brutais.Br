"""Telegram: posta foto (ou vídeo) com legenda no canal ou grupo."""
from .base import ErroPostagem, baixar, enviar, erro_da_resposta

API = "https://api.telegram.org"


def _base(cfg) -> str:
    if not cfg.telegram_token or not cfg.telegram_chat_id:
        raise ErroPostagem("faltam TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID no .env")
    return f"{API}/bot{cfg.telegram_token}"


def publicar(cfg, produto, texto: str) -> str:
    base = _base(cfg)
    if produto.video:
        metodo, campo, endereco = "sendVideo", "video", produto.video
    else:
        metodo, campo, endereco = "sendPhoto", "photo", produto.foto
    dados = {"chat_id": cfg.telegram_chat_id, "caption": texto}
    resposta = enviar("POST", f"{base}/{metodo}", data={**dados, campo: endereco})
    if resposta.status_code == 400 and not produto.video:
        # Algumas lojas não deixam o Telegram buscar a foto: baixamos e enviamos nós mesmos.
        arquivo = baixar(endereco)
        resposta = enviar("POST", f"{base}/{metodo}", data=dados, files={campo: ("foto.jpg", arquivo)})
    corpo = resposta.json() if resposta.content else {}
    if not corpo.get("ok"):
        raise ErroPostagem(f"Telegram recusou: {erro_da_resposta(resposta)}")
    return str(corpo["result"]["message_id"])


def testar(cfg) -> str:
    base = _base(cfg)
    eu = enviar("GET", f"{base}/getMe", tentativas=1).json()
    if not eu.get("ok"):
        raise ErroPostagem("token do Telegram não aceito")
    canal = enviar("GET", f"{base}/getChat", params={"chat_id": cfg.telegram_chat_id}, tentativas=1).json()
    if not canal.get("ok"):
        raise ErroPostagem("o bot não enxerga o canal/grupo (ele é administrador lá?)")
    return f"bot @{eu['result']['username']} no canal '{canal['result'].get('title', '?')}'"
