from flask import Flask, request, render_template
from datetime import datetime, date
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

        # <!-- consulta a la bd -->
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

        # <!-- guarda la nueva entrada -->
        nueva_entrada = registrohorario(
            fecha=fecha_actual,
            horaentrada=datetime.now().time(),
            horasalida=None,
            dependencia=dependencia,
            idtrabajador=trabajador_existente.id
        )
        # <!-- agrega a la bd -->
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


# <!--   FUNCIONALIDAD 3   -->
@app.route('/consultar_registros', methods=['GET', 'POST'])
def consultar_registros():
    if request.method == 'POST':
        legajo = request.form.get('legajo')
        dni = str(request.form.get('dni_4'))
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        # <!-- verifica los campos -->
        if not all([legajo, dni, fecha_inicio, fecha_fin]):
            return render_template('error.html', error="Todos los campos son obligatorios")
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return render_template('error.html', error="Formato de fecha incorrecto (Usar Año-Mes-Día)")

        # <!-- consulta a la bd -->
        trabajador_existente = trabajador.query.filter(
            trabajador.legajo == legajo,
            trabajador.dni.like(f"%{dni}")
        ).first()

        if not trabajador_existente:
            return render_template('error.html', error="Trabajador no registrado")

        # <!-- consulta a la bd y ordena -->
        registros = registrohorario.query.filter(
            registrohorario.idtrabajador == trabajador_existente.id,
            registrohorario.fecha >= fecha_inicio,
            registrohorario.fecha <= fecha_fin
        ).order_by(registrohorario.fecha).all()
        
        # <!-- muestra html con los resultados -->
        return render_template('resultado_consulta.html', 
                            registros=registros,
                            trabajador=trabajador_existente,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin)
    
    return render_template('formulario.html', modo='consulta')


# <!--   FUNCIONALIDAD 4   --> 
@app.route('/informe/general', methods=['GET', 'POST'])
def informe_general():
    if request.method == 'POST':
        paso = request.form.get('paso', '1').strip()
        # <!-- paso 1 -->
        if paso == '1':
            legajo = request.form.get('legajo')
            dni_4 = request.form.get('dni_4')
            
            # <!-- verifica los campos -->
            if not legajo or not dni_4:
                return render_template('error.html', error="Todos los campos son obligatorios")
            
            # <!-- consulta a la bd -->
            admin = trabajador.query.filter_by(
                legajo=legajo,
                funcion='AD'
            ).first()
            
            if not admin:
                return render_template('error.html', error="Credencial de administrativo inválida")
            
            return render_template('formulario.html', paso=2, legajo=legajo, dni_4=dni_4)
        
        # <!-- paso 2 -->
        elif paso == '2':
            legajo = request.form.get('legajo')
            dni_4 = request.form.get('dni_4')
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            funcion = request.form.get('funcion', 'todas')
            dependencia = request.form.get('dependencia', 'todas')
            
            if not fecha_inicio or not fecha_fin:
                return render_template('error.html', error="Debe ingresar ambas fechas")
            
            registros = registrohorario.query.filter(
                registrohorario.fecha.between(fecha_inicio, fecha_fin)
            ).all()
            
            # <!-- recorre los registros traidos de la query -->
            resultados = []
            for registro in registros:
                trabajador_asociado = trabajador.query.get(registro.idtrabajador)

                horasTrabajadas = "vacio"
                if registro.horaentrada and registro.horasalida:
                    entrada_dt = datetime.combine(date.today(), registro.horaentrada)
                    salida_dt = datetime.combine(date.today(), registro.horasalida)
                    horasTrabajadas = str(salida_dt - entrada_dt) # <!-- calculo de horas -->

                # <!-- diccionario, agrega a la lista resultados -->
                resultados.append({
                    'apellido': trabajador_asociado.apellido,
                    'nombre': trabajador_asociado.nombre,
                    'fecha': registro.fecha.strftime('%Y-%m-%d'),
                    'entrada': registro.horaentrada.strftime('%H:%M'),
                    'salida': registro.horasalida.strftime('%H:%M'),
                    'horas_trabajadas': horasTrabajadas
                })

            # ordenar por apellido
            resultados.sort(key=lambda x: x['apellido']) # como es un dict no basta con __lt__ y sort, con la key se puede ordenar por el campo apellido
            
            # <!-- muestra html con los resultados -->
            return render_template('informeG.html',
                                   registros=resultados,
                                   fecha_inicio=fecha_inicio,
                                   fecha_fin=fecha_fin,
                                   funcion=funcion,
                                   dependencia=dependencia)
    
    return render_template('formulario.html', paso=1)

