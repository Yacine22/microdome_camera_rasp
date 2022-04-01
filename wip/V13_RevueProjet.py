class RevueProjet:
    
    def __init__(self,master):
        #management fenetre
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.attributes("-fullscreen",True)
        self.window.configure(background=_from_rgb((41,40,46)))
        self.frame = Frame(self.window,background=_from_rgb((41,40,46))) 
        #images
        self.iconeretour = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeRetour.png").resize((75,75),Image.BILINEAR))
        self.imageOk = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeOk.png").resize((75,75),Image.BILINEAR))
        self.photoFermer = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"IconeAnnuler.png").resize((75,75),Image.BILINEAR))
        #bouttons
        self.boutonOk1 = Button(self.frame, text="Copie Projet", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP, command=self.CopyOne)
        self.boutonOk2 = Button(self.frame, text="Copie TOUT", image=self.imageOk,foreground=_from_rgb((176,175,179)),relief="flat",background=_from_rgb((41,40,46)), compound=TOP, command=self.CopyAll)
        self.boutonSuppr1 = Button(self.frame, text="Suppr Projet",relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)),command=self.DeleteOne)
        self.boutonSuppr2 = Button(self.frame, text="Suppr TOUT",relief="flat",foreground=_from_rgb((176,175,179)),image=self.photoFermer,compound=TOP,background=_from_rgb((41,40,46)),command=self.DeleteAll)
        self.boutonRetour = Button(self.frame, text="Retour", image=self.iconeretour,foreground=_from_rgb((176,175,179)),relief="flat",width = 75, height = 75,background=_from_rgb((41,40,46)),compound=TOP, command=self.window.destroy)
        #self.boutonOk = Button(self.window,text = "Ok",image=self.imageOk,cursor="tcross",command=self.visionage3D)
        #preview
        self.previewPhoto = ImageTk.PhotoImage(Image.open(PATHRESSOURCES+"fondProjet.png"))
        self.label = Label(self.frame,text="Preview",image=self.previewPhoto)
        #scrollbar
        self.scrollbar = Scrollbar(self.frame)
        #listbox
        liste = os.listdir(PATHPROJET)
        liste.sort()
        #print (liste)
        NomProjet = StringVar(value = liste)
        self.listeProjet = Listbox(self.frame,yscrollcommand = self.scrollbar.set,font=('TkDefaultFont',15,'bold'))
        for projet in liste:
            self.listeProjet.insert(END,projet) 
        self.listeProjet.bind("<<ListboxSelect>>", self.selection)
        listeUSB = os.listdir(PATHUSB)
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
    
    def afficher(self):
        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)
        Grid.rowconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 0, weight=4)
        Grid.rowconfigure(self.frame, 1, weight=40)
        Grid.columnconfigure(self.frame, 1, weight=1)
        Grid.rowconfigure(self.frame, 2, weight=10)
        Grid.columnconfigure(self.frame, 2, weight=10)              
        self.scrollbar.grid(row=1,column=1,sticky='nesw')
        self.listeProjet.grid(row=1,column=0,sticky='nesw')
        self.frame.grid(row=0,column=0,sticky='nesw')
        self.label.grid(row=1,column=2,sticky='nesw')
        self.boutonRetour.grid(row=0,column=0,sticky='nesw')
        self.boutonOk1.grid(row=0,column=3,sticky='nesw')
        self.boutonOk2.grid(row=0,column=4,sticky='nesw')
        self.boutonSuppr1.grid(row=2,column=3,sticky='nesw')
        self.boutonSuppr2.grid(row=2,column=4,sticky='nesw')

        
        #self.boutonOk.grid(row=3,column=4)
    def CopyOne(self):
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        if not len(liste):
            print ("Pas de clé branchée")
        else: 
            usbname= ''.join(listeUSB)
            usbname= usbname.replace(" ","\\ ")
            print("USB NAME:"+ usbname)
            cmd = r"rsync -ruv "+PATHPROJET+""+projetSelectionner" /media/pi/"+str(usbname)+""
            print(cmd)
            os.system(cmd)
            
    def CopyAll(self):
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        if not len(liste):
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
        if not len(liste):
            print ("Pas de clé branchée")
        else: 
            usbname= ''.join(listeUSB)
            usbname= usbname.replace(" ","\\ ")
            print("USB NAME:"+ usbname)
            cmd = r"rm -rf "+PATHPROJET+""+projetSelectionner""
            print(cmd)
            #os.system(cmd)
        self.afficher()
            
    def visionage3D(self):
        projetSelectionner = self.listeProjet.get(self.listeProjet.curselection())
        #os.system("meshlab "+PATHPROJET+projetSelectionner+"/C3DC_QuickMac.ply")
        print("Vous avez séléctionné ce projet!")