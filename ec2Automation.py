import subprocess
import boto3
import os 
from os.path import dirname,join
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__),".env")
ACCESS_KEY = os.environ("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ("SECRET_ACCESS_KEY")
REGION = os.environ("REGION")

#-------------------------------------------------------#
# This Program is EC2 automation system.
# It does get EC2's groval IP address, start EC2 instance
# and make shortcut of Teraterm that auto connecting
# EC2 instance by SSH.
#
# Author : EnomotoYUKI
# Date : 2023.01.29
# Version : 1.0
#
# Feel free to modify this program.
#---------------------SETTING  AREA----------------------#
# PATHTERATERM : Write your Teratarm(ttermpro.exe)'s directry.
# PATHOPENKEY : Write your openkey used by SSH 
# nameWDB : Write shortcut name for webdb
# nameNAGI : Write shortcut name for Nagios

PATHTERATERM = r"D:\Program Files (x86)\teraterm\ttermpro.exe"
PATHOPENKEY  = r"D:\Users\0enok\Documents\hb-intern-202301.pem"
nameWDB = "WebDB"
nameNAGI = "Nagios"
local_path = "C:\Windows\System32\drivers\etc\hosts"
#------------------- SETTING AREA End -------------------# 
def ec2Start_and_getIP():
    ec2 = boto3.resource('ec2',
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_ACCESS_KEY,
                            region_name= "ap-northeast-1"
                            )

    instance_id_wdb = "i-0fc288937b1cf7852"
    instance_id_nagi = "i-0715441d4fd135642"

    instance_wdb = ec2.Instance(instance_id_wdb)
    instance_nagi = ec2.Instance(instance_id_nagi)

    instance_wdb.start()
    instance_nagi.start()

    instance_wdb.wait_until_running()
    instance_nagi.wait_until_running()

    ipWdb = instance_wdb.public_ip_address
    ipNagi = instance_nagi.public_ip_address

    print(f"WebDB Groval IP: {ipWdb}")
    print(f"Nagios Groval IP: {ipNagi}")
    return ipWdb,ipNagi

def write_localfile(wdb,nagi):
    f = open(local_path,"w")
    f.writelines([f"{wdb} yuki-webdb\n",f"{nagi} yuki-nagios"])
    f.close()


ipAdd = ec2Start_and_getIP()
write_localfile(ipAdd[0],ipAdd[1])



def setWSH(ipAdd,filName,pathTERA,pathOPENkey):
    wshText = \
f'Set shell = WScript.CreateObject("WScript.Shell")\n\
fil =  "{filName}.lnk"\n\
Set shortCut = shell.CreateShortcut(fil)\n\
shortCut.TargetPath = "{pathTERA}"\n\
shortCut.Arguments = "{ipAdd}:22 /auth=publickey /user=ec2-user /keyfile={pathOPENkey}"\n\
shortCut.Save'
    return wshText

def makeShortCut(wdbIP,nagiIP):
    with open("wdbSC.vbs", mode = "w+") as wdbF:
        wdbF.write(setWSH(wdbIP,nameWDB,PATHTERATERM,PATHOPENKEY))

    with open("nagiSC.vbs" , mode = "w+") as nagiF:
        nagiF.write(setWSH(nagiIP,nameNAGI,PATHTERATERM,PATHOPENKEY))

    subprocess.call('nagiSC.vbs',shell = True)
    subprocess.call("wdbSC.vbs",shell = True)


ipAdd = ec2Start_and_getIP()
write_localfile(ipAdd[0],ipAdd[1])
makeShortCut("18.181.79.237","54.92.108.213")