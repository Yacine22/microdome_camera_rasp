#!/usr/bin/python3
# -*- coding: utf-8 -*-

#title         :V04_Microdôme
#description     :Interface de controle des leds et camera du micro dôme
#author       :Eloi Gattet
#date           :27/03/2019
#version         :1.0
#usage         :python3 V04_udome.py
#notes         :
#python_version  :3
#==============================================================================#

"""
Rajout du contrôle des LED
v11
bitbanging leds pour RTI
V13:
Copie et suppression de projets ok
log revue projet

TODO:
mode "photogrammetry + turntable    "
Rajouter "zoom" 1:1 pour mise au point
Preview plus rapide? Acquisition sans preview avec curseur / toggle pour accélérer
Transfert des dossiers vers clé usb, supprimer projet
Montrer l'espace libre quelque part
Splashscreen
√ Actualiser texte après mise à jour du nom de projet
Mettre les réglages en place : nom de projet
installer "no log" sur le raspberry
boot plus rapide / boot to docker / lancement automatique au boot
"""
#################
#   IMPORT   #
#################


import os
import shutil
import io
import time
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image
from PIL import ImageTk
import picamera
#import subprocess
import RPi.GPIO as gp


#Pin connected to ST_CP of 74HC595
latchPin = 31
#Pin connected to SH_CP of 74HC595
clockPin = 29
#Pin connected to DS of 74HC595
dataPin = 33
nbbras=8
tabled=[1,2,4,8,16,32,64,128]
ledposition=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,64]

CAMERASPEED = None
EXPOSURECOMPENSATION = None
nomprojet = None
defaultprojet = None
defaultprojet = str("Projet")
nbimg = 64
nbimgphotog = 50
usbishere=False

#PATHTEST = os.getcwd()+"/"
PATHUSB="/media/pi"
PATHTEST = "/home/pi/"
PATHPROJET =  PATHTEST+"Projet/"
PATHTMP = PATHTEST+"tmp/"
PATHRESSOURCES = PATHTEST+"Ressources/"
PATHPHOTOG = PATHTEST+"ProjetPhoto"
#################
#   Fenetres    #
#################
class FenetrePrincipale:

    def __init__(self):
        #fenetre
        self.fenetre = tk.Tk()
        #self.fenetre.geometry("+400+80")
        self.fenetre.attributes("-fullscreen",True)
        self.fenetre.configure(background=_from_rgb((41,40,46)))
        global nomprojet

        #images
        self.photoCamera = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconePhoto.png").resize((186,154),Image.BILINEAR)) #945 × 780
        self.photoRepertoire = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRepertoire.png").resize((200,154),Image.BILINEAR))
        self.photoFermer = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeAnnuler.png").resize((75,75),Image.BILINEAR))
        self.photoSettings = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeSettings.png").resize((75,75),Image.BILINEAR))
        self.photoEteindre = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeEteindre.png").resize((75,75),Image.BILINEAR))

        #Frame
        self.frame = Frame(self.fenetre,background=_from_rgb((41,40,46)))
        #Boutons
        self.boutonCapture = Button(self.frame, text="Nouveau projet",foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),image=self.photoCamera,compound=TOP,cursor="tcross",command=self.ouvrirCapture)
        self.boutonRepertoire = Button(self.frame, text="Projets passés",foreground=_from_rgb((176,175,179)),bd=0,relief="flat",image=self.photoRepertoire,compound=TOP,background=_from_rgb((41,40,46)),command=self.ouvrirRepertoire)
        self.boutonFermer = Button(self.frame, text="Fermer",relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)),command=self.bureau)
        self.boutonSettings = Button(self.frame,text="Réglages",image=self.photoSettings,foreground=_from_rgb((176,175,179)),relief="flat",compound=TOP,background=_from_rgb((41,40,46)),command=self.settings)
        self.boutonEteindre = Button(self.frame,text="Eteindre",image=self.photoEteindre,foreground=_from_rgb((176,175,179)),compound=TOP,highlightcolor=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),command=self.eteindre)
        #label
        #self.labelMap = Label(self.fenetre,image=self.photoMAP)

    def afficher(self):
        Grid.rowconfigure(self.fenetre, 0, weight=1)
        Grid.columnconfigure(self.fenetre, 0, weight=1)
        Grid.rowconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 0, weight=1)
        self.boutonCapture.grid(row=2,column=2,sticky='news')
        self.boutonRepertoire.grid(row=2,column=3,sticky='news') #columnspan=2,
        self.boutonFermer.grid(row=3,column=4,sticky='news')
        self.boutonSettings.grid(row=1,column=1,padx =0,pady=0,sticky='news')
        self.boutonEteindre.grid(row=3,column=5,padx=0,pady=0,sticky='news')
        self.frame.grid(row=0,column=0)
        #self.frame.pack(fill=X, expand=YES)
        #self.labelMap.grid(row=2,column=1,padx=5,pady=5)

    def ouvrirRepertoire(self): #ouvre un repertoire
        print("on ouvre le repertoire")
        fenetreprojet = RevueProjet(self.fenetre)
        #fenetreProjet = FenetreProjet(self.fenetre)
        #fenetreProjet.attributes("-fullscreen",True)

    def ouvrirCapture(self):
        fenetreCapture = FenetreCapture(self.fenetre)
        print("on ouvre la fenetre de capture")

    def mainloop(self):
        self.fenetre.mainloop()

    def bureau(self):
    #os.system('xdotool key ctrl+super+d')
        self.fenetre.destroy()
        
    def settings(self):
        fenetreReglages = Reglages(self.fenetre)

    def eteindre(self):
        os.system('sudo shutdown -h 0')
        print("byebye")

