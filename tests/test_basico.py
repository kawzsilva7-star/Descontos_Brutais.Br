import logging
import tempfile
import unittest
from pathlib import Path

from src.config import carregar_config
from src.historico.registro import Historico
from src.main import _EscondeSegredos
from src.produtos import manual, selecao
from src.produtos.manual import Produto, ler_comissao, ler_preco
from src.texto import modelos


def _produto(**extra):
    base = dict(id="abc123", nome="Fone Bluetooth", preco=129.9, link="https://loja.teste/p1",
                foto="https://loja.teste/f1.jpg", comissao=12.0, categoria="")
    base.update(extra)
    return Produto(**base)


def _config(**extra):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / ".env"
        arquivo.write_text("DRY_RUN=true\nCOMISSAO_MINIMA_PERCENTUAL=10\n", encoding="utf-8")
        cfg = carregar_config(arquivo)
    for chave, valor in extra.items():
        setattr(cfg, chave, valor)
    return cfg


class Precos(unittest.TestCase):
    def test_formatos(self):
        self.assertEqual(ler_preco("R$ 1.299,90"), 1299.90)
        self.assertEqual(ler_preco("129,90"), 129.90)
        self.assertEqual(ler_preco("129.90"), 129.90)
        self.assertEqual(ler_preco("1.299"), 1299.0)
        self.assertIsNone(ler_preco("grátis"))

    def test_comissao(self):
        self.assertEqual(ler_comissao("12%"), 12.0)
        self.assertEqual(ler_comissao("12,5"), 12.5)
        self.assertIsNone(ler_comissao(""))


class Regras(unittest.TestCase):
    def test_passa(self):
        self.assertIsNone(selecao.motivo_de_exclusao(_produto(), _config(), set()))

    def test_comissao_baixa(self):
        self.assertIn("comissão", selecao.motivo_de_exclusao(_produto(comissao=9.9), _config(), set()))

    def test_comissao_em_branco_passa(self):
        self.assertIsNone(selecao.motivo_de_exclusao(_produto(comissao=None), _config(), set()))

    def test_comissao_exata_passa(self):
        self.assertIsNone(selecao.motivo_de_exclusao(_produto(comissao=10.0), _config(), set()))

    def test_repetido(self):
        self.assertIn("já postado", selecao.motivo_de_exclusao(_produto(), _config(), {"abc123"}))

    def test_sem_limite_de_preco_por_padrao(self):
        self.assertIsNone(selecao.motivo_de_exclusao(_produto(preco=99999), _config(), set()))

    def test_limite_de_preco_quando_configurado(self):
        cfg = _config(preco_maximo=100.0)
        self.assertIn("máximo", selecao.motivo_de_exclusao(_produto(), cfg, set()))

    def test_link_de_exemplo_e_sem_foto_nao_entram(self):
        self.assertIsNotNone(selecao.motivo_de_exclusao(_produto(link="https://exemplo.com/x"), _config(), set()))
        self.assertIsNotNone(selecao.motivo_de_exclusao(_produto(foto=""), _config(), set()))
        self.assertIsNotNone(selecao.motivo_de_exclusao(_produto(link="http://loja.teste/p"), _config(), set()))

    def test_primeiro_da_lista_vence(self):
        a, b = _produto(id="a", comissao=5), _produto(id="b"),
        escolhido, excluidos = selecao.escolher([a, b], _config(), set())
        self.assertEqual(escolhido.id, "b")
        self.assertEqual(len(excluidos), 1)


