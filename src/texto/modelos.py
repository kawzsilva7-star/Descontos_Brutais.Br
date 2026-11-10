"""Textos dos posts. Nada de inventar: só entram nome, preço e link informados pelo dono."""
import hashlib
import unicodedata

GANCHOS = [
    "Achado do dia:",
    "Separei este produto pra você:",
    "Dica de compra:",
    "Olha esse achadinho:",
    "Pra quem estava procurando:",
]

AVISO = "📢 Publicidade: link de afiliado, posso receber comissão pela sua compra."
AVISO_SAUDE = "⚠️ Produto ligado à saúde: tome cuidado e consulte um médico antes de usar."
# Além da categoria "saúde", estas palavras (sem acento) no nome ou na descrição também ativam o aviso.
PALAVRAS_DE_SAUDE = ("pressao", "suplement", "creatina", "glutamina", "whey", "vitamina", "nasal", "ortoped",
                     "protetor solar", "remedio", "medicamento", "cápsulas", "capsulas",
                     "soro", "nafazolina", "cloridrato", "descongestionante", "nariz")
LIMITE_TELEGRAM = 1000  # o Telegram aceita 1024 na legenda de foto
LIMITE_INSTAGRAM = 2000  # o Instagram aceita 2200


def formatar_preco(valor: float) -> str:
    inteiro = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {inteiro}"


def _gancho(produto) -> str:
    # Escolha fixa por produto: o mesmo produto sempre recebe o mesmo gancho.
    indice = int(hashlib.sha1(produto.id.encode()).hexdigest(), 16) % len(GANCHOS)
    return GANCHOS[indice]


def _nome_curto(nome: str, maximo: int = 110) -> str:
    nome = " ".join(nome.split())
    return nome if len(nome) <= maximo else nome[: maximo - 1].rstrip() + "…"


def _sem_acento(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c))


def _e_de_saude(produto) -> bool:
    if _sem_acento(produto.categoria or "").strip().lower() in ("saude", "saúde"):
        return True
    texto = _sem_acento(f"{produto.nome} {getattr(produto, 'descricao', '')}").lower()
    return any(_sem_acento(p) in texto for p in PALAVRAS_DE_SAUDE)


def _corpo(produto, rede: str) -> str:
    # Se o dono escreveu uma descrição curta na planilha, ela vira o título do post.
    # Sem descrição, usa o nome do anúncio, como antes.
    titulo = " ".join((getattr(produto, "descricao", "") or "").split()) or _nome_curto(produto.nome)
    linhas = [f"{_gancho(produto)} {titulo}", ""]
    linhas.append(f"💰 Preço: {formatar_preco(produto.preco)} (pode mudar, confira na loja)")
    if rede == "instagram":
        # No Instagram o link da legenda não clica: manda o público para a página do link da bio.
        linhas.append("🛒 Clique no link da bio para comprar")
    else:
        linhas.append(f"🛒 Compre aqui: {produto.link}")
    linhas += ["", AVISO]
    if _e_de_saude(produto):
        linhas += ["", AVISO_SAUDE]
    if rede == "instagram":
        linhas += ["", "#publi #achadinhos #ofertas"]
    return "\n".join(linhas)


def montar(produto, rede: str) -> str:
    """Texto final do post para a rede ('telegram', 'facebook' ou 'instagram')."""
    texto = _corpo(produto, rede)
    limite = LIMITE_INSTAGRAM if rede == "instagram" else LIMITE_TELEGRAM
    if len(texto) > limite:
        # Nunca corta o link nem o aviso: encurta só o nome.
        sobra = len(texto) - limite
        nome = _nome_curto(produto.nome, max(20, 110 - sobra - 5))
        copia = type(produto)(**{**produto.__dict__, "nome": nome})
        texto = _corpo(copia, rede)
    return texto