class FenetreCapture:

    def __init__(self, master):
        #Parametres globaux
        global nomprojet
        global CAMERASPEED
        global nbimg
        nomprojet = str(defaultprojet+str(ConfigNumProjet(PATHPROJET)))
        self.varprogress = IntVar()
        self.txtboutonFrameCamera = StringVar()
        self.varprogress.set(int(0))
        self.txtboutonFrameCamera.set("Lancer la prévisualisation")
        # management fenetre
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.attributes("-fullscreen",True)
        self.window.configure(background=_from_rgb((41,40,46)))
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)
        #Images
        self.iconeretour = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRetour.png").resize((75,75),Image.BILINEAR))
        self.imageOk = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeOk.png").resize((75,75),Image.BILINEAR))
        #Frame
        self.frame = Frame(self.window,background=_from_rgb((41,40,46))) #,height=50,width=10
        #Label 
        self.labelExpo = Label(self.frame, text="Exposition",foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP)
        self.labelLed = Label(self.frame, text="LED",foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP)
        
        #Boutons
        self.labelProjet = Button(self.frame, text=nomprojet,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), command=self.OuvreTextEntry)
        self.boutonOk = Button(self.frame, text="Capture", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP, command=self.startCapture)
        self.boutonRetour = Button(self.frame, text="Retour", image=self.iconeretour,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),compound=TOP, command=self.fermerFenetreCapture)
        self.boutonFrameCamera = Button(self.frame,textvariable=self.txtboutonFrameCamera, foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),command=self.startPreview) 
        self.boutonkill = Button(self.frame,text="REBOOT",anchor="s", foreground=_from_rgb((41,40,46)),relief="flat",background=_from_rgb((41,40,46)),command=self.killswitch,state='disabled') 

        #Slides
        self.sliderExpo = Scale(self.frame, orient='vertical', from_=-25, to=25, resolution=1, tickinterval=5,relief = "flat",foreground=_from_rgb((176,175,179)),background=_from_rgb((41,40,46)), command=self.updateExposure)
        self.sliderLed = Scale(self.frame, orient='vertical', from_=0, to=64, resolution=1,relief = "flat",foreground=_from_rgb((176,175,179)),background=_from_rgb((41,40,46)),command=self.updateLed)
        self.progressbar = ttk.Progressbar(self.window,maximum=nbimg,variable=self.varprogress,orient ="horizontal",mode ="determinate")
        #Camera
        #On récupère la taille de la fenêtre
        self.camerapreviewX = 400
        self.camerapreviewY = int(self.camerapreviewX * 3 / 4)
        self.cameraposX= int((self.window.winfo_screenwidth() / 2) - (self.camerapreviewX / 2))
        self.cameraposY= int((self.window.winfo_screenheight() / 2) - (self.camerapreviewY / 2))
        #print("cameraposX = "+ str(self.cameraposX))
        #On crée une frame pour décaler les boutons autour
        #self.frameCamera = Frame(self.frame,background=_from_rgb((100,100,100)),width=self.camerapreviewX+20, height=self.camerapreviewY+50)
        self.afficher()
        self.startPreview()

    def afficher(self):
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.frame, 0, weight=1)
        Grid.rowconfigure(self.frame, 1, weight=5)
        Grid.rowconfigure(self.frame, 2, weight=1)
        Grid.rowconfigure(self.frame, 3, weight=1)
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=5)
        Grid.columnconfigure(self.frame, 2, weight=1)
        #Grid.rowconfigure(self.frameCamera, 0, weight=1)
        #Grid.columnconfigure(self.frameCamera, 0, weight=1)
        self.frame.grid(row=0,column=0,sticky='nsew')
        self.boutonRetour.grid(row=0, column=0,sticky='nsew')
        self.labelProjet.grid(row=0,column=1,sticky="nsew")
        self.boutonOk.grid(row=0, column=2,sticky='nsew')
        self.sliderExpo.grid(row=1,column=0,sticky='nsew')
        #self.frameCamera.grid(row=1,column=1,sticky='news')
        self.boutonFrameCamera.grid(row=1,column=1,sticky='nsew') #dans le frame camera
        self.sliderLed.grid(row=1,column=2,sticky='nsew')
        self.labelExpo.grid(row=2,column=0,pady=50,sticky='nsew')
        self.labelLed.grid(row=2,column=2,pady=50,sticky='nsew')
        self.progressbar.grid(row=3,column=0,sticky="ew")
        self.boutonkill.grid(row=2,column=1,sticky='news')
        self.boutonFrameCamera.configure(state='disabled')
        self.boutonkill.configure(state='disabled')
        self.boutonkill.grid_remove()

    def startPreview(self):
        #Lancement Camera
        self.labelProjet.configure(text=nomprojet)
        self.window.update()
        self.window.update_idletasks()
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.camerapreviewX,self.camerapreviewY)
        self.camera.exposure_compensation = 0
        self.camera.iso=100
        self.camera.rotation = 180
        self.camera.awb_mode= 'auto'
        time.sleep(0.5)
        self.camera._check_camera_open()
        self.camera.preview_fullscreen = False
        self.camera.preview_window = (self.cameraposX,self.cameraposY,self.camerapreviewX,self.camerapreviewY)
        self.camera.start_preview()
        self.boutonFrameCamera.configure(state='disabled')
        zero()
        LED(57)

    def fermerFenetreCapture(self):
        zero()
        self.camera.stop_preview()
        self.camera.close()
        self.window.destroy()

    def OuvreTextEntry(self):
        self.camera.stop_preview()
        self.camera.close()
        #self.window.destroy()
        fenetreTextEntry = TextEntry(self.master)
        self.boutonFrameCamera.grid()
        self.boutonFrameCamera.configure(state='active')
        print("on ouvre la fenetre de saisieTexte")

    def updateExposure(self,abc):
        self.camera.exposure_compensation = self.sliderExpo.get()
        #print(str(self.camera.exposure_compensation))

    def killswitch(self):
        os.system("sudo reboot")

    def updateLed(self,abc):
        start = time.time()
        zero2()
        LED(ledposition[int(self.sliderLed.get())])
        end = time.time()
        print(end - start)

    def startCapture(self):
        global nbimg
        global CAMERASPEED
        global EXPOSURECOMPENSATION
        self.boutonkill.configure(state='active')
        self.boutonkill.configure(foreground=_from_rgb((176,175,179)))
        self.boutonkill.grid()
        self.window.update()
        self.window.update_idletasks()
        EXPOSURECOMPENSATION = self.sliderExpo.get()
        CAMERASPEED = self.camera.exposure_speed
        self.camera.shutter_speed= CAMERASPEED
        print("shutter_speed = "+ str(CAMERASPEED))
        print("exposure_compensation = "+ str(EXPOSURECOMPENSATION))
        self.camera.awb_mode = 'off'
        AWB_GAINS = self.camera.awb_gains
        self.camera.stop_preview()
        self.camera.close()
        time.sleep(0.1)
        #self.window.destroy()
        self.sliderExpo.configure(state='disabled')
        self.sliderLed.configure(state='disabled')
        self.boutonOk.configure(state='disabled')
        self.boutonRetour.configure(state='disabled')
        self.labelProjet.configure(state='disabled')
        self.window.update()
        #Camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1640, 1232) #3280 × 2464 
        self.camera.iso=100
        self.camera.rotation = 180
        self.camera.preview_fullscreen = False
        self.camera.preview_window = (self.cameraposX,self.cameraposY,self.camerapreviewX,self.camerapreviewY)
        time.sleep(0.2)
        self.camera._check_camera_open()
        zero()
        LED(int(ledposition[int(0)]))
        self.camera.start_preview()
        time.sleep(1)
        self.camera.exposure_mode = 'off'
        self.camera.shutter_speed= CAMERASPEED
        self.camera.exposure_compensation = EXPOSURECOMPENSATION
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = AWB_GAINS
        ##############
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        ##############

        for i in range(0,nbimg,1):
            zero2()
            LED(ledposition[int(i)])
            time.sleep(0.75)
            self.camera.capture(PATHTMP +'{0:02d}'.format(i)+".jpg",format='jpeg',quality=95,use_video_port=True)
            time.sleep(0.25)
            self.varprogress.set(int(i))
            self.window.update()
            self.window.update_idletasks()
        self.camera.stop_preview()


        ##############
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        ##############
        zero()
        self.boutonOk.configure(command=self.Continuer,text="Continuer")
        self.txtboutonFrameCamera.set("Fin de la prise de vue")
        self.boutonOk.configure(state='active')
        self.boutonRetour.configure(state='active')
        self.camera.close()

    def pdv(self,img):
        imagepath = PATHTMP +'{0:02d}'.format(img)+".jpg"
        print("On prend la photo numéro : "+str(imagepath))
        self.camera.capture(imagepath,format='jpeg',quality=100,use_video_port=True)

    def Continuer(self):
        zero()
        self.movefiles()
        self.window.destroy()

    def movefiles(self):
        global nomprojet
        dossierprojet = PATHPROJET + nomprojet
        os.system("mkdir "+dossierprojet)#Cree un nouveau repertoire pour un projet
        #os.system("mkdir "+PATHPROJET+str(num)+"/miniature") 
        cmd1 = "cp "+PATHTMP+"01.jpg "+PATHTMP+"miniature.jpg"
        cmd2 = "convert "+PATHTMP+"miniature.jpg -thumbnail 320x240 "+PATHTMP+"miniature.jpg"
        #find src_image_dir/ -type f -name '*.jpg' -print0 | xargs -0r mv -t dst_image_dir/
        #cmd3 = "mv "+PATHTMP+"*.jpg "+dossierprojet
        cmd3 = "find "+PATHTMP+" -type f -name '*.jpg' -print0 | xargs -0r mv -t "+dossierprojet
        os.system(cmd1)
        os.system(cmd2)
        os.system(cmd3) #deplace les photos dans ce repertoire

