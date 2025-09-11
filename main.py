from flask import Flask, render_template, request, flash, redirect, url_for
import fdb

app = Flask(__name__)
app.secret_key = 'OI'

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\1-09.FDB'
user = 'SYSDBA'
pasword = 'sysdba'

con = fdb.connect(host=host, database=database,user=user, password=pasword)

@app.route('/')
def index():
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
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)