"""Separa os produtos da página em nichos (banho, cozinha, pet, academia...).

Primeiro olha o NOME do produto (palavras-chave). Se nenhuma bater, usa a coluna
"categoria" da planilha. Se nada servir, o produto vai para "Outros achados".
Para mudar um nicho, basta editar a lista NICHOS abaixo.
"""
import re
import unicodedata

OUTROS = ("Outros achados", "⭐")

# (nome do nicho, emoji, palavras-chave). A ORDEM importa: o primeiro que bater ganha.
# Palavra terminada em * vale como começo de palavra (suplement* pega suplemento, suplementos...).
NICHOS = [
    ("Nutrição e saúde", "💊", ["creatina", "whey", "glutamina", "biotina", "multivitamin*", "vitamina*", "suplement*",
                               "psyllium", "fibra", "pressao", "oximetro", "termometro", "respiron", "nasal", "nariz",
                               "soro", "nafazolina", "cloridrato", "descongestionante", "medicamento*",
                               "ortoped*", "remedio*", "capsula*", "colageno"]),
    # "elástico de cabelo" é beleza: por isso aqui só elásticos de treino.
    ("Academia", "🏋️", ["academia", "fitness", "shaker", "coqueteleira", "dryfit", "halter*", "treino", "yoga",
                        "extensor*", "faixa elastica", "mini band", "corda de pular"]),
    ("Gamer", "🎮", ["gamer", "game*", "headset", "console", "playstation", "xbox", "nintendo", "joystick"]),
    ("Acessórios para computador", "🖥️", ["mouse", "teclado", "notebook", "monitor", "webcam", "pendrive", "hub usb",
                                          "computador", "mousepad", "ssd"]),
    ("Música", "🎸", ["guitarra*", "violao", "violoes", "ukulele", "cavaquinho", "contrabaixo", "instrumento musical",
                     "instrumentos musicais", "partitura*"]),
    ("Eletrônicos", "📱", ["smartphone", "celular", "fone*", "camera", "tablet", "smartwatch", "caixa de som", "tv",
                          "carregador", "power bank", "filtro de linha", "regua de energia", "estabilizador", "nobreak"]),
    ("Pet", "🐾", ["pet", "caes", "cao", "gatos", "gato", "cachorro*", "coleira", "racao", "arranhador"]),
    ("Carro e bike", "🚗", ["carro*", "moto", "motos", "bike", "bicicleta", "pneu*", "porta-malas", "automotiv*",
                           "veicular"]),
    ("Bolsas", "👜", ["bolsa*", "mochila*", "lancheira", "carteira", "necessaire", "pochete", "sacola*", "ecobag"]),
    ("Limpeza", "🧽", ["limpeza", "lixeira*", "lixo", "papel higienico", "vassoura*", "rodo", "detergente*",
                      "desinfetante*", "esponja*", "pano de chao", "balde*", "mop"]),
    ("Banho", "🛁", ["toalha*", "chuveiro", "banheiro", "banho", "roupao", "tapete de banheiro", "sabonete*"]),
    ("Cozinha", "🍳", ["cozinha", "panela*", "pote*", "tigela*", "ralador", "fatiador", "descascador", "processador",
                      "triturador", "tapioqueira", "frigideira*", "airfryer", "air fryer", "talher*", "copo*",
                      "garrafa termica", "liquidificador"]),
    # Beleza antes de ferramentas: "alicate de cutícula" é manicure, não ferramenta.
    ("Beleza", "💄", ["unha*", "manicure", "cuticula", "esmalte*", "acetona", "protetor solar", "aparador",
                     "maquiagem", "cabelo*", "pente*", "presilha*", "tiara*", "xuxinha*", "shampoo*",
                     "condicionador*", "perfume*", "skincare", "hidratante*", "secador", "chapinha", "barbeador"]),
    # Infantil vem antes da moda: "vestido infantil" é infantil, não moda feminina.
    ("Infantil e família", "🧸", ["bebe", "infantil", "brinquedo*", "figurinha*", "crianca*", "boneca*"]),
    # Bijuteria antes da moda: "colar feminino" é bijuteria.
    ("Bijuterias e acessórios", "💍", ["bijuteria*", "joia*", "brinco*", "colar", "colares", "pulseira*", "anel",
                                       "aneis", "pingente*", "tornozeleira*", "piercing*", "oculos"]),
    # Moda: só vai para feminina/masculina se o anúncio disser. Sem dizer, fica em "Moda unissex" (não inventamos).
    ("Moda feminina", "👗", ["feminin*", "vestido*", "saia*", "cropped", "biquini*", "sutia*", "calcinha*",
                            "legging*", "cowgirl"]),
    ("Moda masculina", "👔", ["masculin*", "cueca*"]),
    ("Moda unissex", "👕", ["unissex", "calca*", "camiseta*", "camisa*", "cinto*", "meia*", "tenis", "relogio*",
                           "top", "short*", "bermuda*", "jaqueta*", "blusa*", "moletom", "chinelo*", "sandalia*",
                           "bone*"]),
    ("Ferramentas e reforma", "🔧", ["parafusadeira", "furadeira", "ferramenta*", "alicate", "chave de fenda", "trena",
                                     "torneira*", "tomada*", "prego*", "parafuso*", "janela*", "fechadura*",
                                     "dobradica*", "porta de madeira", "porta de correr", "interruptor*", "disjuntor*",
                                     "fita isolante", "cimento"]),
    ("Dia a dia", "☂️", ["guarda-chuva", "guarda chuva", "garrafa*", "palmilha*", "squeeze", "organizador*"]),
    ("Casa", "🏠", ["ventilador*", "espelho*", "led*", "natal", "refletor*", "decoracao", "luminaria*", "cortina*",
                   "lampada*", "travesseiro*", "lencol", "lencois", "coberta*", "cobertor*", "edredom", "manta*",
                   "tapete*", "mesa*", "cadeira*", "sofa*", "estante*", "prateleira*", "caixa organizadora"]),
    ("Livros", "📚", ["livro*", "biblia"]),
]

