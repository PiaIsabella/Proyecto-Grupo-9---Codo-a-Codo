from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import mysql.connector.errorcode
from werkzeug.utils import secure_filename
import os
import time
app = Flask (__name__)
CORS(app)

class Catalogo:

    def __init__(self,host,user,password,database):
        self.conn = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database=database
        )
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS mascotas (codigo INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255) NOT NULL, edad VARCHAR(255) NOT NULL, descripcion VARCHAR(255) NOT NULL, imagen_url VARCHAR(255))''')
        self.conn.commit()
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_mascotas(self):
        self.cursor.execute("SELECT * FROM mascotas")
        mascotas = self.cursor.fetchall()
        return mascotas

    def consultar_mascota(self, codigo):
        self.cursor.execute(f"SELECT * FROM mascotas WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def mostrar_mascota(self, codigo):
        mascota = self.consultar_mascota(codigo)
        if mascota:
            print('=' * 40)
            print (f"Codigo..........: {mascota['codigo']}")
            print (f"Nombre..........: {mascota['nombre']}")
            print (f"Edad............: {mascota['edad']}")
            print (f"Descripción.....: {mascota['descripcion']}")
            print (f"Imagen..........: {mascota['imagen_url']}")
            print('=' * 50 )
        else:
            print("Producto no encontrado.")

    def agregar_mascota(self,nombre,edad,descripcion,imagen):
        sql = "INSERT INTO mascotas (nombre,edad,descripcion,imagen_url) VALUES (%s, %s, %s, %s)"
        valores = (nombre, edad, descripcion, imagen)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.lastrowid

    def modificar_mascota(self,codigo,nuevo_nombre,nueva_edad,nueva_descripcion,nueva_imagen):
        sql = "UPDATE mascotas SET nombre = %s, edad = %s, descripcion = %s, imagen_url = %s WHERE codigo = %s"
        valores = (nuevo_nombre, nueva_edad, nueva_descripcion, nueva_imagen, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def eliminar_mascota(self, codigo):
        self.cursor.execute(f"DELETE FROM mascotas WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

catalogo = Catalogo(host='localhost', user='root', password='', database='miapp')
ruta_destino = './static/imagenes/'

@app.route("/mascotas", methods=["GET"])
def listar_mascotas():
    mascotas = catalogo.listar_mascotas()
    return jsonify(mascotas)

@app.route("/mascotas/<int:codigo>", methods=["GET"])
def mostrar_mascota(codigo):
    mascota = catalogo.consultar_mascota(codigo)
    if mascota:
        return jsonify(mascota), 201
    else:
        return "Producto no encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)
