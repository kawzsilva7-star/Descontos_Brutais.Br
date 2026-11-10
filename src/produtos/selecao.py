"""Regras para decidir qual produto pode ser postado."""
import hashlib
import re
import unicodedata
from datetime import datetime

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


def atrasados(produtos: list, cfg, na_origem: set, na_rede: set) -> list:
    """Produtos já postados na rede de origem (Telegram) que ainda não saíram na rede em atraso.

    Mantém a ordem da planilha. As regras de qualidade valem; a de repetição não (é justamente repostar).
    """
    return [p for p in produtos
            if p.id in na_origem and p.id not in na_rede and motivo_de_exclusao(p, cfg, set()) is None]


# Palavras comuns demais para dizer que dois produtos são "parecidos".
PALAVRAS_COMUNS = {
    "kit", "para", "com", "sem", "tamanho", "preto", "preta", "branco", "branca", "azul", "rosa",
    "verde", "cinza", "bivolt", "portatil", "digital", "eletrico", "eletrica", "recarregavel",
    "pratico", "pratica", "cozinha", "infantil", "profissional", "original", "premium", "controle",
    "remoto", "sortidos", "unissex", "masculino", "feminino", "marca", "modelo", "novo", "nova",
    "pares", "jogo", "conjunto", "dois", "tres", "cores", "cor",
}


def _sem_acento(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c))


def _palavras(produto) -> set:
    """Palavras que identificam o tipo do produto (ex.: 'ventilador', 'lixadeira', 'aspirador')."""
    texto = re.sub(r"[^a-z ]", " ", _sem_acento(produto.nome).lower())
    return {p for p in texto.split() if len(p) >= 6 and p not in PALAVRAS_COMUNS}


def _chave_categoria(produto) -> str:
    return _sem_acento(produto.categoria or "").strip().lower()


def _pontos_de_repeticao(produto, ultimos: list) -> int:
    """Quanto maior, mais parecido com o que saiu há pouco (e mais deve esperar)."""
    pontos, palavras = 0, _palavras(produto)
    for posicao, anterior in enumerate(ultimos):
        if palavras & _palavras(anterior):
            pontos += 10 - posicao          # mesmo tipo de produto: pesa bastante
        if posicao < 2 and _chave_categoria(produto) and _chave_categoria(produto) == _chave_categoria(anterior):
            pontos += 3                     # mesma categoria dos 2 últimos posts
    return pontos


def _desempate(produto, dia: str) -> str:
    # Embaralha de um jeito que muda a cada dia: a ordem em que o dono mandou os links não manda.
    return hashlib.sha1(f"{dia}{produto.id}".encode()).hexdigest()


def escolher(produtos: list, cfg, recentes: set, ultimos_ids: list | None = None, dia: str | None = None) -> tuple:
    """Devolve (produto escolhido ou None, lista de (produto, motivo) dos excluídos).

    Entre os que passam nas regras, escolhe o que MENOS se parece com os últimos posts
    (tipo de produto e categoria). Se empatar, sorteia de forma fixa por dia: a ordem da
    planilha não define a ordem dos posts.
    """
    por_id = {p.id: p for p in produtos}
    ultimos = [por_id[i] for i in (ultimos_ids or []) if i in por_id]
    dia = dia or datetime.now().strftime("%Y-%m-%d")
    excluidos, candidatos = [], []
    for produto in produtos:
        motivo = motivo_de_exclusao(produto, cfg, recentes)
        if motivo:
            excluidos.append((produto, motivo))
        else:
            candidatos.append(produto)
    if not candidatos:
        return None, excluidos
    escolhido = min(candidatos, key=lambda p: (_pontos_de_repeticao(p, ultimos), _desempate(p, dia)))
    return escolhido, excluidos
