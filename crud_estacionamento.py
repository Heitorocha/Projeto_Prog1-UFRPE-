import tkinter as tk
from tkinter import messagebox, simpledialog
import os

# ======================== ESTILO GLOBAL ========================
BG_PRINCIPAL = "#1a002b"
BG_CARD = "#2d004d"
FG_TEXTO = "#e5d4ff"
BOTAO_BG = "#7a15ff"
BOTAO_BG_HOVER = "#6a0fe0"
BOTAO_TEXTO = "white"
FONT_PADRAO = ("Arial", 12)
FONT_TITULO = ("Arial", 18, "bold")

# ======================== FUNÇÃO HOVER ========================
def aplicar_hover(botao):
    botao.bind("<Enter>", lambda e: botao.config(bg=BOTAO_BG_HOVER))
    botao.bind("<Leave>", lambda e: botao.config(bg=BOTAO_BG))

# ===============   CRUD EM ARQUIVO TXT   ==================
class EstacionamentoCRUD:
    def _init_(self, arquivo="veiculos.txt"):
        self.arquivo = arquivo

        # cria o arquivo se não existir
        if not os.path.exists(self.arquivo):
            with open(self.arquivo, "w"):
                pass

    # CREATE
    def adicionar(self, placa, valor_fixo, valor_hora):
        placa = placa.upper()
        veiculos = self.ler_todos()

        # Verifica se placa já existe
        for v in veiculos:
            if v["placa"] == placa:
                return False, "Essa placa já existe."

        # Salva no formato: placa;fixo;hora
        with open(self.arquivo, "a") as f:
            f.write(f"{placa};{valor_fixo};{valor_hora}\n")

        return True, "Veículo adicionado com sucesso."
    
    # READ
    def ler_todos(self):
        veiculos = []
        with open(self.arquivo, "r") as f:
            for linha in f:
                if linha.strip():
                    placa, fixo, hora = linha.strip().split(";")
                    veiculos.append({
                        "placa": placa,
                        "fixo": float(fixo),
                        "hora": float(hora)
                    })
        return veiculos
    
    # UPDATE
    def atualizar(self, placa_antiga, nova_placa):
        placa_antiga = placa_antiga.upper()
        nova_placa = nova_placa.upper()

        veiculos = self.ler_todos()

        # Verifica se placa atual existe
        registro = None
        for v in veiculos:
            if v["placa"] == placa_antiga:
                registro = v
                break

        if not registro:
            return False, "Placa atual não encontrada."

        # Verifica se nova placa já existe
        for v in veiculos:
            if v["placa"] == nova_placa:
                return False, "A nova placa já existe."

        # Atualiza placa mantendo valores individuais
        registro["placa"] = nova_placa

        self.salvar_lista(veiculos)
        return True, "Placa atualizada com sucesso."

    # DELETE
    def remover(self, placa, horas):
        placa = placa.upper()
        veiculos = self.ler_todos()

        registro = None
        for v in veiculos:
            if v["placa"] == placa:
                registro = v
                break

        if not registro:
            return False, "Veículo não encontrado."

        veiculos = [v for v in veiculos if v["placa"] != placa]
        self.salvar_lista(veiculos)

        # Calcula total com valores individuais gravados
        valor_total = registro["fixo"] + registro["hora"] * horas

        return True, valor_total
    
    # WRITE
    def salvar_lista(self, lista):
        with open(self.arquivo, "w") as f:
            for v in lista:
                f.write(f"{v['placa']};{v['fixo']};{v['hora']}\n")

