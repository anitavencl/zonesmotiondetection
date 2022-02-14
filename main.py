# This is a sample Python script.

from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk
import os
from tkinter import filedialog
from tkinter import font
import cv2
import imutils
import math
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import timeit
import statistics


class Proakustik:
    """Handles Login and Register functions"""

    # initialization function, every class needs to inherit master window
    def __init__(self, master):
        self.master = master
        # initializing frame that holds login form
        self.login_frame = Frame(self.master, highlightbackground="black")
        self.login_frame.pack(pady=30)
        # logo
        im = PhotoImage(file="/Users/anitavencl/Documents/Fer/rad/proakustik/photofiles/unnamed.gif")
        im = im.zoom(15)  # with 250, I ended up running out of memory
        im = im.subsample(32)
        self.label = Label(self.login_frame, width=200, height=200)
        self.label.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys i
        self.label.configure(image=im)
        self.label.pack(side=TOP)

        # adding buttons for log in and registration
        Label(self.login_frame, text="").pack()
        Button(self.login_frame, text="Prijava", height="2", width="30", command=self.login).pack()
        Label(self.login_frame, text="").pack()
        Button(self.login_frame, text="Registracija", height="2", width="30", command=self.register).pack()
        Label(self.login_frame, text="").pack(ipady=20)  # label for more space under register button

        Label(self.login_frame, text=" ").pack(side="bottom")  # label for more space for exit btn
        self.btn_exit = Button(master, text="Izlaz", command=master.quit)
        self.btn_exit.pack(side="bottom")
        # button to proceed to the program, disabled when user not registered
        self.button_start = Button(self.login_frame, text="Dalje", state="disabled", command=self.beginProgram)
        self.button_start.pack()

    def beginProgram(self):
        """Open main window after user is signed in """
        self.login_frame.destroy()  # deleting windows that are no longer needed
        self.btn_exit.destroy()
        # creating instance of a class that will be used next
        p = DetectionOptionsWindow(self.master)
        self.master.mainloop()

    def login(self):
        """login function, user inputs his credentials"""

        # popup window login screen
        self.login_screen = Toplevel(self.master)
        self.login_screen.title("Prijava")
        self.login_screen.geometry("400x300")
        Label(self.login_screen, text="").pack()
        Label(self.login_screen, text="Korisničko ime i lozinka: ").pack()
        Label(self.login_screen, text="").pack()

        # username and password entered are string variables- so they can be easily changed and compared
        self.username_verify = StringVar()
        self.password_verify = StringVar()

        # loging in
        # username entry
        Label(self.login_screen, text="Korisničko ime:").pack()
        self.username_login_entry = Entry(self.login_screen, textvariable=self.username_verify)
        self.username_login_entry.pack()
        Label(self.login_screen, text="").pack()

        # password entry
        Label(self.login_screen, text="Lozinka:").pack()
        self.password_login_entry = Entry(self.login_screen, textvariable=self.password_verify, show="*")
        self.password_login_entry.pack()
        Label(self.login_screen, text="").pack()

        # try login with butotn
        Button(self.login_screen, text="Prijavi se", width=7, height=1, command=self.login_verify).pack()

    def login_verify(self):
        """checks if user can log in (if he is already registered)"""

        global username
        username = self.username_verify.get()  # if variable used is StringVar or IntVar, get() method must be called
        password = self.password_verify.get()
        self.username_for_greeting = username
        self.username_login_entry.delete(0,
                                         END)  # deleting text in entries, so its clean for next login attempt(if it happens)
        self.password_login_entry.delete(0, END)

        # checking for a file which contains user credentials, if it exists and password is correct eventLoginSucces() happens.
        # If user name file exists but password is wrong, event is eventWrongPassword().

        list_of_files = os.listdir()
        if username in list_of_files:
            file1 = open(username, "r")
            verify = file1.read().splitlines()
            if password in verify:
                self.eventLoginSucces()
            else:
                self.eventWrongPassword()
        else:
            self.eventUserNotFound()

    def eventLoginSucces(self):
        """Gives feedback to user if he has logged in successfully."""
        self.login_success_screen = Toplevel(self.login_screen)  # pop up window with success message
        self.login_success_screen.title("Uspjeh!")
        self.login_success_screen.geometry("150x100")
        Label(self.login_success_screen, text="").pack(ipady=3)
        Label(self.login_success_screen, text="Uspješna prijava!").pack()

        Button(self.login_success_screen, text="OK", command=self.deleteLoginSuccesWindow).pack()
        # activating "Next" button
        self.button_start.config(state="active")

    def deleteLoginSuccesWindow(self):
        """window in which login success was displayed"""
        self.login_success_screen.destroy()
        self.login_screen.destroy()

    def eventWrongPassword(self):
        """Gives feedback to user if wrong password was input."""
        self.wrong_password_screen = Toplevel(self.login_screen)
        self.wrong_password_screen.title("Greška")
        self.wrong_password_screen.geometry("200x100")
        Label(self.wrong_password_screen, text="Pogrešna lozinka, pokušajte ponovo", fg="red").pack()
        Button(self.wrong_password_screen, text="OK", command=self.deleteWrongPasswordWindow).pack()

    def deleteWrongPasswordWindow(self):
        """deleting window from wrong password event"""
        self.wrong_password_screen.destroy()

    def eventUserNotFound(self):
        """Gives feedback to user if wrong username was input."""
        self.user_not_found_screen = Toplevel(self.login_screen)
        self.user_not_found_screen.title("Pogreška : korisnik ne postoji!")
        self.user_not_found_screen.geometry("150x100")
        Label(self.user_not_found_screen, text="Korisnik ne postoji").pack()
        Button(self.user_not_found_screen, text="OK", command=self.deleteUserNotFoundWindow).pack()

    #
    def deleteUserNotFoundWindow(self):
        """Delete window with notification about wrong username."""
        self.user_not_found_screen.destroy()

    def register(self):
        """Handles admin registration process and  new user registration process"""
        self.register_screen = Toplevel(self.master)
        self.register_screen.title("Registracija")
        self.register_screen.geometry("350x350")

        self.admin_username = StringVar()
        self.admin_password = StringVar()

        Label(self.register_screen, text="Unesite instalaterske podatke \n za početak registracije",
              font=("calibri", 15)).pack(pady=5)
        Label(self.register_screen, text="").pack()

        label_username = Label(self.register_screen, text="Unesite korisničko ime :")
        label_username.pack()
        # entry for admin username
        self.username_entry = Entry(self.register_screen, textvariable=self.admin_username)
        self.username_entry.pack()

        label_password = Label(self.register_screen, text="Unesite lozinku:")
        label_password.pack()
        # entry for admin password
        self.password_entry = Entry(self.register_screen, textvariable=self.admin_password, show="*")
        self.password_entry.pack()

        Label(self.register_screen, text="").pack()
        Button(self.register_screen, text="Registracija", width=10, height=1, command=self.register_user).pack()

    def register_user(self):
        """Checks if admin credentials have been input."""
        username = self.admin_username.get()
        password = self.admin_password.get()

        if username.lower() == "admin" and password.lower() == "admin": self.registrationSucces()
        if username.lower() == "admin" and password.lower() != "admin": self.eventWrongAdminPass()
        if username.lower() != "admin" and password.lower() == "admin": self.eventWrongAdminName()
        if username.lower() != "admin" and password.lower() != "admin": self.eventWrongCredentials()

    def registrationSucces(self):
        """Lets user register with his new info, after successful admin registration."""

        global email_adress
        self.new_username = StringVar()
        self.new_password = StringVar()
        self.new_email = StringVar()
        # new user registration prompt
        self.registration_succes_screen = Toplevel(self.master)
        self.registration_succes_screen.title("Registracija uspješna!")
        self.registration_succes_screen.geometry("300x200")
        Label(self.registration_succes_screen, text="Registracija uspješna", fg="green", font=("calibri", 15)).pack(
            pady=5)
        Label(self.registration_succes_screen, text="Unesite podatke za daljnje prijave", font=("calibri", 14)).pack(
            pady=3)
        Label(self.registration_succes_screen, text="Novo korisničko ime", font=("calibri", 14)).pack()
        self.entry_username = Entry(self.registration_succes_screen, textvariable=self.new_username)
        self.entry_username.pack()
        Label(self.registration_succes_screen, text="Nova lozinka", font=("calibri", 14)).pack()
        self.entry_password = Entry(self.registration_succes_screen, textvariable=self.new_password, show="*")
        self.entry_password.pack()
        Label(self.registration_succes_screen, text="E-mail za slanje obavijesti", font=("calibri", 14)).pack()
        self.entry_email = Entry(self.registration_succes_screen, textvariable=self.new_email)
        self.entry_email.pack()
        email_adress = self.new_email
        self.btn_success_ok = Button(self.registration_succes_screen, text="Ok",
                                     command=self.deleteRegistrationSuccessWindow)
        self.btn_success_ok.pack()

    def deleteRegistrationSuccessWindow(self):
        """Saves new credentials and destroys all used windows and deletes entries"""
        username = self.entry_username.get()
        password = self.entry_password.get()
        email = self.new_email.get()

        # writing user info in a file that can be accessed later
        self.file = open(username, "w")
        self.file.write(username)
        self.file.write("\n")
        self.file.write(password)
        self.file.write("\n")
        self.file.write(email)
        self.file.close()

        self.entry_username.delete(0, END)
        self.entry_password.delete(0, END)
        self.registration_succes_screen.destroy()
        time.sleep(0.1)  # for better user experience
        self.register_screen.destroy()

    def eventWrongAdminPass(self):
        """Used for notifying user if worng admin pass has been used in pop up window"""
        self.wrong_admin_pass_screen = Toplevel(self.register_screen)
        self.wrong_admin_pass_screen.title("Pogrešna lozinka")
        self.wrong_admin_pass_screen.geometry("300x150")
        Label(self.wrong_admin_pass_screen, text="").pack(pady=2)
        Label(self.wrong_admin_pass_screen, text="Pogrešan instalaterski podatak: Lozinka.",
              font=("helvetica", 14, "bold")).pack()
        Label(self.wrong_admin_pass_screen, text="Pokušajte ponovno.").pack()
        Label(self.wrong_admin_pass_screen, text="").pack(pady=5)

        Button(self.wrong_admin_pass_screen, text="OK", command=self.deleteEventWrongAdminPassWindow).pack()

    def deleteEventWrongAdminPassWindow(self):
        """Delete entried and wrong admin pass screen"""
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.wrong_admin_pass_screen.destroy()

    def eventWrongAdminName(self):
        """Inform user that wrong adin name was input"""
        self.wrong_admin_name_screen = Toplevel(self.register_screen)
        self.wrong_admin_name_screen.title("Pogrešno korisničko ime")
        self.wrong_admin_name_screen.geometry("300x150")
        Label(self.wrong_admin_name_screen, text="").pack(pady=2)

        Label(self.wrong_admin_name_screen, text="Pogrešan instalaterski\n podatak: Korisničko ime.",
              font=("helvetica", 14, "bold")).pack()
        Label(self.wrong_admin_name_screen, text="Pokušajte ponovno.").pack()
        Button(self.wrong_admin_name_screen, text="OK", command=self.deleteEventWrongAdminNameWindow).pack(pady=5)

    def deleteEventWrongAdminNameWindow(self):
        """Delete entries and wrong admin username screen"""
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.wrong_admin_name_screen.destroy()

    def eventWrongCredentials(self):
        """Inform user that wrong credentials were input"""
        self.wrong_credentials_screen = Toplevel(self.register_screen)
        self.wrong_credentials_screen.title("Pogrešni kredencijali")
        self.wrong_credentials_screen.geometry("400x150")
        Label(self.wrong_credentials_screen, text="").pack()
        Label(self.wrong_credentials_screen, text="Pogrešni adminski kredencijali : Korisničko ime i lozinka",
              font=("helvetica", 14, "bold")).pack(pady=3)

        Label(self.wrong_credentials_screen,
              text="Pokušajte ponovno upisati adminske kredencijale .\n Ako ih ne znate, potražite u dokumentaciji programa.").pack()
        Label(self.wrong_credentials_screen, text="").pack(pady=5)
        Button(self.wrong_credentials_screen, text="OK", command=self.deleteEventWrongCredentialsWindow).pack()

    def deleteEventWrongCredentialsWindow(self):
        """Delete entries and wrong admin username and pass screen"""
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.wrong_credentials_screen.destroy()