class FenetreCapturePhoto:

    def __init__(self, master):
        #Parametres globaux
        global nomprojet
        global CAMERASPEED
        global nbimgphotog
        nomprojet = str(defaultprojet+str(ConfigNumProjet(PATHPROJET)))
        self.varprogress = IntVar()
        self.txtboutonFrameCamera = StringVar()
        self.varprogress.set(int(0))
        self.txtboutonFrameCamera.set("Lancer la prévisualisation")
        # management fenetre
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.attributes("-fullscreen",True)
        self.window.configure(background=_from_rgb((41,40,46)))
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)
        #Images
        self.iconeretour = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRetour.png").resize((75,75),Image.BILINEAR))
        self.imageOk = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeOk.png").resize((75,75),Image.BILINEAR))
        #Frame
        self.frame = Frame(self.window,background=_from_rgb((41,40,46))) #,height=50,width=10
        #Label 
        self.labelExpo = Label(self.frame, text="Exposition",foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP)
        self.labelLed = Label(self.frame, text="LED",foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP)
        
        #Boutons
        self.labelProjet = Button(self.frame, text=nomprojet,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), command=self.OuvreTextEntry)
        self.boutonOk = Button(self.frame, text="Capture", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP, command=self.startCapture)
        self.boutonRetour = Button(self.frame, text="Retour", image=self.iconeretour,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),compound=TOP, command=self.fermerFenetreCapture)
        self.boutonFrameCamera = Button(self.frame,textvariable=self.txtboutonFrameCamera, foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),command=self.startPreview) 
        #Slides
        self.sliderExpo = Scale(self.frame, orient='vertical', from_=-25, to=25, resolution=1, tickinterval=5,relief = "flat",foreground=_from_rgb((176,175,179)),background=_from_rgb((41,40,46)), command=self.updateExposure)
        self.sliderLed = Scale(self.frame, orient='vertical', from_=0, to=64, resolution=1,relief = "flat",foreground=_from_rgb((176,175,179)),background=_from_rgb((41,40,46)),command=self.updateLed)
        self.progressbar = ttk.Progressbar(self.window,maximum=nbimg,variable=self.varprogress,orient ="horizontal",mode ="determinate")
        #Camera
        #On récupère la taille de la fenêtre
        self.camerapreviewX = 400
        self.camerapreviewY = int(self.camerapreviewX * 3 / 4)
        self.cameraposX= int((self.window.winfo_screenwidth() / 2) - (self.camerapreviewX / 2))
        self.cameraposY= int((self.window.winfo_screenheight() / 2) - (self.camerapreviewY / 2))
        #print("cameraposX = "+ str(self.cameraposX))
        #On crée une frame pour décaler les boutons autour
        #self.frameCamera = Frame(self.frame,background=_from_rgb((100,100,100)),width=self.camerapreviewX+20, height=self.camerapreviewY+50)
        
        self.startPreview()
        self.afficher()

    def afficher(self):
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.frame, 0, weight=1)
        Grid.rowconfigure(self.frame, 1, weight=5)
        Grid.rowconfigure(self.frame, 2, weight=1)
        Grid.rowconfigure(self.frame, 3, weight=1)
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=5)
        Grid.columnconfigure(self.frame, 2, weight=1)
        #Grid.rowconfigure(self.frameCamera, 0, weight=1)
        #Grid.columnconfigure(self.frameCamera, 0, weight=1)
        self.frame.grid(row=0,column=0,sticky='nsew')
        self.boutonRetour.grid(row=0, column=0,sticky='nsew')
        self.labelProjet.grid(row=0,column=1,sticky="nsew")
        self.boutonOk.grid(row=0, column=2,sticky='nsew')
        self.sliderExpo.grid(row=1,column=0,sticky='nsew')
        #self.frameCamera.grid(row=1,column=1,sticky='news')
        self.boutonFrameCamera.grid(row=1,column=1,sticky='nsew') #dans le frame camera
        self.sliderLed.grid(row=1,column=2,sticky='nsew')
        self.labelExpo.grid(row=2,column=0,pady=50,sticky='nsew')
        self.labelLed.grid(row=2,column=2,pady=50,sticky='nsew')
        self.progressbar.grid(row=3,column=0,sticky="ew")
        self.boutonFrameCamera.configure(state='disabled')

    def startPreview(self):
        #Lancement Camera
        self.labelProjet.configure(text=nomprojet)
        self.window.update()
        self.window.update_idletasks()
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.camerapreviewX,self.camerapreviewY)
        self.camera.exposure_compensation = 0
        self.camera.iso=100
        self.camera.rotation = 180
        self.camera.awb_mode= 'auto'
        time.sleep(0.5)
        self.camera._check_camera_open()
        self.camera.preview_fullscreen = False
        self.camera.preview_window = (self.cameraposX,self.cameraposY,self.camerapreviewX,self.camerapreviewY)
        self.camera.start_preview()
        self.boutonFrameCamera.configure(state='disabled')
        zero()
        LED(1)

    def fermerFenetreCapture(self):
        zero()
        self.camera.stop_preview()
        self.camera.close()
        self.window.destroy()

    def OuvreTextEntry(self):
        self.camera.stop_preview()
        self.camera.close()
        #self.window.destroy()
        fenetreTextEntry = TextEntry(self.master)
        self.window.destroy()
        self.__init__(self.master)
        self.startPreview(self)
        self.boutonFrameCamera.configure(state='active')
        print("on ouvre la fenetre de saisieTexte")

    def updateExposure(self,abc):
        self.camera.exposure_compensation = self.sliderExpo.get()
        #print(str(self.camera.exposure_compensation))

    def updateLed(self,abc):
        zero()
        LED(ledposition[int(self.sliderLed.get())])

    def startCapture(self):
        global nbimg
        global CAMERASPEED
        global EXPOSURECOMPENSATION
        EXPOSURECOMPENSATION = self.sliderExpo.get()
        CAMERASPEED = self.camera.exposure_speed
        self.camera.shutter_speed= CAMERASPEED
        print("shutter_speed = "+ str(CAMERASPEED))
        print("exposure_compensation = "+ str(EXPOSURECOMPENSATION))
        self.camera.awb_mode = 'off'
        AWB_GAINS = self.camera.awb_gains
        self.camera.stop_preview()
        self.camera.close()
        time.sleep(0.1)
        #self.window.destroy()
        self.sliderExpo.configure(state='disabled')
        self.sliderLed.configure(state='disabled')
        self.boutonOk.configure(state='disabled')
        self.boutonRetour.configure(state='disabled')
        self.labelProjet.configure(state='disabled')

        #Camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1640, 1232) #3280 × 2464 
        self.camera.iso=100
        self.camera.rotation = 180
        self.camera.preview_fullscreen = False
        self.camera.preview_window = (self.cameraposX,self.cameraposY,self.camerapreviewX,self.camerapreviewY)
        time.sleep(0.2)
        self.camera._check_camera_open()
        zero2()
        LED2(ledposition[int(0)])
        """
        gp.output(latchPin, False)
        gp.output(dataPin, True)
        time.sleep(0.01)
        gp.output(clockPin, True)
        time.sleep(0.01)
        gp.output(clockPin, False)
        time.sleep(0.01)
        gp.output(dataPin, False)
        gp.output(latchPin, True)
        time.sleep(0.01)
        """
        self.camera.start_preview()
        time.sleep(1)
        self.camera.exposure_mode = 'off'
        self.camera.shutter_speed= CAMERASPEED
        self.camera.exposure_compensation = EXPOSURECOMPENSATION
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = AWB_GAINS
        ##############
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        ##############
        """
        """
        gp.output(dataPin, False)

        for i in range(0,nbimg):
            """gp.output(dataPin, False)
            gp.output(latchPin, False)
            time.sleep(0.1)
            gp.output(clockPin, True)
            time.sleep(0.1)
            gp.output(clockPin, False)
            time.sleep(0.1)
            gp.output(latchPin, True)
            time.sleep(0.5)
            """
            LED2(ledposition[int(i)])
            time.sleep(0.5)
            self.camera.capture(PATHTMP +'{0:02d}'.format(i)+".jpg",format='jpeg',quality=95,use_video_port=True)
            self.varprogress.set(int(i))
            self.window.update()
            self.window.update_idletasks()
        self.camera.stop_preview()


        ##############
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        #    PDV.   #
        ##############
        zero()
        self.boutonOk.configure(command=self.Continuer,text="Continuer")
        self.txtboutonFrameCamera.set("Fin de la prise de vue")
        self.boutonOk.configure(state='active')
        self.boutonRetour.configure(state='active')
        self.camera.close()

    def pdv(self,img):
        imagepath = PATHTMP +'{0:02d}'.format(img)+".jpg"
        print("On prend la photo numéro : "+str(imagepath))
        self.camera.capture(imagepath,format='jpeg',quality=100,use_video_port=True)

    def Continuer(self):
        zero()
        self.movefiles()
        self.window.destroy()

    def movefiles(self):
        global nomprojet
        dossierprojet = PATHPROJET + nomprojet
        os.system("mkdir "+dossierprojet)#Cree un nouveau repertoire pour un projet
        #os.system("mkdir "+PATHPROJET+str(num)+"/miniature") 
        cmd1 = "cp "+PATHTMP+"01.jpg "+PATHTMP+"miniature.jpg"
        cmd2 = "convert "+PATHTMP+"miniature.jpg -thumbnail 320x240 "+PATHTMP+"miniature.jpg"
        #find src_image_dir/ -type f -name '*.jpg' -print0 | xargs -0r mv -t dst_image_dir/
        #cmd3 = "mv "+PATHTMP+"*.jpg "+dossierprojet
        cmd3 = "find "+PATHTMP+" -type f -name '*.jpg' -print0 | xargs -0r mv -t "+dossierprojet
        os.system(cmd1)
        os.system(cmd2)
        os.system(cmd3) #deplace les photos dans ce repertoire

