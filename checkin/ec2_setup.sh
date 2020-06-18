#! /bin/bash

echo 'alias start-server="uvicorn api:app --reload --port 8080 --host 0.0.0.0"' > ~/.bash_profile

iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -I OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-ports 8080

# https://docs.anaconda.com/anaconda/install/silent-mode/
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
source ~/.bashrc

git clone https://github.com/dmarx/checkin.git
cd checkin/checkin
conda env create -f environment2.yml
activate checkin
python prepopulate_event_types.py

nohup start-server &