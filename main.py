from flask import Flask, request, json, render_template
from bson.objectid import ObjectId
from pymongo import MongoClient
import atexit
import subprocess
import os
import pymongo
from bson.json_util import dumps

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
    if len(resultados1 + resultados2) == 0:
        return "No se han encontrado mensajes entre estos usuarios."
    return json.jsonify(resultados1 + resultados2)

@app.route("/api/v1/busqueda/<texto>")
def search_message(texto):
    texto = texto.split(",")
    mensajes.create_index([("message", 'text')])
    lista = []
    for t in texto:
       t = "\"" + t +"\""
       lista.append(t)
    tex = " ".join(lista)
    resultado = list(mensajes.find({"$text": {"$search": tex}},{"_id":0}))
    if len(resultado) == 0:
        return 'No hay resultados para esa búsqueda'
    return json.jsonify(resultado)

@app.route("/api/v1/busqueda/<texto>/<int:uid>")
def search_message_user(texto,uid):
    texto = texto.split(",")
    mensajes.create_index([("message", 'text')])
    lista = []
    for t in texto:
       t = "\"" + t +"\""
       lista.append(t)
    tex = " ".join(lista)
    resultado = list(mensajes.find({"$and": [{"$text": {"$search": tex}},{"sender":uid}]},{"_id":0}))
    if len(resultado) == 0:
        return 'No hay resultados para esa búsqueda'
    return json.jsonify(resultado)

@app.route("/api/v1/busqueda2/<texto>")
def search_message2(texto):
    texto = texto.split(",")
    mensajes.create_index([("message",'text')])
    tex = " ".join(texto)
    tex = '"\"' + tex + '\""'
    resultado = list(mensajes.find({"$text": {"$search": tex}},{"_id":0}))
    if len(resultado) == 0:
        return 'No hay resultados para esa búsqueda'
    return json.jsonify(resultado)

@app.route("/api/v1/busqueda2/<texto>/<int:uid>")
def search_message_user2(texto,uid):
    texto = texto.split(",")
    mensajes.create_index([("message",'text')])
    tex = " ".join(texto)
    tex = '"\"' + tex + '\""'
    resultado = list(mensajes.find({"$and": [{"$text": {"$search": tex}},{"sender":uid}]},{"_id":0}))
    if len(resultado) == 0:
        return 'No hay resultados para esa búsqueda'
    return json.jsonify(resultado)

@app.route("/api/v1/busqueda3/<texto>")
def search_message3(texto):
    texto = texto.split(",")
    lista = []
    contador = 0
    resultados = [u for u in mensajes.find({})]
    for i in resultados:
        for p in texto:
            if p.lower() in i['message'].lower():
                contador +=1
        if contador == 0:
            i['_id'] = str(i['_id'])
            lista.append(i)
        else:
            contador = 0
    if len(lista) == 0:
        return 'No hay resultados para esa búsqueda'
    return json.jsonify(lista)


@app.route("/api/v1/busqueda3/<texto>/<int:uid>")
def search_message_user3(texto,uid):
    texto = texto.split(",")
    lista = []
    contador = 0
    resultados = [u for u in mensajes.find({"sender":uid})]
    for i in resultados:
        for p in texto:
            if p.lower() in i['message'].lower():
                contador +=1
        if contador == 0:
            i['_id'] = str(i['_id'])
            lista.append(i)
        else:
            contador = 0
    if len(lista) == 0:
        return 'No hay resultados para esa búsqueda'
    return json.jsonify(lista)

@app.route("/api/v1/message/<int:uid1>/<int:uid2>", methods=['POST'])
def create_message(uid1, uid2):
    data = request.get_json(force=True)
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

@app.route('/api/v1/message/<mid>', methods=['DELETE'])
def delete_message(mid):
    mensajes.delete_one({"_id":ObjectId(mid)})
    message = f'Mensaje con _id = {mid} ha sido eliminado'
    return json.jsonify({'result': 'success', 'message': message})

if __name__ == "__main__":
    app.run(debug=True)

if os.name == 'nt':
    app.run()