class TextEntry:

    def __init__(self, master):
        # management fenetre
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.attributes("-fullscreen",True)
        self.window.configure(background=_from_rgb((41,40,46)))
        #Frame
        self.frame = Frame(self.window,background=_from_rgb((41,40,46))) 
        self.framekeyboard = Frame(self.window,background=_from_rgb((41,40,46))) #,height=50,width=10
        #Images
        self.iconeretour = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRetour.png").resize((75,75),Image.BILINEAR))
        self.imageOk = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeOk.png").resize((75,75),Image.BILINEAR))
        #Boutons
        self.boutonOk = Button(self.frame, text="Capture", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",width = 75, height = 75,background=_from_rgb((41,40,46)), compound=TOP, command=self.ValiderNom)
        self.boutonRetour = Button(self.frame, text="Retour", image=self.iconeretour,foreground=_from_rgb((176,175,179)),relief="flat",width = 75, height = 75,background=_from_rgb((41,40,46)),compound=TOP, command=self.fermerFenetreCapture)
        self.buttons = [
                    'a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','7','8','9',
                    'q', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l','m','4','5','6',
                    'w', 'x', 'c', 'v', 'b', 'n', 'VIDE','1','2','3',
                    'SPACE','BACK','0'
                    ]           
        self.entry = Entry(self.frame,font=('TkDefaultFont',20,'bold')) #,width=50
        self.entry.insert(END,str(nomprojet))
        self.afficher()

    def afficher(self):
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.window, 1, weight=2)
        Grid.columnconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 0, weight=0)
        Grid.columnconfigure(self.frame, 1, weight=3)
        Grid.columnconfigure(self.frame, 2, weight=0)
        #frame en 0 0
        #keyboard en 1 0
        self.frame.grid(row=0,column=0,sticky='nsew')
        self.framekeyboard.grid(row=1,column=0,sticky='nsew')
        self.boutonOk.grid(row=0, column=2,sticky='nsew')
        self.entry.grid(row=0,column=1,sticky='nsew')
        self.boutonRetour.grid(row=0, column=0,sticky='nsew')
        varRow = 2
        varColumn = 0

        for button in self.buttons:
            self.command = lambda x=button: self.select(x)
            if button == "SPACE" or button == "BACK":
                tk.Button(self.framekeyboard,text= button, background=_from_rgb((41,40,46)), foreground=_from_rgb((176,175,179)),
                    activebackground = "#ffffff", activeforeground="#3c4987", relief='flat', padx=0,
                    pady=0, bd=0,command=self.command).grid(row=varRow,column=varColumn,columnspan=5,sticky='nsew') #,width=15
                varColumn+=5
            elif button == "VIDE":
                tk.Label(self.framekeyboard,text= button, bg=_from_rgb((41,40,46)), foreground=_from_rgb((41,40,46)),
                    activebackground = "#ffffff", activeforeground="#3c4987", relief='flat', padx=1,
                    pady=1, bd=0).grid(row=varRow,column=varColumn,columnspan=5,sticky='nsew') #,width=4
                varColumn+=3
            elif button == "BACK":
                tk.Button(self.framekeyboard,text= button, bg=_from_rgb((41,40,46)), foreground=_from_rgb((176,175,179)),
                    activebackground = "#ffffff", activeforeground="#3c4987", relief='flat', padx=0,
                    pady=0, bd=0,command=self.command).grid(row=varRow,column=varColumn,columnspan=1,sticky='nsew') #,width=15
                varColumn+=3
            else:
                tk.Button(self.framekeyboard,text= button, bg=_from_rgb((41,40,46)), foreground=_from_rgb((176,175,179)),
                    activebackground = "#ffffff", activeforeground="#3c4987", relief='flat', padx=1,
                    pady=1, bd=1,font=('TkDefaultFont',20,'bold'),command=self.command).grid(row=varRow,column=varColumn,sticky='nsew') #,width=4
            varColumn +=1 
            if varColumn > 12 and varRow == 2:
                varColumn = 0
                varRow+=1
            if varColumn > 12 and varRow == 3:
                varColumn = 0
                varRow+=1
            if varColumn > 12 and varRow == 4:
                varColumn = 0
                varRow+=1
            Grid.columnconfigure(self.framekeyboard, varColumn, weight=1)
            Grid.rowconfigure(self.framekeyboard, varRow, weight=1)

    def ValiderNom(self):
        global nomprojet
        print(self.entry.get())
        nomprojet=str(self.entry.get())
        #if os.path.exists(PATHPROJET + nomprojet):
        #fenetreCapture = FenetreCapture(self.master)
        self.window.destroy()
    def fermerFenetreCapture(self):
        #fenetreCapture = FenetreCapture(self.master)
        self.window.destroy()
    def select(self,value):
        if value == "BACK":
            self.entry.delete(len(self.entry.get())-1,END)
            
        elif value == "SPACE":
            self.entry.insert(END, ' ')
        else :
            self.entry.insert(END,value)

