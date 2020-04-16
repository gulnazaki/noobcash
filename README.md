# noobcash
A simple cryptocurrency/blockchain system in Python


## Install
```
git clone https://github.com/gulnazaki/noobcash.git
cd noobcash
python3.7 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
## Start node backend
```
python nbc.py --ip-addr [--port] [--bootstrap] [--max-nodes] [--NBC] [--capacity] [--difficulty]
```
## Basic CLI usage
```
python cli.py t [-sender_ip] [-sender_port] -amount -recip_addr (or recip_id)
python cli.py view
python cli.py balance [-my_ip] [-my_port]
```