# <!--   FUNCIONALIDAD 5   --> 
@app.route('/informe/individual', methods=['GET', 'POST'])
def informe_individual():
    if request.method == 'POST':
        paso = request.form.get('paso', '1').strip()
        # <!-- paso 1 -->
        if paso == '1':
            legajo = request.form.get('legajo')
            dni_4 = request.form.get('dni_4')
            # <!-- verifica los campos -->
            if not legajo or not dni_4:
                return render_template('error.html', error="Todos los campos son obligatorios")
            
            # <!-- consulta a la bd si es administrativo-->
            admin = trabajador.query.filter_by(
                legajo=legajo,
                funcion='AD'
            ).first()
            if not admin:
                return render_template('error.html', error="Credencial de administrativo inválida")

            return render_template('formulario.html', paso=2, legajo=legajo, dni_4=dni_4)
        
        # <!-- paso 2 -->
        elif paso == '2':
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            dni_4 = request.form.get('dni_4')
            # <!-- valida campos -->
            if not fecha_inicio or not fecha_fin:
                return render_template('error.html', error="Debe ingresar ambas fechas")
            
            # <!-- consulta a la bd -->
            trabajador_existente = trabajador.query.filter(
                trabajador.dni.like(f"%{dni_4}")
            ).first()

        if not trabajador_existente:
            return render_template('error.html', error="Trabajador no encontrado")
        
        # <!-- obtiene registros del trabajador en el rango de fechas de la bd -->     
        registros = registrohorario.query.filter(
            registrohorario.idtrabajador == trabajador_existente.id,
            registrohorario.fecha >= fecha_inicio,
            registrohorario.fecha <= fecha_fin
        ).order_by(registrohorario.fecha).all()
        
        resultados = []
        total_horas = 0  # <!-- acumulador -->
        
        # <!-- recorre los registros traidos de la query -->
        for r in registros:
            horas_trabajadas = "vacio"
            if r.horaentrada and r.horasalida:
                entrada_dt = datetime.combine(date.today(), r.horaentrada)
                salida_dt = datetime.combine(date.today(), r.horasalida)
                duracion = salida_dt - entrada_dt

                horas_trabajadas = str(duracion)
                total_horas += duracion.total_seconds()
                
            # <!-- diccionario, agrega a la lista -->
            resultados.append({
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'entrada': r.horaentrada.strftime('%H:%M'),
                'salida': r.horasalida.strftime('%H:%M'),
                'horas_trabajadas': horas_trabajadas
            })
            
        # <!-- ordenar por fecha ascendente -->
        resultados.sort(key=lambda x: x['fecha'])

        # <!-- convertir a horas (segundos) -->
        horas = int(total_horas // 3600)
        minutos = int((total_horas % 3600) // 60)
        horas_convertidas = f"{horas:02d}:{minutos:02d}"

        # <!-- muestra html con los resultados -->
        return render_template(
            'informeI.html',
            registros=resultados,
            trabajador=trabajador_existente,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            horas_totales=horas_convertidas
        )

    return render_template('formulario.html', paso=1)

if __name__ == '__main__':
    with app.app_context():
        database.create_all()
    app.run(debug=True)
