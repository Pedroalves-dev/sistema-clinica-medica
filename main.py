"""Ponto de entrada da aplicação."""
import tkinter as tk
from interface import AplicacaoClinica


def main():
    raiz = tk.Tk()
    AplicacaoClinica(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
