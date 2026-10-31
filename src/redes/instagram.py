"""Instagram: posta foto (ou Reel, se o produto tem vídeo) pela API oficial da Meta."""
import time

import requests

from . import facebook
from .base import ErroPostagem, enviar, erro_da_resposta

GRAPH = facebook.GRAPH


def _checar(cfg) -> None:
    if not cfg.instagram_id or not cfg.meta_page_token:
        raise ErroPostagem("faltam INSTAGRAM_BUSINESS_ID ou META_PAGE_ACCESS_TOKEN no .env")


def _ja_e_jpeg(endereco: str) -> bool:
    try:
        resposta = requests.get(endereco, stream=True, timeout=(10, 20))
        tipo = resposta.headers.get("Content-Type", "").lower()
        resposta.close()
        return "jpeg" in tipo or "jpg" in tipo
    except requests.RequestException:
        return False


def _esperar_pronto(cfg, container: str, limite_s: int) -> None:
    """O Instagram processa a mídia antes de publicar; espera ficar FINISHED."""
    inicio = time.time()
    while time.time() - inicio < limite_s:
        info = enviar("GET", f"{GRAPH}/{container}", tentativas=1,
                      params={"fields": "status_code", "access_token": cfg.meta_page_token}).json()
        status = info.get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise ErroPostagem(f"o Instagram não conseguiu processar a mídia ({status})")
        time.sleep(5)
    raise ErroPostagem("o Instagram demorou demais para processar a mídia")


def publicar(cfg, produto, texto: str) -> str:
    _checar(cfg)
    dados = {"caption": texto, "access_token": cfg.meta_page_token}
    if produto.video:
        dados.update({"media_type": "REELS", "video_url": produto.video})
        espera = 300
    else:
        foto = produto.foto if _ja_e_jpeg(produto.foto) else facebook.foto_publica_em_jpeg(cfg, produto.foto)
        dados["image_url"] = foto
        espera = 90
    # Criar o "rascunho" da mídia é seguro de repetir: ainda não publicou nada.
    resposta = enviar("POST", f"{GRAPH}/{cfg.instagram_id}/media", data=dados)
    corpo = resposta.json() if resposta.content else {}
    if "id" not in corpo:
        raise ErroPostagem(f"Instagram recusou: {erro_da_resposta(resposta)}")
    container = corpo["id"]
    _esperar_pronto(cfg, container, espera)
    # Publicar NÃO é repetido (tentativas=1) para nunca duplicar.
    resposta = enviar("POST", f"{GRAPH}/{cfg.instagram_id}/media_publish", tentativas=1,
                      data={"creation_id": container, "access_token": cfg.meta_page_token})
    corpo = resposta.json() if resposta.content else {}
    if "id" not in corpo:
        raise ErroPostagem(f"Instagram não publicou: {erro_da_resposta(resposta)}")
    return str(corpo["id"])


def testar(cfg) -> str:
    _checar(cfg)
    resposta = enviar("GET", f"{GRAPH}/{cfg.instagram_id}", tentativas=1,
                      params={"fields": "username", "access_token": cfg.meta_page_token})
    if resposta.status_code != 200:
        raise ErroPostagem(f"Instagram recusou: {erro_da_resposta(resposta)}")
    return f"conta @{resposta.json().get('username', '?')}"