class DetectionOptionsWindow:
    """User may choose one detection option"""

    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.pack(expand=TRUE, fill="y")
        Label(self.frame, text="").pack()
        self.greeting = Label(self.frame, text="Dobrodošli ", font=("american typewriter", 35))
        self.greeting.pack(side=TOP, pady=50)
        self.btn_exit = Button(self.master, text="Izlaz", command=self.master.quit)
        self.btn_exit.pack(side=BOTTOM)

        # frame, image and button for option 1
        self.frm_opt1 = Frame(self.frame)
        self.frm_opt1.pack(side=LEFT)
        # im = PhotoImage(file="/Users/anitavencl/Documents/Fer/rad/proakustik/photofiles/img1.png")
        im = PhotoImage(file="photofiles/img1.png")

        im = im.zoom(10)  # with 250, I ended up running out of memory
        im = im.subsample(32)
        self.lbl_img1 = Label(self.frm_opt1)
        self.lbl_img1.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys it
        self.lbl_img1.configure(image=im)
        self.lbl_img1.pack(side=TOP)
        self.btn_goto_poly_detect = Button(self.frm_opt1, text="Detekcija po zonama", command=self.beginZoneOptions)
        self.btn_goto_poly_detect.pack(side=BOTTOM)

        # frame, image and button for option 2
        self.frm_opt2 = Frame(self.frame)
        self.frm_opt2.pack(side=LEFT)
        im = PhotoImage(file="photofiles/img2.png")
        im = im.zoom(10)
        im = im.subsample(32)
        self.lbl_img2 = Label(self.frm_opt2)
        self.lbl_img2.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys it
        self.lbl_img2.configure(image=im)
        self.lbl_img2.pack(side=TOP)
        self.btn_goto_line_detect = Button(self.frm_opt2, text="Detekcija prelaska linije",
                                           command=self.beginLineOptions)
        self.btn_goto_line_detect.pack(side=BOTTOM)

        # frame, image and button for option 3
        self.frm_opt3 = Frame(self.frame)
        self.frm_opt3.pack(side=LEFT)
        im = PhotoImage(file="photofiles/img3.png")
        im = im.zoom(10)
        im = im.subsample(32)
        self.lbl_img3 = Label(self.frm_opt3)
        self.lbl_img3.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys it
        self.lbl_img3.configure(image=im)
        self.lbl_img3.pack(side=TOP)
        self.btn_goto_tracking = Button(self.frm_opt3, text="Detekcija ljudi", command=self.beginPersonOptions)
        self.btn_goto_tracking.pack(side=BOTTOM)

    def beginLineOptions(self):
        """Makes object of class that contains line detection options"""
        self.frame.destroy()
        self.btn_exit.destroy()
        p = LineOptions(self.master)
        self.master.mainloop()

    def beginZoneOptions(self):
        """Makes object of class that contains zone detection options"""
        self.frame.destroy()
        self.btn_exit.destroy()
        p = ZoneOptions(self.master)
        self.master.mainloop()

    def beginPersonOptions(self):
        """Makes object of class that contains people detection options"""
        self.frame.destroy()
        self.btn_exit.destroy()
        p = PersonOptions(self.master)
        self.master.mainloop()


class LineOptions:
    """Options for line detection parameters."""

    def __init__(self, master):
        self.master = master
        # all IntVars that are used in radio buttons are set to some default value
        self.selected1 = IntVar()
        self.selected2 = IntVar()
        self.selected3 = IntVar()
        self.selected4 = IntVar()
        self.selected1.set(2)
        self.selected2.set(2)
        self.selected3.set(2)
        self.selected4.set(1)
        self.g_noise = 15
        self.size_of_detection_area = 10000
        self.b_tresh = 50

        # main frame that holds all other frames
        self.frame = Frame(self.master)
        self.frame.pack()
        Label(self.frame, text="").pack()
        Label(self.frame, text="Odaberite opcije ili kliknite 'Dalje' za nastavak sa zadanim postavkama").pack(
            fill=BOTH, ipady=20)
        # second main frame, reason is that only that way page looks good
        self.frm_main = Frame(self.frame)
        self.frm_main.pack(side=TOP, ipady=20)

        # frame for detection area options
        self.frm_det_area_opt = Frame(self.frm_main, highlightbackground="gray", highlightthickness=1,
                                      highlightcolor="blue")
        self.frm_det_area_opt.pack(side=LEFT, padx=20)
        Label(self.frm_det_area_opt, text="Veličina detektiranog objekta:").pack()
        self.rad_det_area1 = Radiobutton(self.frm_det_area_opt, text="Mali", value=1, variable=self.selected1,
                                         command=self.chooseOption1)
        self.rad_det_area1.pack()
        self.rad_det_area2 = Radiobutton(self.frm_det_area_opt, text="Srednje", value=2, variable=self.selected1,
                                         command=self.chooseOption1)
        self.rad_det_area2.pack()
        self.rad_det_area3 = Radiobutton(self.frm_det_area_opt, text="Veliko", value=3, variable=self.selected1,
                                         command=self.chooseOption1)
        self.rad_det_area3.pack()

        # frame for noise options
        self.frm_noise_opt = Frame(self.frm_main, highlightbackground="gray", highlightthickness=1)
        self.frm_noise_opt.pack(side=LEFT, padx=20)
        Label(self.frm_noise_opt, text="Šum").pack()
        self.rad_noise1 = Radiobutton(self.frm_noise_opt, text="Mali", value=1, variable=self.selected2,
                                      command=self.chooseOption2)
        self.rad_noise1.pack()
        self.rad_noise2 = Radiobutton(self.frm_noise_opt, text="Srednje", value=2, variable=self.selected2,
                                      command=self.chooseOption2)
        self.rad_noise2.pack()
        self.rad_noise3 = Radiobutton(self.frm_noise_opt, text="Veliko", value=3, variable=self.selected2,
                                      command=self.chooseOption2)
        self.rad_noise3.pack()

        # frame for thresh options
        self.frm_thresh_opt = Frame(self.frm_main, highlightbackground="gray", highlightthickness=1)
        self.frm_thresh_opt.pack(side=LEFT, padx=20)
        Label(self.frm_thresh_opt, text="Osjetljivost:").pack()
        self.rad_thresh1 = Radiobutton(self.frm_thresh_opt, text="Mali", value=1, variable=self.selected3,
                                       command=self.chooseOption3)
        self.rad_thresh1.pack()
        self.rad_thresh2 = Radiobutton(self.frm_thresh_opt, text="Srednje", value=2, variable=self.selected3,
                                       command=self.chooseOption3)
        self.rad_thresh2.pack()
        self.rad_thresh3 = Radiobutton(self.frm_thresh_opt, text="Veliko", value=3, variable=self.selected3,
                                       command=self.chooseOption3)
        self.rad_thresh3.pack()

        self.btn_next = Button(self.frame, text="Dalje", command=self.beginLineDet)
        self.btn_next.pack()

        Label(self.frame, text="").pack()
        # info text about parameters
        text = "Veličina detektiranog objekta - minimalna veličina objekta koji će program detektirati \n Šum - vrijednost Gaussovog zamućenje koje filtrira šum, djeluje kao NP filtar \n "

        self.lbl_info = Label(self.frame, text=text)
        self.lbl_info.pack()

        self.btn_back = Button(self.frame, text="Nazad na izbornik", command=self.goBackToMenu)
        self.btn_back.pack()

    def goBackToMenu(self):
        self.frame.destroy()
        p = DetectionOptionsWindow(self.master)
        self.master.mainloop()

    # setting values for parameters has to be done in different function than where it has been chosen by the user because
    # .get() method cant get values that have been set inside the same funciton
    def chooseOption2(self):
        if self.selected2.get() == 1:
            self.g_noise = 11

        if self.selected2.get() == 3:
            self.g_noise = 31

    def chooseOption1(self):
        if self.selected1.get() == 1:
            self.size_of_detection_area = 5000

        if self.selected1.get() == 3:
            self.size_of_detection_area = 20000

    def chooseOption3(self):
        if self.selected3.get() == 1:
            self.b_tresh = 30

        if self.selected3.get() == 3:
            self.b_tresh = 70

    def beginLineDet(self):
        """Destroy previous windows and make instance of class for line detection"""
        self.frame.destroy()
        self.frm_det_area_opt.destroy()
        self.frm_noise_opt.destroy()
        self.frm_thresh_opt.destroy()
        self.btn_next.destroy()

        p = LineDetection(self.master, self.size_of_detection_area, self.g_noise, self.b_tresh)
        self.master.mainloop()


