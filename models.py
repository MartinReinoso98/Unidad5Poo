from sqlalchemy import Time, Date
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class trabajador(database.Model):
    __tablename__ = 'trabajador'
    id = database.Column(database.Integer, primary_key=True, nullable=False)
    nombre = database.Column(database.String(20), nullable=False)  # <!-- nullable hace que la columna no pueda tener NULL -->
    apellido = database.Column(database.String(20), nullable=False)
    dni = database.Column(database.String(10), nullable=False)
    correo = database.Column(database.String(30), nullable=False)
    legajo = database.Column(database.Integer, nullable=False)
    horas = database.Column(database.Integer, nullable=False)
    funcion = database.Column(database.String(2), nullable=False)   # <!-- 'AD' para administrativo, 'GE' para gerente, 'TE' para técnico -->
    registrohorario = database.relationship('registrohorario', backref='trabajador', cascade="all, delete-orphan")
    
    # <!-- sobrecarga -->
    def __lt__(self, otro):
        return (self.apellido) < (otro.apellido)
    
    
class registrohorario(database.Model):
    __tablename__ = 'registrohorario'
    id = database.Column(database.Integer, primary_key=True)
    fecha = database.Column(Date, nullable=False)
    horaentrada = database.Column(Time, nullable=False)
    horasalida = database.Column(Time, nullable=False)
    dependencia = database.Column(database.String(3), nullable=False)
    idtrabajador = database.Column(database.Integer, database.ForeignKey('trabajador.id'))
