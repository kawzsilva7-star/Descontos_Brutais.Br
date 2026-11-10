"""Gera a página de links (o "link da bio") no visual do Beacons do dono.

Topo com logo e botões amarelos das redes; embaixo, os produtos já postados, separados
por nicho (banho, cozinha, pet...). Cada produto aparece com a foto pequena e o nome.
É um arquivo HTML único, sem programas externos, que abre bem no celular.
"""
import html
from datetime import datetime
from pathlib import Path

from .nichos import EMOJI, ORDEM, nicho_do_produto

TITULO = "Descontos Brutais"
SUBTITULO = "Achadinhos de tudo um pouco, separados por nicho"
LOGO = ("https://cdn.beacons.ai/user_content/qZBe35MoD9fK6ooFIY99KqGcdZs1/referenced_images/"
        "b58ba55f-42d7-4423-991a-3c83d4ad2f53__user_content/qZBe35MoD9fK6ooFIY99KqGcdZs1/"
        "profile_descontosszbrutais__74e35381-0f4d-4539-adc5-f21f9e5a4839.webp")
AVISO = ("Publicidade: os links são de afiliado. Posso receber comissão pela sua compra, sem custo extra "
         "para você. Preço e estoque podem mudar, confira na loja.")
AVISO_SAUDE = "⚠️ Produtos ligados à saúde: tome cuidado e consulte um médico antes de usar."
NICHO_SAUDE = "Nutrição e saúde"
QUANTOS_NOVOS = 6

# Links públicos das redes (os mesmos do Beacons do dono). Para trocar, edite aqui.
REDES = [
    ("telegram", "📲 GRUPO DE PROMOÇÃO", "https://t.me/+WY_THiOo4R9mNzM5"),
    ("tiktok", "📱 MEU TIKOTEKO", "https://www.tiktok.com/@achadosbiblicais"),
    ("instagram", "📸 MEU INSTAGRAM", "https://www.instagram.com/descontos_brutaiss/"),
    ("facebook", "⌨️ PÁGINA DO FACE", "https://www.facebook.com/share/1EbD7KuES1/"),
]

# Ícones das redes (desenhos da biblioteca Simple Icons, licença CC0).
ICONES = {
    "telegram": "M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z",
    "tiktok": "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.110 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.920-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z",
    "instagram": "M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.760-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z",
    "facebook": "M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z",
}

CSS = """
:root{--fundo:#000;--cartao:#141414;--borda:#262626;--texto:#fff;--suave:#a3a3a3;--amarelo:#f2b300;--tinta:#111}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.4 "Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.pagina{max-width:560px;margin:0 auto;padding:32px 16px 40px}
header{text-align:center}
.logo{width:132px;height:132px;border-radius:50%;margin:0 auto;display:grid;place-items:center;overflow:hidden;
  border:3px solid #fff;box-shadow:0 0 0 3px #000,0 0 28px rgba(255,140,0,.45);background:#1a1a1a;font-size:56px}
.logo img{width:100%;height:100%;object-fit:cover;display:block}
h1{margin:18px 0 6px;font-size:32px;font-weight:800;letter-spacing:-.3px}
.sub{margin:0;color:var(--suave);font-size:15px}
.icones{display:flex;justify-content:center;gap:22px;margin:16px 0 26px}
.icones a{color:#fff;display:inline-flex}
.icones svg{width:30px;height:30px;fill:currentColor}
.botoes{display:grid;gap:14px}
.botao{position:relative;display:flex;align-items:center;justify-content:center;min-height:66px;padding:10px 64px;
  background:var(--amarelo);color:var(--tinta);border-radius:999px;text-decoration:none;font-size:17px;font-weight:600;
  text-align:center;transition:transform .12s}
.botao:hover,.botao:focus-visible{transform:scale(1.015)}
.botao .bola{position:absolute;left:10px;top:50%;transform:translateY(-50%);width:46px;height:46px;border-radius:50%;
  background:var(--tinta);display:grid;place-items:center}
.botao .bola svg{width:24px;height:24px;fill:var(--amarelo)}
h2{margin:36px 0 6px;text-align:center;font-size:22px;font-weight:800}
.dica{margin:0 0 14px;text-align:center;color:var(--suave);font-size:14px}
.busca{width:100%;padding:13px 18px;border-radius:999px;border:1px solid var(--borda);background:var(--cartao);color:#fff;
  font-size:16px;outline:none;margin-bottom:14px}
.busca:focus{border-color:var(--amarelo)}
details{margin-bottom:12px}
summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;min-height:58px;padding:8px 20px;
  background:var(--amarelo);color:var(--tinta);border-radius:999px;font-weight:700;font-size:17px;user-select:none}
summary::-webkit-details-marker{display:none}
summary .qtd{margin-left:auto;background:var(--tinta);color:var(--amarelo);border-radius:999px;padding:2px 10px;font-size:13px}
summary .seta{transition:transform .2s;font-size:14px}
details[open] summary .seta{transform:rotate(180deg)}
.lista{display:grid;gap:10px;padding:12px 4px 4px}
.item{display:flex;align-items:center;gap:12px;padding:8px 14px 8px 8px;background:var(--cartao);border:1px solid var(--borda);
  border-radius:16px;color:inherit;text-decoration:none}
.item:hover,.item:focus-visible{border-color:var(--amarelo)}
.item img{width:58px;height:58px;border-radius:12px;object-fit:cover;background:#fff;flex:none}
.item .nome{flex:1;min-width:0;font-size:15px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.item .ir{color:var(--amarelo);font-size:22px;flex:none}
.aviso-saude{margin:4px 4px 0;color:#ffd166;font-size:13px}
.vazio{color:var(--suave);text-align:center;padding:24px 0}
footer{margin-top:36px;color:var(--suave);font-size:12px;text-align:center}
footer p{margin:6px 0}
"""

