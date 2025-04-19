from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3
import os
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key'

# Database initialization
db.criar_banco_dados()

# Context processor for current year
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# Global HEAD request handler
@app.before_request
def handle_head_request():
    if request.method == 'HEAD':
        return '', 200

# Routes
@app.route('/', methods=['GET', 'HEAD'])
def index():
    if request.method == 'HEAD':
        return '', 200
    return render_template('index.html')

@app.route('/servicos', methods=['GET'])
def servicos():
    conn = db.get_db_connection()
    servicos = conn.execute('SELECT * FROM servicos ORDER BY tipo').fetchall()
    conn.close()
    return render_template('servicos.html', servicos=servicos)

@app.route('/servicos/adicionar', methods=['POST'])
def adicionar_servico():
    try:
        tipo = request.form['tipo']
        valor = float(request.form['valor'])
        
        conn = db.get_db_connection()
        conn.execute('INSERT INTO servicos (tipo, valor) VALUES (?, ?)', (tipo, valor))
        conn.commit()
        conn.close()
        
        flash('Serviço adicionado com sucesso!', 'success')
        return redirect(url_for('servicos'))
    except Exception as e:
        flash(f'Erro ao adicionar serviço: {str(e)}', 'danger')
        return redirect(url_for('servicos'))

@app.route('/servicos/remover/<int:id>', methods=['GET'])
def remover_servico(id):
    try:
        conn = db.get_db_connection()
        conn.execute('DELETE FROM servicos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        flash('Serviço removido com sucesso!', 'success')
        return redirect(url_for('servicos'))
    except Exception as e:
        flash(f'Erro ao remover serviço: {str(e)}', 'danger')
        return redirect(url_for('servicos'))

@app.route('/veiculos', methods=['GET'])
def veiculos():
    conn = db.get_db_connection()
    veiculos = conn.execute('''
        SELECT v.*, s.tipo as servico_tipo, s.valor as servico_valor 
        FROM veiculos v LEFT JOIN servicos s ON v.tipo_servico_id = s.id
        WHERE v.data_saida IS NULL
        ORDER BY v.data_entrada
    ''').fetchall()
    servicos = conn.execute('SELECT * FROM servicos ORDER BY tipo').fetchall()
    conn.close()
    
    return render_template('veiculos.html', veiculos=veiculos, servicos=servicos)

@app.route('/veiculos/entrada', methods=['POST'])
def entrada_veiculo():
    try:
        dados = {
            'nome_cliente': request.form['nome_cliente'],
            'contato': request.form['contato'],
            'placa': request.form['placa'].upper(),
            'marca': request.form['marca'],
            'modelo': request.form['modelo'],
            'tipo_servico_id': int(request.form['tipo_servico']),
            'data_entrada': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Em lavagem'
        }
        
        conn = db.get_db_connection()
        conn.execute('''
            INSERT INTO veiculos 
            (nome_cliente, contato, placa, marca, modelo, tipo_servico_id, data_entrada, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(dados.values()))
        conn.commit()
        conn.close()
        
        flash('Veículo registrado com sucesso!', 'success')
        return redirect(url_for('veiculos'))
    except Exception as e:
        flash(f'Erro ao registrar veículo: {str(e)}', 'danger')
        return redirect(url_for('veiculos'))

@app.route('/veiculos/saida/<int:id>', methods=['POST'])
def saida_veiculo(id):
    try:
        status = request.form['status']
        valor_pago = float(request.form.get('valor_pago', 0))
        
        conn = db.get_db_connection()
        
        if status == 'Finalizado':
            data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute('''
                UPDATE veiculos 
                SET status = ?, data_saida = ?, valor_pago = ?
                WHERE id = ?
            ''', (status, data_saida, valor_pago, id))
        else:
            conn.execute('''
                UPDATE veiculos 
                SET status = ?
                WHERE id = ?
            ''', (status, id))
        
        conn.commit()
        conn.close()
        
        flash('Status do veículo atualizado!', 'success')
        return redirect(url_for('veiculos'))
    except Exception as e:
        flash(f'Erro ao atualizar status: {str(e)}', 'danger')
        return redirect(url_for('veiculos'))

@app.route('/relatorios', methods=['GET'])
def relatorios():
    try:
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        
        query = '''
            SELECT v.*, s.tipo as servico_tipo, s.valor as servico_valor 
            FROM veiculos v LEFT JOIN servicos s ON v.tipo_servico_id = s.id
            WHERE v.data_saida IS NOT NULL
        '''
        params = []
        
        if data_inicio and data_fim:
            query += ' AND v.data_entrada BETWEEN ? AND ?'
            params.extend([data_inicio, data_fim + ' 23:59:59'])
        elif data_inicio:
            query += ' AND v.data_entrada >= ?'
            params.append(data_inicio)
        elif data_fim:
            query += ' AND v.data_entrada <= ?'
            params.append(data_fim + ' 23:59:59')
        
        query += ' ORDER BY v.data_entrada DESC'
        
        conn = db.get_db_connection()
        registros = conn.execute(query, params).fetchall()
        total = conn.execute('SELECT SUM(valor_pago) FROM veiculos WHERE data_saida IS NOT NULL').fetchone()[0] or 0
        conn.close()
        
        return render_template('relatorios.html', 
                             registros=registros, 
                             total=total, 
                             data_inicio=data_inicio, 
                             data_fim=data_fim)
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'HEAD'])
def dashboard():
    if request.method == 'HEAD':
        return '', 200
        
    try:
        hoje = datetime.now().strftime('%Y-%m-%d')
        
        conn = db.get_db_connection()
        em_andamento = conn.execute('SELECT COUNT(*) FROM veiculos WHERE data_saida IS NULL').fetchone()[0]
        finalizados_hoje = conn.execute('''
            SELECT COUNT(*) FROM veiculos 
            WHERE DATE(data_saida) = ? AND status = 'Finalizado'
        ''', (hoje,)).fetchone()[0]
        faturamento_hoje = conn.execute('''
            SELECT SUM(valor_pago) FROM veiculos 
            WHERE DATE(data_saida) = ? AND status = 'Finalizado'
        ''', (hoje,)).fetchone()[0] or 0
        ultimos_servicos = conn.execute('''
            SELECT v.placa, v.nome_cliente, s.tipo as servico, v.data_entrada, v.data_saida, v.valor_pago
            FROM veiculos v LEFT JOIN servicos s ON v.tipo_servico_id = s.id
            WHERE v.data_saida IS NOT NULL
            ORDER BY v.data_saida DESC
            LIMIT 5
        ''').fetchall()
        conn.close()
        
        return render_template('dashboard.html', 
                            em_andamento=em_andamento,
                            finalizados_hoje=finalizados_hoje,
                            faturamento_hoje=faturamento_hoje,
                            ultimos_servicos=ultimos_servicos)
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)