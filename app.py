import sqlite3
import os
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO ---
def conectar():
    return sqlite3.connect('sisvenda_cli.db')

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT, preco REAL, estoque INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto_id INTEGER, quantidade INTEGER,
                        valor_total REAL, data DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE, senha TEXT)''')
    try:
        cursor.execute("INSERT INTO usuarios (username, senha) VALUES ('admin', '1234')")
    except: pass
    conn.commit()
    conn.close()

# --- FUNÇÕES DE CADASTRO ---

def cadastrar_usuario():
    print("\n--- Cadastro de Novo Usuário ---")
    user = input("Nome de usuário: ")
    senha = input("Senha: ")
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, senha) VALUES (?, ?)", (user, senha))
        conn.commit()
        print("✔ Usuário cadastrado com sucesso!")
    except:
        print("✖ Erro: Este usuário já existe.")
    finally:
        conn.close()

def cadastrar_produto():
    print("\n--- Cadastro de Produto ---")
    nome = input("Nome do produto: ")
    preco = float(input("Preço: R$ "))
    estoque = int(input("Quantidade em estoque: "))
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    conn.commit()
    conn.close()
    print(f"✔ Produto '{nome}' cadastrado!")

# --- OPERAÇÕES ---

def realizar_venda():
    listar_produtos()
    try:
        id_p = int(input("\nID do produto para venda: "))
        qtd = int(input("Quantidade: "))
        
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("SELECT nome, preco, estoque FROM produtos WHERE id = ?", (id_p,))
        p = cursor.fetchone()
        
        if p and p[2] >= qtd:
            total = qtd * p[1]
            cursor.execute("INSERT INTO vendas (produto_id, quantidade, valor_total) VALUES (?, ?, ?)", (id_p, qtd, total))
            cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, id_p))
            conn.commit()
            print(f"✔ Venda concluída! Total: R$ {total:.2f}")
            # Gerar recibo TXT
            with open(f"venda_{datetime.now().strftime('%H%M%S')}.txt", "w") as f:
                f.write(f"RECIBO\nItem: {p[0]}\nQtd: {qtd}\nTotal: R$ {total:.2f}")
        else:
            print("✖ Estoque insuficiente ou produto não encontrado.")
        conn.close()
    except ValueError:
        print("✖ Entrada inválida.")

def listar_produtos():
    print("\n--- Estoque Atual ---")
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    for p in cursor.fetchall():
        print(f"ID: {p[0]} | Nome: {p[1]:<15} | Preço: R${p[2]:>7.2f} | Estoque: {p[3]}")
    conn.close()

# --- MENU PRINCIPAL ---

def menu_principal():
    while True:
        print("\n========================")
        print("    SISVENDA TERMINAL")
        print("========================")
        print("1. Realizar Venda")
        print("2. Cadastrar Produto")
        print("3. Listar Produtos / Estoque")
        print("4. Cadastrar Novo Usuário")
        print("5. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1': realizar_venda()
        elif opcao == '2': cadastrar_produto()
        elif opcao == '3': listar_produtos()
        elif opcao == '4': cadastrar_usuario()
        elif opcao == '5': break
        else: print("Opção inválida.")

# --- LOGIN SIMPLES ---
def login():
    print("--- LOGIN SISTEMA ---")
    u = input("Usuário: ")
    s = input("Senha: ")
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND senha=?", (u, s))
    if cursor.fetchone():
        conn.close()
        menu_principal()
    else:
        print("Acesso negado.")

if __name__ == "__main__":
    inicializar_banco()
    login()