"""Facebook: posta foto (ou vídeo) com legenda na Página."""
from .base import ErroPostagem, enviar, erro_da_resposta

GRAPH = "https://graph.facebook.com/v21.0"


def _checar(cfg) -> None:
    if not cfg.meta_page_id or not cfg.meta_page_token:
        raise ErroPostagem("faltam META_PAGE_ID ou META_PAGE_ACCESS_TOKEN no .env")


def publicar(cfg, produto, texto: str) -> str:
    _checar(cfg)
    if produto.video:
        url = f"{GRAPH}/{cfg.meta_page_id}/videos"
        dados = {"file_url": produto.video, "description": texto}
    else:
        url = f"{GRAPH}/{cfg.meta_page_id}/photos"
        dados = {"url": produto.foto, "caption": texto}
    dados["access_token"] = cfg.meta_page_token
    resposta = enviar("POST", url, data=dados)
    corpo = resposta.json() if resposta.content else {}
    if resposta.status_code != 200 or "id" not in corpo:
        raise ErroPostagem(f"Facebook recusou: {erro_da_resposta(resposta)}")
    return str(corpo.get("post_id") or corpo["id"])


def foto_publica_em_jpeg(cfg, endereco: str) -> str:
    """Sobe a foto na Página SEM publicar e devolve um endereço público em JPEG.

    O Instagram só aceita JPEG; o Facebook converte para nós.
    """
    _checar(cfg)
    resposta = enviar(
        "POST", f"{GRAPH}/{cfg.meta_page_id}/photos",
        data={"url": endereco, "published": "false", "access_token": cfg.meta_page_token},
    )
    corpo = resposta.json() if resposta.content else {}
    if "id" not in corpo:
        raise ErroPostagem(f"Facebook não converteu a foto: {erro_da_resposta(resposta)}")
    info = enviar("GET", f"{GRAPH}/{corpo['id']}", tentativas=1,
                  params={"fields": "images", "access_token": cfg.meta_page_token}).json()
    imagens = info.get("images") or []
    if not imagens:
        raise ErroPostagem("o Facebook não devolveu o endereço da foto convertida")
    return imagens[0]["source"]


def testar(cfg) -> str:
    _checar(cfg)
    resposta = enviar("GET", f"{GRAPH}/{cfg.meta_page_id}", tentativas=1,
                      params={"fields": "name", "access_token": cfg.meta_page_token})
    if resposta.status_code != 200:
        raise ErroPostagem(f"Facebook recusou: {erro_da_resposta(resposta)}")
    return f"Página '{resposta.json().get('name', '?')}'"
