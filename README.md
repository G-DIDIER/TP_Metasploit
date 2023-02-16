<!-- Usage guide of api.py and log_parser.py -->
# Usage guide of api.py and log_parser.py

## Install requirements :
``` bash
pip install -r requirements.txt
```

## Run MongoDB with docker compose :
``` bash
docker-compose up -d
```

## Run Victim docker :
``` bash
git clone https://github.com/fvvsantana/metasploitPlayground.git
sudo docker build -t dvictim metasploitPlayground/victim
docker run -it -d --rm --name victim_docker --network host -v /etc/timezone:/etc/timezone:ro dvictim
```

## Run Flask server :
Flask server is required for web interface to work.
(running on port 5000)
``` bash
python api.py
```

## Run log parser :
Log parser is required to parse the log file and store it in database.
The Victim docker must be running before running the log parser.

- Create the log directory (used to mount directory from the docker)
``` bash
mkdir log
```
- Run the log parser
``` bash
python log_parser.py
```
The password of the docker user will be asked.
enter : `msfadmin` (by default)
Once logged in, the script will mount the logs directory of the docker and parse the logs.
