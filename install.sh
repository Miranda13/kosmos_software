#!/bin/bash

#Effectuer une mise a jour la carte
sudo apt update
sudo apt upgrade
sudo apt autoremove




#Installation des packages python necessaires 
#sudo apt install `cat requirements.txt`

#Recuperation du nom de la raspberry
nom_raspberry=$(whoami)
echo "$nom_raspberry"


# Creation de l'environnement Python
mkdir -p /home/$nom_raspberry/env_kosmos
python3 -m venv --system-site-packages /home/$nom_raspberry/env_kosmos/kosmos

source /home/$nom_raspberry/env_kosmos/kosmos/bin/activate
pip install --upgrade pip
pip install numpy
pip install opencv-python
pip install flask-cors
pip install smbus2



#Desactivation du bluetooth (raisons énergétiques)
sudo systemctl disable bluetooth

#Creation du fichier de lancement
cd /home/$nom_raspberry
echo "#!/bin/bash" > lancement_kosmos.sh

#Ajout de la commande de lancement du programme
sudo echo "sleep 20

# On se place dans l'environnement python 
source /home/$nom_raspberry/kosmos/bin/activate

# Demarrage du serveur
cd /home/$nom_raspberry/kosmos_software/frontend
sudo python3 -m http.server 80 &

#Lance kosmos_main.py 
cd /home/$nom_raspberry/kosmos_software/kosmosV3-env
sudo python3 kosmos_main5.py" >> lancement_kosmos.sh

#Rendre le lancement.sh executable
sudo chmod 755 /home/$nom_raspberry/lancement_kosmos.sh

#Activation de i2c (capteur pression température) et du vnc (communication)
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_vnc 0

#Ajout de la ligne de commande dans crontab qui permet le lancement au demarrage et création d'un dossier log
mkdir -p /home/$nom_raspberry/logfile_kosmos
(sudo crontab -l; echo "@reboot sudo bash /home/$nom_raspberry/lancement_kosmos.sh > /home/$nom_raspberry/logfile_kosmos/log.txt 2>&1";) | uniq - | sudo crontab
sudo crontab -l

exit 0
