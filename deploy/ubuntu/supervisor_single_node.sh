#!/bin/bash

apt-get update
apt-get install -y supervisor python-setuptools python-pip python-dev libffi-dev

echo "[program:docrane]
autorestart=true
autostart=true
command=/usr/local/bin/docrane -v /docrane
redirect_stderr=true
stdout_logfile=/var/log/docrane.log
stdout_logfile_maxbytes=5MB
stdout_logfile_backups=10" > /etc/supervisor/conf.d/docrane.conf

# Start etcd container
read -p "Docker Host's IP Address: " HostIP
export $HostIP
docker run -d -p 4001:4001 -p 2380:2380 -p 2379:2379 --name etcd quay.io/coreos/etcd:v2.0.13  -name etcd0  -advertise-client-urls http://${HostIP}:2379,http://${HostIP}:4001  -listen-client-urls http://0.0.0.0:2379,http://0.0.0.0:4001  -initial-advertise-peer-urls http://${HostIP}:2380  -listen-peer-urls http://0.0.0.0:2380  -initial-cluster-token etcd-cluster-1  -initial-cluster etcd0=http://${HostIP}:2380  -initial-cluster-state new

# Install etcdctl on host
wget https://github.com/coreos/etcd/releases/download/v2.0.13/etcd-v2.0.13-linux-amd64.tar.gz 
tar xvzf etcd-v2.0.13-linux-amd64.tar.gz 
mv etcd-v2.0.13-linux-amd64/etcdctl /usr/local/bin
rm -Rf etcd-v2.0.13-linux-amd64 etcd-v2.0.13-linux-amd64.tar.gz

# Install docrane
cd $(dirname "${BASH_SOURCE[0]}") && cd ../../
pip install -r requirements.txt
python setup.py install
etcdctl mkdir /docrane

# Restart supervisor
supervisorctl reload
