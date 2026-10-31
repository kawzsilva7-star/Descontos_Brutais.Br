"""Fonte de produtos: uma planilha CSV que o dono preenche com os links de afiliado.

Quando a Shopee (ou outra loja) tiver API, entra um arquivo novo nesta pasta que
devolve a mesma lista de `Produto`. O resto do bot não muda.
"""
import csv
import hashlib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

# Nomes de coluna aceitos (sem acento, minúsculos) -> campo do produto.
APELIDOS = {
    "nome": "nome", "titulo": "nome", "produto": "nome",
    "preco": "preco", "valor": "preco",
    "link": "link", "link_afiliado": "link", "afiliado": "link", "url": "link",
    "foto": "foto", "foto_url": "foto", "imagem": "foto", "imagem_url": "foto",
    "comissao": "comissao", "comissao_percentual": "comissao", "percentual": "comissao",
    "categoria": "categoria",
    "video": "video", "video_url": "video",
    "loja": "loja", "marketplace": "loja",
}


@dataclass
class Produto:
    id: str
    nome: str
    preco: float | None
    link: str
    foto: str
    comissao: float | None
    categoria: str = ""
    video: str = ""
    loja: str = ""


def _sem_acento(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c))


def _cabecalho(nome: str) -> str:
    limpo = _sem_acento(nome).strip().lower().replace(" ", "_").replace("%", "")
    return APELIDOS.get(limpo.strip("_"), "")


def ler_preco(texto: str) -> float | None:
    """Aceita 'R$ 1.299,90', '129,90', '129.90' e '1299'."""
    texto = re.sub(r"[^\d.,]", "", texto or "")
    if not texto:
        return None
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", texto):
        texto = texto.replace(".", "")
    try:
        return float(texto)
    except ValueError:
        return None


def ler_comissao(texto: str) -> float | None:
    """Aceita '12', '12%' e '12,5'."""
    return ler_preco((texto or "").replace("%", ""))


def _id_do_produto(link: str) -> str:
    chave = link.strip().lower().split("#")[0].rstrip("/")
    return hashlib.sha1(chave.encode("utf-8")).hexdigest()[:12]


def _abrir(caminho: Path) -> str:
    bruto = caminho.read_bytes()
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            return bruto.decode(codificacao)
        except UnicodeDecodeError:
            continue
    return bruto.decode("latin-1")


def carregar(caminho: Path) -> tuple:
    """Lê a planilha. Devolve (produtos, avisos). Linhas com problema viram aviso."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(
            f"Não achei a lista de produtos: {caminho}. "
            "Copie dados/produtos.exemplo.csv para dados/produtos.csv e preencha."
        )
    texto = _abrir(caminho)
    amostra = texto[:2000]
    try:
        dialeto = csv.Sniffer().sniff(amostra, delimiters=";,\t")
    except csv.Error:
        dialeto = csv.excel
    leitor = csv.reader(texto.splitlines(), dialeto)
    linhas = [l for l in leitor if any(c.strip() for c in l)]
    if not linhas:
        return [], ["A lista de produtos está vazia."]
    campos = [_cabecalho(c) for c in linhas[0]]
    produtos, avisos, vistos = [], [], set()
    for numero, linha in enumerate(linhas[1:], start=2):
        dados = {}
        for campo, valor in zip(campos, linha):
            if campo:
                dados[campo] = valor.strip()
        link = dados.get("link", "")
        if not link:
            avisos.append(f"linha {numero}: sem link, ignorada")
            continue
        produto = Produto(
            id=_id_do_produto(link),
            nome=dados.get("nome", ""),
            preco=ler_preco(dados.get("preco", "")),
            link=link,
            foto=dados.get("foto", ""),
            comissao=ler_comissao(dados.get("comissao", "")),
            categoria=dados.get("categoria", ""),
            video=dados.get("video", ""),
            loja=dados.get("loja", ""),
        )
        if produto.id in vistos:
            avisos.append(f"linha {numero}: link repetido na lista, ignorada")
            continue
        vistos.add(produto.id)
        produtos.append(produto)
    return produtos, avisos
