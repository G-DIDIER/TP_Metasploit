import os
import re
import time

import pymongo

# Connexion à la base de données MongoDB
client = pymongo.MongoClient("mongodb://root:example@127.0.0.1:27017/")
db = client["logs_db"]

# Répertoire contenant les fichiers de logs
log_dir = "log/"

# Collection unique pour les logs
log_collection = "logs"
os.system(
    "sshfs -o KexAlgorithms=diffie-hellman-group14-sha1 "
    "-oHostKeyAlgorithms=+ssh-dss msfadmin@127.0.0.1:/var/log/ ./log")

idx_id = 0
# Boucle infinie
while True:
    # Boucle sur les fichiers de logs
    for root, dirs, files in os.walk(log_dir):
        for filename in files:
            # Vérification que le fichier est un fichier de log
            if filename.endswith(".log"):
                # Détermination du nom de service
                service_name = re.sub(r'\..*', '', filename)

                # Ouverture du fichier de log
                file_path = os.path.join(root, filename)
                try:
                    if filename.endswith(".log"):
                        log_file = open(file_path, "r")
                    else:
                        continue
                except Exception as e:
                    continue

                # Boucle sur les lignes du fichier de log
                for line in log_file:
                    timestamp = time.time()

                    # Rename some services
                    if service_name == "error":
                        service_name = "apache_error"
                    if service_name == "access":
                        service_name = "apache_access"
                    if service_name == "access":
                        service_name = "apache_access"

                    # Extraction des informations de la ligne
                    # (cette partie dépend des formats de vos fichiers de log)
                    log_info = {
                        "service": service_name,
                        "id": idx_id,
                        "timestamp": timestamp,
                        "filename": filename,
                        "line": line
                    }

                    # Vérification que la ligne n'a pas déjà été insérée
                    if not db[log_collection].find_one({"line": line}):
                        # Enregistrement des informations dans la base de données
                        db[log_collection].insert_one(log_info)
                        idx_id = idx_id + 1

                # Fermeture du fichier de log
                log_file.close()

    # Pause avant la prochaine itération
    time.sleep(5)

# Fermeture de la connexion à la base de données
client.close()
