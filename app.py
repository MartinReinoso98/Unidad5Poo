from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import database, trabajador, registroHorario


app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')
        
@app.route('/registro', methods=['GET', 'POST'])
def registrar_entrada():
    if request.method == 'POST':
        legajo = request.form['legajo']
        dni4 = request.form['dni']
        dependencia = request.form['dependencia']

        if not legajo or not dni4 or not dependencia:
            return render_template('error.html', error="Todos los campos son obligatorios")

        # verifica que el trabajador exista
        trabajador_existente = trabajador.query.filter_by(legajo_e=legajo).first() # si o si se tiene que filtrar por legajo, dni y dependencia? para asegurarme que ese legajo tenga el dni que se ingreso
        if not trabajador_existente:
            return render_template('error.html', error="Trabajador no registrado")

        # verifica si ya tiene una entrada para hoy (no se como hacerlo)
        pass
    
    

        # registra una entrada
        nueva_entrada = registroHorario(legajo_e=legajo, fecha_hora=datetime.now())
        database.session.add(nueva_entrada)
        database.session.commit()
        return render_template('anuncio.html')


if __name__ == '__main__':
    app.run(debug = True)
        
    