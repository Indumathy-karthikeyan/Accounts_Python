# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import ttk
from datetime import datetime as dt

import config


import Customer as Cus
import Product as Prod
import Narration as Narr
import Gst as Gst

import Entries as Ent
import Transaction as Trans

import DayBook as Db
import Ledger as Lg
import Stock as St
import Register as Reg
import TrialBalance as Trial
import subprocess
from tkinter import messagebox
import Demo as dd
import mysql.connector as con

config.Root = tk.Tk()
config.Root.geometry("2000x1000")
config.Root.title('Sri Narayana Trading company')

# calculating the current accounting year
today = str(dt.today())
year = today[:4]
print(year)
month = today[5:7]
#month = "3"
print(month)
if int(month) > 3:
    config.Year = year + "-" + str(int(year)+1)
else:
    config.Year = str(int(year)-1) + "-" + year

#config.Year = "2022-2023"
config.Company_Name = "Sri Narayana Trading Company"
config.Db_Name = "Accounts"
config.Pwd = "Vijayam1952"

print(config.Year)

Accmenu = tk.Menu(config.Root)
config.Root.config(menu=Accmenu)
Details_menu = tk.Menu(Accmenu)
Accmenu.add_cascade(label="Details    ", menu=Details_menu)
Details_menu.add_command(command=lambda: show_cus(), label="Customer")
Details_menu.add_command(command=lambda: show_prod(), label="Product")
Details_menu.add_command(command=lambda: show_narr(), label="Narration")
Details_menu.add_command(command=lambda: show_gst(), label="Gst")

Entries_menu = tk.Menu(Accmenu)
Accmenu.add_cascade(label="Entries     ", menu=Entries_menu)
Entries_menu.add_command(command=lambda: show_entries("Cash"), label="Cash")
Entries_menu.add_command(command=lambda: show_entries("Journal"), label="Journal")

Billing_menu = tk.Menu(Accmenu)
Accmenu.add_cascade(label="Billing   ", menu=Billing_menu)
Billing_menu.add_command(command=lambda: show_bill("Computer Cash Bill"), label="Computer Cash Bill")
Billing_menu.add_command(command=lambda: show_bill("Manual Cash Bill"), label="Manual Cash Bill")
Billing_menu.add_command(command=lambda: show_bill("Computer Credit Bill"), label="Computer Credit Bill")
Billing_menu.add_command(command=lambda: show_bill("Manual Credit Bill"), label="Manual Credit Bill")

View_menu = tk.Menu(Accmenu)
Accmenu.add_cascade(label="View  ", menu=View_menu)
View_menu.add_command(command=lambda: show_reg("Sales"), label="Sales Register")
#View_menu.add_command(command=lambda: show_reg("Purchase"), label="Purchase Register")
View_menu.add_command(command=lambda: show_stock(), label="Stock")
View_menu.add_command(command=lambda: show_daybook(), label="Day Book")
View_menu.add_command(command=lambda: show_ledger(), label="Ledger")

Trial_menu = tk.Menu(Accmenu)
View_menu.add_cascade(label="TrialBalance", menu=Trial_menu)
Trial_menu.add_command(command=lambda: show_trialbalance("A&L"), label="Assets and Liabilities")
Trial_menu.add_command(command=lambda: show_trialbalance("Nominal"), label="Nominal Accounts")

exit_menu = tk.Menu(Accmenu)
Accmenu.add_cascade(label="Exit", command=lambda: exit())

my_tab = ttk.Notebook(config.Root)
my_tab.place(x=10, y=10)


def exit():
    if tk.messagebox.askokcancel(config.Company_Name,"Take Backup"):
        bat_file_path = "C:\\Users\\vpvij\\Documents\\workspace\\accounts\\mysql_backup.bat"
        # Run the .bat file
        subprocess.call(bat_file_path)
    config.Root.destroy()

