import tkinter as tk
from tkinter import messagebox
import datetime
import mysql.connector as con

from fpdf.fpdf import FPDF

#import config

# from datetime import datetime as dt

Year = ""
Root = None
Company_Name = ""
Db_Name = ""
Pwd = ""


def check_date(year, month, day):
    # correct_date = None
    try:
        newdate = datetime.datetime(year, month, day)
        correct_date = True
    except ValueError:
        print("Error")
        correct_date = False
    return correct_date


def validate_dt(st):
    lst = st.split("-")
    print(lst)
    flag = False
    if len(lst) == 3:
        print("checking date")
        if check_date(int(lst[2]), int(lst[1]), int(lst[0])):
            yr = Year.split("-")
            if lst[2] == yr[0]:
                if int(lst[1]) >= 4:
                    flag = True
            elif lst[2] == yr[1]:
                if int(lst[1]) <= 3:
                    flag = True

    return flag

def enter_date(s):
    print()
    i = len(s) -1
    if i != -1:
        if (not '0' <= s[i] <= '9') and (not s[i] == "-"):
            tk.messagebox.showinfo(Company_Name, "only numbers")
            s = s[:i]
            print(s)
        else:
            if i != 2 and i != 5:
                n = int(s[i])
                print(n)
                if i == 0:
                    if n > 3:
                        s = "0" + s + "-"
                elif i == 1:
                    no = int(s[i-1])
                    if no == 3:
                        if n != 0 and n != 1:
                            tk.messagebox.showinfo(Company_Name, "Invalid number")
                            s = s[:1]
                        else:
                            s = s + "-"
                    else:
                        s = s + "-"
                elif i == 3:
                    if n != 1:
                        s = s[:i] + "0" + str(n)
                        if n > 3:
                            yr = Year[:4]
                            print(yr)
                            s = s + "-" + yr
                        else:
                            yr = Year[-4:]
                            s = s + "-" + yr
    return s

def validate_date(lst):
    # list contains sday,smonth,syear,eday,emonth,eyear
    flag = False
    finlst = []
    if lst[0] == "":
        tk.messagebox.showinfo("", "Enter start day")
    elif lst[1] == 0:
        tk.messagebox.showinfo("", "Enter start month")
    elif lst[2] == "":
        tk.messagebox.showinfo("", "Enter start year")
    else:
        if not check_date(int(lst[2]), lst[1], int(lst[0])):
            tk.messagebox.showinfo("", "Invalid start date")
        else:
            if lst[3] != "" and lst[4] != 0 and lst[5] != "":
                if not check_date(int(lst[5]), lst[4], int(lst[3])):
                    tk.messagebox.showinfo("", "Invalid end date")
                else:
                    dt = lst[0] + "-" + str(lst[1]) + "-" + lst[2]
                    stdate = datetime.datetime.strptime(dt, "%d-%m-%Y")
                    dt = lst[3] + "-" + str(lst[4]) + "-" + lst[5]
                    enddate = datetime.datetime.strptime(dt, "%d-%m-%Y")
                    print(stdate, "  ", enddate)
                    if enddate < stdate:
                        tk.messagebox.showinfo("", "Invalid end date")
                    elif enddate >= stdate:
                        finlst = [stdate, enddate]
                        flag = True
            elif lst[3] == "" and lst[4] == 0 and lst[5] == "":
                dt = lst[0] + "-" + str(lst[1]) + "-" + lst[2]
                print(dt)
                stdate = datetime.datetime.strptime(dt, "%d-%m-%Y")
                print(stdate)
                finlst = [stdate, ""]
                flag = True
            elif lst[3] == "":
                tk.messagebox.showinfo("", "Enter End day")
            elif lst[4] == 0:
                tk.messagebox.showinfo("", "Enter End month")
            elif lst[5] == "":
                tk.messagebox.showinfo("", "Enter End Year")

    return finlst


def check_records(tname, fname, value):
    # opens the connection and fetches the records from Customer table
    myconn = con.connect(user='root', password=Pwd, host='127.0.0.1', database=Db_Name)
    cur = myconn.cursor()

    s = "Select * from " + tname + " where " + fname + " = '" + value + "' and Year = '" + Year + "'"
    cur.execute(s)
    res = cur.fetchall()
    if len(res) > 0:
        flag = True
    else:
        flag = False

    return flag


def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


class BillPDF(FPDF):
    def header(self):
        # adding gstno and landline number in line 1
        strtmp = "GSTIN : 33AABPV6902D1ZZ"
        content = ('{:<75}'.format(strtmp))
        content = content + "Cell: 9444167258"
        self.set_font("helvetica", size=10)
        self.cell(0, 5, txt=content, ln=1, align="L")

        # adding CASH BILL and cellno in line2
        strtmp = "FSSAI No.12420030000486"
        content = ('{:<85}'.format(strtmp))
        content = content + "9487747293"
        # self.set_font("helvetica", size=10)
        self.cell(0, 5, txt=content, ln=1, align="L")


        # addding Company Name as center text in line3
        self.set_font("helvetica", size=14, style="B")
        # self.cell(0, 8, txt="  ", ln=1, align="C")
        self.cell(0, 8, txt="Sri Narayana Trading Company", ln=1, align='C')
        # addding Company address as center text in line4
        self.set_font("helvetica", size=8)
        self.cell(0, 5, txt="No.120, Mundy Street VELLORE - 632004", ln=1, align="C")


class BillPDFWithFooter(BillPDF):

    def footer(self):
        # addding Bank details as footer
        self.set_font("helvetica", size=10)
        self.cell(0, 8, txt="  ", ln=1, align="L")
        self.cell(0, 8, txt="Bank Details", ln=1, align='C')
        # addding Company address as center text in line4
        content = ('{:<83}'.format("Canara Bank"))
        #content += "Syndicate Bank"
        self.cell(0, 5, txt=content, ln=1, align="L")

        content = ('{:<75}'.format("A/C No. 120000019400"))
        #content += "A/C No. 120000019400"
        self.cell(0, 5, txt=content, ln=1, align="L")

        content = ('{:<70}'.format("IFSC Code: CNRB0016250"))
        #content += "IFSC Code: CNRB0016250"
        self.cell(0, 5, txt=content, ln=1, align="L")


class MyPDF(FPDF):
    def header(self):
        # addding Company Name as center text in line1
        self.set_font("helvetica", size=26, style="B")
        self.cell(0, 8, txt="Sri Narayana Trading Company", ln=1, align='C')

        self.set_font("helvetica", size=16)
        content = "Accounting year " + Year
        self.cell(0, 8, txt=content, ln=1, align="C")
        self.cell(0, 8, txt="", ln=1, align='C')
