import socket
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import requests
from flask import Flask, render_template
from flask import jsonify
from flask_restful import Api
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://root:example@127.0.0.1:27017/")
db = client["logs_db"]
logs = db["logs"]


def check_service_status(hostname, port):
    try:
        sock = socket.create_connection((hostname, port), timeout=2)
        return True
    except OSError:
        return False


@app.route('/logs/<string:service>/<int:limit>')
def get_logs(service, limit):
    if service == "all":
        result = logs.find({}).sort("id", -1).limit(limit)
    else:
        result = logs.find({"service": service}).sort("id", -1).limit(limit)
    return [{"service": log["service"],
             "id": str(log["_id"]),
             "timestamp": log["timestamp"],
             "filename": log["filename"],
             "line": log["line"]}
            for log in result]


@app.route('/status')
def status():
    hostname = '127.0.0.1'
    apache_status = 'Running' if check_service_status(hostname, 80) else 'Stopped'
    mysql_status = 'Running' if check_service_status(hostname, 3306) else 'Stopped'
    telnet_status = 'Running' if check_service_status(hostname, 23) else 'Stopped'
    return render_template('status.html', apache_status=apache_status, mysql_status=mysql_status,
                           telnet_status=telnet_status)


@app.route('/')
def index():
    # Appel à l'API
    response = requests.get("http://127.0.0.1:5000/logs/all/25")
    # Récupération des logs
    logs = response.json()
    # Formatage des logs pour l'affichage
    formatted_logs = []
    for log in logs:
        if log["timestamp"] is not None:
            date = datetime.fromtimestamp(log["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        else:
            date = ""
        service = log["service"]
        formatted_logs.append({"date": date, "service": service, "line": log["line"]})
    # Affichage des logs dans un tableau
    return render_template("index.html", logs=formatted_logs)


# Route pour récupérer le nombre de documents générés depuis la dernière seconde pour chaque service
@app.route('/services')
def services():
    # Recuperation de toutes les valeurs (distinctes) de la clé "service"
    services = logs.distinct("service")
    # Initialisation du dictionnaire de résultats
    result = {}
    # Boucle sur les services
    for service in services:
        # Récupération du nombre de documents générés par service
        count = logs.count_documents({"service": service})
        # Ajout du résultat au dictionnaire
        result[service] = count

    # Retour du dictionnaire de résultats
    return jsonify(result)


@app.route('/logs/minutes')
def logs_per_minute():
    # Récupération des données de la base de données
    now = datetime.now()
    start_time = now - timedelta(minutes=30)
    logs_list = list(logs.find({"timestamp": {"$gte": start_time.timestamp()}}, {"_id": -1, "timestamp": 1}))

    # Création d'un dictionnaire pour stocker le nombre de logs par minute
    logs_per_minute = {}
    for log in logs_list:
        timestamp = datetime.fromtimestamp(log["timestamp"])
        minute = timestamp.replace(second=0, microsecond=0)
        if minute in logs_per_minute:
            logs_per_minute[minute] += 1
        else:
            logs_per_minute[minute] = 1

    # Création d'un graphique à partir des données
    plt.figure()
    plt.title("Nombre de logs par minute (30 dernières minutes)")
    plt.xlabel("Temps")
    plt.ylabel("Nombre de logs")
    plt.xticks(rotation=45)
    x = []
    y = []
    for minute, count in logs_per_minute.items():
        x.append(minute.strftime("%Y-%m-%d %H:%M"))
        y.append(count)
    plt.plot(x, y)
    plt.tight_layout()
    plt.savefig("static/logs_per_minute.png")
    return {"status": "ok"}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
