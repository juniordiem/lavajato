import sqlite3
from datetime import datetime

def criar_banco_dados():
    conn = sqlite3.connect('lavajato.db')
    cursor = conn.cursor()
    
    # Tabela de Serviços
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL
    )
    ''')
    
    # Tabela de Veículos/Clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        contato TEXT,
        placa TEXT NOT NULL,
        marca TEXT,
        modelo TEXT,
        tipo_servico_id INTEGER,
        data_entrada TEXT NOT NULL,
        data_saida TEXT,
        status TEXT NOT NULL DEFAULT 'Em lavagem',
        valor_pago REAL,
        FOREIGN KEY (tipo_servico_id) REFERENCES servicos(id)
    )
    ''')
    
    # Inserir serviços básicos se a tabela estiver vazia
    cursor.execute('SELECT COUNT(*) FROM servicos')
    if cursor.fetchone()[0] == 0:
        servicos_iniciais = [
            ('Lavagem Simples', 30.00),
            ('Lavagem Completa', 50.00),
            ('Lavagem com Cera', 70.00),
            ('Polimento', 120.00),
            ('Lavagem de Motor', 40.00)
        ]
        cursor.executemany('INSERT INTO servicos (tipo, valor) VALUES (?, ?)', servicos_iniciais)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('lavajato.db')
    conn.row_factory = sqlite3.Row
    return conn