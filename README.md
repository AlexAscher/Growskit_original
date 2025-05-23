setup server:

```bash
sudo apt install python3 python3-pip git nginx
sudo /etc/init.d/nginx start

git clone 
cd growskit

pip install -r requirements.txt --break-system-packages

sudo ln -s $(pwd) /etc/nginx/sites-enabled

sudo usermod -a -G ${USER} www-data

\<setup growskit-daemon\>
\<setup mysql\>

# (re)start app
sudo /etc/init.d/nginx restart
systemctl restart growskit
```


setup growskit-daemon:

```bash
# file /lib/systemd/system/growskit.service
# (ex. nano, then after paste it (right click for paste) - ctrl+o (save), enter, ctrl+x (exit))

[Unit]
Description = growskit

[Service]
Type             = simple
User             = root
Group            = root
LimitNOFILE      = 4096
Restart          = always
RestartSec       = 5s
StandardOutput   = append:/root/growskit/std.log
StandardError    = append:/root/growskit/std.log
WorkingDirectory = /growskit
ExecStart        = /usr/bin/python3 /growskit/manage.py runserver 0.0.0.0

[Install]
WantedBy = multi-user.target
# end file

systemctl enable growskit.service
systemctl start growskit
```


setup mysql:

```bash
wget https://dev.mysql.com/get/mysql-apt-config_0.8.33-1_all.deb # or newer
sudo dpkg -i mysql-apt-config_0.8.33-1_all.deb # use OK and continue
sudo apt-get update
sudo apt-get install mysql-server
# check daemon
systemctl status mysql # (re)start if needed

# create database
mysql -u root -p # password in .env
CREATE DATABASE growskit; # for exit - type "exit"

# check for more actions: https://app-generator.dev/docs/technologies/mysql/index.html
# ready
```