# ===============   INTERFACE GRÁFICA   ====================
class EstacionamentoGUI:
    def _init_(self, root):
        self.root = root
        self.root.title("Estacionamento - Interface Gráfica")
        self.root.geometry("420x450")
        self.root.configure(bg=BG_PRINCIPAL)

        # Instancia o CRUD
        self.crud = EstacionamentoCRUD()

        frame = tk.Frame(root, padx=25, pady=25, bg=BG_CARD)
        frame.pack(pady=40)

        titulo = tk.Label(frame, text="Painel do Estacionamento",
                          font=FONT_TITULO, fg=FG_TEXTO, bg=BG_CARD)
        titulo.pack(pady=10)

        botoes = [
            ("Adicionar Veículo", self.adicionar),
            ("Remover Veículo", self.remover),
            ("Listar Veículos", self.listar),
            ("Atualizar Placa", self.atualizar),
            ("Sair", root.quit)
        ]

        for texto, comando in botoes:
            b = tk.Button(frame, text=texto, font=FONT_PADRAO, width=25,
                          bg=BOTAO_BG, fg=BOTAO_TEXTO,
                          activebackground=BOTAO_BG_HOVER,
                          command=comando)
            b.pack(pady=6)
            aplicar_hover(b)

    # ------------- GUI chama o CRUD -----------------
    def adicionar(self):
        placa = simpledialog.askstring("Adicionar", "Digite a placa:")
        if not placa:
            return

        valor_fixo = simpledialog.askfloat("Valor Fixo", "Digite o valor fixo:")
        if valor_fixo is None:
            return

        valor_hora = simpledialog.askfloat("Valor por Hora", "Digite o valor por hora:")
        if valor_hora is None:
            return

        sucesso, msg = self.crud.adicionar(placa, valor_fixo, valor_hora)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
        else:
            messagebox.showerror("Erro", msg)

    def remover(self):
        placa = simpledialog.askstring("Remover", "Digite a placa:")
        if not placa:
            return

        veiculos = self.crud.ler_todos()
        placas_existentes = [v["placa"] for v in veiculos]

        if placa.upper() not in placas_existentes:
            messagebox.showerror("Erro", "Veículo não encontrado.")
            return

        horas = simpledialog.askfloat("Horas", "Tempo estacionado (horas):")
        if horas is None:
            return

        sucesso, resultado = self.crud.remover(placa, horas)

        if sucesso:
            messagebox.showinfo("Total", f"Valor a pagar: R$ {resultado:.2f}")
        else:
            messagebox.showerror("Erro", resultado)

    def listar(self):
        veiculos = self.crud.ler_todos()
        if not veiculos:
            messagebox.showinfo("Lista", "Nenhum veículo cadastrado.")
            return
        
        texto = ""
        for v in veiculos:
            texto += f"{v['placa']} - Fixo: R${v['fixo']:.2f} / Hora: R${v['hora']:.2f}\n"
        
        messagebox.showinfo("Veículos", texto)

    def atualizar(self):
        atual = simpledialog.askstring("Atualizar", "Placa atual:")
        if not atual:
            return

        nova = simpledialog.askstring("Nova Placa", "Digite a nova placa:")
        if not nova:
            return

        sucesso, msg = self.crud.atualizar(atual, nova)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
        else:
            messagebox.showerror("Erro", msg)

# ======================== LOGIN ============================
class LoginScreen:
    def _init_(self, root):
        self.root = root
        self.root.title("Login - Estacionamento")
        self.root.geometry("350x320")
        self.root.configure(bg=BG_PRINCIPAL)

        frame = tk.Frame(root, padx=25, pady=25, bg=BG_CARD)
        frame.pack(pady=40)

        title = tk.Label(frame, text="Acesso ao Sistema",
                         font=FONT_TITULO, fg=FG_TEXTO, bg=BG_CARD)
        title.pack(pady=10)

        tk.Label(frame, text="Usuário", fg=FG_TEXTO, bg=BG_CARD, font=FONT_PADRAO).pack(anchor="w")
        self.usuario = tk.Entry(frame, font=FONT_PADRAO, width=25)
        self.usuario.pack(pady=5)

        tk.Label(frame, text="Senha", fg=FG_TEXTO, bg=BG_CARD, font=FONT_PADRAO).pack(anchor="w")
        self.senha = tk.Entry(frame, show="*", font=FONT_PADRAO, width=25)
        self.senha.pack(pady=5)

        b = tk.Button(frame, text="Entrar", font=FONT_PADRAO,
                      bg=BOTAO_BG, fg=BOTAO_TEXTO, width=20,
                      activebackground=BOTAO_BG_HOVER,
                      command=self.login)
        b.pack(pady=15)
        aplicar_hover(b)

        # Pressionar ENTER:
        root.bind("<Return>", lambda event: self.login())

    def login(self):
        if self.usuario.get() == "admin" and self.senha.get() == "123":
            self.root.destroy()
            main = tk.Tk()
            EstacionamentoGUI(main)
            main.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

# ======================== MAIN ============================
if _name_ == "_main_":
    login_root = tk.Tk()
    LoginScreen(login_root)
    login_root.mainloop()
