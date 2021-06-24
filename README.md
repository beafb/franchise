# ALMA

## Installation

S'assurer que python3 est bien installé https://docs.python-guide.org/starting/install3/osx/

S'assurer que sqlite3 est installé, https://www.servermania.com/kb/articles/install-sqlite/
Normalement sqlite3 est installé par défaut sur les mac

Installer **virtualenv** : https://gist.github.com/Geoyi/d9fab4f609e9f75941946be45000632b
C'est un utilitaire qui permet d'encapsuler les dépendances du script pour ne pas avoir à les installer sur toute la machine et entrer en conflit avec d'autres scripts.

Une fois dans le dossier "franchise", entrer dans le terminal :

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt


## Lancement

Une fois les dépendances installées il faut créer un fichier d'entrée sur ce modèle :
https://docs.google.com/spreadsheets/d/1DVNsIJjXGp_GRVCHo9ROUpDEMsaUyrNNQdqtz5e-URg/edit#gid=0
Il faut garder tous les headers mais seuls les champs id et adresses doivent être remplis.
Ensuite il faut télécharger ce fichier en csv et le déplacer dans le dossier du programme.
Pour lancer le programme :

    python app.py <<nom de la base de données>> <<nom du fichier d'entrée>>
Donc dans notre cas :

    python app.py optic2000 optic2000.csv

## Récupération des données

Le script constitue une base de données sql.

    sqlite3 <<nom de la base de données>>
donc :

    sqlite3 optic2000
    .mode csv
    .headers on
    .output optic2000_out.csv
    select * from optic2000;
    .quit

Il y a maintenant un fichier nommé *optic2000_out.csv* que l'on peut uploader dans google Sheet :

https://docs.google.com/spreadsheets/d/1DVNsIJjXGp_GRVCHo9ROUpDEMsaUyrNNQdqtz5e-URg/edit#gid=1430701624
