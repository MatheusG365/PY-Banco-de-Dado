from flask import Flask, render_template, request, flash, redirect, url_for, send_file
import fdb
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'OI'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\Lumi-re\PY-Banco-de-Dado\1-09.FDB'
user = 'SYSDBA'
pasword = 'sysdba'

con = fdb.connect(host=host, database=database,user=user, password=pasword)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("SELECT p.ID_PESSOA, p.NOME, p.EMAIL FROM PESSOA p")
    usuarios = cursor.fetchall()

    cursor.close()

    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/login')
def login():
    return render_template('login.html', titulo="Login")

@app.route('/logar', methods=['POST'])
def logar():
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute("SELECT p.email, p.senha FROM PESSOA p WHERE p.email = ?", (email,))
        usuario = cursor.fetchone()
        if usuario :
            if senha == usuario[1]:
                flash("Login realizado com sucesso")
                return redirect(url_for('livros'))

    finally:
        cursor.close
    flash("Senha ou email incorreto")
    return redirect(url_for('login'))

@app.route('/cadatrar')
def cadastrar():
    return render_template('cadastro.html', titulo="Cadastro")

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()

        try:
            cursor.execute('Select 1 from PESSOA p where p.EMAIL = ?', (email,))
            if cursor.fetchone(): #se existir algum usuario com o email passado
                flash("Erro: Email já cadastrado", 'error')
                return redirect(url_for('login'))

            cursor.execute('INSERT INTO PESSOA ( NOME, EMAIL, SENHA)VALUES (?,?, ?)', (nome, email, senha))
            con.commit()
        finally:
            cursor.close()
        flash('Usuario cadastrado com sucesso', 'success')
    return redirect(url_for('login'))

@app.route('/editarusuario')
def editarusuario():
    return render_template('editarusuario.html', titulo="Editar Usuario")

@app.route('/usuarioedit/<int:id>', methods=['GET', 'POST'])
def usuarioedit(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_PESSOA , NOME, EMAIL, SENHA FROM pessoa WHERE id_pessoa = ?", (id,))
    usuarios = cursor.fetchone()

    if not usuarios:
        cursor.close()
        flash('Usuario não encontrado')
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        cursor.execute('update pessoa set nome = ?, email = ?, senha= ? where id_pessoa = ?',
                       (nome, email, senha, id))

        con.commit()
        flash('Usuario atulizado com sucesso')
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editarusuario.html', usuario=usuarios, titulo='Editar Usuario')

@app.route('/delete2/<int:id>', methods=['POST'])
def delete2(id):
    cursor = con.cursor()  # Abre o cursor
    try:
        cursor.execute('delete from pessoa where id_pessoa = ?', (id,))
        con.commit()
        flash('Usuario removido com sucesso')

    except Exception as e:
        con.rollback()
        flash('Erro ao delete o usuario')
    finally:
        cursor.close()
        return redirect(url_for('index'))

@app.route('/livros')
def livros():
    cursor = con.cursor()
    cursor.execute("SELECT l.ID_LIVRO, l.TITULO, l.AUTOR, l.ANO_PUBLICADO FROM LIVRO l")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('livros.html', livros=livros)

@app.route("/novo")
def novo():
    return render_template('novo.html', titulo="Novo Livro")

@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM LIVRO l WHERE l.TITULO = ?', (titulo,))
        if cursor.fetchone(): #se existir algum livro com o titulo passado
            flash("Erro: Livro já cadastrado", 'error')
            return redirect(url_for('novo'))

        cursor.execute(''' INSERT INTO LIVRO (TITULO, AUTOR, ANO_PUBLICADO)
                           VALUES (?, ?, ?)''', (titulo, autor, ano_publicacao))

        con.commit()
    finally:
        cursor.close()
    flash('Livro cradastrado com sucesso', 'success')
    return  redirect(url_for('index'))

@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo="Editar Livro")

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor=con.cursor() # abre cursor
    cursor.execute('SELECT id_livro, titulo, autor, ano_publicado FROM LIVRO where id_livro = ?',(id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash('Livro não encontrado')
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicacao']

        cursor.execute('update livro set titulo = ?, autor = ?, ano_publicado= ? where id_livro = ?',
                       (titulo, autor, ano_publicado, id))

        con.commit()
        flash('Livro atualizado com sucesso')
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cursor = con.cursor()  # Abre o cursor
    try:
        cursor.execute('delete from livro where id_livro = ?', (id,))
        con.commit()
        flash('Livro removido com sucesso')

    except Exception as e:
        con.rollback()
        flash('Erro ao delete o livro')
    finally:
        cursor.close()
        return redirect(url_for('livros'))


## PDF Generation Route (Optional)
@app.route('/livros/relatorio', methods=['GET']) 
def relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicado FROM livro")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')

    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha

    pdf.set_font("Arial", size=12)
    for livro in livros:    
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)

    contador_livros = len(livros)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')

    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')     


if __name__ == '__main__':
    app.run(debug=True)
