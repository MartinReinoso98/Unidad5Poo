from flask import Flask, request, render_template
from datetime import datetime
from models import database, trabajador, registrohorario

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.sqlite3'
database.init_app(app)

@app.route('/')
def inicio():
    return render_template('index.html')

    # <!--   FUNCIONALIDAD 1   -->
@app.route('/registrar-entrada', methods=['GET', 'POST'])
def registrar_entrada():
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        dni = str(request.form.get('dni_4'))
        dependencia = request.form.get('dependencia')
        
        # <!-- verifica los campos -->
        if not all([legajo, dni, dependencia]):
            return render_template('error.html', error="Todos los campos son obligatorios")

        # <!-- peticion a la bd -->
        trabajador_existente = trabajador.query.filter(
            trabajador.legajo == legajo,
            trabajador.dni.like(f"%{dni}")
        ).first()

        if not trabajador_existente:
            return render_template('error.html', error="Trabajador no registrado")

        # <!-- verifica si hay una entrada ya registrada -->
        fecha_actual = datetime.today().date()
        registro = registrohorario.query.filter_by(
            idtrabajador=trabajador_existente.id,
            fecha=fecha_actual
        ).first()

        if registro:
            return render_template('error.html', error="Ya registró su entrada hoy")

        # <!-- agrega a la bd una entrada -->
        nueva_entrada = registrohorario(
            fecha=fecha_actual,
            horaentrada=datetime.now().time(),
            horasalida=None,
            dependencia=dependencia,
            idtrabajador=trabajador_existente.id
        )
        database.session.add(nueva_entrada)
        database.session.commit()
        return render_template('anuncio.html', anuncio="Entrada registrada correctamente")
    
    return render_template('formulario.html', tipo='entrada')

    # <!--   FUNCIONALIDAD 2   -->
@app.route('/registrar-salida', methods=['GET', 'POST'])
def registrar_salida():
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        dni = str(request.form.get('dni_4'))
        dependencia = request.form.get('dependencia')
        
        # <!-- verifica los campos -->
        if not all([legajo, dni, dependencia]):
            return render_template('error.html', error="Todos los campos son obligatorios")

        # <!-- peticion a la bd -->
        trabajador_existente = trabajador.query.filter(
            trabajador.legajo == legajo,
            trabajador.dni.like(f"%{dni}")
        ).first()

        if not trabajador_existente:
            return render_template('error.html', error="Trabajador no registrado")

        # <!-- verifica si hay una salida ya registrada -->
        fecha_actual = datetime.today().date()
        registro = registrohorario.query.filter_by(
            idtrabajador=trabajador_existente.id,
            fecha=fecha_actual
        ).first()

        if not registro:
            return render_template('error.html', error="No hay entrada registrada para hoy")
        
        if registro.horasalida:
            return render_template('error.html', error="Ya registró su salida hoy")

        # <!-- agrega a la bd una salida (no hace falta el add porque ya esta en la bd) -->
        registro.horasalida = datetime.now().time()
        database.session.commit()
        return render_template('anuncio.html', anuncio="Salida registrada correctamente")
    
    return render_template('formulario.html', tipo='salida')

'''

    # <!--   FUNCIONALIDAD 3   -->
@app.route('/templates/consulta.html', methods=['GET'])
def consultarRegistroHorario(): 
     
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        dni = request.form.get('dni_4')
        # Verificar que el trabajador exista
        trabajador_existente = trabajador.query.filter_by(legajo=legajo, dni=dni).first()

        if not trabajador_existente:
            fecha_str = request.form.get('fecha')
    
            if not fecha_str:
                return render_template('error.html', error="Fecha requerida")
            
            dias = dias_desde_fecha(fecha_str)
            
            if dias is None:
                return render_template('error.html', error="Formato de fecha inválido. Use DD/MM/AAAA")
            
            else: 
                for i in range(len(dias)):
                    horaE = registrohorario[i].query.filter_by(horaentrada = request.form.get('horaentrada')).all()
                    horas = registrohorario[i].query.filter_by(horasalida = request.form.get('horasalida')).all()
                    if horaE != None and horas != None:
                        trabajado =  horas - horaE
                        print(dia, horas trabajadas)

                   
            
            return render_template('resultado.html', dias=dias)


'''

if __name__ == '__main__':
    with app.app_context():
        database.create_all()
    app.run(debug=True)