class LineDetection:
    """Main line detection class"""

    def __init__(self, master, size_of_detection_area, g_noise, b_tresh):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=0)
        # getting values from selected options
        self.size_of_detection_area = size_of_detection_area  # minimal area
        self.g_noise = g_noise  # Gaussian blur
        self.b_tresh = b_tresh  # binary threshold

        # welcome photo
        im = PhotoImage(file="photofiles/wait_photo.png")
        im = im.zoom(10)
        im = im.subsample(10)
        # frame that holds menu buttons Učitaj, Označi, Detekcija
        self.menu_frame = Frame(self.frame)
        self.menu_frame.grid(row=0, column=0, sticky="N", pady=25)  # Sticky da ostane gore, inače se pomicao
        self.l3 = Label(self.frame, text="")
        self.l3.grid(row=1, column=0)
        self.frm_go_back = Frame(self.frame, highlightbackground="black")
        self.frm_go_back.grid(row=2, column=0, sticky="S")
        self.item_frame = Frame(self.frame, width=600, height=400)
        self.item_frame.grid(row=0, column=1)
        # label for welcome photo
        self.lbl_img1 = Label(self.item_frame)
        self.lbl_img1.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys i
        self.lbl_img1.configure(image=im)
        self.lbl_img1.grid(column=0, row=0)

        # Menu buttons

        self.btn_menu1 = Button(self.menu_frame, text="Učitaj", command=self.loadingNewFile)
        self.btn_menu1.grid(row=0, column=0)
        self.btn_menu2 = Button(self.menu_frame, text="Označi", command=self.chooseArea)
        self.btn_menu2.grid(row=1, column=0)
        self.btn_menu3 = Button(self.menu_frame, text="Detekcija", command=self.preDetection)
        self.btn_menu3.grid(row=2, column=0)
        self.l1 = Label(self.menu_frame, text=" ").grid(row=3, column=0)
        self.l2 = Label(self.menu_frame, text=" ").grid(row=4, column=0)

        btn_go_back = Button(self.frm_go_back, text="Nazad na izbornik", command=self.beginOpenOptions)
        btn_go_back.grid(column=0, row=0)

        # Exit button
        self.btn_exit = Button(self.master, text="Izlaz", command=self.master.destroy)
        self.btn_exit.grid(row=5, column=3)

    def beginOpenOptions(self):
        """Destroy previous screens and proceed to line detection option screen"""

        self.frame.destroy()
        self.btn_exit.destroy()
        self.l3.destroy()
        p = LineOptions(self.master)
        self.master.mainloop()

    def loadingNewFile(self):
        """For choosing video source, it has 3 radio buttons, by clicking on one their proper functions are called"""

        self.clear(self.item_frame)
        self.lbl_info_choose_video = Label(self.item_frame, text="Izaberite jednu opciju :")
        self.lbl_info_choose_video.grid(column=0, row=0)

        # Radio Buttons for video option
        self.selected = IntVar()
        self.rad1 = Radiobutton(self.item_frame, text="Video", width=10, value=1, variable=self.selected,
                                command=self.chooseVideo)
        self.rad2 = Radiobutton(self.item_frame, text="Kamera", width=10, value=2, variable=self.selected,
                                command=self.chooseVideo)
        self.rad3 = Radiobutton(self.item_frame, text="RTSP", width=10, value=3, variable=self.selected,
                                command=self.chooseVideo)

        self.rad1.grid(column=0, row=1)
        self.rad2.grid(column=1, row=1)
        self.rad3.grid(column=2, row=1)
        # Stop video button
        self.btn_end = Button(self.item_frame, text="Zaustavi video", state="disabled", command=self.endVideo)
        self.btn_end.grid(column=0, row=5, columnspan=2)
        self.lbl_video = Label(self.item_frame)
        self.lbl_video.grid(column=0, row=4, columnspan=2)

    def chooseVideo(self):
        """Starts video from a source that user has choosen with radio buttons."""
        global cap
        # If you select that you want to load video from file
        if self.selected.get() == 1:
            self.video_path = filedialog.askopenfilename(filetypes=[  # opening system dialog where you choose the file
                ("all video format", ".mp4"),
                ("all video format", ".mov")])
            if len(self.video_path) > 0:  # if a file has been choosen
                self.btn_end.configure(state="active")  # activate the button that can stop the video
                self.rad1.configure(
                    state="disabled")  # disable buttons that chooses type of video, they will be enabled once video stream is over
                self.rad2.configure(state="disabled")
                self.cap = cv2.VideoCapture(self.video_path)
                self.showVideo()

        if self.selected.get() == 2:  # if you choose to stream from some kind of stream
            self.btn_end.configure(state="active")  # activate the button that can stop the video
            self.rad1.configure(
                state="disabled")  # disable buttons that chooses type of video, they will be enabled once video stream is over
            self.rad2.configure(state="disabled")
            self.video_path = 0
            self.cap = cv2.VideoCapture(self.video_path)
            self.showVideo()

    def showVideo(self):
        """Transforms images in proper format and shows video """

        self.ret, frame = self.cap.read()  # get frame from cap
        if self.ret == True:
            frame = imutils.resize(frame, width=600, height=400)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # color correcting
            # change format of frame 2 times so it can go on label
            self.im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=self.im)
            self.lbl_video.configure(image=img)  # images are shown on labels
            self.lbl_video.image = img
            self.lbl_video.after(10, self.showVideo)  # calling function every 10 miliseconds


        else:
            self.im = self.im.save("reference.jpg")  # save reference photo for drawing, later
            self.rad1.configure(state="active")
            self.rad2.configure(state="active")
            self.btn_end.configure(state="disabled")
            self.selected.set(0)  # unselect source
            self.cap.release()  # realise capturing device

    def endVideo(self):
        """Ends video if user clicks the button to end video"""
        self.ret = False
        self.im = self.im.save("reference.jpg")
        self.rad1.configure(state="active")
        self.rad2.configure(state="active")
        self.selected.set(0)
        self.cap.release()  # realise capturing device

    def clear(self, object):
        slaves = object.grid_slaves()
        for x in slaves:
            x.destroy()

    def chooseArea(self):
        """Handles all widgets and variables needed to draw polygons"""
        dim = (600, 400)
        coord = []
        self.list_of_points = []  # for saving coordinates of each click position

        self.clear(self.item_frame)  # clear screen of previous widgets
        Label(self.item_frame, text="Označite").grid(column=0, row=0)
        # Canvas for image and drawing
        self.canvas = Canvas(self.item_frame, bg="#e8e6e1", width=580, height=380, borderwidth=3, relief="solid")
        self.canvas.grid(column=0, row=1, padx=0, pady=0)
        image = Image.open("reference.jpg")  # reference image to draw on top of
        image = image.resize(dim)
        self.img_ref = ImageTk.PhotoImage(image)
        # canvas is created because its possible to draw on it
        self.canvas.create_image(0, 0, anchor=NW, image=self.img_ref)
        self.frm_buttons = Frame(self.item_frame)
        self.frm_buttons.grid(row=2, column=0)
        # restart function if user wants retry drawing
        self.btn_delete_line = Button(self.frm_buttons, text="Izbriši", command=self.chooseArea)
        self.btn_delete_line.grid(row=0, column=0, pady=10)
        # saving drawing and going in to detection
        self.btn_save_line = Button(self.frm_buttons, text="Spremi", command=self.preDetection)
        self.btn_save_line.grid(row=0, column=1, pady=10)

        # binding left mouse click - when user now clicks on a canvas it will start drawing a line
        self.canvas.bind("<Button-1>", self.drawLine)

    def drawLine(self, event):
        """Creates coordinates out of mouse clicks events-"""
        self.mouse_xy = (event.x, event.y)

        self.funcDrawLine(self.mouse_xy)

    def funcDrawLine(self, mouse_xy):
        """Draws points and a line after user defines it, it takes coordinates of latest mouse click as argument."""
        self.mouse_xy = mouse_xy
        # latest mouse click coordinates are now cordinates of points (2 points create a line)
        self.center_x, self.center_y = self.mouse_xy
        # making list of points, in this scenario only 2 points
        self.list_of_points.append((self.center_x, self.center_y))

        for self.pt in self.list_of_points:
            self.x, self.y = self.pt
            # draw dot over place clicked
            self.x1, self.y1 = (self.x - 1), (self.y - 1)
            self.x2, self.y2 = (self.x + 1), (self.y + 1)
            # drawing little ovals to emphasize where the points are
            self.canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill='green', outline='green', width=5)

            # just for drawing
            self.y11 = self.y1 - 45
            self.y22 = self.y2 - 45

        self.numberofPoint = len(self.list_of_points)

        if self.numberofPoint == 2:  # if 2 points exist, create a line
            self.canvas.create_line(self.list_of_points, fill="green", width=3)
            self.canvas.unbind("<Button-1>")  # unbind left mouse button
        else:
            print("Its a dot")

    def preDetection(self):
        """Initialises variables and widgets used for motion detection"""

        self.clear(self.item_frame)
        self.lbl_video = Label(self.item_frame, width=600, height=400, borderwidth=3, relief="solid")
        self.lbl_video.grid(column=1, row=1)

        # add buttons and options
        self.frame_detection_log = Frame(self.item_frame)
        self.frame_detection_log.grid(column=1, row=4, pady=10)
        self.lbl_is_detected = Label(self.frame_detection_log, width=8, height=3, bg="#b2e8a9", anchor=CENTER, padx=6)
        self.lbl_is_detected.grid(row=0, column=0)
        self.btn_detection_log = Button(self.frame_detection_log, text="Povijest detekcije", command=self.detectionLog)
        self.btn_detection_log.grid(row=1, column=0)
        self.i = IntVar()
        self.email_btn = Checkbutton(self.frame_detection_log, text="E-mail?", variable=self.i)
        self.email_btn.grid(row=2, column=0)
        self.cap = cv2.VideoCapture(self.video_path)

        global timestamp_list
        timestamp_list = []
        self.res_timestamp_list = []

        self.x1, self.y1 = self.list_of_points[0]  # points of drawn line
        self.x2, self.y2 = self.list_of_points[1]
        self.path = "photo_detection"  # for saving photos
        self.counter = 0

        time.sleep(1)  # for user experience (so it doesnt change too fast)
        self.detection()

    def detection(self):
        """This function handles loading new frames and displaying returned analysed frames"""

        ret, frame1 = self.cap.read()  # get frame from cap
        # for detection of movement
        ret, frame2 = self.cap.read()

        dim = (600, 400)

        if ret == True:

            frame = cv2.resize(frame1, dim)  # drugačiji resize jer se ovaj koristi za prikaz slike
            frame1 = cv2.resize(frame1, dim)  # a ovaj za cv2 radnje!!
            frame2 = cv2.resize(frame2, dim)
            frame = self.detection2(frame1, frame2)
            # change format of frames so it can be put on label
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            self.lbl_video.configure(image=img)
            self.lbl_video.image = img

            self.lbl_video.after(10, self.detection)

        else:

            self.cap.release()

    def detection2(self, frame1, frame2):
        """Image is edited and analysed for motion and location of motion if it exists"""

        isClosed = True
        color = (0, 200, 0)
        thickness = 2
        path = self.path

        self.frame1 = frame1
        self.frame2 = frame2

        dateTimeObj = datetime.now()  # for exact time of detection
        global timestamp_list

        email = self.i.get()  # get True or False for email

        diff = cv2.absdiff(frame1, frame2)  # Calc the difference between frames
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)  # Transform to grayscale
        blur = cv2.GaussianBlur(gray, (self.g_noise, self.g_noise), 0)  # Add Gaussian blur to filter noises
        _, thresh = cv2.threshold(blur, self.b_tresh, 250,
                                  cv2.THRESH_BINARY)  # Decide a threshold for turning into binary'
        dilated = cv2.dilate(thresh, None, iterations=30)  # Dilate all positive binary values
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # Make contours of them

        # line drawing
        frame1 = cv2.line(frame1, (self.list_of_points[0]), (self.list_of_points[1]), (0, 255, 0), 2)

        for contour in contours:
            if cv2.contourArea(contour) < self.size_of_detection_area: continue  # preskoci ako je premalo podrucje
            (x, y, w, h) = cv2.boundingRect(contour)

            # centroid of detected area
            xt = ((2 * x + w) / 2)
            yt = ((2 * y + h) / 2)

            # distance from the line to the centroid of detected area
            val = (abs((self.x2 - self.x1) * (yt - self.y1) - (self.y2 - self.y1) * (xt - self.x1))) / math.sqrt(
                (self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

            thresh = 60  # minimal pixel distance

            if val < thresh:

                if email == 1 and self.counter % 200 == 0:
                    self.emailNotification()

                self.counter = self.counter + 1

                # drawing rectangle around object that crossed the line
                frame1 = cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 0, 255), 6)
                # update label
                self.lbl_is_detected.configure(text="Detekcija prelaska linije ")
                # write in detection log
                timestamp = "Detekcija : " + str(dateTimeObj.day) + "." + str(dateTimeObj.month) + "." + str(
                    dateTimeObj.year) + " u " + str(dateTimeObj.hour) + ":" + str(dateTimeObj.minute) + ":" + str(
                    dateTimeObj.second)
                timestamp_list.append(timestamp)
                # save all photos in moments of detection
                cv2.imwrite(os.path.join(path, " U %s .jpg" % str(dateTimeObj)), frame1)

        return frame1

    def detectionLog(self):
        """Shows user detection log and option of saving the data into a txt file """
        self.detection_log_screen = Toplevel(self.master)
        self.detection_log_screen.title("Povijest detekcije")

        # removing entries with same seconds
        [self.res_timestamp_list.append(x) for x in timestamp_list if x not in self.res_timestamp_list]

        Label(self.detection_log_screen, text=" ", width=2).grid(row=0, column=0)
        # label with list of all detection moments
        self.lbl_info = Label(self.detection_log_screen, width=40, height=20)
        self.lbl_info.grid(column=1, row=0)
        self.lbl_info.configure(text=("\n".join(self.res_timestamp_list)))

        self.btn_back = Button(self.detection_log_screen, text="Nazad", command=self.goBack)
        self.btn_back.grid(column=1, row=2)
        # exporting data to txt file
        self.btn_export = Button(self.detection_log_screen, text="Izvezi sve podatke", command=self.exportLog)
        self.btn_export.grid(column=1, row=1)

    def exportLog(self):
        """Exports data of recorded detection to txt file"""
        with open('prelazak_linije_povijest.txt', 'w') as f:
            f.write("Povijest prelaska linije : \n")
            f.write("\n".join(self.res_timestamp_list))

    def goBack(self):
        """Go back from viewing detecion log"""
        self.lbl_info.destroy()
        self.btn_back.destroy()
        self.detection_log_screen.destroy()

    def emailNotification(self):
        """This function sends e-mails with notifications"""
        global username

        f = open(username, 'r')  # open file that contains info about user that is currently logged in
        lines = f.readlines()  # read lines from .txt file
        email = lines[2]  # read user email

        msg = MIMEMultipart()  # handles all e-mail parts : from, to, body, subject, photos...
        msg['From'] = 'obavijesti.aplikacije@gmail.com'
        msg['To'] = 'anitaa.vencl@gmail.com'
        msg['Subject'] = 'Obavijest sustava'

        email_user = 'obavijesti.aplikacije@gmail.com'
        email_send = email

        body = 'Detektiran je pokret na sticenoj lokaciji!'
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('obavijesti.aplikacije@gmail.com', 'obavijesti987')
        server.sendmail(email_user, email_send, text)
        server.quit()


