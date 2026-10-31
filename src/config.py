"""Lê o .env e entrega as configurações do bot."""
import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _ler_env(caminho: Path) -> dict:
    dados = {}
    if caminho.exists():
        for linha in caminho.read_text(encoding="utf-8-sig").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                chave, valor = linha.split("=", 1)
                dados[chave.strip()] = valor.strip().strip('"').strip("'")
    return dados


def _numero(valor: str, padrao: float | None) -> float | None:
    valor = (valor or "").strip().replace(",", ".")
    if not valor:
        return padrao
    try:
        return float(valor)
    except ValueError:
        return padrao


@dataclass
class Config:
    simular: bool
    comissao_minima: float
    preco_maximo: float | None
    dias_sem_repetir: int
    fuso: str
    posts_por_dia: int
    instagram_posts_por_dia: int
    redes_ativas: list
    arquivo_produtos: Path
    arquivo_historico: Path
    arquivo_pagina: Path
    telegram_token: str
    telegram_chat_id: str
    meta_page_id: str
    meta_page_token: str
    instagram_id: str

    def segredos(self) -> list:
        """Valores que nunca podem aparecer em log ou na tela."""
        valores = [self.telegram_token, self.meta_page_token]
        return [v for v in valores if v and len(v) >= 8]


def carregar_config(arquivo_env: Path | None = None) -> Config:
    env = _ler_env(arquivo_env or RAIZ / ".env")
    env.update({k: v for k, v in os.environ.items() if k in env})

    def pegar(chave: str, padrao: str = "") -> str:
        return env.get(chave, padrao)

    redes = [r.strip().lower() for r in pegar("REDES_ATIVAS", "telegram,facebook,instagram").split(",") if r.strip()]
    return Config(
        # Só desliga a simulação se estiver escrito exatamente "false".
        simular=pegar("DRY_RUN", "true").strip().lower() != "false",
        comissao_minima=_numero(pegar("COMISSAO_MINIMA_PERCENTUAL"), 10.0),
        preco_maximo=_numero(pegar("PRECO_MAXIMO_REAIS"), None),
        dias_sem_repetir=int(_numero(pegar("DIAS_SEM_REPETIR"), 30)),
        fuso=pegar("FUSO_HORARIO", "America/Sao_Paulo") or "America/Sao_Paulo",
        posts_por_dia=int(_numero(pegar("POSTS_POR_DIA"), 3)),
        instagram_posts_por_dia=int(_numero(pegar("INSTAGRAM_POSTS_POR_DIA"), 1)),
        redes_ativas=redes,
        arquivo_produtos=RAIZ / (pegar("ARQUIVO_PRODUTOS") or "dados/produtos.csv"),
        arquivo_historico=RAIZ / "dados" / "historico.db",
        arquivo_pagina=RAIZ / "docs" / "index.html",
        telegram_token=pegar("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=pegar("TELEGRAM_CHAT_ID"),
        meta_page_id=pegar("META_PAGE_ID"),
        meta_page_token=pegar("META_PAGE_ACCESS_TOKEN"),
        instagram_id=pegar("INSTAGRAM_BUSINESS_ID"),
    )
