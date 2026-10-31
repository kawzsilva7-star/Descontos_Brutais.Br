"""Nomes padronizados de categoria (usados na página de links e na legenda do Instagram)."""
import unicodedata

ORDEM = ["Casa", "Dia a dia", "Carro", "Eletrônicos", "Gamers", "Ferramentas", "Moda", "Beleza"]
OUTROS = "Outros"

EMOJI = {
    "Casa": "🏠", "Dia a dia": "🛍️", "Carro": "🚗", "Eletrônicos": "📱", "Gamers": "🎮",
    "Ferramentas": "🔧", "Moda": "👕", "Beleza": "💄", OUTROS: "⭐",
}

_APELIDOS = {
    "casa": "Casa", "cozinha": "Casa", "utilidades": "Casa", "casa e cozinha": "Casa",
    "dia a dia": "Dia a dia", "dia-a-dia": "Dia a dia", "diaadia": "Dia a dia", "cotidiano": "Dia a dia",
    "carro": "Carro", "carros": "Carro", "automotivo": "Carro", "auto": "Carro", "moto": "Carro",
    "eletronicos": "Eletrônicos", "eletronico": "Eletrônicos", "tecnologia": "Eletrônicos",
    "gamer": "Gamers", "gamers": "Gamers", "games": "Gamers", "game": "Gamers",
    "ferramentas": "Ferramentas", "ferramenta": "Ferramentas",
    "moda": "Moda", "roupas": "Moda", "beleza": "Beleza", "cosmeticos": "Beleza",
}


def _sem_acento(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c))


def nome_da_categoria(texto: str) -> str:
    chave = _sem_acento(texto or "").strip().lower()
    if not chave:
        return OUTROS
    return _APELIDOS.get(chave, (texto or "").strip().title())


def ordenar(nomes) -> list:
    """Categorias conhecidas na ordem fixa, depois as outras em ordem alfabética, 'Outros' por último."""
    nomes = set(nomes)
    conhecidas = [n for n in ORDEM if n in nomes]
    extras = sorted(n for n in nomes if n not in ORDEM and n != OUTROS)
    return conhecidas + extras + ([OUTROS] if OUTROS in nomes else [])
