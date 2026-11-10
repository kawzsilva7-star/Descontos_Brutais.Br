r"""Troca o token curto do Facebook por um token de Página que não expira e grava no .env.

Uso (na pasta do projeto):
    .venv\Scripts\python.exe scripts\renovar_token_meta.py

O token curto é lido da área de transferência (basta clicar no ícone de copiar do
Explorador). Se não houver um copiado, o script pede para colar. Nada é mostrado na
tela nem enviado a ninguém além do Facebook.
"""
import subprocess
import sys
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
ENV = RAIZ / ".env"
GRAPH = "https://graph.facebook.com/v21.0"


def ler_env() -> dict:
    dados = {}
    for linha in ENV.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, valor = linha.split("=", 1)
            dados[chave.strip()] = valor.strip().strip('"').strip("'")
    return dados


def gravar_env(chave: str, valor: str) -> None:
    linhas = ENV.read_text(encoding="utf-8-sig").splitlines()
    novas, achou = [], False
    for linha in linhas:
        if linha.split("=", 1)[0].strip() == chave:
            novas.append(f"{chave}={valor}")
            achou = True
        else:
            novas.append(linha)
    if not achou:
        novas.append(f"{chave}={valor}")
    ENV.write_text("\n".join(novas) + "\n", encoding="utf-8")


def limpar(texto: str) -> str:
    """Tira espaços, quebras de linha e caracteres invisíveis que vêm junto na colagem."""
    return "".join(c for c in (texto or "") if c.isalnum() or c in "-_.")


def token_da_area_de_transferencia() -> str:
    try:
        saida = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True, text=True, timeout=15,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    token = limpar(saida)
    return token if token.startswith("EAA") and len(token) >= 50 else ""


def pedir(url: str, **params) -> dict:
    resposta = requests.get(url, params=params, timeout=30)
    corpo = resposta.json() if resposta.content else {}
    if resposta.status_code != 200:
        erro = (corpo.get("error") or {}).get("message", f"HTTP {resposta.status_code}")
        sys.exit(f"O Facebook recusou: {erro}")
    return corpo


def main() -> None:
    env = ler_env()
    faltam = [c for c in ("META_APP_ID", "META_APP_SECRET", "META_PAGE_ID") if not env.get(c)]
    if faltam:
        sys.exit("Faltam no .env: " + ", ".join(faltam))

    curto = ""
    for tentativa in range(3):
        input("\nNo Explorador da Graph API, clique no ícone de COPIAR ao lado do token.\n"
              "Quando tiver copiado, volte aqui e aperte Enter (não cole nada): ")
        curto = token_da_area_de_transferencia()
        if curto:
            break
        print("O que está copiado não é um token de usuário (ele começa com EAA). "
              "Copie de novo, só o token, e tente outra vez.")
    if not curto:
        sys.exit("Não consegui ler um token. Rode o script de novo quando estiver com o token copiado.")
    print("Token lido da área de transferência.")

    longo = pedir(
        f"{GRAPH}/oauth/access_token",
        grant_type="fb_exchange_token",
        client_id=env["META_APP_ID"],
        client_secret=env["META_APP_SECRET"],
        fb_exchange_token=curto,
    ).get("access_token")
    if not longo:
        sys.exit("O Facebook não devolveu o token longo.")

    pagina = pedir(f"{GRAPH}/{env['META_PAGE_ID']}", fields="access_token,name", access_token=longo)
    token_pagina = pagina.get("access_token")
    if not token_pagina:
        sys.exit("Não veio o token da Página. Confira se você é administrador da Página e marcou a Página na hora de gerar o token.")

    info = pedir(
        f"{GRAPH}/debug_token",
        input_token=token_pagina,
        access_token=f"{env['META_APP_ID']}|{env['META_APP_SECRET']}",
    ).get("data", {})
    nunca_expira = info.get("expires_at", 1) == 0

    gravar_env("META_PAGE_ACCESS_TOKEN", token_pagina)
    print(f"Pronto. Token da Página '{pagina.get('name', '?')}' gravado no .env.")
    print("Validade: nunca expira." if nunca_expira else "Atenção: este token TEM data de validade (expires_at != 0).")
    print("Agora rode: .venv\\Scripts\\python.exe -m src.main --testar-conexao")


if __name__ == "__main__":
    main()