class PersonOptions:
    def __init__(self, master):
        # menu frame holds menu buttons and options
        self.master = master
        # default values of parameters (user can change them in options)
        self.e_winstride = IntVar()
        self.e_padding = IntVar()
        self.e_scale = IntVar()
        self.e_winstride.set(4)
        self.e_padding.set(8)
        self.e_scale.set(1.02)

        self.frame = Frame(self.master)
        self.frame.pack()

        Label(self.frame, text="").pack()
        Label(self.frame, text="Odaberite opcije ili kliknite 'Dalje' za nastavak sa zadanim postavkama").pack(
            fill=BOTH, ipady=20)
        self.frm_main = Frame(self.frame)
        self.frm_main.pack(side=TOP, ipady=20)

        # frames for all options

        self.frm_winstride = Frame(self.frm_main)
        self.frm_winstride.pack(side=LEFT)
        self.frm_padding = Frame(self.frm_main)
        self.frm_padding.pack(side=LEFT)
        self.frm_scale = Frame(self.frm_main)
        self.frm_scale.pack(side=LEFT)

        # entries with default values of all options

        Label(self.frm_winstride, text="Window Stride :").pack()
        self.entry_winstride = Entry(self.frm_winstride, textvariable=self.e_winstride)
        self.entry_winstride.pack()

        Label(self.frm_padding, text="Padding :").pack()
        self.entry_padding = Entry(self.frm_padding, textvariable=self.e_padding)
        self.entry_padding.pack()

        Label(self.frm_scale, text="Scale :").pack()
        self.entry_scale = Entry(self.frm_scale, textvariable=self.e_scale)
        self.entry_scale.pack()

        self.btn_next = Button(self.frame, text="Dalje", command=self.setParameters)
        self.btn_next.pack()

        Label(self.frame, text="").pack()

        # informational text about parameters

        text = "Window stride: određuje veličinu koraka putujućeg prozora \n  -manja vrijednost = bolja detekcija, ali puno sporije \n\n"

        text2 = " Padding: broj piksela koji je nadodan svakom prozoru prije ekstrakcije značajki\n  -tipične vrijednosti su 8,16,24 \n\n"

        text3 = "Scale: faktor skaliranja piramide slika koje se koriste za ekstrakciju značajki\n  -manja vrijednost= veći broj slojeva piramide, sporija obrada\n"

        self.lbl_info = Label(self.frame, text=text + text2 + text3)
        self.lbl_info.pack()

        self.btn_back = Button(self.frame, text="Nazad na izbornik", command=self.goBackToMenu)
        self.btn_back.pack()

    def goBackToMenu(self):
        """Go back from main screen to detection options window"""
        self.frame.destroy()
        p = DetectionOptionsWindow(self.master)
        self.master.mainloop()

    def setParameters(self):
        """Gets parameters for people detector. This has to be done outside the function where the parameters have been set/written in entry"""
        self.winstride = self.e_winstride.get()
        self.padding = self.e_padding.get()
        self.scale = self.e_scale.get()
        self.beginPersonDetection()

    def beginPersonDetection(self):
        """Destroy previous windows and create object of class for people detection"""

        self.frame.destroy()
        self.btn_next.destroy()
        p = PersonDetection(self.master, self.winstride, self.padding, self.scale)
        self.master.mainloop()


