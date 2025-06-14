from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import database, trabajador, registrohorario
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')


#FUNCIONALIDAD 1        
@app.route('/templates/formulario.html', methods=['GET', 'POST'])
def verificar_entrada():
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        dni = str(request.form.get('dni_4'))

        # Validar campos
        if not legajo or not dni:
            return render_template('error.html', error="Todos los campos son obligatorios")

        # Verificar que el trabajador exista
        trabajador_existente = trabajador.query.filter(
            trabajador.legajo == legajo,
            trabajador.dni.like(f"%{dni}")
        ).first()
        print("trabajador")
        print(trabajador_existente)
        if trabajador_existente:
            #verificar
            fecha_actual = datetime.today().date()
            print("trabajdor:",trabajador_existente.id)
            registro_existente = registrohorario.query.filter_by(
                idtrabajador=trabajador_existente.id,
                fecha=fecha_actual
            ).first()
            print(f"hay un registro:{registro_existente}")

            if registro_existente:
                return render_template('error.html', error="Ya se registró una entrada para hoy")
            else:
                # Crear registro de horario asociado al trabajador
                hora_actual = datetime.now().time()
                fecha_actual = datetime.today().date()

                nueva_entrada = registrohorario(
                    fecha=fecha_actual,
                    horaentrada=hora_actual,
                    horasalida=None,
                    dependencia="DO1",
                    idtrabajador=trabajador_existente.id
                )
                database.session.add(nueva_entrada)
                database.session.commit()
                return render_template('anuncio.html', anuncio="Nueva entrada registrada")

        else:
            return render_template('error.html', error="Trabajador no registrado en la base de datos")

            #GET - mostrar formulario
    return render_template('formulario.html')


#FUNCIONALIDAD 2   
@app.route('/templates/formulario.html', methods=['GET', 'POST'])
def verificar_salida():
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        dni = str(request.form.get('dni_4'))

        # Validar campos
        if not legajo or not dni:
            return render_template('error.html', error="Todos los campos son obligatorios")

        # Verificar que el trabajador exista
        trabajador_existente = trabajador.query.filter(
            trabajador.legajo == legajo,
            trabajador.dni.like(f"%{dni}")
        ).first()

        print("trabajador")
        print(trabajador_existente)
        if trabajador_existente:   #si trabajador es distinto de None
            
            fecha_actual = datetime.today().date()  #guarda la fehca de hoy 
            print("trabajdor:",trabajador_existente.id)  #Imprime en consola el ID del trabajador que se encontró previamente en la base de datos. Verifica que trabajador_existente contiene un objeto válido
            registro_existente = registrohorario.query.filter_by(  #Busca en la tabla registrohorario registros que cumplan las dos condiciones
                idtrabajador=trabajador_existente.id,
                fecha=fecha_actual
            ).first() # La funcion first() Retorna el primer registro que cumpla las condiciones o None si no existe
            print(f"hay un registro:{registro_existente}")

            if registro_existente: # si ya hay un registro de estrada para el trabajador en la fecha actual 
                 # Crear registro de horario asociado al trabajador
                hora_actual = datetime.now().time()

                if registro_existente.horasalida == None:
                    nueva_entrada = registrohorario(
                        fecha = fecha_actual,
                        horaentrada = registro_existente.horaentrada, #No se debe modificar la hora de entrada
                        horasalida = hora_actual,
                        dependencia = "DO1", #modifcar debe acceder a los datos de la dependencia
                        idtrabajador = trabajador_existente.id
                    )
                    database.session.add(nueva_entrada)
                    database.session.commit()
                    return render_template('anuncio.html', anuncio="Horario de Salida registrada")
                else:
                    return render_template('error.html', error="Ya se registró una salida para hoy")
                
            else:
               return render_template('error.html', error="Aun no se ha registrado una entrada para hoy")

        else:
            return render_template('error.html', error="Trabajador no registrado en la base de datos")

            #GET - mostrar formulario
    return render_template('formulario.html')


'''

#FUNCIONALIDAD 3
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
    app.run(debug = True)
        
    
