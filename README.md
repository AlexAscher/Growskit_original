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