class PersonDetection:
    def __init__(self, master, winstride, padding, scale):
        self.master = master
        self.winstride = winstride
        self.padding = padding
        self.scale = scale
        # initializing HOG descriptor that will find and classify people contours
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        self.menu_frame = Frame(self.master, highlightbackground="black", highlightthickness=1)
        self.menu_frame.grid(row=0, column=0, sticky="N")  # Sticky da ostane gore, inače se pomicao

        self.item_frame = Frame(self.master)
        self.item_frame.grid(row=0, column=1)

        im = PhotoImage(file="photofiles/wait_photo.png")
        im = im.zoom(10)
        im = im.subsample(10)

        # Menu buttons

        self.btn_menu1 = Button(self.menu_frame, text="Učitaj", command=self.loadingNewFile)
        self.btn_menu1.grid(row=0, column=0)
        self.btn_menu3 = Button(self.menu_frame, text="Detekcija", command=self.detectionInit)
        self.btn_menu3.grid(row=2, column=0)
        # Exit button
        self.btn_exit = Button(self.master, text="Izlaz", command=master.quit)
        self.btn_exit.grid(row=5, column=3)

        self.lbl_img1 = Label(self.item_frame)
        self.lbl_img1.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys i
        self.lbl_img1.configure(image=im)
        self.lbl_img1.grid(column=0, row=0)
        self.frm_go_back = Frame(self.master)
        self.frm_go_back.grid(row=2, column=0, sticky="S")
        btn_go_back = Button(self.frm_go_back, text="Nazad na izbornik", command=self.beginOpenOptions)
        btn_go_back.grid(column=0, row=0)

    # self.video_path=0

    def beginOpenOptions(self):
        """Destroy previous windows and create object of class for people detection"""

        self.menu_frame.destroy()
        self.item_frame.destroy()
        self.frm_go_back.destroy()
        self.btn_exit.destroy()

        p = PersonOptions(self.master)
        self.master.mainloop()

    def loadingNewFile(self):
        """For choosing video source, it has 3 radio buttons, by clicking on one their proper functions are called"""

        self.clear(self.item_frame)
        self.lbl_info_choose_video = Label(self.item_frame, text="Izaberite jednu opciju :")
        self.lbl_info_choose_video.grid(column=0, row=0)

        # Radio Buttons for video option
        self.selected = IntVar()
        self.rad1 = Radiobutton(self.item_frame, text="Odaberi video", width=20, value=1, variable=self.selected,
                                command=self.chooseVideo)
        self.rad2 = Radiobutton(self.item_frame, text=" Kamera", width=20, value=2, variable=self.selected,
                                command=self.chooseVideo)
        self.rad1.grid(column=0, row=1)
        self.rad2.grid(column=1, row=1)
        # Stop video button
        self.btn_end = Button(self.item_frame, text="Zaustavi video", state="disabled", command=self.endVideo)
        self.btn_end.grid(column=0, row=5, columnspan=2)
        self.lbl_video = Label(self.item_frame)
        self.lbl_video.grid(column=0, row=4, columnspan=2)

    def chooseVideo(self):
        """Starts video from a source that user has choosen with radio buttons."""
        global cap
        # If you select that you want to load video from file
        if self.selected.get() == 1:
            self.video_path = filedialog.askopenfilename(filetypes=[  # opening system dialog where you choose the file
                ("all video format", ".mp4"),
                ("all video format", ".mov")])
            if len(self.video_path) > 0:  # if a file has been choosen
                self.btn_end.configure(state="active")  # activate the button that can stop the video
                self.rad1.configure(
                    state="disabled")  # disable buttons that chooses type of video, they will be enabled once video stream is over
                self.rad2.configure(state="disabled")
                self.cap = cv2.VideoCapture(self.video_path)
                self.showVideo()

        if self.selected.get() == 2:  # if you choose to stream from some kind of stream
            self.btn_end.configure(state="active")  # activate the button that can stop the video
            self.rad1.configure(
                state="disabled")  # disable buttons that chooses type of video, they will be enabled once video stream is over
            self.rad2.configure(state="disabled")
            self.video_path = 0
            self.cap = cv2.VideoCapture(self.video_path)
            self.showVideo()

    def showVideo(self):
        """Transforms images in proper format and shows video """

        self.ret, frame = self.cap.read()  # get frame from cap
        if self.ret == True:
            frame = imutils.resize(frame, width=600, height=400)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # adjusting color, by default its a weird color scheme
            self.im = Image.fromarray(frame)
            self.img = ImageTk.PhotoImage(
                image=self.im)  # transforming to this format is only way of showing images in gui

            self.lbl_video.configure(image=self.img)
            self.lbl_video.image = self.img
            self.lbl_video.after(10, self.showVideo)  # calling function again after 10 milisecs


        else:
            self.im = self.im.save("reference.jpg")  # this image will be used for drawing background
            self.rad1.configure(state="active")
            self.rad2.configure(state="active")
            self.btn_end.configure(state="disabled")
            self.selected.set(0)
            self.cap.release()

    def endVideo(self):
        """Closes video capture and reactivates buttons that choose video source"""
        self.ret = False
        self.rad1.configure(state="active")
        self.rad2.configure(state="active")
        self.selected.set(0)
        self.cap.release()  # release capturing devices

    def clear(self, object):
        slaves = object.grid_slaves()
        for x in slaves:
            x.destroy()

    def detectionInit(self):
        """Initialises variables and widgets used for  detection"""
        self.clear(self.item_frame)
        global timestamp_list
        timestamp_list = []
        self.res_timestamp_list = []

        self.lbl_video = Label(self.item_frame, width=600, height=400, borderwidth=3, relief="solid")
        self.lbl_video.grid(column=1, row=1)
        self.frame_detection_log = Frame(self.item_frame)
        self.frame_detection_log.grid(column=1, row=4, pady=10)
        self.lbl_is_detected = Label(self.frame_detection_log, width=28, height=3, anchor=CENTER, padx=6)
        self.lbl_is_detected.grid(row=0, column=0)
        self.btn_detection_log = Button(self.frame_detection_log, text="Povijest detekcije", command=self.detectionLog)
        self.btn_detection_log.grid(row=1, column=0)
        self.cap = cv2.VideoCapture(self.video_path)
        self.av = []
        self.path = "photo_people"
        time.sleep(1)
        self.detectionSetup()

    def detectionSetup(self):
        """This function handles loading new frames and displaying returned analysed frames"""

        self.ret, frame = self.cap.read()  # get frame from cap

        self.start = time.perf_counter()
        if self.ret == True:
            frame = imutils.resize(frame, width=600, height=400)
            frame = self.detectionMain(frame)  # drugačiji resize jer se ovaj koristi za prikaz slike
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            self.lbl_video.configure(image=img)
            self.lbl_video.image = img
            self.lbl_video.after(10, self.detectionSetup)

        else:

            self.cap.release()

    def detectionMain(self, frame):
        """Extracts HOG features and classifies them (as either people or not people)"""
        path = self.path
        dateTimeObj = datetime.now()  # for getting exact time
        global timestamp_list
        (regions, _) = self.hog.detectMultiScale(frame,
                                                 winStride=(self.winstride, self.winstride),
                                                 padding=(self.padding, self.padding),
                                                 scale=self.scale)

        for (x, y, w, h) in regions:
            self.lbl_is_detected.configure(text="Detekcija !")
            timestamp = "Detekcija " + str(dateTimeObj.day) + "." + str(dateTimeObj.month) + "." + str(
                dateTimeObj.year) + " u " + str(dateTimeObj.hour) + ":" + str(dateTimeObj.minute) + ":" + str(
                dateTimeObj.second)
            timestamp_list.append(timestamp)

            frame = cv2.rectangle(frame, (x, y),  # draw rect around people
                                  (x + w, y + h),
                                  (0, 0, 255), 2)
            # saving photos with timestamp
            cv2.imwrite(os.path.join(path, " U %s .jpg" % str(dateTimeObj)), frame)

        return frame

    def detectionLog(self):
        """Shows user detection log and option of saving the data into a txt file """
        self.detection_log_screen = Toplevel(self.master)
        self.detection_log_screen.title("Login")
        self.detection_log_screen.geometry("500x400")

        # removing entries with same seconds
        [self.res_timestamp_list.append(x) for x in timestamp_list if x not in self.res_timestamp_list]

        Label(self.detection_log_screen, text=" ", width=2).grid(row=0, column=0)
        self.lbl_info = Label(self.detection_log_screen, width=40, height=20)
        self.lbl_info.grid(column=1, row=0)
        self.lbl_info.configure(text=("\n".join(self.res_timestamp_list)))
        self.btn_back = Button(self.detection_log_screen, text="Nazad", command=self.goBack)
        self.btn_back.grid(column=1, row=2)
        self.btn_export = Button(self.detection_log_screen, text="Izvezi sve podatke", command=self.exportLog)
        self.btn_export.grid(column=1, row=1)

    def exportLog(self):
        """Exports data of recorded detection to txt file"""
        with open('detekcija_ljudi_povijest.txt', 'w') as f:
            f.write("\n".join(self.res_timestamp_list))

    def goBack(self):
        """Go back from detection log screen (to main)"""
        self.lbl_info.destroy()
        self.btn_back.destroy()
        self.detection_log_screen.destroy()


