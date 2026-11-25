"""Interface gráfica Tkinter do sistema de senhas."""
import tkinter as tk
from tkinter import ttk, messagebox

from filas import ESPECIALIDADES, CATEGORIAS, GerenciadorFilas


class AplicacaoClinica:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Clínica Médica | Gerenciamento de Senhas")
        self.raiz.geometry("1200x800")
        self.raiz.minsize(1000, 650)
        self.gerenciador = GerenciadorFilas()
        self.especialidade = tk.StringVar(value="CG")
        self.categoria = tk.StringVar(value="N")
        self.senha_consulta = tk.StringVar()
        self.status = tk.StringVar(value="Sistema pronto para emitir senhas.")
        self.ultima = tk.StringVar(value="Nenhuma senha chamada")
        self.detalhes_ultima = tk.StringVar(value="Especialidade: — | Categoria: —")
        self.quantidade_total = tk.StringVar(value="Total aguardando: 0")
        self.painel_tv = None
        self.indicadores = {}
        self._montar()
        self._atualizar()

    def _montar(self):
        self.raiz.configure(bg="#eef2f7")
        estilo = ttk.Style()
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("TFrame", background="#eef2f7")
        estilo.configure("TLabel", background="#eef2f7", foreground="#17324d", font=("Arial", 11))
        estilo.configure("TLabelframe", background="#eef2f7")
        estilo.configure("TLabelframe.Label", background="#eef2f7", foreground="#17324d")
        estilo.configure("TButton", font=("Arial", 11, "bold"), padding=9)
        estilo.configure("Acao.TButton", background="#087f8c", foreground="white")
        estilo.map("Acao.TButton", background=[("active", "#05616b")])
        estilo.configure("Treeview", rowheight=29, font=("Arial", 10), background="white", fieldbackground="white")
        estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#dbe7ef")
        estilo.configure("Titulo.TLabel", font=("Arial", 22, "bold"), background="#eef2f7")
        estilo.configure("Painel.TLabelframe", padding=12)
        estilo.configure("Painel.TLabelframe.Label", font=("Arial", 11, "bold"))
        estilo.configure("Destaque.TLabel", font=("Arial", 21, "bold"))

        conteudo = ttk.Frame(self.raiz, padding=16)
        conteudo.pack(fill="both", expand=True)
        cabecalho = tk.Frame(conteudo, bg="#17324d", padx=18, pady=15)
        cabecalho.pack(fill="x", pady=(0, 12))
        tk.Label(cabecalho, text="CLÍNICA MÉDICA  |  Central de atendimento", bg="#17324d", fg="white", font=("Arial", 21, "bold")).pack(side="left")
        ttk.Button(cabecalho, text="Abrir painel TV", command=self._abrir_tv).pack(side="right")
        cards = ttk.Frame(conteudo)
        cards.pack(fill="x", pady=(0, 12))
        for sigla, nome in ESPECIALIDADES.items():
            card = tk.Frame(cards, bg="white", padx=15, pady=10, highlightbackground="#cbdbe5", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=4)
            tk.Label(card, text=nome, bg="white", fg="#17324d", font=("Arial", 12, "bold")).pack(anchor="w")
            self.indicadores[sigla] = tk.StringVar()
            tk.Label(card, textvariable=self.indicadores[sigla], bg="white", fg="#087f8c", font=("Arial", 13)).pack(anchor="w")

        operacoes = ttk.LabelFrame(conteudo, text="Emissão e chamada", style="Painel.TLabelframe")
        operacoes.pack(fill="x", pady=(0, 10))
        ttk.Label(operacoes, text="Especialidade:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        especialidades = ttk.Combobox(operacoes, state="readonly", width=24,
                                     values=list(ESPECIALIDADES.values()))
        especialidades.current(0)
        especialidades.grid(row=0, column=1, sticky="w", pady=5)
        especialidades.bind("<<ComboboxSelected>>", lambda _evento: self._mudar_especialidade(especialidades.current()))

        ttk.Label(operacoes, text="Categoria:").grid(row=0, column=2, padx=(20, 8), sticky="w")
        ttk.Radiobutton(operacoes, text="Normal", variable=self.categoria, value="N").grid(row=0, column=3, sticky="w")
        ttk.Radiobutton(operacoes, text="Preferencial", variable=self.categoria, value="P").grid(row=0, column=4, sticky="w")
        ttk.Button(operacoes, text="Emitir senha", style="Acao.TButton", command=self._emitir).grid(row=1, column=1, sticky="ew", pady=10)
        ttk.Button(operacoes, text="Chamar próxima", style="Acao.TButton", command=self._chamar).grid(row=1, column=3, columnspan=2, sticky="ew", pady=10)

        painel = ttk.LabelFrame(conteudo, text="Painel de atendimento", style="Painel.TLabelframe")
        painel.pack(fill="x", pady=(0, 10))
        ttk.Label(painel, text="ÚLTIMA SENHA CHAMADA").pack(anchor="center")
        ttk.Label(painel, textvariable=self.ultima, style="Destaque.TLabel").pack()
        ttk.Label(painel, textvariable=self.detalhes_ultima).pack(pady=(0, 6))
        ttk.Label(painel, textvariable=self.quantidade_total).pack(anchor="w")

        meio = ttk.Frame(conteudo)
        meio.pack(fill="both", expand=True, pady=(0, 10))
        filas_frame = ttk.LabelFrame(meio, text="Filas de espera por especialidade", style="Painel.TLabelframe")
        filas_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.tabela = ttk.Treeview(filas_frame, columns=("especialidade", "categoria", "senha", "espera"), show="headings", height=9)
        for coluna, titulo, largura in (("especialidade", "Especialidade", 150),
                                         ("categoria", "Categoria", 100), ("senha", "Senha", 105), ("espera", "Espera", 80)):
            self.tabela.heading(coluna, text=titulo)
            self.tabela.column(coluna, width=largura, anchor="center")
        barra = ttk.Scrollbar(filas_frame, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.tabela.pack(fill="both", expand=True)
        self.tabela.tag_configure("P", background="#e0f4f2")
        self.tabela.tag_configure("N", background="#ffffff")

        historico_frame = ttk.LabelFrame(meio, text="Histórico de chamadas", style="Painel.TLabelframe")
        historico_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.historico_lista = tk.Listbox(historico_frame, height=9, font=("Arial", 10))
        barra_h = ttk.Scrollbar(historico_frame, orient="vertical", command=self.historico_lista.yview)
        self.historico_lista.configure(yscrollcommand=barra_h.set)
        barra_h.pack(side="right", fill="y")
        self.historico_lista.pack(fill="both", expand=True)

        consulta = ttk.LabelFrame(conteudo, text="Consultar estimativa de espera", style="Painel.TLabelframe")
        consulta.pack(fill="x", pady=(0, 10))
        ttk.Label(consulta, text="Senha:").pack(side="left", padx=(0, 8))
        ttk.Entry(consulta, textvariable=self.senha_consulta, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(consulta, text="Consultar", command=self._consultar).pack(side="left")
        ttk.Label(conteudo, textvariable=self.status, foreground="#185a8d", wraplength=880).pack(anchor="w")

    def _mudar_especialidade(self, indice):
        self.especialidade.set(list(ESPECIALIDADES)[indice])

    def _emitir(self):
        try:
            senha = self.gerenciador.emitir(self.especialidade.get(), self.categoria.get())
            espera = self.gerenciador.estimativa(senha)
            self.senha_consulta.set(senha)
            self.status.set(f"Senha emitida: {senha} | Estimativa atual: {espera} minutos.")
            self._atualizar()
        except ValueError as erro:
            messagebox.showerror("Erro na emissão", str(erro))

    def _chamar(self):
        try:
            registro = self.gerenciador.chamar(self.especialidade.get())
            self.ultima.set(registro["senha"])
            self.detalhes_ultima.set(f"Especialidade: {registro['especialidade']} | Categoria: {registro['categoria']}")
            self.status.set(f"Senha {registro['senha']} chamada às {registro['horario']}.")
            self._atualizar()
        except ValueError as erro:
            messagebox.showwarning("Fila vazia", str(erro))

    def _consultar(self):
        try:
            senha = self.senha_consulta.get().strip().upper()
            if not senha:
                raise ValueError("Digite uma senha para consultar.")
            espera = self.gerenciador.estimativa(senha)
            self.status.set(f"Senha {senha}: estimativa atual de {espera} minutos até a chamada.")
        except ValueError as erro:
            messagebox.showwarning("Consulta inválida", str(erro))

    def _atualizar(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for sigla, nome in ESPECIALIDADES.items():
            for categoria in ("P", "N"):
                for senha in self.gerenciador.filas[sigla][categoria]:
                    self.tabela.insert("", "end", values=(nome, CATEGORIAS[categoria], senha, f"{self.gerenciador.estimativa(senha)} min"), tags=(categoria,))
        self.quantidade_total.set(f"Total aguardando: {self.gerenciador.quantidade()}")
        for sigla, var in self.indicadores.items():
            filas = self.gerenciador.filas[sigla]
            var.set(f"{len(filas['N'])} normais  |  {len(filas['P'])} preferenciais")
        if self.painel_tv is not None and self.painel_tv.winfo_exists():
            self._atualizar_tv()
        self.historico_lista.delete(0, tk.END)
        for registro in reversed(self.gerenciador.historico):
            self.historico_lista.insert(tk.END, f"{registro['senha']} | {registro['especialidade']} | {registro['horario']}")

    def _abrir_tv(self):
        """Abre uma janela de chamadas sincronizada com a central."""
        if self.painel_tv is not None and self.painel_tv.winfo_exists():
            self.painel_tv.lift()
            return
        self.painel_tv = tk.Toplevel(self.raiz)
        self.painel_tv.title("Clínica Médica | Painel de chamadas")
        self.painel_tv.geometry("900x550")
        self.painel_tv.configure(bg="#17324d")
        tk.Label(self.painel_tv, text="PAINEL DE ATENDIMENTO", bg="#17324d", fg="white", font=("Arial", 25, "bold")).pack(pady=25)
        tk.Label(self.painel_tv, textvariable=self.ultima, bg="#17324d", fg="#7ce5d8", font=("Arial", 48, "bold"), wraplength=850).pack(pady=20)
        tk.Label(self.painel_tv, textvariable=self.detalhes_ultima, bg="#17324d", fg="white", font=("Arial", 17)).pack(pady=10)
        tk.Label(self.painel_tv, textvariable=self.quantidade_total, bg="#17324d", fg="white", font=("Arial", 17)).pack(pady=10)
        self.tv_filas = tk.Listbox(self.painel_tv, font=("Arial", 13), bg="#ffffff", fg="#17324d", height=6)
        self.tv_filas.pack(fill="both", expand=True, padx=35, pady=15)
        self._atualizar_tv()

    def _atualizar_tv(self):
        self.tv_filas.delete(0, tk.END)
        for sigla, nome in ESPECIALIDADES.items():
            for senha in self.gerenciador.aguardando(sigla):
                self.tv_filas.insert(tk.END, f"{nome}  |  {senha}")
