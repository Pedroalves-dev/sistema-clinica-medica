"""Regras de negócio do gerenciamento de senhas da clínica."""
from collections import deque
from datetime import datetime

ESPECIALIDADES = {
    "CG": "Clínica Geral",
    "CA": "Cardiologia",
    "OR": "Ortopedia",
}
CATEGORIAS = {"P": "Preferencial", "N": "Normal"}
MINUTOS_POR_ATENDIMENTO = 30


class GerenciadorFilas:
    """Mantém seis filas FIFO: uma por especialidade e categoria."""

    def __init__(self):
        self.filas = {
            sigla: {"P": deque(), "N": deque()}
            for sigla in ESPECIALIDADES
        }
        self.contadores = {
            sigla: {"P": 0, "N": 0}
            for sigla in ESPECIALIDADES
        }
        self.historico = []

    def _validar_especialidade(self, especialidade):
        if especialidade not in ESPECIALIDADES:
            raise ValueError("Selecione uma especialidade válida.")

    def _validar_categoria(self, categoria):
        if categoria not in CATEGORIAS:
            raise ValueError("Selecione uma categoria válida.")

    def emitir(self, especialidade, categoria):
        """Emite senha única dentro da especialidade e categoria."""
        self._validar_especialidade(especialidade)
        self._validar_categoria(categoria)
        self.contadores[especialidade][categoria] += 1
        numero = self.contadores[especialidade][categoria]
        senha = f"{especialidade}-{categoria}{numero:03d}"
        self.filas[especialidade][categoria].append(senha)
        return senha

    def chamar(self, especialidade):
        """Atende preferenciais primeiro; FIFO em cada categoria."""
        self._validar_especialidade(especialidade)
        if self.filas[especialidade]["P"]:
            categoria = "P"
        elif self.filas[especialidade]["N"]:
            categoria = "N"
        else:
            raise ValueError("Não há pacientes aguardando nessa especialidade.")

        senha = self.filas[especialidade][categoria].popleft()
        registro = {
            "senha": senha,
            "especialidade": ESPECIALIDADES[especialidade],
            "categoria": CATEGORIAS[categoria],
            "horario": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        self.historico.append(registro)
        return registro

    def aguardando(self, especialidade=None):
        """Lista senhas na ordem de atendimento atual."""
        if especialidade is not None:
            self._validar_especialidade(especialidade)
            return (list(self.filas[especialidade]["P"]) +
                    list(self.filas[especialidade]["N"]))
        return {sigla: self.aguardando(sigla) for sigla in ESPECIALIDADES}

    def quantidade(self, especialidade=None):
        if especialidade is not None:
            return len(self.aguardando(especialidade))
        return sum(self.quantidade(sigla) for sigla in ESPECIALIDADES)

    def estimativa(self, senha):
        """Minutos até a chamada, supondo 1 profissional por especialidade.

        A posição é calculada na ordem atual; preferenciais emitidas no futuro
        podem alterar a espera de senhas normais.
        """
        if not isinstance(senha, str):
            raise ValueError("Informe uma senha válida.")
        for sigla in ESPECIALIDADES:
            fila = self.aguardando(sigla)
            if senha in fila:
                return fila.index(senha) * MINUTOS_POR_ATENDIMENTO
        raise ValueError("Senha não encontrada nas filas de espera.")

    def ultima_chamada(self):
        return self.historico[-1] if self.historico else None