class ZoneOptions:
    def __init__(self, master):
        # menu frame holds menu buttons and options
        self.master = master
        self.selected1 = IntVar()
        self.selected2 = IntVar()
        self.selected3 = IntVar()
        self.selected1.set(2)
        self.selected2.set(2)
        self.selected3.set(2)
        self.g_noise = 15
        self.size_of_detection_area = 240000 * 0.08
        self.b_tresh = 50

        self.frame = Frame(self.master)
        self.frame.pack()

        Label(self.frame, text="").pack()
        Label(self.frame, text="Odaberite opcije ili kliknite 'Dalje' za nastavak sa zadanim postavkama").pack(
            fill=BOTH, ipady=20)
        self.frm_main = Frame(self.frame)
        self.frm_main.pack(side=TOP, ipady=20)
        # frame for detection area options
        self.frm_det_area_opt = Frame(self.frm_main, highlightbackground="black", highlightthickness=1,
                                      highlightcolor="blue")
        self.frm_det_area_opt.pack(side=LEFT, padx=20)
        Label(self.frm_det_area_opt, text="Veličina detektiranog objekta:").pack()
        self.rad_det_area1 = Radiobutton(self.frm_det_area_opt, text="Mali 1% ekrana", value=1, variable=self.selected1,
                                         command=self.chooseOption1)
        self.rad_det_area1.pack()

        self.rad_det_area2 = Radiobutton(self.frm_det_area_opt, text="Srednji 8% ekrana", value=2,
                                         variable=self.selected1, command=self.chooseOption1)
        self.rad_det_area2.pack()

        self.rad_det_area3 = Radiobutton(self.frm_det_area_opt, text="Veliki 20% ekrana", value=3,
                                         variable=self.selected1, command=self.chooseOption1)
        self.rad_det_area3.pack()

        # frame for noise options
        self.frm_noise_opt = Frame(self.frm_main, highlightbackground="black", highlightthickness=1)
        self.frm_noise_opt.pack(side=LEFT, padx=20)
        Label(self.frm_noise_opt, text="Gaussovo zamućenje:").pack()
        self.rad_noise1 = Radiobutton(self.frm_noise_opt, text="Malo", value=1, variable=self.selected2,
                                      command=self.chooseOption2)
        self.rad_noise1.pack()

        self.rad_noise2 = Radiobutton(self.frm_noise_opt, text="Srednje", value=2, variable=self.selected2,
                                      command=self.chooseOption2)
        self.rad_noise2.pack()

        self.rad_noise3 = Radiobutton(self.frm_noise_opt, text="Veliko", value=3, variable=self.selected2,
                                      command=self.chooseOption2)
        self.rad_noise3.pack()

        # frame for thresh options
        self.frm_thresh_opt = Frame(self.frm_main, highlightbackground="black", highlightthickness=1)
        self.frm_thresh_opt.pack(side=LEFT, padx=20)
        Label(self.frm_thresh_opt, text="Osjetljivost:").pack()
        self.rad_thresh1 = Radiobutton(self.frm_thresh_opt, text="Mala", value=1, variable=self.selected3,
                                       command=self.chooseOption3)
        self.rad_thresh1.pack()

        self.rad_thresh2 = Radiobutton(self.frm_thresh_opt, text="Srednja", value=2, variable=self.selected3,
                                       command=self.chooseOption3)
        self.rad_thresh2.pack()

        self.rad_thresh3 = Radiobutton(self.frm_thresh_opt, text="Velika", value=3, variable=self.selected3,
                                       command=self.chooseOption3)
        self.rad_thresh3.pack()

        self.rad_det_area_ok = Button(self.frm_det_area_opt, text="OK", command=None)

        self.btn_next = Button(self.frame, text="Dalje", command=self.beginPolygonDet)
        self.btn_next.pack()

        Label(self.frame, text="").pack()

        text = "Veličina detektiranog objekta - minimalna veličina objekta koji će program detektirati \n \n Gaussovo zamućenje - vrijednost Gaussovog zamućenje koje filtrira šum, djeluje kao NP filtar \n \n Osjetljivost - prag koji određuje pokret \n \n \n "

        self.lbl_info = Label(self.frame, text=text)
        self.lbl_info.pack()

        self.btn_back = Button(self.frame, text="Nazad na izbornik", command=self.goBackToMenu)
        self.btn_back.pack()

    def goBackToMenu(self):
        """Destroy previous windows and creates object of class for detection options"""
        self.frame.destroy()
        p = DetectionOptionsWindow(self.master)
        self.master.mainloop()

    def chooseOption1(self):
        if self.selected1.get() == 1:
            self.size_of_detection_area = 240000 * 0.01

        if self.selected1.get() == 3:
            self.size_of_detection_area = 240000 * 0.2

    def chooseOption2(self):

        if self.selected2.get() == 1:
            self.g_noise = 11

        if self.selected2.get() == 3:
            self.g_noise = 31

    def chooseOption3(self):
        if self.selected3.get() == 1:
            self.b_tresh = 70

        if self.selected3.get() == 3:
            self.b_tresh = 30

    def beginPolygonDet(self):
        """Destroy previous windows and creates object of class for zone detection"""
        self.frame.destroy()
        self.frm_det_area_opt.destroy()
        self.frm_noise_opt.destroy()
        self.frm_thresh_opt.destroy()
        self.btn_next.destroy()

        p = ZoneDetection(self.master, self.size_of_detection_area, self.g_noise, self.b_tresh)
        self.master.mainloop()


