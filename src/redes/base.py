"""Envio de pedidos às redes, com a regra de nunca postar duas vezes."""
import logging
import time

import requests

log = logging.getLogger("bot")

# Falhas em que o pedido com certeza não chegou a postar: pode tentar de novo.
_SEM_POSTAR = (requests.ConnectionError, requests.ConnectTimeout)
_STATUS_REPETIVEIS = (429, 500, 502, 503, 504)


class ErroPostagem(Exception):
    """Não postou (ou a rede recusou). A mensagem nunca contém chaves."""


class PostagemIncerta(ErroPostagem):
    """O pedido saiu mas a resposta não voltou: pode ter postado. Não repetir."""


def enviar(metodo: str, url: str, tentativas: int = 2, **kwargs) -> requests.Response:
    """Faz o pedido. Tenta de novo (uma vez) só quando é seguro."""
    kwargs.setdefault("timeout", (10, 90))
    for tentativa in range(1, tentativas + 1):
        ultima = tentativa == tentativas
        try:
            resposta = requests.request(metodo, url, **kwargs)
        except _SEM_POSTAR as erro:
            if ultima:
                raise ErroPostagem(f"sem conexão ({type(erro).__name__})") from None
            log.warning("Sem conexão, tentando de novo em 5 segundos.")
            time.sleep(5)
            continue
        except requests.ReadTimeout:
            raise PostagemIncerta("a rede não respondeu a tempo; não vou repetir") from None
        except requests.RequestException as erro:
            raise ErroPostagem(f"falha no envio ({type(erro).__name__})") from None
        if resposta.status_code in _STATUS_REPETIVEIS and not ultima:
            log.warning("A rede respondeu %s, tentando de novo em 5 segundos.", resposta.status_code)
            time.sleep(5)
            continue
        return resposta
    raise ErroPostagem("não consegui enviar")  # nunca deveria chegar aqui


def baixar(url: str, limite_mb: int = 10) -> bytes:
    """Baixa uma foto ou vídeo para enviar como arquivo."""
    try:
        resposta = requests.get(url, timeout=(10, 60), stream=True)
        resposta.raise_for_status()
        dados = bytearray()
        for pedaco in resposta.iter_content(65536):
            dados += pedaco
            if len(dados) > limite_mb * 1024 * 1024:
                raise ErroPostagem(f"arquivo maior que {limite_mb} MB")
        return bytes(dados)
    except requests.RequestException as erro:
        raise ErroPostagem(f"não consegui baixar a foto ({type(erro).__name__})") from None


def erro_da_resposta(resposta: requests.Response) -> str:
    """Texto curto do erro devolvido pela rede (sem chaves)."""
    try:
        corpo = resposta.json()
    except ValueError:
        return f"HTTP {resposta.status_code}"
    if isinstance(corpo, dict):
        if "error" in corpo and isinstance(corpo["error"], dict):
            return f"{corpo['error'].get('message', 'erro')} (HTTP {resposta.status_code})"
        if "description" in corpo:
            return f"{corpo['description']} (HTTP {resposta.status_code})"
    return f"HTTP {resposta.status_code}"
