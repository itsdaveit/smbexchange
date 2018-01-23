import os, subprocess, datetime, time, shutil
import sys
import configparser
import logging

logger = logging.getLogger('smbexchange')
hdlr = logging.FileHandler('smbexchange.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info("Programmstart")

config = configparser.ConfigParser()
config.read("smbexchange.ini")
letter = config["main"]["letter"]
host = config["main"]["host"]
share = config["main"]["share"]
wait_before_action = config["main"]["wait_before_action"]

fetch_from_folder = letter + ":\\" + config["main"]["fetch_from_folder"]
fetch_to_folder = config["main"]["fetch_to_folder"]
move_after_fetch_folder = letter + ":\\" + config["main"]["move_after_fetch_folder"]


upload_from_folder = config["main"]["upload_from_folder"]
upload_to_folder = config["main"]["upload_to_folder"]
move_after_upload_folder = config["main"]["move_after_upload_folder"]

if config["main"]["user"] != "" and config["main"]["password"] != "":
    print("UP")
    mount_command = r"net use " + letter + ": \\\\" + host + "\\" + share + " " + config["main"]["password"] + " /user:" + config["main"]["user"]
else:
    mount_command = r"net use " + letter + ": \\\\" + host + "\\" + share

print(mount_command)
response = subprocess.call(mount_command, shell=True)
if response != 0:
    exit(1)

logger.info("Dateien holen und verschieben...")
files_to_fetch = []
for f in os.listdir(fetch_from_folder):
    file_with_path = os.path.join(fetch_from_folder, f)
    if os.path.isfile(file_with_path):
        files_to_fetch.append(file_with_path)
        logger.info("Datei gefunden: " + file_with_path)

logger.info("Warte "+ wait_before_action + " Sekunden...")
time.sleep(int(wait_before_action))

for f in files_to_fetch:
    logger.info("kopiere: " + f)
    try:
        shutil.copy2(f,fetch_to_folder)
    except Exception as e:
        logger.error(str(e))
        continue
    logger.info("verschiebe: " + f)
    try:
        shutil.move(f,move_after_fetch_folder)
    except Exception as e:
        logger.error(str(e))
        continue

logger.info("Dateien uploaden und verschieben...")

files_to_upload = []
for f in os.listdir(upload_from_folder):
    file_with_path = os.path.join(upload_from_folder, f)
    if os.path.isfile(file_with_path):
        files_to_upload.append(file_with_path)
        logger.info("Datei gefunden: " + file_with_path)

logger.info("Warte "+ wait_before_action + " Sekunden...")
time.sleep(int(wait_before_action))

for f in files_to_upload:
    logger.info("kopiere: " + f)
    try:
        shutil.copy2(f,upload_to_folder)
    except Exception as e:
        logger.error(str(e))
        continue

    logger.info("verschiebe: " + f)
    try:
        shutil.move(f,move_after_upload_folder)
    except Exception as e:
        logger.error(str(e))
        continue

subprocess.call("net use " + letter + ": /delete /yes", shell=True)