def show_cus():
    # creating frames for the Customer tab
    cus_tab = ttk.Frame(my_tab, width=1500, height=900)
    my_tab.add(cus_tab, text="Customer Detials      ")
    #my_tab.focus_force()
    my_tab.focus_set()
    cus = Cus.Customer()
    cus.preparing_window(cus_tab)
    my_tab.select(cus_tab)


def show_prod():
    # creating frames for the Product tab
    prod_tab = ttk.Frame(my_tab, width=1500, height=900)
    my_tab.add(prod_tab, text="Product Details      ")
    my_tab.focus_set()
    prod = Prod.Product()
    prod.preparing_window(prod_tab)
    my_tab.select(prod_tab)


def show_narr():
    # creating frames for the Narration tab
    narr_tab = ttk.Frame(my_tab, width=1500, height=900)
    my_tab.add(narr_tab, text="Narration Detials      ")
    narr = Narr.Narration()
    narr.preparing_window(narr_tab)
    my_tab.select(narr_tab)


def show_gst():
    # creating frames for the Gst tab
    gst_tab = ttk.Frame(my_tab, width=1500, height=900)
    my_tab.add(gst_tab, text="Gst Detials      ")
    gst = Gst.Gst()
    gst.preparing_window(gst_tab)
    my_tab.select(gst_tab)


def show_entries(type):
    # creating frames for the Entries tab
    ent_tab = ttk.Frame(my_tab, width=1500, height=900)
    s = type + "    "
    my_tab.add(ent_tab, text=s)
    ent = Ent.Entries()
    ent.preparing_window(ent_tab, type)
    my_tab.select(ent_tab)


def show_bill(bill_type):
    # creating frames for the Entries tab
    bill_tab = ttk.Frame(my_tab, width=1500, height=900)
    my_tab.add(bill_tab, text=bill_type)
    #entryno=163
    # opens the connection to fetch the  percentage of tax from the Gst table
    #myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
    #cur = myconn.cursor()

    #for i in range(30,164):
    #    s = "update transaction set entryno=" + str(entryno) +  " where billno='MCH" + str(i) + "'"
    #    cur.execute(s)
    #    myconn.commit()
    #    entryno+=1
    bill = Trans.Transaction()
    bill.preparing_window(bill_tab, bill_type)
    my_tab.select(bill_tab)


def show_reg(type):
    # creating frames for the Entries tab
    reg_tab = ttk.Frame(my_tab, width=1600, height=900)
    s = type + "Register"
    my_tab.add(reg_tab, text=s)
    reg = Reg.Register()
    reg.preparing_window(reg_tab, type)
    my_tab.select(reg_tab)

def show_stock():
    # creating frames for the Entries tab
    st_tab = ttk.Frame(my_tab, width=1500, height=800)
    my_tab.add(st_tab, text="Stock")
    st = St.Stock()
    st.preparing_window(st_tab)
    my_tab.select(st_tab)

def show_daybook():
    # creating frames for the Entries tab
    db_tab = ttk.Frame(my_tab, width=1500, height=800)
    my_tab.add(db_tab, text="Day Book")
    db = Db.DayBook()
    db.preparing_window(db_tab)
    my_tab.select(db_tab)

def show_ledger():
    # creating frames for the Entries tab
    lg_tab = ttk.Frame(my_tab, width=1500, height=800)
    my_tab.add(lg_tab, text="Day Book")
    lg = Lg.Ledger()
    lg.preparing_window(lg_tab)
    my_tab.select(lg_tab)

def show_trialbalance(type):
    # creating frames for the Customer tab
    trial_tab = ttk.Frame(my_tab, width=1500, height=800)
    if type == "A&L":
        my_tab.add(trial_tab, text="Assets and Liabilities")
    elif type == "Nominal":
        my_tab.add(trial_tab, text="Nominal Accounts")
    trial = Trial.TrialBalance()
    trial.preparing_window(trial_tab, type)
    my_tab.select(trial_tab)


config.Root.mainloop()
