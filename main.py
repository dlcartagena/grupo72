from flask import Flask, request, json, render_template
from bson.objectid import ObjectId
from pymongo import MongoClient
import atexit
import subprocess
import os

app = Flask(__name__)
mongod = subprocess.Popen('mongod', stdout=subprocess.DEVNULL)
atexit.register(mongod.kill)
client = MongoClient('localhost', connect=False)
db = client["entrega4db"]
usuarios = db.users
mensajes = db.messages
message_keys = ['date', 'lat', 'long', 'message']


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

@app.route("/api/v1/users")
def get_users():
    resultados = [u for u in usuarios.find({}, {'_id':0})]
    return json.jsonify(resultados)

@app.route("/api/v1/users/<int:uid>")
def get_user(uid):
    resultados = [u for u in usuarios.find({"uid": uid}, {'_id':0})]
    resultados[0]['messages'] = [m for m in mensajes.find({"sender": uid}, {'_id': 0})]
    return json.jsonify(resultados)

@app.route("/api/v1/conversation/<int:uid1>/<int:uid2>")
def get_conversation(uid1, uid2):
    resultados1 = [m for m in mensajes.find({"receptant":uid1, "sender": uid2},{"_id":0})]
    resultados2 = [m for m in mensajes.find({"receptant":uid2, "sender": uid1},{"_id":0})]
    return json.jsonify(resultados1 + resultados2)

@app.route("/api/v1/message/<int:uid1>/<int:uid2>", methods=['POST'])
def create_message(uid1, uid2):
    data = {key: request.json[key] for key in message_keys}
    data["sender"] = uid1
    data["receptant"] = uid2
    result = mensajes.insert_one(data)
    if (result):
        message = 'Se ha creado un mensaje exitosamente.'
        success = True
    else:
        message = 'No se ha podido crear el mensaje.'
        success = False

    return json.jsonify([{'success': success, 'message': message}])





if __name__ == "__main__":
    app.run(debug=True)

if os.name == 'nt':
    app.run()
