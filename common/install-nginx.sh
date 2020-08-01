sudo apt install -y nginx
sudo systemctl stop apache2
sudo systemctl disable apache2
pip install uwsgi
pushd ~/app/python/
cat <<EOF > server.ini
[uwsgi]
module = app
callable = app
master = true
processes = 1
socket = server.sock
chmod-socket = 666
vacuum = true
die-on-term = true
touch-reload = app.py
EOF
sudo sed -i '/ExecStart/c\ExecStart=/home/isucon/.local/bin/uwsgi --ini server.ini' /etc/systemd/system/niita_python.service
sudo unlink /etc/nginx/sites-enabled/default
cat <<EOF > niita
server {
  listen 80;
  server_name _;
  location / {
    include uwsgi_params;
    uwsgi_pass unix:///home/isucon/app/python/server.sock;
  }
}
EOF
sudo mv niita /etc/nginx/sites-enabled/niita
sudo systemctl daemon-reload
sudo systemctl restart niita_python
sudo systemctl restart nginx
popd