# Quando o nome não diz nada, a coluna "categoria" da planilha decide.
POR_CATEGORIA = {
    "saude": "Nutrição e saúde", "academia": "Academia", "esportes": "Academia", "gamer": "Gamer",
    "gamers": "Gamer", "eletronicos": "Eletrônicos", "pet": "Pet", "carro": "Carro e bike", "bolsas": "Bolsas",
    "banho": "Banho", "cozinha": "Cozinha", "beleza": "Beleza", "moda": "Moda unissex", "moda feminina": "Moda feminina", "moda masculina": "Moda masculina","familia": "Infantil e família",
    "ferramentas": "Ferramentas e reforma", "reforma": "Ferramentas e reforma", "limpeza": "Limpeza", "musica": "Música", "bijuteria": "Bijuterias e acessórios", "bijuterias": "Bijuterias e acessórios", "acessorios": "Bijuterias e acessórios", "dia a dia": "Dia a dia", "casa": "Casa", "livros": "Livros",
}

EMOJI = {nome: emoji for nome, emoji, _ in NICHOS}
EMOJI[OUTROS[0]] = OUTROS[1]
ORDEM = [nome for nome, _, _ in NICHOS] + [OUTROS[0]]


def _limpo(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in base if not unicodedata.combining(c)).lower()


def _padrao(palavra: str) -> str:
    if palavra.endswith("*"):
        return r"\b" + re.escape(palavra[:-1])
    return r"\b" + re.escape(palavra) + r"\b"


_REGRAS = [(nome, re.compile("|".join(_padrao(_limpo(p)) for p in palavras))) for nome, _, palavras in NICHOS]


def nicho_do_produto(produto) -> str:
    nome = _limpo(produto.nome)
    for nicho, regra in _REGRAS:
        if regra.search(nome):
            return nicho
    categoria = _limpo(produto.categoria).strip().replace("-", " ")
    if categoria in POR_CATEGORIA:
        return POR_CATEGORIA[categoria]
    # A planilha pode já trazer o nome exato de um nicho (ex.: "Banho").
    for nicho in ORDEM:
        if _limpo(nicho) == categoria:
            return nicho
    return OUTROS[0]
