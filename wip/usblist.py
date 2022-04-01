import os
PATHUSB="/media/pi"
PATHTEST = r"/home/pi/"
PATHPROJET =  PATHTEST+"Projet/"
usbishere=False
'''
output = subprocess.Popen("lsblk", stdout=subprocess.PIPE, shell=True)
for out in output.communicate()[0].split():
    if'media' in out.decode('utf-8'):
        print(out)
        usbishere=True
if usbishere==False:
    print("NO USB")
'''   
liste = os.listdir(PATHUSB)
#print(liste)
if not len(liste):
    print ("Pas de clé branchée")
else: 
    usbname= ''.join(liste)
    usbname= usbname.replace(" ","\\ ")
    print("USB NAME:"+ usbname)
    cmd = r"rsync -ruv "+PATHPROJET+" /media/pi/"+str(usbname)+""
    os.system(cmd)