class RevueProjet:
    
    def __init__(self,master):
        #variables
        self.logtext = StringVar()
        self.logtext.set("Hello")
        #management fenetre
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.attributes("-fullscreen",True)
        self.window.configure(background=_from_rgb((41,40,46)))
        self.frame = Frame(self.window,background=_from_rgb((41,40,46)))
        self.framevalider = Frame(self.window,background=_from_rgb((41,40,46)))
        #images
        self.iconeretour = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRetour.png").resize((75,75),Image.BILINEAR))
        self.imageOk = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeOk.png").resize((75,75),Image.BILINEAR))
        self.photoFermer = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeAnnuler.png").resize((75,75),Image.BILINEAR))
        #bouttons
        self.boutonOk1 = Button(self.frame, text="Copie Projet", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP, command=self.CopyOne)
        self.boutonOk2 = Button(self.frame, text="Copie TOUT", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP, command=self.CopyAll)
        self.boutonSuppr1 = Button(self.frame, text="Supprimer un projet",relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)),command=self.DeleteOne)
        self.boutonSuppr2 = Button(self.frame, text="Supprimer tous les projets",font=('TkDefaultFont',20,'bold'),relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)),command=self.DeleteAll)
        self.boutonRetour = Button(self.frame, text="Retour", image=self.iconeretour,foreground=_from_rgb((176,175,179)),relief="flat",width = 75, height = 75,background=_from_rgb((41,40,46)),compound=TOP, command=self.window.destroy)
        #self.boutonOk = Button(self.window,text = "Ok",image=self.imageOk,cursor="tcross",command=self.visionage3D)
        #preview
        self.previewPhoto = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"fondProjet.png"))
        self.label = Label(self.frame,text="Preview",image=self.previewPhoto)
        self.loglabel = Label(self.frame,textvariable=self.logtext,foreground=_from_rgb((176,175,179)),background=_from_rgb((41,40,46)),relief="flat", anchor="w", justify="left")
        #scrollbar
        self.scrollbar = Scrollbar(self.frame)
        #listbox
        liste = os.listdir(PATHPROJET)
        liste.sort()
        #print (liste)
        NomProjet = StringVar(value = liste)
        self.listeProjet = Listbox(self.frame, yscrollcommand = self.scrollbar.set,font=('TkDefaultFont',15,'bold'))
        for projet in liste:
            self.listeProjet.insert(END,projet) 
        self.listeProjet.bind("<<ListboxSelect>>", self.selection)
        self.scrollbar.config(command=self.listeProjet.yview)
        listeUSB = os.listdir(PATHUSB)
        self.logtext.set("Espace libre sur microdome: "+getfreespace('/')+" Gb")
        if not len(listeUSB):
            self.logtext.set(self.logtext.get()+"\nPas de clé branchée")
        else: 
            usbname= ''.join(listeUSB)
            spacecle = str(getfreespace("/media/pi/"+str(usbname)))
            self.logtext.set(self.logtext.get()+"\nClé USB detectée")
            self.logtext.set(self.logtext.get()+"\nEspace libre sur "+ usbname+": "+spacecle+" Gb")
        #affiche le tout
        self.afficher()
        
    def selection(self,event):
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        print("Projet : "+projetSelectionner)
        previewPilPhoto = Image.open(PATHPROJET+projetSelectionner+"/miniature.jpg")
        self.previewPhoto = ImageTk.PhotoImage(previewPilPhoto)
        self.label.configure(image = self.previewPhoto)
        self.label.image = self.previewPhoto
        #self.master.update()
        
    def update(self):
        #listbox
        liste = os.listdir(PATHPROJET)
        liste.sort()
        #print (liste)
        NomProjet = StringVar(value = liste)
        self.listeProjet('0','end')
        for projet in liste:
            self.listeProjet.insert(END,projet) 
        self.listeProjet.bind("<<ListboxSelect>>", self.selection)
        self.window.update()
        self.window.update_idletasks()
        
    def afficher(self):
        Grid.rowconfigure(self.window, 0, weight=60)
        Grid.columnconfigure(self.window, 0, weight=100)
        Grid.rowconfigure(self.frame, 0, weight=10)
        Grid.rowconfigure(self.frame, 1, weight=40)
        Grid.rowconfigure(self.frame, 2, weight=10)
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=1)
        Grid.columnconfigure(self.frame, 2, weight=25)
        Grid.columnconfigure(self.frame, 3, weight=25)        
        self.frame.grid(row=0,column=0,sticky='nesw')
        self.listeProjet.grid(row=1,column=0,sticky='nesw')
        self.scrollbar.grid(row=1,column=1,sticky='nesw')
        self.label.grid(row=1,column=2,columnspan=2, sticky='nesw')
        self.loglabel.grid(row=2,column=0,columnspan=2,sticky='nsew')
        self.boutonRetour.grid(row=0,column=0,columnspan=2,sticky='nesw')
        self.boutonOk1.grid(row=0,column=2,sticky='nesw')
        self.boutonOk2.grid(row=0,column=3,sticky='nesw')
        self.boutonSuppr1.grid(row=2,column=2,sticky='nesw')
        self.boutonSuppr2.grid(row=2,column=3,sticky='nesw')

        
        #self.boutonOk.grid(row=3,column=4)
    def CopyOne(self):
        listeUSB = os.listdir(PATHUSB)
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        if not len(listeUSB):
            print ("Pas de clé branchée")
        else: 
            usbname= ''.join(listeUSB)
            usbname= usbname.replace(" ","\\ ")
            print("USB NAME:"+ usbname)
            cmd = r"rsync -ruv "+PATHPROJET+""+projetSelectionner+" /media/pi/"+str(usbname)+""
            print(cmd)
            self.logtext.set(self.logtext.get()+"\nCopie de "+projetSelectionner+" en cours")
            self.window.update_idletasks()
            os.system(cmd)
            self.logtext.set(self.logtext.get()+"\nCopie terminée")
            
    def CopyAll(self):
        listeUSB = os.listdir(PATHUSB)        
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        if not len(listeUSB):
            print ("Pas de clé branchée")
        else: 
            usbname= ''.join(listeUSB)
            usbname= usbname.replace(" ","\\ ")
            print("USB NAME:"+ usbname)
            cmd = r"rsync -ruv "+PATHPROJET+" /media/pi/"+str(usbname)+""
            print(cmd)
            os.system(cmd)
            
    def DeleteOne(self):
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        self.frame.destroy()
        self.label1=Label(self.framevalider, text="Etes vous sûr de vouloir supprimer: "+projetSelectionner,font=('TkDefaultFont',20,'bold'))
        self.buttonYes=Button(self.framevalider, text="OUI",relief="flat",foreground=_from_rgb((176,175,179)),image=self.imageOk,compound=TOP,background=_from_rgb((41,40,46)), command=lambda:self.DeleteOnebis(projetSelectionner))
        self.buttonNon=Button(self.framevalider, text="NON",relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)), command=lambda:self.Nopenopenope())
        self.framevalider.pack(fill="both",expand=True)
        self.framevalider.grid_rowconfigure(0,weight=1)
        self.framevalider.grid_columnconfigure(0,weight=1)
        self.label1.pack(fill="x")
        self.buttonYes.pack(fill='both',expand=True,side='left')
        self.buttonNon.pack(fill='both',expand=True,side='right')

    def Nopenopenope(self):
        self.framevalider.destroy()
        self.window.destroy()
        self.__init__(self.master)

    def DeleteOnebis(self,projetSelectionner):
        listeUSB = os.listdir(PATHUSB)
        cmd = r"rm -rf "+PATHPROJET+""+projetSelectionner+""
        print(cmd)
        os.system(cmd)
        self.framevalider.destroy()
        self.window.destroy()
        self.__init__(self.master)
        
      
    def DeleteAll(self):
        self.frame.destroy()
        self.label1=Label(self.framevalider, text="Etes vous sûr de vouloir TOUT supprimer??",font=('TkDefaultFont',20,'bold'))
        self.buttonYes=Button(self.framevalider, text="OUI",relief="flat",foreground=_from_rgb((176,175,179)),image=self.imageOk,compound=TOP,background=_from_rgb((41,40,46)), command=lambda:self.DeleteAllbis())
        self.buttonNon=Button(self.framevalider, text="NON",relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)), command=lambda:self.Nopenopenope())
        self.framevalider.pack(fill="both",expand=True)
        self.framevalider.grid_rowconfigure(0,weight=1)
        self.framevalider.grid_columnconfigure(0,weight=1)
        self.label1.pack(fill="x")
        self.buttonYes.pack(fill='both',expand=True,side='left')
        self.buttonNon.pack(fill='both',expand=True,side='right')

    def DeleteAllbis(self):
        cmd = r"rm -rf "+PATHPROJET+""
        print(cmd)
        #os.system(cmd)
        self.framevalider.destroy()
        self.window.destroy()
        self.__init__(self.master)
        
    def visionage3D(self):
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        #os.system("meshlab "+PATHPROJET+projetSelectionner+"/C3DC_QuickMac.ply")
        print("Vous avez séléctionné ce projet!")


