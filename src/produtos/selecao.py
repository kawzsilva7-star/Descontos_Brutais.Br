"""Regras para decidir qual produto pode ser postado."""

# Endereços de exemplo que nunca devem ir ao ar.
DOMINIOS_FALSOS = ("exemplo.com", "example.com", "seu-link", "link-aqui")


def _endereco_valido(url: str) -> bool:
    return url.lower().startswith("https://") and not any(d in url.lower() for d in DOMINIOS_FALSOS)


def motivo_de_exclusao(produto, cfg, recentes: set) -> str | None:
    """Devolve por que o produto não pode entrar, ou None se pode."""
    if not produto.nome:
        return "sem nome"
    if not _endereco_valido(produto.link):
        return "link inválido (precisa começar com https:// e não ser de exemplo)"
    if not _endereco_valido(produto.foto):
        return "sem foto válida"
    if produto.video and not _endereco_valido(produto.video):
        return "endereço do vídeo inválido"
    if produto.preco is None or produto.preco <= 0:
        return "sem preço"
    # Comissão em branco = o dono garante que está dentro da regra (lista manual).
    if produto.comissao is not None and produto.comissao < cfg.comissao_minima:
        return f"comissão {produto.comissao:g}% abaixo do mínimo de {cfg.comissao_minima:g}%"
    if cfg.preco_maximo is not None and produto.preco > cfg.preco_maximo:
        return "preço acima do máximo configurado"
    if produto.id in recentes:
        return f"já postado nos últimos {cfg.dias_sem_repetir} dias"
    return None


def escolher(produtos: list, cfg, recentes: set) -> tuple:
    """Devolve (produto escolhido ou None, lista de (produto, motivo) dos excluídos).

    A ordem da planilha manda: o primeiro que passa nas regras é o escolhido.
    """
    excluidos, escolhido = [], None
    for produto in produtos:
        motivo = motivo_de_exclusao(produto, cfg, recentes)
        if motivo:
            excluidos.append((produto, motivo))
        elif escolhido is None:
            escolhido = produto
    return escolhido, excluidos
