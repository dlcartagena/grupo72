from flask import Flask, request, json, render_template
from bson.objectid import ObjectId
from pymongo import MongoClient
import atexit
import subprocess
import os

app = Flask(__name__)
mongod = subprocess.Popen('mongod', stdout=subprocess.DEVNULL)
atexit.register(mongod.kill)
client = MongoClient('localhost')
db = client["entrega4db"]
usuarios = db.users
mensajes = db.messages


@app.route("/")  # Solicitud del tipo GET
def home():
    return "Web API Grupo 72"

@app.route("/api/v1/messages")
def get_messages():
    resultados = [u for u in mensajes.find({})]
    for i in resultados:
        i['_id'] = str(i['_id'])
    return json.jsonify(resultados)


@app.route("/api/v1/messages/<mid>")
def get_message(mid):
    mensaje = list(mensajes.find({"_id":ObjectId(mid)}))
    for i in mensaje:
        i['_id'] = str(i['_id'])
    return json.jsonify(mensaje)


if __name__ == "__main__":
    app.run(debug=True)

if os.name == 'nt':
    app.run()
