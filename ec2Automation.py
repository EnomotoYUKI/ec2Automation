#-------------------------------------------------------#
# This Program is EC2 automation system.
# It does get EC2's groval IP address, start EC2 instance
# and make shortcut of Teraterm that auto connecting
# EC2 instance by SSH.
#
# Author : EnomotoYUKI
# Date : 2023.01.30
# Version : 1.1
#
# Feel free to modify this program.
#-------------------------------------------------------#

import subprocess
import boto3
import os 
from os.path import dirname,join
from dotenv import load_dotenv



load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__),".env")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")

#---------------------SETTING  AREA----------------------#
# PATHTERATERM : Write your Teratarm(ttermpro.exe)'s directry.
# PATHOPENKEY : Write your openkey used by SSH 
# nameWDB : Write shortcut name for webdb
# nameNAGI : Write shortcut name for Nagios
# host_path : Write host file path

PATHTERATERM = r"D:\Program Files (x86)\teraterm\ttermpro.exe"
PATHOPENKEY  = r"D:\Users\0enok\Document\hb-intern-202301.pem"
PATHSHORTCUTDIR = r"C:\Users\0enok\Desktop"
nameWDB = "WebDB"
nameNAGI = "Nagios"
yourname = "yuki"
hostPath = "C:\Windows\System32\drivers\etc\hosts"

# Setting access key and secret access key by .env file.
# Detailed explain is written by README.txt.

load_dotenv(verbose=True)
dotenvPath = join(dirname(__file__),".env")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")

#------------------- SETTING AREA End -------------------# 

ec2 = boto3.resource('ec2',
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_ACCESS_KEY,
                        region_name= "ap-northeast-1"
                        )

class ec2Automation:

    def __init__(self,id,nameInstance,domain):
        self.instanceID = id
        self.instance = ec2.Instance(self.instanceID)
        self.instanceName = nameInstance
        self.domain = domain

    def startEC2(self):

        self.instance.start()
        self.instance.wait_until_running()

    def getEC2Address(self):
        self.groIP = self.instance.public_ip_address
        print(f"{self.instanceName} Groval IP Address : {self.groIP}")

    def makeTeratarmShortCut(self):
        wshText = \
f'Set shell = WScript.CreateObject("WScript.Shell")\n\
fil =  "{PATHSHORTCUTDIR}\{self.instanceName}.lnk"\n\
Set shortCut = shell.CreateShortcut(fil)\n\
shortCut.TargetPath = "{PATHTERATERM}"\n\
shortCut.Arguments = "{self.groIP}:22 /auth=publickey /user=ec2-user /keyfile={PATHOPENKEY}"\n\
shortCut.Save'

        with open(f"{self.instanceName}.vbs", mode = "w") as t:
            t.write(wshText)
        subprocess.call(f'{self.instanceName}.vbs',shell = True)

    def changeHostFile(self):
        flg = cont = 0
        tx = f"{self.groIP} {self.domain}\n"
        with open(hostPath,"r") as h:
            tmp = h.readlines()

        for i in tmp:
            if self.domain in i:
                tmp[cont] = tx
                flg = 1
                if cont > 1: del tmp[cont]
            cont += 1
            if flg == 0:
                tmp.append(tx)

            with open(hostPath,"w") as h:
                h.writelines(tmp)
    
    def ec2Automation(self):
        self.startEC2()
        self.getEC2Address()
        self.makeTeratarmShortCut()
        self.changeHostFile()

webdbIns = ec2Automation("i-0fc288937b1cf7852",nameWDB,"yuki-webdb")
nagiosIns = ec2Automation("i-0715441d4fd135642",nameNAGI,"yuki-nagios")
dbIns = ec2Automation("i-0f4dc7507c315db19","DB","yuki-db")
webdbIns.ec2Automation()
nagiosIns.ec2Automation()
dbIns.ec2Automation()