JS = """
const b=document.getElementById('busca');
if(b){b.addEventListener('input',()=>{const t=b.value.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim();
document.querySelectorAll('main details').forEach(d=>{let n=0;d.querySelectorAll('.item').forEach(i=>{const ok=!t||i.dataset.busca.includes(t);i.hidden=!ok;if(ok)n++});
d.hidden=t&&!n;if(t)d.open=n>0});});}
"""


def _svg(rede: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONES[rede]}"/></svg>'


def _sem_acento_minusculo(texto: str) -> str:
    import unicodedata
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c)).lower()


def _item(produto) -> str:
    nome = html.escape(produto.nome)
    busca = html.escape(_sem_acento_minusculo(produto.nome), quote=True)
    return (
        f'<a class="item" data-busca="{busca}" href="{html.escape(produto.link, quote=True)}" '
        f'target="_blank" rel="sponsored noopener">'
        f'<img src="{html.escape(produto.foto, quote=True)}" alt="" loading="lazy" width="58" height="58">'
        f'<span class="nome">{nome}</span><span class="ir" aria-hidden="true">›</span></a>'
    )


def _nicho(nome: str, produtos: list, aberto: bool = False, classe: str = "nicho") -> str:
    aviso = f'<p class="aviso-saude">{html.escape(AVISO_SAUDE)}</p>' if nome == NICHO_SAUDE else ""
    return (
        f'<details class="{classe}"{" open" if aberto else ""}><summary><span>{EMOJI.get(nome, "🔥")}</span>'
        f'<span>{html.escape(nome)}</span><span class="qtd">{len(produtos)}</span><span class="seta">▼</span></summary>'
        f'<div class="lista">{"".join(_item(p) for p in produtos)}</div>{aviso}</details>'
    )


def gerar_html(produtos_com_data: list, agora: datetime | None = None) -> str:
    """`produtos_com_data` = [(produto, data_do_post)]. Os mais novos aparecem primeiro."""
    agora = agora or datetime.now()
    ordenados = [p for p, _ in sorted(produtos_com_data, key=lambda par: par[1], reverse=True)]
    grupos = {}
    for produto in ordenados:
        grupos.setdefault(nicho_do_produto(produto), []).append(produto)

    icones = "".join(
        f'<a href="{html.escape(link, quote=True)}" target="_blank" rel="noopener" aria-label="{rede}">{_svg(rede)}</a>'
        for rede, _, link in REDES
    )
    botoes = "".join(
        f'<a class="botao" href="{html.escape(link, quote=True)}" target="_blank" rel="noopener">'
        f'<span class="bola">{_svg(rede)}</span>{html.escape(texto)}</a>'
        for rede, texto, link in REDES
    )
    if ordenados:
        novos = _nicho("Novos achados", ordenados[:QUANTOS_NOVOS], aberto=True, classe="novos")
        nichos = "".join(_nicho(n, grupos[n]) for n in ORDEM if n in grupos)
        produtos = (
            '<input id="busca" class="busca" type="search" placeholder="🔎 Procurar produto (ex.: toalha, creatina)" '
            f'aria-label="Procurar produto">{novos}{nichos}'
        )
    else:
        produtos = '<p class="vazio">Em breve, novos achados por aqui.</p>'

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITULO} ⚡ Achados e ofertas</title>
<meta name="description" content="{html.escape(SUBTITULO)}">
<meta name="theme-color" content="#000000">
<style>{CSS}</style>
</head>
<body>
<div class="pagina">
<header>
<div class="logo"><img src="{LOGO}" alt="Logo {TITULO}" onerror="this.parentNode.textContent='⚡'"></div>
<h1>{TITULO} ⚡</h1>
<p class="sub">{html.escape(SUBTITULO)}</p>
<nav class="icones" aria-label="Redes sociais">{icones}</nav>
</header>
<section class="botoes" aria-label="Minhas redes">{botoes}</section>
<h2>🛒 Produtos</h2>
<p class="dica">Toque no nicho e depois no produto para ver na loja.</p>
<main>{produtos}</main>
<footer><p>{html.escape(AVISO)}</p><p>Atualizado em {agora.strftime("%d/%m/%Y %H:%M")}</p></footer>
</div>
<script>{JS}</script>
</body>
</html>
"""


def escrever(caminho: Path, produtos_com_data: list, agora: datetime | None = None) -> Path:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(gerar_html(produtos_com_data, agora), encoding="utf-8")
    return caminho
