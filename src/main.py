"""Roda UMA publicação. O Agendador do Windows chama isto 3 vezes por dia.

Uso (na pasta do projeto):
    python -m src.main                  escolhe um produto e posta (ou simula, se DRY_RUN=true)
    python -m src.main --listar         mostra quais produtos podem ou não ser postados
    python -m src.main --testar-conexao confere as chaves sem postar nada
    python -m src.main --rede telegram  usa só uma rede
    python -m src.main --forcar         ignora o limite de posts do dia
"""
import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import RAIZ, carregar_config
from .historico.registro import Historico
from .pagina import gerador
from .produtos import manual, selecao
from .redes import facebook, instagram, telegram
from .redes.base import ErroPostagem, PostagemIncerta
from .texto import modelos

REDES = {"telegram": telegram, "facebook": facebook, "instagram": instagram}
log = logging.getLogger("bot")


class _EscondeSegredos(logging.Filter):
    """Troca qualquer chave por *** antes de escrever no log ou na tela."""

    def __init__(self, segredos):
        super().__init__()
        self.segredos = segredos

    def filter(self, registro):
        texto = registro.getMessage()
        for segredo in self.segredos:
            texto = texto.replace(segredo, "***")
        registro.msg, registro.args = texto, ()
        return True


def _preparar_log(cfg) -> None:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    pasta = RAIZ / "logs"
    pasta.mkdir(exist_ok=True)
    formato = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%d/%m/%Y %H:%M:%S")
    filtro = _EscondeSegredos(cfg.segredos())
    log.setLevel(logging.INFO)
    log.handlers.clear()
    for destino in (RotatingFileHandler(pasta / "bot.log", maxBytes=500_000, backupCount=3, encoding="utf-8"),
                    logging.StreamHandler(sys.stdout)):
        destino.setFormatter(formato)
        destino.addFilter(filtro)
        log.addHandler(destino)


def _carregar_produtos(cfg, caminho: Path | None):
    produtos, avisos = manual.carregar(caminho or cfg.arquivo_produtos)
    for aviso in avisos:
        log.warning("Lista de produtos: %s", aviso)
    return produtos


def listar(cfg, historico, caminho) -> int:
    produtos = _carregar_produtos(cfg, caminho)
    escolhido, excluidos = selecao.escolher(produtos, cfg, historico.postados_recentes(cfg.dias_sem_repetir))
    log.info("%d produtos na lista. Próximo a ser postado: %s", len(produtos), escolhido.nome if escolhido else "nenhum")
    for produto, motivo in excluidos:
        log.info("  fora: %s -> %s", (produto.nome or produto.link)[:60], motivo)
    return 0


def testar_conexao(cfg) -> int:
    falhou = False
    for nome in cfg.redes_ativas:
        modulo = REDES.get(nome)
        if not modulo:
            log.error("%s: rede desconhecida em REDES_ATIVAS", nome)
            falhou = True
            continue
        try:
            log.info("%s: OK, %s", nome, modulo.testar(cfg))
        except ErroPostagem as erro:
            log.error("%s: PROBLEMA, %s", nome, erro)
            falhou = True
    return 1 if falhou else 0


def gerar_pagina(cfg, historico, caminho_produtos, saida: Path | None = None) -> int:
    """Refaz a página do link da bio com os produtos postados nos últimos dias."""
    produtos = {p.id: p for p in _carregar_produtos(cfg, caminho_produtos)}
    datas = historico.postados_com_data(cfg.dias_sem_repetir)
    na_pagina = [(produtos[pid], quando) for pid, quando in datas.items() if pid in produtos]
    destino = gerador.escrever(saida or cfg.arquivo_pagina, na_pagina)
    log.info("Página do link da bio atualizada (%d produtos): %s", len(na_pagina), destino)
    return 0


def _postar_numa_rede(cfg, historico, produto, rede: str, texto: str) -> str:
    """Posta e registra. Devolve 'ok', 'incerto' ou 'erro'."""
    try:
        identificador = REDES[rede].publicar(cfg, produto, texto)
    except PostagemIncerta as erro:
        historico.registrar(produto, rede, "incerto", str(erro))
        log.warning("%s: não sei se postou (%s). Confira a rede e não repito.", rede, erro)
        return "incerto"
    except ErroPostagem as erro:
        historico.registrar(produto, rede, "erro", str(erro))
        log.error("%s: ERRO, %s", rede, erro)
        return "erro"
    except Exception as erro:  # nada pode derrubar as outras redes
        historico.registrar(produto, rede, "erro", type(erro).__name__)
        log.error("%s: ERRO inesperado (%s)", rede, type(erro).__name__)
        return "erro"
    historico.registrar(produto, rede, "ok", identificador)
    log.info("%s: postado (id %s)", rede, identificador)
    return "ok"