class ZoneDetection:
    def __init__(self, master, size_of_detection_area, g_noise, b_tresh):  # konstruktor

        self.master = master
        # values from selected options
        self.size_of_detection_area = size_of_detection_area  # minimal area
        self.g_noise = g_noise  # Gaussian noise
        self.b_tresh = b_tresh  # binary threshold

        im = PhotoImage(file="photofiles/wait_photo.png")
        im = im.zoom(10)
        im = im.subsample(10)

        self.menu_frame = Frame(self.master)
        self.menu_frame.grid(row=0, column=0, sticky="N", pady=25)  # Sticky da ostane gore, inače se pomicao
        # item frame holds paiges when you chane it
        self.l3 = Label(self.master, text="")
        self.l3.grid(row=1, column=0)
        self.frm_go_back = Frame(self.master, highlightbackground="black")
        self.frm_go_back.grid(row=2, column=0, sticky="S")
        self.item_frame = Frame(self.master, width=600, height=400)
        self.item_frame.grid(row=0, column=1)
        self.lbl_img1 = Label(self.item_frame)
        self.lbl_img1.image = im  # you have to anchor the image twice for reason there has to be permanent referene to it, otherwise python destroys i
        self.lbl_img1.configure(image=im)
        self.lbl_img1.grid(column=0, row=0)

        # Menu buttons

        self.btn_menu1 = Button(self.menu_frame, text="Učitaj", command=self.loadingNewFile)
        self.btn_menu1.grid(row=0, column=0)
        self.btn_menu2 = Button(self.menu_frame, text="Označi", command=self.chooseArea)
        self.btn_menu2.grid(row=1, column=0)
        self.btn_menu3 = Button(self.menu_frame, text="Detekcija", command=self.detectionInit)
        self.btn_menu3.grid(row=2, column=0)

        self.l1 = Label(self.menu_frame, text=" ").grid(row=3, column=0)
        self.l2 = Label(self.menu_frame, text=" ").grid(row=4, column=0)

        btn_go_back = Button(self.frm_go_back, text="Nazad na izbornik", command=self.beginOpenOptions)
        btn_go_back.grid(column=0, row=0)

        # Exit button
        self.btn_exit = Button(self.master, text="Izlaz", command=self.master.destroy)
        self.btn_exit.grid(row=5, column=3)

    def beginOpenOptions(self):

        """Destroy previous windows and creates object of class for line detection"""

        self.menu_frame.destroy()
        self.item_frame.destroy()
        self.frm_go_back.destroy()
        self.btn_exit.destroy()
        self.l3.destroy()
        p = ZoneOptions(self.master)
        self.master.mainloop()

    def loadingNewFile(self):
        """For choosing video source, it has 3 radio buttons, by clicking on one their proper functions are called"""

        self.clear(self.item_frame)
        self.lbl_info_choose_video = Label(self.item_frame, text="Izaberite jednu opciju :")
        self.lbl_info_choose_video.grid(column=0, row=0, sticky="N")

        # Radio Buttons for video option
        self.selected = IntVar()
        self.rad1 = Radiobutton(self.item_frame, text="Video", width=10, value=1, variable=self.selected,
                                command=self.chooseVideo)
        self.rad2 = Radiobutton(self.item_frame, text="Kamera", width=10, value=2, variable=self.selected,
                                command=self.chooseVideo)
        self.rad3 = Radiobutton(self.item_frame, text="RTSP", width=10, value=3, variable=self.selected,
                                command=self.chooseVideo)

        self.rad1.grid(column=0, row=1)
        self.rad2.grid(column=1, row=1)
        self.rad3.grid(column=2, row=1)
        # Stop video button
        self.btn_end = Button(self.item_frame, text="Zaustavi video", state="disabled", command=self.endVideo)
        self.btn_end.grid(column=0, row=5, columnspan=2)
        self.lbl_video = Label(self.item_frame)
        self.lbl_video.grid(column=0, row=4, columnspan=2)

    def chooseVideo(self):
        """Starts video from a source that user has choosen with radio buttons."""
        global cap
        global video_path

        # If you select that you want to load video from file
        if self.selected.get() == 1:
            video_path = filedialog.askopenfilename(filetypes=[  # open system dialog where you choose the file
                ("all video format", ".mp4"),
                ("all video format", ".mov")])
            if len(video_path) > 0:  # if a file has been choosen
                self.btn_end.configure(state="active")  # activate the button that can stop the video
                self.rad1.configure(
                    state="disabled")  # disable buttons that chooses type of video, they will be enabled once video stream is over
                self.rad2.configure(state="disabled")
                self.cap = cv2.VideoCapture(video_path)
                self.showVideo()

        if self.selected.get() == 2:  # if you choose to stream from some kind of stream
            self.btn_end.configure(state="active")  # activate the button that can stop the video
            self.rad1.configure(state="disabled")  # disable buttons that chooses type of video
            self.rad2.configure(state="disabled")
            video_path = 0
            self.cap = cv2.VideoCapture(video_path)
            self.showVideo()

        if self.selected.get() == 3:
            self.rtsp = StringVar()  # if you choose to stream from some kind of rtsp stream
            self.btn_end.configure(state="active")  # activate the button that can stop the video
            self.rad1.configure(
                state="disabled")  # disable buttons that chooses type of video, they will be enabled once video stream is over
            self.rad2.configure(state="disabled")
            self.rtsp_screen = Toplevel(self.master)
            self.rtsp_screen.title("Upis RTSP ")
            self.rtsp_screen.geometry("600x400")
            self.lbl_rtsp = Label(self.rtsp_screen, text="rtsp:")
            self.lbl_rtsp.grid(row=0, column=0, padx=20)

            self.entry_rtsp = Entry(self.rtsp_screen, textvariable=self.rtsp)
            self.entry_rtsp.grid(row=0, column=1)
            btn_ok = Button(self.rtsp_screen, text="Ok", command=self.destroyRTSPScreen)
            btn_ok.grid(row=2, column=1)

    def destroyRTSPScreen(self):
        """Go back from RTSP screen (to main view)"""

        self.video_path = str(self.rtsp.get())
        self.cap = cv2.VideoCapture((self.video_path))

        self.showVideo()

    def showVideo(self):
        """Transforms images in proper format and shows video """
        self.ret, frame = self.cap.read()  # get frame from cap
        if self.ret == True:
            frame = imutils.resize(frame, width=600, height=400)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.im = Image.fromarray(frame)
            self.img = ImageTk.PhotoImage(image=self.im)
            self.lbl_video.configure(image=self.img)
            self.lbl_video.image = self.img
            self.lbl_video.after(10, self.showVideo)


        else:
            self.im = self.im.save("reference.jpg")  # will be used for drawing later
            self.rad1.configure(state="active")
            self.rad2.configure(state="active")
            self.btn_end.configure(state="disabled")
            self.selected.set(0)
            self.cap.release()

    def endVideo(self):
        """Ends video only on user click"""
        self.ret = False
        self.rad1.configure(state="active")
        self.rad2.configure(state="active")
        self.selected.set(0)
        self.cap.release()

    def clear(self, object):
        slaves = object.grid_slaves()
        for x in slaves:
            x.destroy()

    def chooseArea(self):
        """Handles all widgets and variables needed to draw polygons"""
        self.clear(self.item_frame)

        self.list_poly = []  # list of all polygons
        self.list_of_points = []  # list of points in one poly
        self.zone_name = StringVar()  # user given zone name
        self.zone_names = []  # list of zone names

        dim = (600, 400)

        self.poly = None

        Label(self.item_frame, text="Označite").grid(column=0, row=0)
        self.canvas = Canvas(self.item_frame, bg="#e8e6e1", width=580, height=380, borderwidth=3, relief="solid")
        self.canvas.grid(column=0, row=1, padx=0, pady=0)

        image = Image.open("reference.jpg")  # open reference image so user can draw over it
        image = image.resize(dim)
        self.img_ref = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.img_ref)
        self.btn_stop_drawing = Button(self.item_frame, text="Završi označavanje trenutne zone",
                                       command=self.stopDrawing)
        self.btn_stop_drawing.grid(row=3, column=0)
        self.canvas.bind("<Button-1>", self.drawPolygons)  # binding left button click to draw

    def beginOpenOptions2(self):
        """Goes back to options from detection screen."""
        self.menu_frame.destroy()
        self.item_frame.destroy()
        self.btn_exit.destroy()
        self.frm_go_back.destroy()
        p = ZoneOptions(self.master)
        self.master.mainloop()

    def detectionInit(self):
        """Initialises variables and widgets used for motion detection"""
        global timestamp_list
        timestamp_list = []
        self.res_timestamp_list = []
        self.cap = cv2.VideoCapture(video_path)

        self.clear(self.item_frame)
        self.lbl_video = Label(self.item_frame, width=600, height=400, borderwidth=3, relief="solid")
        self.lbl_video.grid(column=1, row=1)

        self.email = self.is_email.get()

        self.frame_detection_log = Frame(self.item_frame)
        self.frame_detection_log.grid(column=1, row=4, pady=10)
        self.lbl_is_detected = Label(self.frame_detection_log, width=28, height=3, anchor=CENTER, padx=6)
        self.lbl_is_detected.grid(row=0, column=0)
        self.btn_detection_log = Button(self.frame_detection_log, text="Povijest detekcije", command=self.detectionLog)
        self.btn_detection_log.grid(row=1, column=0)
        self.counter = 0
        self.path = "photo_detection"  # for saving photos of detection
        time.sleep(1)
        self.av = []
        self.detectionSetup()

    def detectionSetup(self):
        """This function handles loading new frames and displaying returned analysed frames"""

        ret, frame1 = self.cap.read()  # get frame from cap
        # for detection of movement
        ret, frame2 = self.cap.read()

        dim = (600, 400)

        self.start = time.perf_counter()

        if ret == True:

            frame1 = cv2.resize(frame1, dim)
            frame2 = cv2.resize(frame2, dim)
            frame = self.detectionMain(frame1, frame2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            self.lbl_video.configure(image=img)
            self.lbl_video.image = img

            self.lbl_video.after(10, self.detectionSetup)

        else:

            self.cap.release()

    def detectionMain(self, frame1, frame2):
        """In this function image is edited and analysed for motion and location of motion if it exists"""

        path = self.path

        self.frame1 = frame1
        self.frame2 = frame2

        # attributes for drawing zones
        isClosed = True
        color = (0, 200, 0)
        thickness = 2

        dateTimeObj = datetime.now()  # for getting exact time
        global timestamp_list

        diff = cv2.absdiff(self.frame1, self.frame2)  # Calc the difference between frames
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)  # Transform to grayscale
        blur = cv2.GaussianBlur(gray, (self.g_noise, self.g_noise), 0)  # Add Gaussian blur to filter noises
        _, thresh = cv2.threshold(blur, self.b_tresh, 250,
                                  cv2.THRESH_BINARY)  # Decide a threshold for turning into binary'
        dilated = cv2.dilate(thresh, None, iterations=25)  # Dilate all positive binary values
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # Make contours of them

        # every polygon is transformed into np array and they are drawn on the screen
        for i in range(len(self.list_poly)):
            self.list_of_points = self.list_poly[i]

            self.np_list_of_points = np.array(self.list_of_points)

            pts = self.np_list_of_points
            pts = pts.reshape((-1, 1, 2))

            frame1 = cv2.polylines(frame1, [pts],
                                   isClosed, color,
                                   thickness)

        for contour in contours:  # for every contour of a moving object
            if cv2.contourArea(
                contour) < self.size_of_detection_area: continue  # check the area size, if its too small, skip
            (x, y, w, h) = cv2.boundingRect(contour)  # draw virtual rectangle

            middle = ((2 * x + w) / 2, (2 * y + h) / 2)  # calculate rectangle centroid
            middle = Point(middle)  # make instance of Point class

            for i in range(len(self.list_poly)):

                poly = Polygon(self.list_poly[i])

                if poly.contains(middle):  # check if polygon contains centroid

                    self.lbl_is_detected.configure(
                        text="Detekcija u zoni {zone_name}".format(zone_name=self.zone_names[i]))
                    frame1 = cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 23, 255),
                                           6)  # label which writes in real time in
                    # which zone motion has been detected

                    print(self.email)
                    if self.email == 1 and self.counter % 200 == 0:
                        self.emailNotification()

                    self.counter = self.counter + 1

                    # make list of all motion timestamps
                    timestamp = "Detekcija u zoni {zone_name} : ".format(zone_name=self.zone_names[i]) + str(
                        dateTimeObj.day) + "." + str(dateTimeObj.month) + "." + str(dateTimeObj.year) + " u " + str(
                        dateTimeObj.hour) + ":" + str(dateTimeObj.minute) + ":" + str(dateTimeObj.second)
                    timestamp_list.append(timestamp)

                    # save all photos in moments of detection
                    cv2.imwrite(os.path.join(path, " U %s .jpg" % str(dateTimeObj)), frame1)

        end = time.perf_counter()
        self.av.append((end - self.start))

        # print(statistics.mean(self.av))
        return frame1

    def drawPolygons(self, event):
        """Used for passing event of mouse click to funcDrawPolygons"""

        self.mouse_xy = (event.x, event.y)

        self.funcDrawPolygons(self.mouse_xy)

    def funcDrawPolygons(self, mouse_xy):
        """Creates polygons on the screen from points that user has clicked"""

        self.mouse_xy = mouse_xy
        self.center_x, self.center_y = self.mouse_xy  # extracting x and y coordinates
        self.list_of_points.append((self.center_x, self.center_y))  # adding coordinates to list of all points
        self.canvas.delete(self.poly)  # deleting previous poly with n-1 points so we can draw new one

        for self.pt in self.list_of_points:
            self.x, self.y = self.pt
            # draw dot over place clicked
            self.x1, self.y1 = (self.x - 1), (self.y - 1)
            self.x2, self.y2 = (self.x + 1), (self.y + 1)
            self.canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill='green', outline='green',
                                    width=7)  # create little green ovals around points

        self.numberofPoint = len(self.list_of_points)
        if self.numberofPoint > 2:
            self.poly = self.canvas.create_polygon(self.list_of_points, fill='', outline='red',
                                                   width=4)  # create polygon if there is enough points

        if self.numberofPoint == 2:
            self.canvas.create_line(self.list_of_points, fill="red", width=4)  # create a line if there is 2 points

    def stopDrawing(self):
        """This function is called when the user is done with drawing polygonal shape."""
        """It contains pop up window in which user types zone name and/or if email should be sent"""
        """if there is a detection in that particular zone."""

        self.is_email = IntVar()  # determines if user wants email sent
        self.is_email.set(0)  # by default e-mail will not be checked to be sent for every zone

        self.np_list_of_points = np.array(self.list_of_points)  # transform points to np array
        self.list_poly.append(self.list_of_points)  # add latest drawn polygon to list of all polygons

        if len(self.list_of_points) < 2:  # is user did not draw polygon
            self.error_screen = Toplevel(self.master)
            self.error_screen.title("Greška")
            self.error_screen.geometry("300x200")
            self.lbl_error = Label(self.error_screen, text="Nije označena zona, pokušajte ponovno!")
            self.lbl_error.grid(row=0, column=0, padx=20)

            btn_ok = Button(self.error_screen, text="Ok", command=self.destroyErrorScreen)
            btn_ok.grid(row=1, column=0)

        self.list_of_points = []

        for i in range(len(self.list_poly)):  # drawing all polygons on the screen at once

            self.canvas.create_polygon(self.list_poly[i], fill='', outline='red', width=4)

        # zone features window
        self.naming_screen = Toplevel(self.master)
        self.naming_screen.title("Značajke zone")
        self.naming_screen.geometry("600x400")

        self.lbl_zone_name = Label(self.naming_screen, text="Imenujte nacrtanu zonu :")
        self.lbl_zone_name.grid(row=0, column=0, padx=20)
        self.entry_zone_name = Entry(self.naming_screen, textvariable=self.zone_name)
        self.entry_zone_name.grid(row=0, column=1)
        btn_ok = Button(self.naming_screen, text="Ok", command=self.destroyNamingScreen)
        btn_ok.grid(row=2, column=1)
        Label(self.naming_screen, text="Želite li e-mail obavijest za detekciju u ovoj zoni?").grid(row=1, column=0)
        self.rad_yes_email = Radiobutton(self.naming_screen, text="Da", variable=self.is_email, value=1)
        self.rad_yes_email.grid(row=1, column=1)
        self.rad_no_email = Radiobutton(self.naming_screen, text="Ne", variable=self.is_email, value=0)
        self.rad_no_email.grid(row=1, column=2)

    def destroyErrorScreen(self):
        """Go back from error screen (to main view)"""
        self.error_screen.destroy()
        self.naming_screen.destroy()
        self.chooseArea()

    def destroyNamingScreen(self):
        """Go back from zone options screen (to main view)"""
        self.zone_names.append(self.zone_name.get())
        self.entry_zone_name.delete(0, END)
        self.naming_screen.destroy()

    def detectionLog(self):
        """Shows user detection log and option of saving the data into a txt file """
        self.detection_log_screen = Toplevel(self.master)
        self.detection_log_screen.title("Login")
        self.detection_log_screen.geometry("500x400")

        # removing entries with same seconds
        [self.res_timestamp_list.append(x) for x in timestamp_list if x not in self.res_timestamp_list]

        Label(self.detection_log_screen, text=" ", width=2).grid(row=0, column=0)
        self.lbl_info = Label(self.detection_log_screen, width=40, height=20)
        self.lbl_info.grid(column=1, row=0)
        self.lbl_info.configure(text=("\n".join(self.res_timestamp_list)))
        self.btn_back = Button(self.detection_log_screen, text="Nazad", command=self.goBack)
        self.btn_back.grid(column=1, row=2)
        self.btn_export = Button(self.detection_log_screen, text="Izvezi sve podatke", command=self.exportLog)
        self.btn_export.grid(column=1, row=1)

    def exportLog(self):
        """Exports data of recorded detection to txt file"""
        with open('detekcija_zona_povijest.txt', 'w') as f:
            f.write("\n".join(self.res_timestamp_list))

    def goBack(self):
        """Go back from detection log screen (to main)"""
        self.lbl_info.destroy()
        self.btn_back.destroy()
        self.detection_log_screen.destroy()

    def emailNotification(self):
        """This function sends e-mails with notifications"""
        global username

        f = open(username, 'r')  # open file that contains info about user that is currently logged in
        lines = f.readlines()  # read lines from .txt file
        email = lines[2]  # read user email

        msg = MIMEMultipart()  # handles all e-mail parts : from, to, body, subject, photos...
        msg['From'] = 'obavijesti.aplikacije@gmail.com'
        msg['To'] = 'anitaa.vencl@gmail.com'
        msg['Subject'] = 'Obavijest sustava'

        email_user = 'obavijesti.aplikacije@gmail.com'
        email_send = email

        body = 'Detektiran je pokret na sticenoj lokaciji!'
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)  # gmail protocol
        server.starttls()
        server.login('obavijesti.aplikacije@gmail.com', 'obavijesti987')
        server.sendmail(email_user, email_send, text)
        server.quit()


if __name__ == '__main__':
    root = Tk()

    root.title("Proakustik")
    root.geometry("900x600")
    # root.geometry("1400x800")
    p = Proakustik(root)
    root.mainloop()