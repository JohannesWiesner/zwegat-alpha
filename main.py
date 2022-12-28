#!/usr/bin/env python

####################################################################################################################################################################
### ZWEGAT ALPHA ###################################################################################################################################################
####################################################################################################################################################################

'''
Author: - Johannes Wiesner
Notes:  - Debts are not rounded until saving in txt-file or presenting in text-widget
        - Please help me fixing all FIXMES!
        - all rasperry pi specific lines are commented with "rp3:..."         
'''

####################################################################################################################################################################
### Import Modules #################################################################################################################################################
####################################################################################################################################################################

# Modules for Zwegat Alpha
import os
import datetime
import subprocess
import pickle
from collections import Counter

# Modules for tkinter-GUI
import tkinter as tk
from tkinter import ttk
from PIL import Image
from PIL import ImageTk
from tkinter import messagebox
import sys

# pygame for optional playing of audio files
import pygame

# vlc radio for radio page
# import vlc

# weather modules
import json
import codecs
from urllib.request import urlopen

# rp3
# if sys.platform == "linux":
#     import cups
# else:
#     pass

##############################################################################################################################################################
### Set System Variables #####################################################################################################################################
##############################################################################################################################################################

# Date
tday = datetime.date.today().strftime('%Y/%m/%d')

##############################################################################################################################################################
### MODEL ####################################################################################################################################################
##############################################################################################################################################################

# FIXME: The whole special expense part (variables, methods, classmethods) is so similar to the expense stuff (except that all variables and 
# function names have a spcl_ in their name) that I wonder if there's a more elegant way to do this? Status quo is basically a modified copy of all
# instance variables and methods & classmethods.

# Define Class Roomie
class Roomie:

    num_roomies = 5 # number of roomies
    total_exp = 0.00 # sum of all expenses
    total_spcl_exp = 0.00 # sum of all special expenses
    mean_exp = 0.00 # mean expenses
    mean_spcl_exp = 0.00 # mean special expenses
    num_exp = 0 # total count of all expenses for one debts plan
    num_spcl_exp = 0 # total count of all expenses for one debts plan

    # FIXME: How to declare exp, res correctly in pythonic way?
    def __init__(self, fname,exp=0.00,res=0.00,exlist=None,info=None,date=None,pres=None,preslist=None,evlist=None,
        spcl_exp=0.00,spcl_res=0.00,spcl_exlist=None,spcl_info=None,spcl_date=None,partlist=None,spcl_evlist=None):
    
    ## -- EXPENSE -----------------------------------------------------------------------------------------

        self.fname = fname  # roomie name
        self.exp = exp # roomie expenses
        self.res = res # difference roomie expenses to total mean
        self.exlist = [] # list of single roomie expenses
        self.info = [] # list of info for each expense 
        self.date = [] # list of dates each expense was done

        # Additional information for conservative debt calculation
        self.pres = True # boolean value: current presence status of roomie (present/absent)
        self.preslist = [] # list of presence status for expense events
        self.evlist = [] # list of expense events (if spender: amount / if not spender: None)

    ## -- SPECIAL EXPENSE ----------------------------------------------------------------------------------
        
        self.spcl_exp = spcl_exp # roomie special expenses
        self.spcl_res = spcl_res # difference roomie total special expenses to total special expenses mean
        self.spcl_exlist = [] # list of special roomie expenses
        self.spcl_info = [] # list of info for each special expense 
        self.spcl_date = [] # list of dates each special expense was done
        
        # Additional information for special expense debt calculation
        self.partlist = [] # list of participation status for expense events
        self.spcl_evlist = [] # list of special expense events (if spender: amount / if not spender: None)

    ## -- EXPENSE METHODS ----------------------------------------------------------------------------------

    def raiseExp(self,expense):
        self.exp = (self.exp + expense)

    def updateRes(self,mean_exp):
        self.res = self.exp - mean_exp

    def addEx(self,exp):
        self.exlist.append(exp)

    def addInfo(self,exp_info):
        self.info.append(exp_info)

    def addDate(self,tday):
        self.date.append(tday)

    def changePres(self,switch):
        self.pres = switch

    def addPres(self):
        self.preslist.append(self.pres)

    def addEv(self,expense):
        self.evlist.append(expense)
    
    ## -- SPECIAL EXPENSE METHODS --------------------------------------------------------------------------
    
    def raiseSpclExp(self,expense):
        self.spcl_exp = (self.spcl_exp + expense)

    def updateSpclRes(self,mean_spcl_exp):
        self.spcl_res = self.spcl_exp - mean_spcl_exp

    def addSpclEx(self,special):
        self.spcl_exlist.append(special)

    def addSpclInfo(self,specialinfo):
        self.spcl_info.append(specialinfo)

    def addSpclDate(self,tday):
        self.spcl_date.append(tday)

    def addPart(self,switch):
        self.partlist.append(switch)

    def addSpclEv(self,special):
        self.spcl_evlist.append(special)

    ## -- RESET INSTANCE  -----------------------------------------------------------------------------------------------------------

    # FIXME: - Is there a better way to "reset" the instance without hardcoding?
    #        - This version is basically a "pseudo" init-call
    def resetObject(self, exp=0.00,res=0.00,exlist=None,info=None,date=None,pres=None,preslist=None,evlist=None,
        spcl_exp=0.00,spcl_res=0.00,spcl_exlist=None,spcl_info=None,spcl_date=None,partlist=None,spcl_evlist=None):
        
        self.exp = exp
        self.res = res
        self.exlist = []
        self.info = []
        self.date = []

        self.pres = True
        self.preslist = []
        self.evlist = []
        
        self.spcl_exp = spcl_exp
        self.spcl_res = spcl_res
        self.spcl_exlist = []
        self.spcl_info = []
        self.spcl_date = []

        self.partlist = []
        self.spcl_evlist = []

    ## -- CLASSMETHODS - EXPENSES ---------------------------------------------------------------------------------------

    @classmethod
    def raiseTotalExp(cls,single):
        cls.total_exp = cls.total_exp + single

    @classmethod
    def raiseMeanExp(cls):
        cls.mean_exp = cls.total_exp / cls.num_roomies

    @classmethod
    def updateExpNum(cls):
        cls.num_exp += 1

    ## -- CLASSMETHODS - SPECIAL EXPENSES -------------------------------------------------------------------------------

    @classmethod
    def raiseSpclTotalExp(cls,special):
        cls.total_spcl_exp = cls.total_spcl_exp + special

    @classmethod
    def raiseSpclMeanExp(cls):
        cls.mean_spcl_exp = cls.total_spcl_exp / cls.num_roomies

    @classmethod
    def updateSpclExpNum(cls):
        cls.num_spcl_exp += 1

    ## -- RESET CLASS VARIABLES  ---------------------------------------------------------------------------------------
    
    @classmethod
    def resetClass(cls):
        cls.num_roomies = 5
        cls.total_exp = 0.00
        cls.total_spcl_exp = 0.00
        cls.mean_exp = 0.00
        cls.mean_spcl_exp = 0.00
        cls.num_exp = 0 
        cls.num_spcl_exp = 0

# Define Class Roomie instances
roomie_0 = Roomie("Roomie 1")
roomie_1 = Roomie("Roomie 2")
roomie_2 = Roomie("Roomie 3")
roomie_3 = Roomie("Roomie 4")
roomie_4 = Roomie("Roomie 5")

# Create roomie list for later use in functions
# FIXME: It would probably have been better to use dictionary type here?
roomie_list = [roomie_0,roomie_1,roomie_2,roomie_3,roomie_4]

# Function: liberalDebtsDict
# Take:     all roomie.res
# Return:   dictionary with keys = roomie number, values = debts / demands
# Note:     this returns liberal debts dictionary (presence status is not considered)
def liberalDebtsDict():

    debts_dict = {}
    
    for (i,person) in zip(range(0,len(roomie_list)), roomie_list):
        debts_dict[i] = person.res
    
    return debts_dict

# Function: conservativeDebtsDict
# Take:     evlist of all roomies, preslist of all roomies
# Return:   Dictionary with keys = roomie number, values = debts/demands 
# Note:     this returns conservative debts dictionary: debts are ADJUSTED FOR PRESENCE
def conservativeDebtsDict():

    hit = None # saves the current number of roomie who made a purchase
    ev_exp = None # saves the current expense for this roomie
    ev_list_pres = [] # saves current indices for all roomies who were present at this event
    ev_debts = None # saves current debts for all present roomies

    # Output:
    presence_adjusted_dict = {}

    for i in range(0,len(roomie_list)):
        presence_adjusted_dict[i] = 0

    # for idxth-event: who made a purchase? Save number in hit variable
    # for idxth-event: how much did this roomie spent? Save value in ev_exp variable
    # for idxth-event: who was present? Save roomie number in ev_list_pres
    for idx in range(0,Roomie.num_exp):
        for roomie in roomie_list:
            if roomie.evlist[idx] != None:
                hit = roomie_list.index(roomie)
                ev_exp = roomie_list[hit].evlist[idx]
            if roomie.preslist[idx] == True:
                ev_list_pres.append(roomie_list.index(roomie))
            else:
                pass            
        
        # for idxth event: calculate debts depending on present roomies 
        ev_debts = ev_exp / len(ev_list_pres)

        # only for present roomies: add ev_debts
        for spender in ev_list_pres :
            presence_adjusted_dict[spender] += ev_debts

        # reset presence list
        ev_list_pres = []

    # after going trough all events: substract individual debts from individual expenses
    for roomie in presence_adjusted_dict:
        presence_adjusted_dict[roomie] = roomie_list[roomie].exp - presence_adjusted_dict[roomie] 

    return presence_adjusted_dict

# Function: SpecialExpenseDict
# Take:     spcl_evlist of all roomies, partlist of all roomies
# Return:   special expense dictionary with keys = roomie number, values = debts/demands 
# FIXME:    This is basically a copy of conservative debts dict but with different variables
#           -> Merge two functions together, by writing generic function that takes instance attributs as arguments
def specialExpenseDebtsDict():

    hit = None # saves the current number of roomie who made a purchase
    ev_exp = None # saves the current special expense for this roomie
    ev_list_part = [] # saves current indices for all roomies participating in this event
    ev_debts = None # saves current special debts for all present roomies

    # Output:
    special_expense_dict = {}

    for i in range(0,len(roomie_list)):
        special_expense_dict[i] = 0

    # for idxth-event: who made a purchase? Save number in hit variable
    # for idxth-event: how much did this roomie spent? Save value in ev_exp variable
    # for idxth-event: who was present? Save roomie number in ev_list_part
    for idx in range(0,Roomie.num_spcl_exp):
        for roomie in roomie_list:
            if roomie.spcl_evlist[idx] != None:
                hit = roomie_list.index(roomie)
                ev_exp = roomie_list[hit].spcl_evlist[idx]
            if roomie.partlist[idx] == True:
                ev_list_part.append(roomie_list.index(roomie))
            else:
                pass            
        
        # for idxth event: calculate debts depending on present roomies 
        ev_debts = ev_exp / len(ev_list_part)

        # only for present roomies: add ev_debts
        for spender in ev_list_part :
            special_expense_dict[spender] += ev_debts

        # reset presence list
        ev_list_part = []

    # after going trough all events: substract individual debts from individual expenses
    for roomie in special_expense_dict:
        special_expense_dict[roomie] = roomie_list[roomie].spcl_exp - special_expense_dict[roomie] 

    return special_expense_dict