class Reglages:

    def __init__(self, master):
        # management fenetre
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.attributes("-fullscreen",True)
        self.window.configure(background=_from_rgb((41,40,46)))
        #Frame
        self.frametitre = Frame(self.window,background=_from_rgb((41,40,46))) 
        self.framereglages = Frame(self.window,background=_from_rgb((41,40,46))) #,height=50,width=10
        #Images
        self.iconeretour = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRetour.png").resize((75,75),Image.BILINEAR))
        self.imageOk = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeOk.png").resize((75,75),Image.BILINEAR))        
        self.photoCamera = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconePhoto.png").resize((186,154),Image.BILINEAR)) #945 × 780
        self.photoSettings = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeSettings.png").resize((75,75),Image.BILINEAR))
        #Boutons
        self.boutonOk = Button(self.frametitre, text="Valider", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",width = 75, height = 75,background=_from_rgb((41,40,46)), compound=TOP, command=self.Valider)
        self.boutonRetour = Button(self.frametitre, text="Retour", image=self.iconeretour,foreground=_from_rgb((176,175,179)),relief="flat",width = 75, height = 75,background=_from_rgb((41,40,46)),compound=TOP, command=self.fermerFenetre)
        self.labeltitre = Label(self.frametitre, text="Réglages", image=self.photoSettings,foreground=_from_rgb((176,175,179)),relief="flat",compound=TOP,background=_from_rgb((41,40,46)))
        self.boutonMAP = Button(self.frametitre, text="Mise au point microdome",foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)),image=self.photoCamera,compound=TOP,cursor="tcross",command=self.LancerMAP)        
        #Paramètres
        self.afficher()

    def afficher(self):
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.window, 1, weight=5)
        Grid.columnconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.frametitre, 0, weight=1)
        Grid.columnconfigure(self.frametitre, 0, weight=0)
        Grid.columnconfigure(self.frametitre, 1, weight=3)
        Grid.columnconfigure(self.frametitre, 2, weight=0)
        Grid.rowconfigure(self.framereglages, 0, weight=1)
        Grid.columnconfigure(self.framereglages, 0, weight=1)
        #frame en 0 0
        #keyboard en 1 0
        self.frametitre.grid(row=0,column=0,sticky='nsew')
        self.framereglages.grid(row=1,column=0,sticky='nsew')
        self.boutonRetour.grid(row=0, column=0,sticky='nsew')
        self.labeltitre.grid(row=0, column=1,sticky='nsew')
        self.boutonOk.grid(row=0, column=2,sticky='nsew')
        self.boutonMAP.grid(row=2,column=1,sticky='news')
        
    def LancerMAP(self):
        self.camerapreviewX = 600
        self.camerapreviewY = int(self.camerapreviewX * 3 / 4)
        self.cameraposX= int((self.window.winfo_screenwidth() / 2) - (self.camerapreviewX / 2))
        self.cameraposY= int((self.window.winfo_screenheight() / 2) - (self.camerapreviewY / 2))
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.camerapreviewX,self.camerapreviewY)
        self.camera.exposure_compensation = 0
        self.camera.iso=100
        self.camera.rotation = 180
        self.camera.awb_mode= 'auto'
        self.camera.zoom= (0.4,0.4,0.25,0.25)
        time.sleep(0.5)
        self.camera._check_camera_open()
        self.camera.preview_fullscreen = False
        self.camera.preview_window = (self.cameraposX,self.cameraposY,self.camerapreviewX,self.camerapreviewY)
        self.camera.start_preview()
        lightpreview()

    def Valider(self):
        zero()
        self.camera.stop_preview()
        self.camera.close()
        self.window.destroy()
    def fermerFenetre(self):
        zero()
        self.camera.stop_preview()
        self.camera.close()
        self.window.destroy()

