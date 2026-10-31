"""Registro do que já foi postado (SQLite, um arquivo só)."""
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# Estes status contam como "já postado". "incerto" = o pedido foi enviado mas a
# resposta não chegou; por segurança nunca repetimos.
STATUS_POSTADO = ("ok", "incerto")


class Historico:
    def __init__(self, caminho: Path, fuso: str):
        self.caminho = Path(caminho)
        self.fuso = ZoneInfo(fuso)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._conectar()) as con, con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id TEXT NOT NULL,
                    produto_nome TEXT,
                    link TEXT,
                    rede TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detalhe TEXT,
                    quando TEXT NOT NULL)"""
            )

    def _conectar(self):
        return sqlite3.connect(self.caminho)

    def registrar(self, produto, rede: str, status: str, detalhe: str = "") -> None:
        agora = datetime.now(timezone.utc).isoformat()
        with closing(self._conectar()) as con, con:
            con.execute(
                "INSERT INTO posts (produto_id, produto_nome, link, rede, status, detalhe, quando) VALUES (?,?,?,?,?,?,?)",
                (produto.id, produto.nome, produto.link, rede, status, detalhe[:500], agora),
            )

    def postados_recentes(self, dias: int, rede: str | None = None) -> set:
        """Produtos já postados nos últimos `dias`. Com `rede`, olha só aquela rede."""
        limite = (datetime.now(timezone.utc) - timedelta(days=dias)).isoformat()
        marcas = ",".join("?" * len(STATUS_POSTADO))
        filtro_rede, extra = ("AND rede = ?", (rede,)) if rede else ("", ())
        with closing(self._conectar()) as con:
            linhas = con.execute(
                f"SELECT DISTINCT produto_id FROM posts WHERE status IN ({marcas}) AND quando >= ? {filtro_rede}",
                (*STATUS_POSTADO, limite, *extra),
            ).fetchall()
        return {linha[0] for linha in linhas}

    def postados_com_data(self, dias: int) -> dict:
        """{produto_id: quando foi postado (mais recente)} dos últimos `dias`, em horário local."""
        limite = (datetime.now(timezone.utc) - timedelta(days=dias)).isoformat()
        marcas = ",".join("?" * len(STATUS_POSTADO))
        with closing(self._conectar()) as con:
            linhas = con.execute(
                f"SELECT produto_id, MAX(quando) FROM posts WHERE status IN ({marcas}) AND quando >= ? GROUP BY produto_id",
                (*STATUS_POSTADO, limite),
            ).fetchall()
        return {pid: datetime.fromisoformat(q).astimezone(self.fuso) for pid, q in linhas}

    def _inicio_do_dia_utc(self) -> str:
        agora = datetime.now(self.fuso)
        inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        return inicio.astimezone(timezone.utc).isoformat()

    def produtos_postados_hoje(self) -> int:
        marcas = ",".join("?" * len(STATUS_POSTADO))
        with closing(self._conectar()) as con:
            return con.execute(
                f"SELECT COUNT(DISTINCT produto_id) FROM posts WHERE status IN ({marcas}) AND quando >= ?",
                (*STATUS_POSTADO, self._inicio_do_dia_utc()),
            ).fetchone()[0]

    def posts_hoje_na_rede(self, rede: str) -> int:
        marcas = ",".join("?" * len(STATUS_POSTADO))
        with closing(self._conectar()) as con:
            return con.execute(
                f"SELECT COUNT(*) FROM posts WHERE rede = ? AND status IN ({marcas}) AND quando >= ?",
                (rede, *STATUS_POSTADO, self._inicio_do_dia_utc()),
            ).fetchone()[0]