# Take:   Dictionary with keys = roomie number, values = debts / demands
# Do:     Sort dictionary by values but keep corresponding keys
# Note:   See also 'OrderedDict Subclass' from 'collections' module
# Return: Value-sorted dictionary
def valueSortedDict(my_dict):

    keys = list(my_dict.keys())
    values = list(my_dict.values())
    # Note: values get sorted in ascending order from negative to positive
    values_sorted = sorted(my_dict.values())
    keys_sorted = []

    for i in range(0,len(my_dict)):
        values_sorted_val = values_sorted[i]
        values_idx = values.index(values_sorted_val)
        # First: cut out value from original list to prevent from finding this value again using index method
        # Second: insert string type to prevent list from shrinking
        values.pop(values_idx)
        values.insert(values_idx,'checked')
        key_val = keys[values_idx]
        keys_sorted.append(key_val)

    my_sorted_dict = dict(zip(keys_sorted, values_sorted))

    return my_sorted_dict

# Normalize Function
# Take: dictionary with keys = roomie number, values = debts (negative values) / demands (positive values)
# Return: list with 3-element-tuples (Debtor,Creditor,Amount) 
def normalizeDebts(my_dict):

    keys = list(my_dict.keys())
    values = list(my_dict.values())
    stack_list = values
    debts_list = list()

    while any(element != 0  for element in stack_list):

        cur_max_idx = stack_list.index(max(stack_list))
        cur_min_idx = stack_list.index(min(stack_list))
        cur_max_val = stack_list[cur_max_idx]
        cur_min_val = stack_list[cur_min_idx]

        if abs(cur_min_val) < abs(cur_max_val) and cur_min_val < 0 and cur_max_val > 0:
            stack_list[cur_min_idx] = cur_min_val + abs(cur_min_val)
            stack_list[cur_max_idx] = cur_max_val - abs(cur_min_val)
            debts_list.append((keys[cur_min_idx],keys[cur_max_idx],abs(cur_min_val)))
        elif abs(cur_min_val) > abs(cur_max_val) and cur_min_val < 0 and cur_max_val > 0:
            stack_list[cur_min_idx] = cur_min_val + abs(cur_max_val)
            stack_list[cur_max_idx] = cur_max_val - abs(cur_max_val)
            debts_list.append((keys[cur_min_idx],keys[cur_max_idx],abs(cur_max_val)))
        elif abs(cur_min_val) == abs(cur_max_val):
            stack_list[cur_min_idx] = 0
            stack_list[cur_max_idx] = 0
            debts_list.append((keys[cur_min_idx],keys[cur_max_idx],abs(cur_min_val)))
        else:
            break

    return debts_list

def mergeDebts():

    debts_dict = Counter(conservativeDebtsDict())
    spcl_dict = Counter(specialExpenseDebtsDict())

    debts_dict.update(spcl_dict)

    return debts_dict

# Function: saveDebtsTxt
# Take:     Conservative / liberal debts list (3-element-tuples)
# Do:       Save current debts plan as txt file
# Return:   Path of txt-file for later optional printing
# FIXME:    Any way to make variable hyphen dynamic? (hyphen line as long as longest line in text widget)
def saveDebtsTxt(debts_list):
    
    HYPHEN = "-" * 70
    doc_date = datetime.date.today().strftime('%Y_%B')
    zipped = []

    conservative_debtslist = normalizeDebts(valueSortedDict(conservativeDebtsDict()))
    special_debtslist = normalizeDebts(valueSortedDict(specialExpenseDebtsDict()))
    global_debtslist = normalizeDebts(valueSortedDict(mergeDebts()))

    # Create functions for easy writing standard characters such as newline, etc.
    def write(text):
        file.write(text)
    def newLine():
        file.write("\n")
    def doubleNewLine():
        file.write("\n\n")
    def hyphenLine():
        file.write("{}\n\n".format(HYPHEN))

    # Open file
    file = open("RausAusDenSchulden_{}.txt".format(doc_date),"w")
    
    write("Abrechnungsdatum:\t{}".format(datetime.date.today().strftime("%d.%m.%Y")))
    doubleNewLine()
    hyphenLine()
    
    # Write expenses for each roomie including exp_info and date
    write("Normale Ausgaben:")
    doubleNewLine()
    for roomie in roomie_list:
        write("{}:".format(roomie.fname))
        doubleNewLine()
        zipped = list(zip(roomie.date,roomie.exlist,roomie.info))
        for (date,exp,info) in zipped:
            if info != None:
                write("{}\t\t{}€\t{}\n".format(date,exp,info))
            elif info == None:
                write("{}\t\t{}€\t{}\n".format(date,exp,""))
        newLine()
    hyphenLine()

    # Write global info
    write("Totale Ausgaben:\t\t{}€\nMittelwert:\t\t\t{}€\nGesamtzahl getätigter Ausgaben:\t{}".format(round(Roomie.total_exp,2),round(Roomie.mean_exp,2),Roomie.num_exp))
    doubleNewLine()        
    
    # Write debts plan
    write("Konservativer Schuldenplan:")
    doubleNewLine()
    for (creditor,debtor,amount) in conservative_debtslist:
        write('{} schuldet {} {}€\t\n'.format(roomie_list[creditor].fname,roomie_list[debtor].fname,round(amount,2)))
    newLine()
    hyphenLine()

    # Write special expenses for each roomie including info and date
    write("Sonderausgaben:")
    doubleNewLine()
    for roomie in roomie_list:
        write("{}:".format(roomie.fname))
        doubleNewLine()
        zipped = list(zip(roomie.spcl_date,roomie.spcl_exlist,roomie.spcl_info))
        for (date,exp,info) in zipped:
            if info != None:
                write("{}\t\t{}€\t{}\n".format(date,exp,info))
            elif info == None:
                write("{}\t\t{}€\t{}\n".format(date,exp,""))
        newLine()
    hyphenLine()

    # Write global info
    write("Totale Sonderausgaben:\t\t\t{}€\nMittelwert:\t\t\t\t{}€\nGesamtzahl getätigter Sonderausgaben:\t{}".format(round(Roomie.total_spcl_exp,2),
        round(Roomie.mean_spcl_exp,2),Roomie.num_spcl_exp))
    doubleNewLine()
    
    # Write debts plan
    write("Sonderausgaben Schuldenplan:")
    doubleNewLine()
    for (debtor,creditor,amount) in special_debtslist:
        write('{} schuldet {} {}€\t\n'.format(roomie_list[debtor].fname,roomie_list[creditor].fname,round(amount,2)))
    newLine()
    hyphenLine()
    write("Gesamtschuldenplan:")
    for (debtor,creditor,amount) in global_debtslist:
        write('{} schuldet {} {}€\t\n'.format(roomie_list[debtor].fname,roomie_list[creditor].fname,round(amount,2)))


    # save filepath
    file_path = str(os.path.realpath(file.name))

    file.close()

    return file_path

# Take: Path of current debtsplan-text
# Do:   Print this txt-file 
# Note: Implemented if-statement based on current os
def printDebtsPlan():
    
    # windows
    if sys.platform == "win32":
        os.startfile(saveDebtsTxt(normalizeDebts(valueSortedDict(conservativeDebtsDict()))),"print")
    # rp3
    elif sys.platform == "linux":

        conn = cups.Connection()
        printers = conn.getPrinters()

        # Note: Only to check which printers are available
        for printer in printers:
            print(printer,printers[printer]["device-uri"])
        
        file = saveDebtsTxt(normalizeDebts(valueSortedDict(conservativeDebtsDict())))
        printer_name = list(printers.keys())[0]
        conn.printFile(printer_name,file,"",{})
    
    else:
        pass

##############################################################################################################################################################
### AUDIO ###################################################################################################################################################
##############################################################################################################################################################

sound_switch = True # Enable / Disable Sounds