##################
#   Fonctions   #
##################

def ConfigNumImage(Path): #num de l'image
    numero = 0
    while True :
        file = '{0:02d}'.format(numero) + "pic.jpg"
        if os.path.isfile(Path+file) :
            numero+=1
            continue
        else :
            return numero

def ConfigNumProjet(Path):
    numero = 0
    while True:
        projet = str(numero)
        if os.path.exists(Path +"Projet"+ projet):
            numero += 1
            continue
        else:
            return str(numero).zfill(2)

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb 

def configGPIO(): #configue des pins gpio
    gp.setwarnings(False)
    gp.setmode(gp.BOARD)
    gp.setup(latchPin, gp.OUT)
    gp.output(latchPin, False)
    gp.setup(clockPin, gp.OUT)
    gp.output(clockPin, False)
    gp.setup(dataPin, gp.OUT)
    gp.output(dataPin, False)

def ShiftOut2(val):
    if type(val) is bytes:
        val=val[0]
    gp.output(latchPin, 0)
    for x in range(8):
        gp.output(dataPin, (val >> x) & 1)
        gp.output(clockPin, 1)
        gp.output(clockPin, 0)
        gp.output(latchPin, 1)

def shiftOut (dataPin, cPin, order, val):
    #print(val)
    if type(val) is bytes:
        val=val[0]
    if (order == "MSBFIRST"):
        for i in range(7,-1,-1):
            #print("La valeur du bit n°"+str(i)+" est "+str((val >> i) & 0b00000001))
            if (val >> i) & 1 == True:
                gp.output(dataPin, True) 
                #print("1")
            else:
                gp.output(dataPin, False)
            time.sleep(0.0001)
            gp.output(cPin, True)
            time.sleep(0.0001)
            gp.output(cPin, False)
            gp.output(dataPin, False)
            time.sleep(0.0001)
    else:
        print("LSB")
        for i in range(0,7,1):
            if (val >> i) & 1 == True:
                gp.output(dataPin, False) 
            else:
                gp.output(dataPin, True)
            gp.output(cPin, True) 
            gp.output(cPin, False) 