class Historia(unittest.TestCase):
    def test_nao_repete_e_conta_por_dia(self):
        with tempfile.TemporaryDirectory() as pasta:
            h = Historico(Path(pasta) / "h.db", "America/Sao_Paulo")
            p = _produto()
            self.assertEqual(h.postados_recentes(30), set())
            h.registrar(p, "telegram", "erro", "falhou")
            self.assertEqual(h.postados_recentes(30), set())  # erro não conta como postado
            h.registrar(p, "telegram", "ok", "1")
            h.registrar(p, "facebook", "incerto", "sem resposta")  # incerto conta: nunca duplicar
            self.assertEqual(h.postados_recentes(30), {"abc123"})
            self.assertEqual(h.postados_recentes(30, "telegram"), {"abc123"})
            self.assertEqual(h.postados_recentes(30, "instagram"), set())  # ainda não saiu lá
            self.assertEqual(h.produtos_postados_hoje(), 1)
            self.assertEqual(h.posts_hoje_na_rede("telegram"), 1)
            self.assertEqual(h.posts_hoje_na_rede("instagram"), 0)


class Atrasados(unittest.TestCase):
    def test_so_o_que_saiu_no_telegram_e_falta_na_rede(self):
        a, b, c = _produto(id="a"), _produto(id="b"), _produto(id="c")
        fila = selecao.atrasados([a, b, c], _config(), na_origem={"a", "b"}, na_rede={"a"})
        self.assertEqual([p.id for p in fila], ["b"])  # c nunca saiu no Telegram; a já saiu na rede

    def test_mantem_a_ordem_da_planilha_e_barra_produto_invalido(self):
        a, b, c = _produto(id="a"), _produto(id="b", foto=""), _produto(id="c")
        fila = selecao.atrasados([a, b, c], _config(), na_origem={"a", "b", "c"}, na_rede=set())
        self.assertEqual([p.id for p in fila], ["a", "c"])


class Planilha(unittest.TestCase):
    def test_leitura_com_ponto_e_virgula_e_acentos(self):
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "p.csv"
            arq.write_text("Nome;Preço;Link afiliado;Foto;Comissão %\n"
                           "Garrafa térmica;79,00;https://loja.teste/a;https://loja.teste/a.jpg;12\n"
                           "Repetida;10;https://loja.teste/a;https://loja.teste/a.jpg;12\n"
                           ";;;;\n", encoding="utf-8")
            produtos, avisos = manual.carregar(arq)
            self.assertEqual(len(produtos), 1)
            self.assertEqual(produtos[0].preco, 79.0)
            self.assertEqual(produtos[0].comissao, 12.0)
            self.assertEqual(len(avisos), 1)

    def test_planilha_do_excel_em_cp1252(self):
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "p.csv"
            arq.write_bytes("nome;preco;link;foto\nCafeteira Ação;99,90;https://loja.teste/c;https://loja.teste/c.jpg\n".encode("cp1252"))
            produtos, _ = manual.carregar(arq)
            self.assertEqual(produtos[0].nome, "Cafeteira Ação")


class Textos(unittest.TestCase):
    def test_todo_post_tem_link_preco_e_aviso(self):
        for rede in ("telegram", "facebook", "instagram"):
            texto = modelos.montar(_produto(), rede)
            if rede == "instagram":
                self.assertIn("link da bio", texto)
                self.assertNotIn("https://", texto)
            else:
                self.assertIn("https://loja.teste/p1", texto)
            self.assertIn("R$ 129,90", texto)
            self.assertIn("Publicidade", texto)

    def test_nao_inventa_desconto(self):
        texto = modelos.montar(_produto(), "telegram").lower()
        for proibida in ("desconto", "últimas unidades", "relâmpago", "% off"):
            self.assertNotIn(proibida, texto)

    def test_nome_enorme_nao_estoura_limite_nem_corta_o_link(self):
        texto = modelos.montar(_produto(nome="X" * 900), "telegram")
        self.assertLessEqual(len(texto), 1024)
        self.assertIn("https://loja.teste/p1", texto)
        self.assertIn("Publicidade", texto)

    def test_preco_formatado(self):
        self.assertEqual(modelos.formatar_preco(1299.9), "R$ 1.299,90")