pygame.mixer.pre_init(48000, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.init() #turn all of pygame on.

sound_dict = {}

# load sounds
sound_dict[0] = pygame.mixer.Sound("audio/cash-register-purchase-87313.ogg")
sound_dict[1] = pygame.mixer.Sound("audio/cash-register-purchase-87313.ogg")
sound_dict[2] = pygame.mixer.Sound("audio/cash-register-purchase-87313.ogg")
sound_dict[3] = pygame.mixer.Sound("audio/cash-register-purchase-87313.ogg")
sound_dict[4] = pygame.mixer.Sound("audio/cash-register-purchase-87313.ogg")

def playSound(rsound):
    if sound_switch == True:
        pygame.mixer.Sound.play(rsound)

##############################################################################################################################################################
### INPUT ####################################################################################################################################################
##############################################################################################################################################################

# FIXME: Input.presence is not necessary -> Replace Switch Button on Page 20 with Checkbutton-Widget
#        Associate boolean var with Checkbutton
#        When user presses safe -> change instance attribute based on roomie_slc and boolean var value
class Input:

    # which roomie is selected?
    roomie_slc = None
    # user switch input: roomie is absent / roomie is present
    presence = None

    # function: reset Input variables
    @classmethod
    def resetInput(cls):
        cls.roomie_slc = None
        cls.presence = None

####################################################################################################################################################################
### CONTROLLER #####################################################################################################################################################
####################################################################################################################################################################

# font constants
BUTTON_FONT=("Arial 11 bold italic")
TEXT_WIDGET_FONT = ("Arial", 11)

class Zwegat(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        # rp3
        # set main window size to rasperry pi 7" touchscreen size
        tk.Tk.geometry(self,"800x480")

        # application title
        tk.Tk.title(self,"Zwegat Alpha")
        
        # application icon
        # FIXME: iconbitmap-method doesn't work on linux. 
        if sys.platform == "win32":
            tk.Tk.iconbitmap(self,"images/zwegat.ico")
        elif sys.platform == "linux":
            # do something that displays icon on linux
            pass

        # application cursor
        tk.Tk.configure(self,cursor="heart")

        # Create standard frame - all frames are build upon this frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Page00,Page01,Page10,Page20,Page21,Page22,Page30,Page40,Page50,Page60):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid(row=0, column=0, sticky="NSEW")
        
        # avoid this first class, automatically show Page10
        self.showFrame(Page00)

    # Wrapper Function (get arbitrary number of functions (with arbitrary number of arguments) and call them)
    def wrapper(self,*funcs):
        def combined_func(*args,**kwargs):
            for f in funcs:
                f(self,*args, **kwargs)
        return combined_func

    # Function: show frame with page name as argument
    def showFrame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # Function: Select Roomie
    def slcRoomie(self,r):
        Input.roomie_slc=r

    # Function: After selecting roomie on Page10, check current presence status of this particular 
    # roomie and accordingly change switch button layout (this function should be called before showFrame-Function)
    def checkStatus(self):
            
        status = roomie_list[Input.roomie_slc].pres
        button = self.frames[Page20].switch_0
        red = self.frames[Page20].im_0_switch
        green = self.frames[Page20].im_1_switch

        if status == True:
            button.config(relief="sunken")
            button.config(image=green)
        elif status == False:
            button.config(relief="raised")
            button.config(image=red)

    # DAU-Function: Disallow anything but numbers, 1 dot and empty field
    # FIXME:        Double dots should be disallowed as well
    #               After whole line is deleted, function doesn't work anymore
    def giveMeCash(self, d, i, P, s, S, v, V, W):
        
        valid_characters = ["0","1","2","3","4","5","6","7","8","9","."]

        # convert P into list with characters as separate string elements
        listed_P = list(P)
    
        if any(character == S for character in valid_characters) and len(P) < 7 and listed_P[0] != "." or P == "":
            return True
        else:
            self.bell()
            return False

    # Function: transferExpInput
    def transferExpInput(self,roomienum,expinput,infoinput):

        amount=expinput.get()
        info = infoinput.get()
        roomie = roomie_list[roomienum]

        # Only call instance methods if user entered an amount
        if len(amount) > 0:
            float_amount = float(amount)

            # Call instance methods
            roomie.raiseExp(float_amount)
            roomie.addEx(float_amount)
            roomie.addEv(float_amount)
            roomie.addDate(tday)

            # Call class methods
            Roomie.raiseTotalExp(float_amount)
            Roomie.raiseMeanExp()
            Roomie.updateExpNum()

            # Calculate new residuals
            for person in roomie_list:
                person.updateRes(Roomie.mean_exp)
            
            # Update presence list
            for person in roomie_list:
                person.addPres()

            # Add None-value to evlist for every roomie except the one that bought smth
            custom_list = [x for i,x in enumerate(roomie_list) if i!=roomienum]
            for person in custom_list: 
                person.addEv(None)

            # add expense info if user gave input
            if len(info) > 0:
                roomie.addInfo(info)
            elif len(info) == 0:
                roomie.addInfo(None)

        elif len(amount) == 0:
            pass
            # Function: transferExpInput
    
    # FIXME: Same issue as in the init-method. This code is so similar to transferExpInput-function that I wonder if there's
    # a generic function that could combine transferExpInput and transferSpclExpInput
    def transferSpclExpInput(self,roomienum,expinput,infoinput):

        amount=expinput.get()
        info = infoinput.get()
        roomie = roomie_list[roomienum]

        # Only call instance methods if user entered an amount
        if len(amount) > 0:
            float_amount = float(amount)

            # Call instance methods
            roomie.raiseSpclExp(float_amount)
            roomie.addSpclEx(float_amount)
            roomie.addSpclEv(float_amount)
            roomie.addSpclDate(tday)

            # Call class methods
            Roomie.raiseSpclTotalExp(float_amount)
            Roomie.raiseSpclMeanExp()
            Roomie.updateSpclExpNum()

            # Calculate new residuals
            for person in roomie_list:
                person.updateSpclRes(Roomie.mean_exp)

            # Add None-value to evlist for every roomie except the one that bought smth
            custom_list = [x for i,x in enumerate(roomie_list) if i!=roomienum]
            for person in custom_list: 
                person.addSpclEv(None)

            # add expense info if user gave input
            if len(info) > 0:
                roomie.addSpclInfo(info)
            elif len(info) == 0:
                roomie.addSpclInfo(None)

        elif len(amount) == 0:
            pass

    # FIXME: - Input.presence is redundant -> use Checkbutton with associated boolean var
    #        - Take value of boolean var as Input.presence
    def transferStatusChange(self):
        # call changePres-Function
        roomie_list[Input.roomie_slc].changePres(Input.presence)

    def registerParticipation(self):
        for idx in range(0,len(roomie_list)):
            roomie_list[idx].addPart(self.frames[Page22].part_dict[idx].get())

    # Function: 
    # Do: Write current debts plan in text widget on Page30
    # FIXME: Make hypen-variable dynamic based on longest line in text-widget
    def writeTextWidget(self):
        
        conservative_debtslist = normalizeDebts(valueSortedDict(conservativeDebtsDict()))
        special_debtslist = normalizeDebts(valueSortedDict(specialExpenseDebtsDict()))
        global_debtslist = normalizeDebts(valueSortedDict(mergeDebts()))

        text_w = self.frames[Page30].text_0
        
        HYPHEN = "-" * 75
        doc_name = datetime.date.today().strftime('%Y_%B')
        zipped = []

        # Create functions for easy writing 
        def write(t):
            text_w.insert("end",t)
        def newLine():
            text_w.insert("end","\n")
        def doubleNewLine():
            text_w.insert("end","\n\n")
        def hyphenLine():
            text_w.insert("end","{}\n\n".format(HYPHEN))
        
        write("Abrechnungsdatum:\t{}".format(datetime.date.today().strftime("%d.%m.%Y")))
        doubleNewLine()
        hyphenLine()
        
        # Write expenses for each roomie including exp_info and date
        write("Normale Ausgaben:")
        doubleNewLine()
        for roomie in roomie_list:
            write("{}:".format(roomie.fname))
            doubleNewLine()
            zipped = list(zip(roomie.date,roomie.exlist,roomie.info))
            for (date,exp,info) in zipped:
                if info != None:
                    write("{}\t\t{}€\t{}\n".format(date,exp,info))
                elif info == None:
                    write("{}\t\t{}€\t{}\n".format(date,exp,""))
            newLine()
        hyphenLine()

        # Write global info
        write("Totale Ausgaben:\t\t\t\t{}€\nMittelwert:\t\t\t\t{}€\nGesamtzahl getätigter Ausgaben:\t\t\t\t{}".format(round(Roomie.total_exp,2),round(Roomie.mean_exp,2),Roomie.num_exp))
        doubleNewLine()        
        
        # Write debts plan
        write("Konservativer Schuldenplan:")
        doubleNewLine()
        for (creditor,debtor,amount) in conservative_debtslist:
            write('{} schuldet {} {}€\t\n'.format(roomie_list[creditor].fname,roomie_list[debtor].fname,round(amount,2)))
        newLine()
        hyphenLine()

        # Write special expenses for each roomie including info and date
        write("Sonderausgaben:")
        doubleNewLine()
        for roomie in roomie_list:
            write("{}:".format(roomie.fname))
            doubleNewLine()
            zipped = zip(roomie.spcl_date,roomie.spcl_exlist,roomie.spcl_info)
            for (date,exp,info) in zipped:
                print((date,exp,info))
                if info != None:
                    write("{}\t\t{}€\t{}\n".format(date,exp,info))
                elif info == None:
                    write("{}\t\t{}€\t{}\n".format(date,exp,""))
            newLine()
        hyphenLine()

        # Write special info
        write("Totale Sonderausgaben:\t\t\t\t\t{}€\nMittelwert:\t\t\t\t\t{}€\nGesamtzahl getätigter Sonderausgaben:\t\t\t\t\t{}".format(round(Roomie.total_spcl_exp,2),
            round(Roomie.mean_spcl_exp,2),Roomie.num_spcl_exp))
        doubleNewLine()
        
        # Write special debts plan
        write("Sonderausgaben Schuldenplan:")
        doubleNewLine()
        for (debtor,creditor,amount) in special_debtslist:
            write('{} schuldet {} {}€\t\n'.format(roomie_list[debtor].fname,roomie_list[creditor].fname,round(amount,2)))
        newLine()
        hyphenLine()

        write("Gesamtschuldenplan:")
        doubleNewLine()
        for (debtor,creditor,amount) in global_debtslist:
            write('{} schuldet {} {}€\t\n'.format(roomie_list[debtor].fname,roomie_list[creditor].fname,round(amount,2)))

    def enableTxtWidget(self):
        self.frames[Page30].text_0.configure(state="normal")
    
    def disableTxtWidget(self,txtwidget):
        txtwidget.configure(state="disabled")

    # Function: delete TextWidgetContent
    def deleteTxtWidget(self,txtwidget):
        txtwidget.configure(state="normal")
        txtwidget.delete("1.0","end")

    def deleteListbox(self,listbox):
        listbox.delete("0","end")

    def writeForecast(self,txtwidget):

        txtwidget.configure(state="normal")

        def write(text):
            txtwidget.insert("end",text)
        
        # grab forecast data from openweathermap api 
        # returns dictionary with forecast data for the next 5 days / 3 hr interval -  accordingly 40 values in dictionary
        def GrabForecast():
             
            lat = ""
            lon = ""
            appId = ""
            weatherUrl = 'http://api.openweathermap.org/data/2.5/forecast?lat=' + lat + '&lon=' + lon + '&lang=de&units=metric&appid=' + appId
            
            try:
                
                jsonFile = urlopen(weatherUrl)
                jsonFileContent = jsonFile.read().decode('utf-8')
                jsonObject = json.loads(jsonFileContent)

                forecast_dict = {}

                for idx in range(0,40):
                    forecast_dict[idx] = jsonObject['list'][idx]
                    
                return forecast_dict

            except:

                print("error")

        # create customized forecast dictionary only needed forecast information (interval can be changed by adjusting step size in for loop)
        def returnMyForecast(forecast,interval=1):

            def formatTimestamp(timestamp):
                return datetime.datetime.fromtimestamp(timestamp).strftime('%A, %H:%M:%S')

            myforecast = {}

            for idx in range(0,40,interval):
                
                myforecast[idx] = []

                myforecast[idx].append(formatTimestamp(forecast[idx]['dt']))
                myforecast[idx].append(forecast[idx]['main']['temp'])
                myforecast[idx].append(forecast[idx]['main']['humidity'])
                myforecast[idx].append(forecast[idx]['weather'][0]['description'])

            return myforecast

        myforecast = returnMyForecast(GrabForecast(),2)

        for key in myforecast:
            write(myforecast[key][0])
            write('\n')
            write(myforecast[key][1])
            write(" Grad")
            write('\n')
            write(myforecast[key][2])
            write(" {} Luftfeuchtigkeit".format("%"))
            write('\n')
            write(myforecast[key][3])
            write('\n\n')

    # Function: Reset user input vars when "back"-button on PAGE 20 is pressed
    # FIXME: Input.presence is redundant
    def resetInput(self,*args):

        Input.presence = None
        
        # clear entry fields
        for arg in args:
            arg.delete(0,"end")

    # reset checkbutton variable back to False. This will also automatically change Checkbutton-relief back to raised
    def resetCheckbutton(self):
        for idx in range(0,len(roomie_list)):
            self.frames[Page22].part_dict[idx].set(False)

    # Save current debts plan as txt file
    # Customize: Decide here which DebtsDict should be saved
    def savePlan(self):
        try:
            saveDebtsTxt(normalizeDebts(valueSortedDict(conservativeDebtsDict())))
            messagebox.showinfo("Zwegat Alpha","Plan gespeichert")
        except:
            messagebox.showwarning("Zwegat Alpha","Plan konnte nicht gespeichert werden")

    # print current debts plan
    def printPlan(self):
        try:
            printDebtsPlan()
            messagebox.showinfo("Zwegat Alpha","Druckauftrag gesendet")
        except:
            messagebox.showwarning("Zwegat Alpha","Plan konnte nicht gedruckt werden")

    # Do:   Ask user for "Ok"
    #       Call functions based on user decision
    # Note: Provide functions and their arguments as tuples
    # Note: When function takes no argument provide it as a one-element tuple in pythonic fashion -> (element,)
    # See:  https://wiki.python.org/moin/TupleSyntax
    def askOk(self,question,*funcs,cutoff):
    
        ans = messagebox.askokcancel("Zwegat Alpha",question)
        
        # functions to be called when ans = True 
        true_funcs = funcs[:cutoff]
        # function to be called when ans = False
        false_funcs = funcs[cutoff:len(funcs)]

        def callTupleFunc(func,*args):
            func(*args)

        if ans == True:
            for func in true_funcs:
                callTupleFunc(*func)
        elif ans == False:
            for func in false_funcs:
                callTupleFunc(*func)

    def checkCriterion(self,error,*args,cutoff,criterion):

        # all arguments until cutoff are variables to be evaluated
        varlist = args[:cutoff]
        # all arguments after cutoff are functions to be called when all variables match criterion
        funcs = args[cutoff:]
        # boolean that is only true when ALL variables meet criterion and is set to False when >= 1 variables don't meet criterion
        gate = True

        def callTupleFunc(func,*args):
            func(*args)

        for var in varlist:

            # check for case all variables
            if all(var != criterion for var in varlist):
                gate = False

        if gate == True:

            # open askokcancel messagebox
            ans = messagebox.askokcancel("Zwegat Alpha","Speichern und zurück?")
            
            if ans == True:
                for func in funcs:
                    callTupleFunc(*func)
        
        elif gate == False:
                messagebox.showerror("Zwegat Alpha",error)

    # save all instances of Roomie class as pkl-files
    def pickleRoomies(self):

        # save instances
        file_name = "save/Schuldenplan_{}.pkl".format(datetime.date.today().strftime('%Y_%m_%d'))

        with open(file_name,"wb") as file_object:
            pickle.dump(roomie_list,file_object)

        # Save class variables in seperate file
        # FIXME: Since class variables can't be pickled AFTER been manipulated by class methods I had to create a list object
        # containing copies of class variables
        class_vars = []

        class_vars.append(Roomie.num_roomies)
        class_vars.append(Roomie.total_exp)
        class_vars.append(Roomie.total_spcl_exp)
        class_vars.append(Roomie.mean_exp)
        class_vars.append(Roomie.mean_spcl_exp)
        class_vars.append(Roomie.num_exp)
        class_vars.append(Roomie.num_spcl_exp)

        with open("save/classvars_{}.pkl.".format(datetime.date.today().strftime('%Y_%m_%d')),"wb") as file_object:
            pickle.dump(class_vars,file_object)

    # FIXME: List contains duplicates with every call of this function
    def searchAndWritePickles(self):
        
        # search for .pkl files in save directory
        for file in os.listdir("save"):
            if file.startswith("Schuldenplan"):
                self.frames[Page01].picklepath.append(os.path.join("save", file))
       
        # create copy of path list
        pretty_picklepath = list(self.frames[Page01].picklepath)

        # change copy to a more userfriendly appearance
        for path in range(0,len(pretty_picklepath)):
            new_str = pretty_picklepath[path].replace("save\\","")
            new_str = pretty_picklepath[path].replace(".pkl","")
        
        # insert userfriendly path strings to listbox
        for prettypath in pretty_picklepath:
            self.frames[Page01].list_0.insert("end",prettypath)    

    def loadPickle(self):

        global roomie_list
        
        selection = self.frames[Page01].list_0.curselection()
        index = selection[0]
        filepath = self.frames[Page01].picklepath[index]

        file = open(filepath, "rb" )
        
        roomie_list = pickle.load(file)

        # find corresponding class var pickle file
        identifier = filepath[-15:]

        for filepath in os.listdir("save"):
            if filepath.startswith("classvars") and filepath.endswith(identifier):

                with open("save/{}".format(filepath),"rb") as file:
                    classvars = pickle.load(file)

        Roomie.num_roomies = classvars[0]
        Roomie.total_exp = classvars[1]
        Roomie.total_spcl_exp = classvars[2]
        Roomie.mean_exp = classvars[3]
        Roomie.mean_spcl_exp = classvars[4]
        Roomie.num_exp = classvars[5]
        Roomie.num_spcl_exp = classvars[6]

    # Do: Reset all input variables, roomie class attributes, and object attributes back to their initial state
    def resetZwegat(self):
        Input.resetInput()
        Roomie.resetClass()

        for r in roomie_list:
            r.resetObject()

    def closeZwegat(self):
        self.destroy()

####################################################################################################################################################################
### VIEW ###########################################################################################################################################################
####################################################################################################################################################################

class Page00(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        #########################################################################################
        ## PAGE 00: LAYOUT ######################################################################
        #########################################################################################

        # Create master label 
        mlabel = tk.Label(self)
        mlabel.pack(fill="both",expand="yes")
        
        # Label rows and columns are stretchable
        n_rows = 1
        n_columns = 2

        for r in range(0,n_rows):
            mlabel.grid_rowconfigure(r,weight=1)
        for c in range(0,n_columns):
            mlabel.grid_columnconfigure(c,weight=1)

        # background image
        self.image_path = "images/bluestripes.png"
        self.bg_image = ImageTk.PhotoImage(file=self.image_path)

        mlabel.configure(image=self.bg_image)
        mlabel.image = self.bg_image

        # --- BUTTONS -------------------------------------------------------------------------------------

        button_image_list = [
        "images/wickie.png",
        "images/folder.png"
        ]

        button_text = [
        "Neuen Plan erstellen",
        "Alten Plan laden"
        ]

        button_image_dict = {}
        
        for im in range(0,2):
            button_image_dict[im] = ImageTk.PhotoImage(file=button_image_list[im])
            button_image_dict[im].image = ImageTk.PhotoImage(file=button_image_list[im])

        n_buttons = 2
        button_columns= [0,1]
        button_dict = {}

        for b,c in zip(range(0,n_buttons),button_columns):
            button_dict[b] = tk.Button(mlabel)
            button_dict[b].grid(row=0,column=c,sticky="S",padx=50,pady=125)
            button_dict[b].configure(image=button_image_dict[b],text=button_text[b],relief="raised",bd=5)
            button_dict[b].image = button_image_dict[b]

        ########################################################################################
        # PAGE 00: BUTTON COMMANDS #############################################################
        ########################################################################################

        # new plan button
        button_dict[0].configure(command=lambda: controller.showFrame(Page10))

        # load plan button
        button_dict[1].configure(command=lambda: 
            controller.wrapper(
            controller.showFrame(Page01),
            controller.searchAndWritePickles()))

class Page01(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # Page 01: Load debtsplan

        #########################################################################################
        ## PAGE 01: LAYOUT ######################################################################
        #########################################################################################
        
        # create 4 frames as containers
        frames = {}

        for f in range(0,4):
            frames[f] = tk.Frame(self)

        frames[0].grid(row=0,columnspan=2)  #contains top label
        frames[1].grid(row=1,column=0)      #contains text widget
        frames[2].grid(row=1,column=1)      #contains scrollbar
        frames[3].grid(row=2,columnspan=2)  #contains bottom label 

        # all 4 container frames shall expand
        for frame in frames:
            frames[frame].grid_configure(sticky="NSEW")
        
        # make all columns and rows expandable in frame 0,1,2,3
        for f in range(0,4):
            frames[f].grid_columnconfigure(0,weight=1)
            frames[f].grid_rowconfigure(0,weight=1)

        # LABELS
        # Top Label
        label_0 = tk.Label(frames[0])
        label_0.grid(sticky="NSWE")
        label_0.grid_rowconfigure(0,weight=1)
        label_0.grid_columnconfigure(0,weight=1)

        label_0.configure(image=controller.frames[Page00].bg_image)
        label_0.image = controller.frames[Page00].bg_image

        # Bottom Label
        label_1 = tk.Label(frames[3])
        label_1.grid(sticky="NSEW")

        # Bottom Label: make all rows and columns stretchable
        label_1.grid_rowconfigure(0,weight=1)
        label_1.grid_columnconfigure(0,weight=1)
        label_1.grid_columnconfigure(1,weight=1)

        # Put image on bottom label
        label_1.configure(image=controller.frames[Page00].bg_image)
        label_1.image = controller.frames[Page00].bg_image
        
        # --- LISTBOX -------------------------------------------------------------------------------------

        self.list_0 = tk.Listbox(frames[1],height=17)
        self.list_0.grid(sticky="NSEW")
        self.list_0.configure(font=TEXT_WIDGET_FONT,cursor="heart",activestyle="none")

        # list containing paths to all existing pkl-files
        self.picklepath = []

        # SCROLLBAR
        self.scrollbar_0 = tk.Scrollbar(frames[2])
        self.scrollbar_0.grid(sticky="NS")
        self.scrollbar_0.configure(width=40)

        # connect scrollbar and text widget
        self.scrollbar_0.config(command=self.list_0.yview)
        self.list_0.config(yscrollcommand=self.scrollbar_0.set)

        # Create navigation buttons (Back/Save)
        nav_dict = {}
        n_buttons = 2
        nav_names = ["Zurück","Weiter"]
        columns = [0,1]
        for b,c in zip(range(0,n_buttons),columns):
            nav_dict[b] = tk.Button(label_1,text=nav_names[b])
            nav_dict[b].grid(row=1,column=c,pady=30,ipadx=10,ipady=10)
            nav_dict[b].configure(relief = "raise",bd=5,font=BUTTON_FONT)

        #########################################################################################
        ## PAGE 01: BUTTON COMMANDS ###########################################################
        #########################################################################################
        
        # back button
        nav_dict[0].configure(command=lambda:controller.wrapper(
            controller.deleteListbox(self.list_0),
            controller.showFrame(Page00)
            )
        )
        
        # next button 
        nav_dict[1].configure(command=lambda: controller.wrapper(
            controller.showFrame(Page10),
            controller.loadPickle()
            )
        )

class Page10(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        ########################################################################################
        # PAGE 10: LAYOUT ######################################################################
        ########################################################################################

        # roomie button images for Page10
        roomie_image_list = [
        "images/roomie_1.png",     # roomie 0
        "images/roomie_1.png",        # roomie 1
        "images/roomie_1.png",       # roomie 2
        "images/roomie_1.png",   # roomie 3
        "images/roomie_1.png",       # roomie 4
        ]
   
        self.roomie_image_dict = {}

        # load image dict with images
        for image in range(0,len(roomie_image_list)):
            self.roomie_image_dict[image] = ImageTk.PhotoImage(file=roomie_image_list[image])

        # background & button images
        layout_image_list = [
        "images/bluestripes.png",   # background image
        "images/dollar.png",        # settlement button
        "images/radio.png",         # radio button
        "images/todo.png",          # to-do-list button
        "images/sunclouds.png",       # weather button
        "images/exit.png"           # exit button
        ]

        self.layout_image_dict = {}

        # load image dict with images
        for image in range(0,len(layout_image_list)):
            self.layout_image_dict[image] = ImageTk.PhotoImage(file=layout_image_list[image])

        # Create label as master
        # Label expands in all directions
        label_0 = tk.Label(self)
        label_0.grid(row=0,column=0,sticky="NSEW")

        # Label has expandable columns(as many as roomies) and rows
        for c in range(0,len(roomie_list)):
            label_0.grid_columnconfigure(c,weight=1)
        
        label_0.grid_rowconfigure(0,weight =1)
        label_0.grid_rowconfigure(1,weight=1)

        label_0.configure(image=self.layout_image_dict[0])
        label_0.image = self.layout_image_dict[0]

        # roomie button dict
        # Note:  roomie button dict is referenced so that width and height can be printed later 
        self.roomie_button_dict = {}

        for b in range(0,len(roomie_list)):
            self.roomie_button_dict[b] = tk.Button(label_0,image=self.roomie_image_dict[b])
            self.roomie_button_dict[b].image=self.roomie_image_dict[b]
            self.roomie_button_dict[b].grid(row=0,column=b,sticky="NSEW")   
            self.roomie_button_dict[b].grid_configure(padx=25,pady=40)
            self.roomie_button_dict[b].configure(relief = "raise",bd = 5)
        
        # control button dict
        # settlement button, radio button, to-do-list button
        self.menu_button_dict = {}

        for idx,img in zip(range(0,5),range(1,6)):
            self.menu_button_dict[idx] = tk.Button(label_0)
            self.menu_button_dict[idx].grid(row=1,column=idx)
            self.menu_button_dict[idx].grid_configure(padx=5,pady=40)
            self.menu_button_dict[idx].configure(relief="raised",bd=5)
            self.menu_button_dict[idx].configure(image=self.layout_image_dict[img])
            self.menu_button_dict[idx].image = self.layout_image_dict[img]
        
        ########################################################################################
        # PAGE 10: BUTTON COMMANDS #############################################################
        ########################################################################################

        # button commands for settlement button
        self.menu_button_dict[0].configure(command=lambda:
            controller.wrapper(controller.enableTxtWidget(),
            controller.writeTextWidget(),
            controller.disableTxtWidget(controller.frames[Page30].text_0),
            controller.showFrame(Page30)))
        
        # button commands for radio button 
        self.menu_button_dict[1].configure(command=lambda:controller.showFrame(Page40))

        # button commands for to-do-list button
        self.menu_button_dict[2].configure(command=lambda:
            controller.showFrame(Page50))

        # button commands for weather button
        self.menu_button_dict[3].configure(
            command=lambda:
            controller.wrapper(
            controller.showFrame(Page60),
            controller.writeForecast(controller.frames[Page60].text_0),
            controller.disableTxtWidget(controller.frames[Page60].text_0)
                )
            )

        # FIXME: button commands for exit-button
        self.menu_button_dict[4].configure(command=lambda:
            controller.askOk("Willst du Zwegat beenden?",(controller.closeZwegat,),cutoff=1))

        # Button commands for roomie-buttons
        # 1) Call slcRoomie-function when button is pressed
        # 2) Call checkStatus-function -> check roomie status and correspondingly change switch button layout on Page20
        # 3) Show Page20

        for b in range(0,len(roomie_list)):
            self.roomie_button_dict[b].configure(command=lambda b=b: 
                controller.wrapper(controller.slcRoomie(b),
                controller.checkStatus(),
                controller.showFrame(Page20)))

class Page20(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        #########################################################################################
        ## PAGE 20: LAYOUT ######################################################################
        #########################################################################################

        # Create master label 
        mlabel = tk.Label(self)
        mlabel.pack(fill="both",expand="yes")
        
        # Label rows and columns are stretchable
        n_rows = 2
        n_columns = 3

        for r in range(0,n_rows):
            mlabel.grid_rowconfigure(r,weight=1)
        for c in range(0,n_columns):
            mlabel.grid_columnconfigure(c,weight=1)

        # Put background image on master label
        mlabel.configure(image=controller.frames[Page10].layout_image_dict[0])
        mlabel.image = controller.frames[Page10].layout_image_dict[0]

        # --- BUTTONS -------------------------------------------------------------------------------------

        button_image_list = [
        "images/cart.png",
        "images/special.png"
        ]

        button_image_dict = {}
        
        for im in range(0,2):
            button_image_dict[im] = ImageTk.PhotoImage(file=button_image_list[im])
            button_image_dict[im].image = ImageTk.PhotoImage(file=button_image_list[im])

        n_buttons = 2
        button_columns= [0,2]
        self.button_dict = {}

        for b,c in zip(range(0,n_buttons),button_columns):
            self.button_dict[b] = tk.Button(mlabel)
            self.button_dict[b].grid(row=0,column=c,padx=50,pady=90)
            self.button_dict[b].configure(image=button_image_dict[b],relief="raised",bd=5)
            self.button_dict[b].image = button_image_dict[b]

        # --- SWITCH BUTTON -------------------------------------------------------------------------------

        # Note: toogle button is referenced to so it can be accessed from controller
        # This is needed for CheckStatus-Function 
        self.switch_0 = tk.Button(mlabel)
        self.switch_0.grid(row=0,column=1,pady=90)
        self.switch_0.configure(relief="sunken",bd=5)

        # switch Button Images
        self.im_0_switch = ImageTk.PhotoImage(file="images/red-button_150x150.png")
        self.switch_0.im_0 = self.im_0_switch

        self.im_1_switch = ImageTk.PhotoImage(file="images/green-button_150x150.png")
        self.switch_0.configure(image=self.im_1_switch)
        self.switch_0.im_1 = self.im_1_switch

        # Create navigation buttons (Back/Save)
        nav_dict = {}
        n_buttons = 2
        nav_names = ["Zurück","Speichern"]
        columns = [0,2]
        for b,c in zip(range(0,n_buttons),columns):
            nav_dict[b] = tk.Button(mlabel,text=nav_names[b])
            nav_dict[b].grid(row=1,column=c,padx=50,pady=30,ipadx=15,ipady=10,sticky="EW")
            nav_dict[b].configure(relief = "raise",bd=5,font=BUTTON_FONT)

        #########################################################################################
        ## PAGE 20: BUTTON COMMANDS #############################################################
        #########################################################################################

        #switch button 0:
        #Function: change user input presence status for current selected roomie and switch button layout
        def switch():

            if self.switch_0.config("relief") [-1] == "raised":
                self.switch_0.config(relief="sunken")
                self.switch_0.config(image=self.im_1_switch)
                Input.presence = True
            else:
                self.switch_0.config(relief="raised")
                self.switch_0.config(image=self.im_0_switch)
                Input.presence = False

        # bind switch-function to switch button
        self.switch_0.config(command=switch)

        # Back-Button 0: 
        # 1) showFrame: go back to PAGE 10
        nav_dict[0].configure(command=lambda:controller.showFrame(Page10))

        # Save-Button 1:
        # Ask-Ok-function:
        # If yes: 
            # 1) Call transferStatusChange-function
            # 2) Go back to Start Page
        # If no:
            # 5) Go back to Start Page
        nav_dict[1].configure(command=lambda: 
            controller.askOk("Willst du deinen Status ändern?",
                (controller.transferStatusChange,),
                (controller.showFrame,Page10),
                (controller.showFrame,Page20),
                cutoff=2))

        # Expense Button
        # Show Frame 21
        self.button_dict[0].configure(command=lambda:controller.showFrame(Page21))

        # Special Expense Button
        # show Frame 22
        self.button_dict[1].configure(command=lambda:controller.showFrame(Page22))

class Page21(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        # Page 21: Single expense

        #########################################################################################
        ## PAGE 21: LAYOUT ######################################################################
        #########################################################################################

        # Create master label 
        mlabel = tk.Label(self)
        mlabel.pack(fill="both",expand="yes")
        
        # Label rows and columns are stretchable
        n_rows = 2
        n_columns = 2

        for r in range(0,n_rows):
            mlabel.grid_rowconfigure(r,weight=1)
        for c in range(0,n_columns):
            mlabel.grid_columnconfigure(c,weight=1)

        # Put background image on master label
        mlabel.configure(image=controller.frames[Page10].layout_image_dict[0])
        mlabel.image = controller.frames[Page10].layout_image_dict[0]

        # -- FRAME -----------------------------------------------------------------------------

        # Create 1 frames as container with mlabel as master
        frame_0 = tk.Frame(mlabel)
        frame_0.grid(row=0,column=0,padx=120,pady=80,ipadx=5,ipady=50,columnspan=2)
        frame_0.configure(relief="sunken",bd=5)

        for c in range(0,3):
            frame_0.grid_columnconfigure(c,weight=1)

        for r in range(0,2):
            frame_0.grid_rowconfigure(r,weight=1)

        # -- LABELS & ENTRIES  -----------------------------------------------------------------

        label_dict = {}
        label_names = ["Betrag:","€","Info:"]
        label_rows = [0,0,1]
        label_columns = [0,2,0]

        entries = {}
        entry_rows = [0,1]
        entry_columns = [1,1]

        for l,r,c in zip(range(0,4),label_rows,label_columns):
            label_dict[l] = tk.Label(frame_0)
            label_dict[l].grid(row=r,column=c,ipadx=10,ipady=10,sticky="W")
            label_dict[l].configure(text=label_names[l],font=BUTTON_FONT)

        for idx,r,c in zip(range(0,2),entry_rows,entry_columns):
            entries[idx]= tk.Entry(frame_0)
            entries[idx].grid(row=r,column=c,ipady=10,sticky="W")
            entries[idx].configure(font=BUTTON_FONT)

        # -- ENTRY VARIABLES  -----------------------------------------------------------------

        entries_input = {}

        for entry in range(0,2):
            entries_input[entry] = tk.StringVar()
            entries[entry].configure(textvariable=entries_input[entry])

        # -- NAVIGATION BUTTONS  --------------------------------------------------------------

        # Create navigation buttons (Back/Save)
        nav_dict = {}
        n_buttons = 2
        nav_names = ["Zurück","Speichern"]
        columns = [0,1]
        for b,c in zip(range(0,n_buttons),columns):
            nav_dict[b] = tk.Button(mlabel,text=nav_names[b])
            nav_dict[b].grid(row=1,column=c,padx=100,pady=30,ipadx=10,ipady=10)
            nav_dict[b].configure(relief = "raise",bd=5,font=BUTTON_FONT)
            nav_dict[b].grid_configure(sticky="EW")

        #########################################################################################
        ## PAGE 21: DAU FUNCTIONS ###############################################################
        #########################################################################################

        vcmd = (controller.register(controller.giveMeCash),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Entry field 0: call back giveMeCash function for only accepting money input 
        entries[0].configure(validate="key", validatecommand=vcmd)

        # FIXME: Use lambda functions to dynamically call trace <method with variable arguments
        # Reason: Without lambda I have to hardcode limitEntry both on Page 21 and Page 22
        # I would be glad to be teached how lambda works, tried desperately to understand the logic behind this ****
        # See: https://stackoverflow.com/questions/15659342/callback-functions-associated-with-tkinter-traces-in-python3
        # See: https://stackoverflow.com/questions/25460653/pass-multiple-arguments-to-callback-for-a-stringvar-in-tkinter
        
        def limitEntry(*args):
            value = entries_input[1].get()
            if len(value) > 30: 
                entries_input[1].set(value[:30])
                self.bell()
        
        # Entry field 1: allow maximum 30 characters
        entries_input[1].trace("w",limitEntry)

        #########################################################################################
        ## PAGE 21: BUTTON COMMANDS #############################################################
        #########################################################################################

        # Back-Button 0: 
        # 1) resetInput: reset all input vars, clear entry fields
        # 2) showFrame: go back to Page 10

        nav_dict[0].configure(command=lambda: 
            controller.wrapper(controller.resetInput(entries[0],entries[1]),
                controller.showFrame(Page20)))

        # Save-Button 1:
        # Ask-Ok-function:
        # If yes: 
            # 1) Call transferExpInput-function
            # 2) Reset all input vars and clear entry fields
            # 3) Set focus back to first entry field
            # 4) go back to PAGE 10
        # If no:
            # 5) go back to Page20
        nav_dict[1].configure(command=lambda:
            controller.askOk("Speichern und zurück?",
            (controller.transferExpInput,Input.roomie_slc,entries[0],entries[1]),
            (controller.resetInput,entries[0],entries[1]),
            (controller.showFrame,Page10),
            (playSound,sound_dict[Input.roomie_slc]),
            (controller.showFrame,Page20),
            cutoff=4))

class Page22(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Page22: Special Expense

        #########################################################################################
        ## PAGE 22: LAYOUT ######################################################################
        #########################################################################################
        
        # Create label as master
        # Label expands in all directions
        mlabel = tk.Label(self)
        mlabel.grid(row=0,column=0,sticky="NSEW")

        # Label has expandable columns(as many as roomies) and rows
        for c in range(0,len(roomie_list)):
            mlabel.grid_columnconfigure(c,weight=1)
        
        mlabel.grid_rowconfigure(0,weight =1)
        mlabel.grid_rowconfigure(1,weight=1)

        # background image
        mlabel.configure(image=controller.frames[Page10].layout_image_dict[0])
        mlabel.image = controller.frames[Page10].layout_image_dict[0]

        self.checkbutton_dict = {}

        for b in range(0,len(roomie_list)):
            self.checkbutton_dict[b] = tk.Checkbutton(mlabel,indicatoron=0)
            self.checkbutton_dict[b].grid(row=0,column=b)   
            self.checkbutton_dict[b].grid_configure(padx=25,pady=40)
            self.checkbutton_dict[b].configure(relief = "raise",bd = 5)
            self.checkbutton_dict[b].configure(image=controller.frames[Page10].roomie_image_dict[b])
            self.checkbutton_dict[b].image = controller.frames[Page10].roomie_image_dict[b]

        self.part_dict = {}

        for idx in range(0,len(roomie_list)):
            self.part_dict[idx] = tk.BooleanVar()
            self.checkbutton_dict[idx].configure(variable=self.part_dict[idx])

        # -- FRAME -----------------------------------------------------------------------------

        # Create 1 frames as container with mlabel as master
        frame_0 = tk.Frame(mlabel)
        frame_0.grid(row=1,column=0,columnspan=len(roomie_list),padx=25,sticky="EW")
        frame_0.configure(relief="sunken",bd=5)

        for c in range(0,5):
            frame_0.grid_columnconfigure(c,weight=1)

        frame_0.grid_rowconfigure(0,weight=1)

        # -- LABELS & ENTRIES  -----------------------------------------------------------------

        # FIXME:    I wanted to have space between only RIGHT side of € and only left side of Info.
        #           That's why I used this horrible "multiple spaces string"-option
        #           padx-Option always adds space both to the left and right side (as far as I know)
        label_names = ["Sonderbetrag:","€","                                 ","Info:"]
        label_dict = {}
        label_rows = [0,0,0,0]
        label_columns = [0,2,3,4]

        entries = {}
        entry_rows = [0,0,0]
        entry_columns = [1,5]

        for l,r,c in zip(range(0,4),label_rows,label_columns):
            label_dict[l] = tk.Label(frame_0)
            label_dict[l].grid(row=r,column=c,ipady=10,pady=5)
            label_dict[l].configure(text=label_names[l],font=BUTTON_FONT)

        for idx,r,c in zip(range(0,2),entry_rows,entry_columns):
            entries[idx]= tk.Entry(frame_0)
            entries[idx].grid(row=r,column=c,ipady=10,pady=5)
            entries[idx].configure(font=BUTTON_FONT)

        # -- ENTRY VARIABLES  -----------------------------------------------------------------

        entries_input = {}

        for entry in range(0,2):
            entries_input[entry] = tk.StringVar()
            entries[entry].configure(textvariable=entries_input[entry])

        #########################################################################################
        ## PAGE 22: DAU FUNCTIONS ###############################################################
        #########################################################################################

        vcmd = (controller.register(controller.giveMeCash),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Entry field 0: call back giveMeCash function for only accepting money input 
        entries[0].configure(validate="key", validatecommand=vcmd)

        # FIXME: Use lambda functions to dynamically call trace method with variable arguments
        # Reason: Without lambda I have to hardcode limitEntry both on Page 21 and Page 22
        # I would be glad to be teached how lambda works, tried desperately to understand the logic behind this ****
        # See: https://stackoverflow.com/questions/15659342/callback-functions-associated-with-tkinter-traces-in-python3
        # See: https://stackoverflow.com/questions/25460653/pass-multiple-arguments-to-callback-for-a-stringvar-in-tkinter
        
        def limitEntry(*args):
            value = entries_input[1].get()
            if len(value) > 30: 
                entries_input[1].set(value[:30])
                self.bell()
        
        # Entry field 1: allow maximum 30 characters
        entries_input[1].trace("w",limitEntry)

        # -- NAVIGATION BUTTONS  --------------------------------------------------------------

        # Create navigation buttons (Back/Save)
        nav_dict = {}
        n_buttons = 2
        nav_names = ["Zurück","Speichern"]
        columns = [0,len(roomie_list)-1]
        for b,c in zip(range(0,n_buttons),columns):
            nav_dict[b] = tk.Button(mlabel,text=nav_names[b])
            nav_dict[b].grid(row=2,column=c,padx=25,pady=25,ipady=10)
            nav_dict[b].configure(relief = "raise",bd=5,font=BUTTON_FONT)
            nav_dict[b].grid_configure(sticky="EW")
        
        #########################################################################################
        ## PAGE 22: BUTTON COMMANDS ############################################################
        #########################################################################################

        # Back-Button
        nav_dict[0].configure(command=lambda: 
            controller.wrapper(
            controller.resetCheckbutton(),
            controller.resetInput(entries[0],entries[1]),
            controller.showFrame(Page20)))

        # Save Button
        nav_dict[1].configure(command=lambda:
            controller.checkCriterion("Bitte wähle mindestens 1 Mitbewohnerix",
            self.part_dict[0].get(),
            self.part_dict[1].get(),
            self.part_dict[2].get(),
            self.part_dict[3].get(),
            self.part_dict[4].get(),
            (controller.registerParticipation,),
            (controller.transferSpclExpInput,Input.roomie_slc,entries[0],entries[1]),
            (controller.resetCheckbutton,),
            (controller.resetInput,entries[0],entries[1]),
            (controller.showFrame,Page10),
            (playSound,sound_dict[Input.roomie_slc]),
            cutoff=5,
            criterion=True))

class Page30(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)

        # Page 30: Settlement Page

        #########################################################################################
        ## PAGE 30: LAYOUT ######################################################################
        #########################################################################################
        
        # create 4 frames as containers
        frames = {}

        for f in range(0,4):
            frames[f] = tk.Frame(self)

        frames[0].grid(row=0,columnspan=2)  #contains top label
        frames[1].grid(row=1,column=0)      #contains text widget
        frames[2].grid(row=1,column=1)      #contains scrollbar
        frames[3].grid(row=2,columnspan=2)  #contains bottom label 

        # all 4 container frames shall expand
        for frame in frames:
            frames[frame].grid_configure(sticky="NSEW")
        
        # make all columns and rows expandable in frame 0,1,2,3
        for f in range(0,4):
            frames[f].grid_columnconfigure(0,weight=1)
            frames[f].grid_rowconfigure(0,weight=1)

        # -- LABELS -----------------------------------------------------------------------------

        # Top Label
        label_0 = tk.Label(frames[0])
        label_0.grid(sticky="NSWE",ipady=50)
        label_0.grid_rowconfigure(0,weight=1)
        label_0.grid_columnconfigure(0,weight=1)

        # put background image on label
        label_0.configure(image=controller.frames[Page10].layout_image_dict[0])
        label_0.image = controller.frames[Page10].layout_image_dict[0]

        # Bottom Label
        label_1 = tk.Label(frames[3])
        label_1.grid(sticky="NSEW")

        # Bottom Label: make all rows and columns stretchable
        label_1.grid_rowconfigure(0,weight=1)
        label_1.grid_columnconfigure(0,weight=1)
        label_1.grid_columnconfigure(1,weight=1)
        label_1.grid_columnconfigure(2,weight=1)
        label_1.grid_columnconfigure(3,weight=1)

        # Put image on bottom label
        label_1.configure(image=controller.frames[Page10].layout_image_dict[0])
        label_1.image = controller.frames[Page10].layout_image_dict[0]

        # -- BUTTONS --------------------------------------------------------------------------

        button_dict = {}
        button_text = ["Zurück","Drucken","Speichern","Neuer Plan"]

        for b in range(0,len(button_text)):
            button_dict[b] = tk.Button(label_1,text=button_text[b],relief="raised",bd=5)
            button_dict[b].grid_configure(row=0,column=b,sticky="NSEW",padx=50)
            button_dict[b].configure(font=BUTTON_FONT)
            
        # TEXT-WIDGET
        self.text_0 = tk.Text(frames[1])
        self.text_0.grid(sticky="NSEW")
        self.text_0.configure(font=TEXT_WIDGET_FONT,cursor="heart")

        # SCROLLBAR
        self.scrollbar_0 = tk.Scrollbar(frames[2])
        self.scrollbar_0.grid(sticky="NSEW")
        self.scrollbar_0.configure(width=40)

        # connect scrollbar and text widget
        self.scrollbar_0.config(command=self.text_0.yview)
        self.text_0.config(yscrollcommand=self.scrollbar_0.set)

        #########################################################################################
        ## PAGE 30: BUTTON COMMANDS #############################################################
        #########################################################################################

        # BACK-BUTTON
        # 1) Delete Content in text widget
        # 2) Show PAGE 10
        button_dict[0].configure(command=lambda: 
            controller.wrapper(controller.deleteTxtWidget(self.text_0),
                controller.showFrame(Page10)))

        # PRINT-BUTTON
        # 1) Call savePlan-function to create current debts txt (this saves path in Output.file_path)
        # 2) Call printDebtsPlan-function to print this txt
        button_dict[1].configure(command=lambda: 
            controller.wrapper(controller.savePlan(),
                controller.printPlan()))

        # SAVE-BUTTON
        # 1) Call savePlan-function
        button_dict[2].configure(command=lambda: 
            controller.wrapper(
            controller.savePlan(),
            controller.pickleRoomies()
                )
            )

        # NEW-PLAN-BUTTON
        # Function: askOK
        #    If yes:
        #       1) Call resetZwegat-function
        #       2) Delete Content in Text Widget
        #       3) Go back to Page10
        #    If no:
        #       4) showFrame(Page30)        
        button_dict[3].configure(command=lambda:
            controller.askOk("Do you really want to summon a new Zwegat?",
                (controller.resetZwegat,),
                (controller.deleteTxtWidget,self.text_0),
                (controller.showFrame,Page10),
                (controller.showFrame,Page30),cutoff=3)
            )

class Page40(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)

        # Page 40: Radio

        #########################################################################################
        ## PAGE 40: LAYOUT ######################################################################
        #########################################################################################
        
        # Create master label 
        mlabel = tk.Label(self)
        mlabel.pack(fill="both",expand="yes")
        
        # Label has expandable rows and columns
        for roco in range(0,3):
            mlabel.grid_rowconfigure(roco,weight=1)
            mlabel.grid_columnconfigure(roco,weight=1)

        # Put background image on master label
        mlabel.configure(image=controller.frames[Page10].layout_image_dict[0])
        mlabel.image = controller.frames[Page10].layout_image_dict[0]

        # --- Web Radio URLs -------------------------------------------------------------

        radio_url_list = [
            "https://wdr-1live-live.sslcast.addradio.de/wdr/1live/live/mp3/128/stream.mp3",
            "https://wdr-cosmo-live.sslcast.addradio.de/wdr/cosmo/live/mp3/128/stream.mp3",
            "http://st02.dlf.de/dlf/02/128/mp3/stream.mp3",
            "http://radioblau.hoerradar.de/radioblau",
            "http://live-mp3-128.kexp.org:80/kexp128.mp3"
            ]

        radio_urls = {}

        for url in range(0,len(radio_url_list)):
            radio_urls[url] = radio_url_list[url]

        # --- Web Radio Images -----------------------------------------------------------

        radio_images_list = [
            "images/1live.png",
            "images/cosmo.png",
            "images/dlfkultur.png",
            "images/radioblau.png",
            "images/kexp.png",
            ]

        radio_images = {}

        for im in range(0,len(radio_images_list)):
            radio_images[im] = ImageTk.PhotoImage(file=radio_images_list[im])

        # --- Web Radio Buttons -----------------------------------------------------------

        # FIXME: Replace redundant switch button with Checbutton-Class + indicatoron = 1 
        radio_dict = {}

        for r in range(0,len(radio_url_list)):
            radio_dict[r] = tk.Button(mlabel)
            radio_dict[r].configure(image=radio_images[r],relief="raised",bd=5,bg="white")
            radio_dict[r].image = radio_images[r]
        
        radio_dict[0].grid(row=0,column=0)
        radio_dict[1].grid(row=0,column=2)
        radio_dict[2].grid(row=1,column=0)
        radio_dict[3].grid(row=1,column=2)
        radio_dict[4].grid(row=0,column=1)

        # --- Create VLC web radio player -------------------------------------------------

        # class VLCwebRadio:

        #     def __init__(self):
        #         self.radio_list = radio_url_list
        #         self.Player = vlc.Instance('--loop')

        #     def addPlaylist(self):
        #         self.mediaList = self.Player.media_list_new()

        #         for music in self.radio_list:
        #             self.mediaList.add_media(self.Player.media_new(music))

        #         self.listPlayer = self.Player.media_list_player_new()
        #         self.listPlayer.set_media_list(self.mediaList)
            
        #     def playThis(self,idx):
        #         self.listPlayer.play_item_at_index(idx)audio/

        #     def stopPlaying(self):
        #         self.listPlayer.stop()

        # # Creating VLCwebRadio instance
        # radio = VLCwebRadio()
        # radio.addPlaylist()

        # # --- Callback function for dynamic button layout and calling web radio methods -

        # def callbackRadio(switch,radio_idx):

        #     def radioswitch():

        #         # If clicked and current button relief is raised: change to sunken relief
        #         if switch.config("relief") [-1] == "raised":
        #             switch.config(relief="sunken")

        #             # change all other buttons to opposite layout
        #             # FIXME: Only last clicked button must be changed (for-loop is redundant)
        #             for t in radio_dict.values():
        #                 if t != switch:
        #                     t.config(relief="raised")

        #             # play button corresponding web radio
        #             radio.playThis(radio_idx)
                
        #         # If clicked and current button relief is sunken: change to raised relief
        #         elif switch.config("relief") [-1] == "sunken":
        #             switch.config(relief="raised")

        #             # stop playing
        #             radio.stopPlaying()

        #     # bind callback function to switch button
        #     switch.configure(command=radioswitch)

        # # apply callbackRadio-function to all switch buttons
        # for r in range(0,len(radio_url_list)):
        #     radio_dict[r].configure(command=callbackRadio(radio_dict[r],r))

        # Back button
        button_0 = tk.Button(mlabel)
        button_0.grid(row=2,column=1,sticky="EW",ipady=10)
        button_0.configure(text="Zurück",font=BUTTON_FONT,bd=5)

        slider = tk.Scale(mlabel)
        slider.grid(row=2,column=2)
        slider.configure(orient="horizontal",relief="raised")

        # function: all buttons back to raised relief
        # FIXME: Only last clicked button must be changed (for-loop is redundant) 
        # FIXME: There's already a controller function that can handle this!
        def allRaise():
            for t in radio_dict.values():
                t.config(relief="raised")

        #########################################################################################
        ## PAGE 40: BUTTON COMMANDS #############################################################
        #########################################################################################

        # BACK-BUTTON
        # button_0.configure(command=lambda: controller.wrapper(radio.stopPlaying(),allRaise(),controller.showFrame(Page10)))
        button_0.configure(command=lambda: controller.wrapper(allRaise(),controller.showFrame(Page10)))

class Page50(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)

        # Page 50: To-Do-List-Page

        #########################################################################################
        ## PAGE 50: LAYOUT ######################################################################
        #########################################################################################
        
        # create 4 frames as containers
        frames = {}

        for f in range(0,4):
            frames[f] = tk.Frame(self)

        frames[0].grid(row=0,columnspan=2)  #contains top label
        frames[1].grid(row=1,column=0)      #contains text widget
        frames[2].grid(row=1,column=1)      #contains scrollbar
        frames[3].grid(row=2,columnspan=2)  #contains bottom label 

        # all 4 container frames shall expand
        for frame in frames:
            frames[frame].grid_configure(sticky="NSEW")
        
        # make all columns and rows expandable in frame 0,1,2,3
        for f in range(0,4):
            frames[f].grid_columnconfigure(0,weight=1)
            frames[f].grid_rowconfigure(0,weight=1)

        # LABELS
        # Top Label
        label_0 = tk.Label(frames[0])
        label_0.grid(sticky="NSWE",ipady=50)
        label_0.grid_rowconfigure(0,weight=1)
        label_0.grid_columnconfigure(0,weight=1)

        label_0.configure(image=controller.frames[Page10].layout_image_dict[0])
        label_0.image = controller.frames[Page10].layout_image_dict[0]

        # Bottom Label
        label_1 = tk.Label(frames[3])
        label_1.grid(sticky="NSEW")

        # Bottom Label: make all rows and columns stretchable
        label_1.grid_rowconfigure(0,weight=1)
        label_1.grid_columnconfigure(0,weight=1)

        # Put image on bottom label
        label_1.configure(image=controller.frames[Page10].layout_image_dict[0])
        label_1.image = controller.frames[Page10].layout_image_dict[0]

        # BUTTONS
        button_0 = tk.Button(label_1,text="Zurück",relief="raised",bd=5)
        button_0.grid_configure(row=0,column=0,sticky="NSEW",padx=250)
        button_0.configure(font=BUTTON_FONT)
            
        # TEXT-WIDGET
        self.text_0 = tk.Text(frames[1])
        self.text_0.grid(sticky="NSEW")
        self.text_0.configure(font=TEXT_WIDGET_FONT,cursor="heart")

        # SCROLLBAR
        self.scrollbar_0 = tk.Scrollbar(frames[2])
        self.scrollbar_0.grid(sticky="NSEW")
        self.scrollbar_0.configure(width=40)

        # connect scrollbar and text widget
        self.scrollbar_0.config(command=self.text_0.yview)
        self.text_0.config(yscrollcommand=self.scrollbar_0.set)

        #########################################################################################
        ## PAGE 50: BUTTON COMMANDS ###########################################################
        #########################################################################################

        # BACK-BUTTON
        # 1) Show Page10
        button_0.configure(command=lambda:controller.showFrame(Page10))

class Page60(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)

        # Page 60: Weather

        #########################################################################################
        ## PAGE 60: LAYOUT ######################################################################
        #########################################################################################
        
        # create 4 frames as containers
        frames = {}

        for f in range(0,4):
            frames[f] = tk.Frame(self)

        frames[0].grid(row=0,columnspan=2)  #contains top label
        frames[1].grid(row=1,column=0)      #contains text widget
        frames[2].grid(row=1,column=1)      #contains scrollbar
        frames[3].grid(row=2,columnspan=2)  #contains bottom label 

        # all 4 container frames shall expand
        for frame in frames:
            frames[frame].grid_configure(sticky="NSEW")
        
        # make all columns and rows expandable in frame 0,1,2,3
        for f in range(0,4):
            frames[f].grid_columnconfigure(0,weight=1)
            frames[f].grid_rowconfigure(0,weight=1)

        # LABELS
        # Top Label
        label_0 = tk.Label(frames[0])
        label_0.grid(sticky="NSWE",ipady=50)
        label_0.grid_rowconfigure(0,weight=1)
        label_0.grid_columnconfigure(0,weight=1)

        label_0.configure(image=controller.frames[Page10].layout_image_dict[0])
        label_0.image = controller.frames[Page10].layout_image_dict[0]

        # Bottom Label
        label_1 = tk.Label(frames[3])
        label_1.grid(sticky="NSEW")

        # Bottom Label: make all rows and columns stretchable
        label_1.grid_rowconfigure(0,weight=1)
        label_1.grid_columnconfigure(0,weight=1)

        # Put image on bottom label
        label_1.configure(image=controller.frames[Page10].layout_image_dict[0])
        label_1.image = controller.frames[Page10].layout_image_dict[0]

        # BUTTONS
        button_0 = tk.Button(label_1,text="Zurück",relief="raised",bd=5)
        button_0.grid_configure(row=0,column=0,sticky="NSEW",padx=250)
        button_0.configure(font=BUTTON_FONT)
            
        # TEXT-WIDGET
        self.text_0 = tk.Text(frames[1])
        self.text_0.grid(sticky="NSEW")
        self.text_0.configure(font=TEXT_WIDGET_FONT,cursor="heart")

        # SCROLLBAR
        self.scrollbar_0 = tk.Scrollbar(frames[2])
        self.scrollbar_0.grid(sticky="NSEW")
        self.scrollbar_0.configure(width=40)

        # connect scrollbar and text widget
        self.scrollbar_0.config(command=self.text_0.yview)
        self.text_0.config(yscrollcommand=self.scrollbar_0.set)

        #########################################################################################
        ## PAGE 60: BUTTON COMMANDS ###########################################################
        #########################################################################################

        # BACK-BUTTON
        # 1) Show Page10
        button_0.configure(
            command=lambda:
            controller.wrapper(
            controller.deleteTxtWidget(controller.frames[Page60].text_0),
            controller.showFrame(Page10)
                )
            )

app = Zwegat()

# Maximize Zwegat-App to fullscreen
# rp3: comment out this code line if you work on different screen size than 800x480 to get valid visual settings for rp3
# app.attributes("-fullscreen", True)

# Function: Allow esc-button to close main window
def close(event):
    app.destroy() # if you want to exit the entire thing

app.bind('<Escape>', close)

#######################################################################################################################################################
### Info ##############################################################################################################################################
#######################################################################################################################################################

def checkMyTk():

    app.frames[Page10].update()
        
    HYPHEN = "-" * 65

    def newLine():
        print("\n")
    def doubleNewLine():
        print("\n\n")
    def hyphenLine():
        print("{}\n\n".format(HYPHEN))

    print("tkinter info:")
    newLine()

    print("App - width:",app.winfo_screenwidth())
    print("App - height:",app.winfo_screenheight())
    print("Page10 - button_0 - width: ",app.frames[Page10].menu_button_dict[1].winfo_width())
    print("Page10 - button_0 - height: ",app.frames[Page10].menu_button_dict[1].winfo_height())
    print("Page10 - character button - width:",app.frames[Page10].roomie_button_dict[0].winfo_width())
    print("Page10 - character button - height:",app.frames[Page10].roomie_button_dict[0].winfo_height())
    print("Page20 - expense button - width:",app.frames[Page20].button_dict[0].winfo_width())
    print("Page20 - expense button - height:",app.frames[Page20].button_dict[0].winfo_height())
    print("Page20 - special expense button - width:",app.frames[Page20].button_dict[1].winfo_width())
    print("Page20 - special expense button - height:",app.frames[Page20].button_dict[1].winfo_height())
    newLine()
    hyphenLine()

checkMyTk()


# Run app
app.mainloop()

#######################################################################################################################################################
### Check #############################################################################################################################################
#######################################################################################################################################################

def checkMyProgram():
        
    HYPHEN = "-" * 65
    
    def newLine():
        print("\n")
    def doubleNewLine():
        print("\n\n")
    def hyphenLine():
        print("{}\n\n".format(HYPHEN))

    #Print number of single expenses
    print("Gesamtzahl getätigter Ausgaben:",Roomie.num_exp)
    newLine()

    # print liberal debt calculation
    print("Liberale Schuldenberechnung:")
    newLine()
    for roomie in roomie_list:
        idx = roomie_list.index(roomie)+1
        print('Roomie {}:'.format(idx),roomie.fname,'\t','Ausgaben:',roomie.exp,
            'Residuum:',roomie.res,'\t',roomie.exlist,roomie.info,roomie.date)
    print('\nTotal:',Roomie.total_exp,'\nMean:',Roomie.mean_exp,'\n')

    # Print liberal debt plan
    print("Liberaler Schuldenplan:")
    newLine()
    debts = normalizeDebts(valueSortedDict(liberalDebtsDict()))
    for (creditor,debtor,amount) in debts:
        print(roomie_list[creditor].fname,'schuldet',roomie_list[debtor].fname,'{} €'.format(amount))

    # print conservative debt calculation
    print("Konservative Schuldenberechnung:")
    newLine()
    for roomie in roomie_list:
        idx = roomie_list.index(roomie)+1
        print('Roomie {}:'.format(idx),roomie.fname,'\t',"Ausgabenliste:",roomie.evlist,"Anwesenheitsliste:",roomie.preslist)
    print('\nTotal:',Roomie.total_exp,'\nMean:',Roomie.mean_exp,'\n')

    # print conservative debt plan
    print("Konservativer Schuldenplan:")
    newLine()
    adjusted_debts = normalizeDebts(valueSortedDict(conservativeDebtsDict()))
    for (creditor,debtor,amount) in adjusted_debts:
        print(roomie_list[creditor].fname,'schuldet',roomie_list[debtor].fname,'{} €'.format(amount))
    hyphenLine()
    
    print("Sonderausgaben:")
    newLine()
    for roomie in roomie_list:
        idx = roomie_list.index(roomie)+1
        print('Roomie {}:'.format(idx),roomie.fname,"Ausgabenliste:",roomie.spcl_evlist,"Teilnahmeliste:",roomie.partlist,"Infoliste:",roomie.spcl_info,"Datumsliste:",roomie.spcl_date)
    newLine()

    print("Sonderausgaben Schuldenplan:")
    newLine()
    special_expenses = normalizeDebts(valueSortedDict(specialExpenseDebtsDict()))
    for (creditor,debtor,amount) in special_expenses:
        print(roomie_list[creditor].fname,'schuldet',roomie_list[debtor].fname,'{} €'.format(amount))
    hyphenLine()

    print("Sonderausgaben - Schulden:",special_expenses)
    print("Normale Schulden:",adjusted_debts)

    os = sys.platform
    print("Current OS:",os)

    newLine()
    hyphenLine()

checkMyProgram()

######################################################################################################################################################
### Projects ###########################################################################################################################################
#########################################################################################################################################################

# 1) Is there a better, more pythonic, more "clean" way to initialize instance attributes in Roomie class? Maybe exp,res & co. should be set first to None?

# 2) Implement function to create a new roomie / delete roomie

# 5) Implement history-function:
# Use pickle-module?
# User should be able to see past debt plans. See already written but currently unused function below:
# Function: saveDebts
# Save current debts plan in dictionary with key = "year_month" and value = roomie_list
# def saveDebts():
#     timestamp = datetime.date.today().strftime('%Y_%m_%d')
#     Output.history = {timestamp:roomie_list}

# 6) Automatically resize all images to the size of their parents (for example: background image to size of it's parent label,
# or button image to the size of it's button parent) -> I wrote a Label-Subclass which you can pass a picture path to and then
# a resizing method is called on that picture. Unfortunately layout crashes when you want to put widgets on different rows
# and columns on that label --> Ask me for the Subclass Code! 
# This would be very useful cause then you wouldn't have set the size of pictures manually. You could just take any picture and
# it would automatically resize to the size of it's parent. This would also give you the opportunity to easily set up "themes"
# and change the whole look of the Zwegat Alpha by just chosing new pictures from the web.

# 7) # Implement radio volume slider

# 8) Implement GPIO-LED module
# If roomie is present, turn on green led, if absent red led

#######################################################################################################################################################
### STUFF I DIDNT UNDERSTAND BUT HAD TO DEAL WITH #####################################################################################################
#######################################################################################################################################################

# 1)
# lambda b:b .... Bei der dynamischen Erstellung von Button Commands. Musste ich machen, da sonst Parameter nicht iterierten. Funktion gibt also ohne
# diese Änderung immer den gleichen Wert aus (but why??)

# 3)
# Wrapper Function (get arbitrary number of functions (with arbitrary number of arguments) and call them)
    #def wrapper(self,*funcs):
       # def combined_func(self,*args,**kwargs):
            #for f in funcs:
             #   f(self,*args, **kwargs)
       # return combined_func

# Ich musste auch bei combined_func und f(..) "self" davor schreiben, sonst hat es nicht funktioniert.

# 4) Siehe Page20 --> Validate function von Stackoverflow geklaut --> KEINE Ahung, was 
# bei vcmd = .... passiert (vor allem, was die Tk.register() Method macht
# Auch self und die Vererbung damit hat mich komplett verwirrt (muss die Funktion überhaupt dort oben stehen?)

# def onValidate(self, d, i, P, s, S, v, V, W):
#     # Disallow anything but lowercase letters
#         if S == S.lower():
#             return True
#         else:
#             self.bell()
#             return False

# # Create entry fields, use validate command to only allow numbers 
#         vcmd = (controller.register(controller.onValidate),
#         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

#         entry = tk.Entry(frames[1], validate="key", validatecommand=vcmd)
#         entry.grid(row=0,column=1,sticky="W",ipady=10)

# User Input and Output Variables were put in a class for later use as global variables
# Any other way for writing good code without using classes or global keyword?

