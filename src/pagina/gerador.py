"""Gera a página de links (o "link da bio"): produtos postados, separados por categoria.

É um arquivo HTML único, sem programas externos, que abre bem no celular.
"""
import html
from datetime import datetime
from pathlib import Path

from ..produtos.categorias import EMOJI, OUTROS, nome_da_categoria, ordenar
from ..texto.modelos import formatar_preco

TITULO = "Descontos Brutais"
SUBTITULO = "Achados e ofertas em um só lugar"
AVISO = "Alguns links são de afiliado: posso receber comissão pela sua compra, sem custo extra para você. Preços podem mudar, confira na loja."

CSS = """
:root{--fundo:#0b0b0d;--cartao:#16161a;--borda:#2a2a31;--texto:#f4f1ea;--suave:#a8a39a;--ouro:#f5b301;--ouro2:#ffcf4a}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{text-align:center;padding:32px 16px 12px}
h1{margin:0;font-size:28px;letter-spacing:.5px;color:var(--ouro)}
.sub{margin:4px 0 0;color:var(--suave)}
nav{position:sticky;top:0;z-index:5;background:rgba(11,11,13,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--borda);padding:10px 16px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
nav a{flex:none;color:var(--texto);text-decoration:none;border:1px solid var(--borda);border-radius:999px;padding:7px 14px;font-size:14px;background:var(--cartao)}
nav a:hover,nav a:focus{border-color:var(--ouro);color:var(--ouro)}
main{max-width:720px;margin:0 auto;padding:8px 16px 40px}
section{padding-top:22px}
h2{font-size:20px;margin:0 0 12px}
.lista{display:grid;gap:12px}
.cartao{display:flex;gap:12px;background:var(--cartao);border:1px solid var(--borda);border-radius:14px;padding:10px;text-decoration:none;color:inherit}
.cartao:hover{border-color:var(--ouro)}
.cartao img{width:96px;height:96px;object-fit:cover;border-radius:10px;background:#222;flex:none}
.info{display:flex;flex-direction:column;justify-content:space-between;min-width:0;flex:1}
.nome{font-size:15px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.linha{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:6px}
.preco{font-weight:700;color:var(--ouro2)}
.botao{background:var(--ouro);color:#111;font-weight:700;font-size:13px;border-radius:999px;padding:7px 14px;white-space:nowrap}
.vazio{color:var(--suave);text-align:center;padding:40px 0}
footer{max-width:720px;margin:0 auto;padding:0 16px 40px;color:var(--suave);font-size:12px;text-align:center}
"""


def _cartao(produto) -> str:
    nome = html.escape(produto.nome)
    return (
        f'<a class="cartao" href="{html.escape(produto.link, quote=True)}" target="_blank" rel="sponsored noopener">'
        f'<img src="{html.escape(produto.foto, quote=True)}" alt="{nome}" loading="lazy" width="96" height="96">'
        f'<div class="info"><div class="nome">{nome}</div>'
        f'<div class="linha"><span class="preco">{formatar_preco(produto.preco)}</span>'
        f'<span class="botao">Ver oferta</span></div></div></a>'
    )


def _id_da_secao(nome: str) -> str:
    return "c-" + "".join(c if c.isalnum() else "-" for c in nome.lower()).strip("-")


def gerar_html(produtos_com_data: list, agora: datetime | None = None) -> str:
    """`produtos_com_data` = [(produto, data_do_post)]. Os mais novos aparecem primeiro."""
    agora = agora or datetime.now()
    grupos = {}
    for produto, data in sorted(produtos_com_data, key=lambda par: par[1], reverse=True):
        grupos.setdefault(nome_da_categoria(produto.categoria), []).append(produto)
    ordem = ordenar(grupos)
    menu = "".join(
        f'<a href="#{_id_da_secao(n)}">{EMOJI.get(n, EMOJI[OUTROS])} {html.escape(n)}</a>' for n in ordem
    )
    secoes = "".join(
        f'<section id="{_id_da_secao(n)}"><h2>{EMOJI.get(n, EMOJI[OUTROS])} {html.escape(n)}</h2>'
        f'<div class="lista">{"".join(_cartao(p) for p in grupos[n])}</div></section>'
        for n in ordem
    ) or '<p class="vazio">Em breve, novos achados por aqui.</p>'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITULO} | Achados e ofertas</title>
<meta name="description" content="{html.escape(SUBTITULO)}">
<meta name="robots" content="index,follow">
<style>{CSS}</style>
</head>
<body>
<header><h1>⚡ {TITULO}</h1><p class="sub">{SUBTITULO}</p></header>
{"<nav>" + menu + "</nav>" if ordem else ""}
<main>{secoes}</main>
<footer><p>{html.escape(AVISO)}</p><p>Atualizado em {agora.strftime("%d/%m/%Y %H:%M")}</p></footer>
</body>
</html>
"""


def escrever(caminho: Path, produtos_com_data: list, agora: datetime | None = None) -> Path:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(gerar_html(produtos_com_data, agora), encoding="utf-8")
    return caminho
