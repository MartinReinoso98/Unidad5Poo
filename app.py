from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import database, trabajador, registrohorario
from flask_sqlalchemy import SQLAlchemy


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

        # Verificar que el trabajador exista
        trabajador_existente = trabajador.query.filter_by(legajo=legajo, dni=dni).first()
        
        if trabajador_existente:
            # Crear registro de horario asociado al trabajador
            nueva_entrada = registrohorario(
                fecha=datetime.now().date(),
                horaentrada=datetime.now(),
                horasalida=None, 
                dependencia="DO1",
                idtrabajador=trabajador_existente.id
            )
            database.session.add(nueva_entrada)
            database.session.commit()
            return render_template('anuncio.html', anuncio="Nueva entrada registrada")
        else:
            return render_template('error.html', error="Trabajador no registrado en la base de datos")
        return render_template('anuncio.html', anuncio="Nueva entrada registrada")

    # GET - mostrar formulario
    return render_template('formulario.html')


if __name__ == '__main__':
    with app.app_context():
        database.create_all()
    app.run(debug = True)
        
    