class Pagina(unittest.TestCase):
    def test_agrupa_por_nicho_na_ordem_e_escapa_html(self):
        from datetime import datetime
        from src.pagina.gerador import gerar_html
        agora = datetime(2026, 10, 31, 12, 0)
        itens = [
            (_produto(id="a", nome="Fone <b>X</b>", categoria=""), datetime(2026, 10, 30)),
            (_produto(id="b", nome="Kit 5 Toalhas", categoria="casa"), datetime(2026, 10, 29)),
            (_produto(id="c", nome="Coisa sem nicho", categoria=""), datetime(2026, 10, 28)),
            (_produto(id="d", nome="Creatina 1kg", categoria=""), datetime(2026, 10, 27)),
        ]
        pagina = gerar_html(itens, agora)
        self.assertLess(pagina.index("<span>Eletrônicos"), pagina.index("<span>Banho"))
        self.assertLess(pagina.index("<span>Banho"), pagina.index("<span>Outros achados"))
        self.assertIn("consulte um médico", pagina)  # nicho de saúde leva o aviso
        self.assertIn("t.me/", pagina)               # botões das redes
        self.assertNotIn("<b>X</b>", pagina)       # texto da loja nunca vira HTML
        self.assertIn("Fone &lt;b&gt;X&lt;/b&gt;", pagina)
        self.assertIn("afiliado", pagina)          # aviso de publicidade na página
        self.assertIn('rel="sponsored noopener"', pagina)

    def test_pagina_vazia_nao_quebra(self):
        from src.pagina.gerador import gerar_html
        self.assertIn("Em breve", gerar_html([]))

    def test_legenda_do_instagram_manda_para_a_bio(self):
        texto = modelos.montar(_produto(categoria="ferramentas"), "instagram")
        self.assertIn("Clique no link da bio para comprar", texto)
        self.assertNotIn("seção", texto)

    def test_nichos_pelo_nome(self):
        from src.pagina.nichos import nicho_do_produto
        casos = {
            "Kit 5 em 1 Toalhas de Banho": "Banho", "Smartphone Motorola Moto G06": "Eletrônicos",
            "Caminha Iglu para Cães": "Pet", "Coqueteleira Shaker Academia": "Academia",
            "Mouse Gamer RGB": "Gamer", "Guarda-chuva Automático": "Dia a dia",
            "Bolsa Térmica Marmita": "Bolsas", "Jogo 14 Potes Cozinha": "Cozinha",
            "Saia Curta Godê": "Moda feminina", "Calça Masculina Tactel": "Moda masculina",
            "Kit 15 Pares Meias": "Moda unissex", "Vestido Infantil Festa": "Infantil e família",
        }
        for nome, nicho in casos.items():
            self.assertEqual(nicho_do_produto(_produto(nome=nome, categoria="")), nicho, nome)
        self.assertEqual(nicho_do_produto(_produto(nome="Coisa", categoria="pet")), "Pet")

    def test_categorias_apelidos(self):
        from src.produtos.categorias import nome_da_categoria
        self.assertEqual(nome_da_categoria("Eletrônicos"), "Eletrônicos")
        self.assertEqual(nome_da_categoria("gamer"), "Gamers")
        self.assertEqual(nome_da_categoria("dia-a-dia"), "Dia a dia")
        self.assertEqual(nome_da_categoria(""), "Outros")


class Seguranca(unittest.TestCase):
    def test_log_esconde_segredos(self):
        filtro = _EscondeSegredos(["TOKEN-SECRETO-123"])
        registro = logging.LogRecord("bot", logging.INFO, "", 0, "falhou em %s", ("https://x/botTOKEN-SECRETO-123/y",), None)
        filtro.filter(registro)
        self.assertNotIn("TOKEN-SECRETO-123", registro.getMessage())
        self.assertIn("***", registro.getMessage())

    def test_dry_run_so_desliga_com_false(self):
        for valor, esperado in (("true", True), ("", True), ("False", False), ("0", True), ("sim", True)):
            with tempfile.TemporaryDirectory() as pasta:
                arq = Path(pasta) / ".env"
                arq.write_text(f"DRY_RUN={valor}\n", encoding="utf-8")
                self.assertEqual(carregar_config(arq).simular, esperado, valor)


if __name__ == "__main__":
    unittest.main()
