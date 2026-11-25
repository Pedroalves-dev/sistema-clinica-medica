"""Testes automáticos das regras de negócio (sem abrir Tkinter)."""
import unittest
from controllers.filas import GerenciadorFilas


class TesteFilas(unittest.TestCase):
    def setUp(self):
        self.g = GerenciadorFilas()

    def test_emissao_independente(self):
        self.assertEqual(self.g.emitir("CG", "N"), "CG-N001")
        self.assertEqual(self.g.emitir("CG", "N"), "CG-N002")
        self.assertEqual(self.g.emitir("CA", "N"), "CA-N001")
        self.assertEqual(self.g.emitir("CG", "P"), "CG-P001")

    def test_prioridade_e_fifo(self):
        self.g.emitir("CG", "N")
        self.g.emitir("CG", "P")
        self.g.emitir("CG", "P")
        self.g.emitir("CG", "N")
        self.assertEqual([self.g.chamar("CG")["senha"] for _ in range(4)],
                         ["CG-P001", "CG-P002", "CG-N001", "CG-N002"])

    def test_filas_independentes(self):
        self.g.emitir("CG", "N")
        self.g.emitir("OR", "P")
        self.assertEqual(self.g.chamar("OR")["senha"], "OR-P001")
        self.assertEqual(self.g.quantidade("CG"), 1)

    def test_estimativa_com_prioridade(self):
        normal = self.g.emitir("CG", "N")
        preferencial = self.g.emitir("CG", "P")
        self.assertEqual(self.g.estimativa(preferencial), 0)
        self.assertEqual(self.g.estimativa(normal), 30)

    def test_historico(self):
        self.g.emitir("CG", "N")
        registro = self.g.chamar("CG")
        self.assertEqual(self.g.ultima_chamada(), registro)
        self.assertEqual(self.g.quantidade(), 0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            self.g.chamar("CG")
        with self.assertRaises(ValueError):
            self.g.emitir("XX", "N")
        with self.assertRaises(ValueError):
            self.g.emitir("CG", "X")
        with self.assertRaises(ValueError):
            self.g.estimativa("CG-N999")


if __name__ == "__main__":
    unittest.main()