def publicar(cfg, historico, caminho, so_rede: str | None, forcar: bool) -> int:
    modo = "SIMULAÇÃO (nada será postado)" if cfg.simular else "REAL"
    log.info("Início. Modo: %s", modo)
    if not forcar and historico.produtos_postados_hoje() >= cfg.posts_por_dia:
        log.info("Já foram %d posts hoje (limite %d). Nada a fazer.", cfg.posts_por_dia, cfg.posts_por_dia)
        return 0
    produtos = _carregar_produtos(cfg, caminho)
    # Com --rede, só conta o que já saiu naquela rede (permite completar uma rede que ficou para trás).
    produto, excluidos = selecao.escolher(produtos, cfg, historico.postados_recentes(cfg.dias_sem_repetir, so_rede))
    if not produto:
        log.warning("Nenhum produto disponível (%d na lista, %d excluídos). Reponha a planilha.",
                    len(produtos), len(excluidos))
        return 1
    log.info("Produto escolhido: %s", produto.nome[:80])
    redes = [r for r in cfg.redes_ativas if r in REDES and (not so_rede or r == so_rede)]
    resultados = {}
    for rede in redes:
        if rede == "instagram" and not forcar and \
                historico.posts_hoje_na_rede("instagram") >= cfg.instagram_posts_por_dia:
            log.info("instagram: limite de %d post(s) por dia atingido, pulando.", cfg.instagram_posts_por_dia)
            continue
        texto = modelos.montar(produto, rede)
        if cfg.simular:
            tipo = "Reel" if produto.video else "foto"
            print(f"\n----- [{rede}] SIMULAÇÃO ({tipo}: {produto.video or produto.foto}) -----\n{texto}\n")
            continue
        resultados[rede] = _postar_numa_rede(cfg, historico, produto, rede, texto)
    if cfg.simular:
        log.info("Fim da simulação. Para postar de verdade: DRY_RUN=false no .env.")
        return 0
    deu_certo = any(r in ("ok", "incerto") for r in resultados.values())
    if deu_certo:
        try:
            gerar_pagina(cfg, historico, caminho)
        except Exception as erro:  # a página nunca pode atrapalhar os posts
            log.warning("Não consegui atualizar a página do link da bio (%s).", type(erro).__name__)
    return 0 if deu_certo or not resultados else 1


def main(argv=None) -> int:
    analisador = argparse.ArgumentParser(description="Bot de afiliados")
    analisador.add_argument("--listar", action="store_true", help="mostra o que pode ser postado")
    analisador.add_argument("--testar-conexao", action="store_true", help="confere as chaves sem postar")
    analisador.add_argument("--rede", choices=list(REDES), help="usa só esta rede")
    analisador.add_argument("--forcar", action="store_true", help="ignora o limite de posts do dia")
    analisador.add_argument("--produtos", type=Path, help="usa outra planilha de produtos")
    analisador.add_argument("--gerar-pagina", action="store_true", help="refaz a página do link da bio")
    analisador.add_argument("--saida", type=Path, help="com --gerar-pagina: onde salvar o arquivo (para prévia)")
    args = analisador.parse_args(argv)

    cfg = carregar_config()
    _preparar_log(cfg)
    try:
        if args.testar_conexao:
            return testar_conexao(cfg)
        historico = Historico(cfg.arquivo_historico, cfg.fuso)
        if args.listar:
            return listar(cfg, historico, args.produtos)
        if args.gerar_pagina:
            return gerar_pagina(cfg, historico, args.produtos, args.saida)
        return publicar(cfg, historico, args.produtos, args.rede, args.forcar)
    except FileNotFoundError as erro:
        log.error("%s", erro)
        return 1
    except Exception as erro:
        log.error("Erro inesperado: %s", type(erro).__name__)
        return 1


if __name__ == "__main__":
    sys.exit(main())