def zero():
    gp.output(latchPin, False)
    time.sleep(0.001)
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    time.sleep(0.001)
    gp.output(latchPin, True)

def zero2():
    #BitBang flush 0 on all Leds
    gp.output(latchPin, False)
    time.sleep(0.001)
    gp.output(dataPin, False)
    time.sleep(0.0001)
    for i in range(0,64):
        gp.output(clockPin, True)
        time.sleep(0.0001)
        gp.output(clockPin, False)
        time.sleep(0.0001)
    time.sleep(0.0001)
    gp.output(latchPin, True)
# Créer une class LedController
def lightpreview():
    gp.output(latchPin, False)
    time.sleep(0.001)
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x01');
    time.sleep(0.001)
    gp.output(latchPin, True)


def LED(ledindex):
    gp.output(latchPin, False)
    time.sleep(0.001)
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00');
    bras=int(ledindex/8)
    for k in range(bras+1,nbbras,1):
        shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00')  
    #On verifie quel Led dans quel ordre on allume  
    led = tabled[int(ledindex %8)]
    print("On allume la led "+str(int(ledindex % 8)+1)+" de valeur "+str(led)+" du bras "+str(bras+1))
    shiftOut(dataPin, clockPin, "MSBFIRST", int(led))  
    for j in range(0,bras,1):
        shiftOut(dataPin, clockPin, "MSBFIRST", b'\x00') 
        #print("00000000-apres")
    time.sleep(0.001)
    gp.output(latchPin, True)
    print("Led allumée")

def LED2(ledindex):
    bras=int(ledindex/8)
    led = tabled[int(ledindex %8)]
    for k in range(bras+1,nbbras,1):
        ShiftOut2(b'\x00')  
    ShiftOut2(led)  
    for j in range(0,bras,1):
        ShiftOut2(b'\x00') 

def getfreespace(var):
    total,used,free=shutil.disk_usage(var)
    return str((free // (2**30)))

#################
#    Main     #
#################
    
def main():
    configGPIO()
    zero()
    global nomprojet
    global defaultprojet
    os.system("rm "+PATHTMP+"*")
    #num = ConfigNumProjet(PATHPROJET)
    fenetrePrincipale = FenetrePrincipale()
    fenetrePrincipale.afficher()
    fenetrePrincipale.mainloop()


#demarre le programme
main()