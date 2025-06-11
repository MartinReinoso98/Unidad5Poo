from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import database, trabajador, registrohorario


app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')
        
@app.route('/templates/formulario.html', methods=['GET', 'POST'])
def registrar_entrada():
    if request.method == 'POST':
        legajo = request.form['legajo']
        dni = request.form['dni_4']

        # validar campos
        if not legajo or not dni:
            return render_template('error.html', error="Todos los campos son obligatorios")

        # verificar que el trabajador exista
        trabajador_existente = trabajador.query.filter_by(legajo=legajo, dni=dni).first()
        if not trabajador_existente:
            return render_template('error.html', error="Trabajador no registrado")

        # verificar si ya tiene una entrada hoy
        ultima_entrada = registrohorario.query.filter_by(legajo=legajo).order_by(registrohorario.fecha_hora.desc()).first()
        fecha_hoy = datetime.now().date()

        if ultima_entrada and ultima_entrada.fecha_hora.date() == fecha_hoy:
            return render_template('error.html', error="Ya se registró una entrada el día de hoy")

        # registrar la nueva entrada
        nueva_entrada = registrohorario(legajo=legajo, fecha_hora=datetime.now())
        database.session.add(nueva_entrada)
        database.session.commit()

        return render_template('anuncio.html', anuncio="Nueva entrada registrada")

    # GET - mostrar formulario
    return render_template('formulario.html')


if __name__ == '__main__':
    app.run(debug = True)
        
    
