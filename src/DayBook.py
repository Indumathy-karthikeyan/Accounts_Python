import config
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import timedelta
from datetime import datetime as dt
import mysql.connector as con
import win32api
from fpdf.fpdf import FPDF


class DayBook:

    def __init__(self):

        self.tree = self.top = self.tab = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None
        self.seldate_bt = self.print_bt = None
        self.stdate_ent = self.enddate_ent = self.date_ent = None

        self.jndb = self.jncr = self.cashcr = self.cashdb = self.baltype = None
        self.transflag = self.dateflag = None

        self.currow = self.totrow = self.curdate = self.diffdate = self.enddate = self.stdate = None

        self.sdate = tk.StringVar()
        self.edate = tk.StringVar()
        self.strdate = tk.StringVar()

    def my_window(self, _event=None):
        self.top = tk.Toplevel(config.Root)
        self.top.geometry("400x200")
        x = config.Root.winfo_x()
        y = config.Root.winfo_y()
        self.top.geometry("+%d+%d" % (x + 500, y + 250))
        self.top.wm_transient(config.Root)
        self.top.grab_set()

        # adding Start date
        self.sdate.set("")
        self.edate.set("")
        tk.Label(self.top, text="Start Date :", width=8, bd=4).place(x=60, y=30)
        self.stdate_ent = tk.Entry(self.top, width=25, textvariable=self.sdate)
        self.stdate_ent.place(x=150, y=30)
        self.stdate_ent.bind("<KeyRelease>", self.enter_stdate)
        # adding End date
        tk.Label(self.top, text="End Date :", width=8, bd=4).place(x=60, y=80)
        self.enddate_ent = tk.Entry(self.top, width=25, textvariable=self.edate)
        self.enddate_ent.place(x=150, y=80)
        self.enddate_ent.bind("<KeyRelease>", self.enter_enddate)

        # creating ok button
        ok_bt = tk.Button(self.top, text="Ok", underline=0, width=10, command=lambda: self.ok())
        ok_bt.place(x=100, y=140)
        self.top.bind("<Alt-o>", self.ok)

        # creating Cancel button
        cancel_bt = tk.Button(self.top, text="Cancel", underline=0, width=10, command=lambda: self.cancel())
        cancel_bt.place(x=210, y=140)
        self.top.bind("<Alt-c>", self.cancel)

        self.stdate_ent.focus_set()

    def enter_stdate(self, e):
        if e.keysym != "BackSpace" and e.keysym != "Left" and e.keysym != "Right" and e.keysym != "Delete":
            self.sdate.set(config.enter_date(self.sdate.get()))
            self.stdate_ent.icursor(tk.END)

    def enter_enddate(self, e):
        if e.keysym != "BackSpace" and e.keysym != "Left" and e.keysym != "Right" and e.keysym != "Delete":
            self.edate.set(config.enter_date(self.edate.get()))
            self.enddate_ent.icursor(tk.END)

    def ok(self, _event=None):
        # validating start date entered
        if self.sdate.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Enter the starting date")
            self.stdate_ent.focus_set()
        else:
            if not config.validate_dt(self.sdate.get()):
                tk.messagebox.showinfo(config.Company_Name, "Invalid start date")
                self.stdate_ent.focus_set()
            else:
                # if valid start date
                # displaying date in the date text box
                # converting start date to "yy-mm-dd" format for doing query in the database
                self.strdate.set(dt.strftime(dt.strptime(self.sdate.get(), "%d-%m-%Y"), "%d-%m-%Y"))
                self.sdate.set(dt.strftime(dt.strptime(self.sdate.get(), "%d-%m-%Y"), "%Y-%m-%d"))
                self.stdate = dt.strptime(self.sdate.get(), "%Y-%m-%d").date()
                # setting current date to the start date entered
                self.curdate = self.stdate

                # validating end date entered
                if self.edate.get() != "":
                    if not config.validate_dt(self.edate.get()):
                        tk.messagebox.showinfo(config.Company_Name, "Invalid end date")
                        self.enddate_ent.focus_set()
                    else:
                        # if valid end date
                        # converting end date to "yy-mm-dd" format for doing query in the database
                        self.edate.set(dt.strftime(dt.strptime(self.edate.get(), "%d-%m-%Y"), "%Y-%m-%d"))
                        self.enddate = dt.strptime(self.edate.get(), "%Y-%m-%d").date()
                        if self.stdate == self.enddate:
                            # if both startdate and enddate are same setting diffdate to false
                            # inorder to disable navigation
                            self.diffdate = False
                            self.dateflag = ""
                        else:
                            # if both startdate and enddate are same setting diffdate to true
                            # inorder to enable navigation
                            self.diffdate = True
                            self.dateflag = "First"
                else:
                    # if only start date has been entered
                    # setting diffdate to false inorder to disable navigation
                    self.diffdate = False
                    self.dateflag = ""

                # closing the date window
                self.top.destroy()
                # setting navigation buttons according to the dates
                self.set_navi()
                # displaying daybook for the current date
                if self.tree:
                    self.clear_table()
                self.display_daybook()
                self.print_bt.configure(state="normal")
                self.transflag = False

    def cancel(self, _event=None):
        if self.strdate.get() == "":
            # in case of cancelling without any date
            # disabling navigation buttons and print button
            self.first_bt.configure(state="disabled")
            self.prev_bt.configure(state="disabled")
            self.next_bt.configure(state="disabled")
            self.last_bt.configure(state="disabled")
            self.print_bt.configure(state="disabled")
        self.top.destroy()

    def close(self, _event=None):
        self.tab.destroy()

    def set_navi(self):
        # setting navigation buttons acording to the dates
        if not self.diffdate:
            # if only start date is entered
            self.first_bt.configure(state="disabled")
            self.prev_bt.configure(state="disabled")
            self.next_bt.configure(state="disabled")
            self.last_bt.configure(state="disabled")
        else:
            if self.curdate == self.stdate:
                # if curdate is same as start date
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.curdate == self.enddate:
                # if curdate is same as end date
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                # if curdate is between start and end date
                # enable all navigation buttons
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def move_first(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "Last"):
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the end date
            self.dateflag = "First"
            # setting current date to the start date
            self.curdate = self.stdate
            self.sdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            self.strdate.set(dt.strftime(self.curdate, "%d-%m-%Y"))
            self.set_navi()
            # clearing the table and displaying daybook for the current date(start date)
            self.clear_table()
            self.display_daybook()

    def move_prev(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "Last"):
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the end date
            # setting current date to the previous date
            self.curdate = self.curdate - timedelta(days=1)
            if self.stdate == self.curdate:
                self.dateflag = "First"
            else:
                self.dateflag = "Middle"
            self.sdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            self.strdate.set(dt.strftime(self.curdate, "%d-%m-%Y"))
            self.set_navi()
            # clearing the table and displaying daybook for the current date(date before)
            self.clear_table()
            self.display_daybook()

    def move_next(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "First"):
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the start date
            # setting current date to the next date
            self.curdate = self.curdate + timedelta(days=1)
            if self.enddate == self.curdate:
                self.dateflag = "Last"
            else:
                self.dateflag = "Middle"
            self.sdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            self.strdate.set(dt.strftime(self.curdate, "%d-%m-%Y"))
            self.set_navi()
            # clearing the table and displaying daybook for the current date(date after)
            self.clear_table()
            self.display_daybook()

    def move_last(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "First"):
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the start date
            # setting current date to the last date
            self.curdate = self.enddate
            self.dateflag = "Last"
            self.sdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            self.strdate.set(dt.strftime(self.curdate, "%d-%m-%Y"))
            self.set_navi()
            # clearing the table and displaying daybook for the current date(end date)
            self.clear_table()
            self.display_daybook()

    def clear_table(self):
        # clears daybook table
        for row in self.tree.get_children():
            self.tree.delete(row)

    def display_daybook(self):
        self.baltype = ""
        self.cashdb = 0
        self.cashcr = 0
        self.jndb = 0
        self.jncr = 0

        self.transflag = False
        # to get the opening balance for that day
        self.get_prevbalance()
        # to display journal entries from entries table for that day
        self.display_entries("Credit")
        # to display credit sales for that day
        self.display_transaction("Credit")

        # to display cash and journal entries from entries table for that day
        self.display_entries("Cash")
        # to display cash sales for that day
        self.display_transaction("Cash")

        # to display the total credit and debit and balance for that day
        self.display_total()

        if not self.transflag:
            # if no transaction has been made on that day
            tk.messagebox.showinfo(config.Company_Name, "No Transaction for that day")

    def get_prevbalance(self):
        # calculating openning balance for the current date
        db = 0
        cr = 0

        # opens the connection to fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        # getting sales transaction upto previous date to calculate openning balance
        # getting all Manual and Computer Cash Transaction from Transaction table
        s = "select Code, Type, Amount from Transaction where Date <'" + str(self.curdate) \
            + "' and (BillNo like 'CCH%' or BillNo like 'MCH%') and type = 'D' and year = '" + config.Year \
            + "' and cancelled = 'N' order by BillNo"

        cur.execute(s)
        res = cur.fetchall()
        if len(res) > 0:
            # calculating sum of cash Sales amount
            for r in res:
                cr += float(r[2])

        # getting transaction from entries upto previous date to calculate openning balance
        # s = "select Code, Type, Amount from Entries where Date <'" + str(self.curdate) + "' and TransType = 'C'"\
        #    + " and year = '" + config.Year + "'"
        s = "select Code, Type, Amount from Entries where Date <'" + str(self.curdate)\
            + "' and transtype = 'C' and year = '" + config.Year + "'"
        cur.execute(s)
        res = cur.fetchall()

        if len(res) > 0:
            for r in res:
                # adding all credit and debit transaction seperately
                if r[1] == "C":
                    cr += float(r[2])
                else:
                    db += float(r[2])

        bal = 0
        # checking which is more credit or debit amount
        if cr > db:
            # in case if credit is more calculate balance set type to credit
            bal = cr - db
            self.baltype = "C"
            self.cashcr = bal
        elif db > cr:
            # in case if debit is more calculate balance set type to debit
            bal = db - cr
            self.baltype = "D"
            self.cashdb = bal
        else:
            # in case both are equal nill balance
            bal = db - cr
            self.baltype = ""

        self.currow = 0
        # displaying opening balance
        amt = "{:.2f}".format(bal)
        if self.baltype == "":
            self.tree.insert("", index=self.currow, values=["", "Opening Balance of the day (Nill)"])
        elif self.baltype == "D":
            self.tree.insert("", index=self.currow, values=["", "Opening Balance of the day", "", "", "", str(amt), ""])
        elif self.baltype == "C":
            self.tree.insert("", index=self.currow, values=["", "Opening Balance of the day", "", "", "", "", str(amt)])

    def display_transaction(self, type):

        # opens the connection and fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        s = ""
        # displaying customer details for credit transactions
        if type == "Credit":
            s = "select t.code, c.description, t.narration, t.type, t.amount from Transaction as t, customer as c " \
                + " where t.code not like 'E%' and t.code= c.code and (t.BillNo like 'CCR%' or t.BillNo like 'MCR%') "\
                + " and t.date='" + str(self.curdate) + "' and t.type = 'D' and t.year='" + config.Year \
                + "' and cancelled='N' order by Billno"

            cur.execute(s)
            res = cur.fetchall()
            for r in res:
                lst = [r[1], r[2], "", r[4]]
                self.display(lst, type, r[3])

        # displaying product transactions
        content = ""
        billno = ""

        for i in range(0, 2):
            if type == "Credit" and i == 0:
                # displaying product details for credit transactions
                billno = "MCR%"
                content = "Manual Credit Sales"
            elif type == "Credit" and i == 1:
                billno = "CCR%"
                content = "Computer Credit Sales"
            elif type == "Cash" and i == 0:
                billno = "MCH%"
                content = "Manual Cash Sales"
            elif type == "Cash" and i == 1:
                billno = "CCH%"
                content = "Computer Cash Sales"
            transtype = "C"
            s = "select t.code, p.description, t.narration, t.type, t.quantity,t.wt, t.amount from Transaction " \
                + " as t," + "product as p where t.code= p.code and (t.billno like '" + billno + "') " \
                + " and t.code like 'I%' and t.date='" + str(self.curdate) + "' and t.year='" + config.Year \
                + "' and cancelled = 'N' order by t. code, Billno"
            cur.execute(s)
            res = cur.fetchall()
            if len(res) != 0:
                self.transflag = True
                qty = 0
                wt = 0
                amt = 0
                for r in res:
                    # calculating total amount and quatity of all product transacted on that date
                    if not r[4]:
                        wt += r[5]
                    else:
                        qty += r[4]
                    amt += r[6]

                lst = [content, "", qty+wt, amt]
                self.display(lst, type, transtype)

        # displaying tax details
        tax = ["LIST", "LCST", "LSST"]
        for i in range(0, 3):
            if type == "Credit":
                s = "select t.code, c.description, t.narration, t.type, t.amount from Transaction"\
                    + " as t, Customer as c where t.code= c.code and (t.billno like 'CCR%' or t.billno like 'MCR%')"\
                    + " and t.code ='" + tax[i] + "' and t.date='" + str(self.curdate) + "' and t.year='" \
                    + config.Year + "' and cancelled = 'N' order by t.type, Billno"

            elif type == "Cash":
                s = "select t.code, c.description, t.narration, t.type, t.amount from Transaction" \
                    + " as t, Customer as c where t.code= c.code and (t.billno like 'CCH%' or t.billno like 'MCH%')" \
                    + " and t.code ='" + tax[i] + "' and t.date='" + str(self.curdate) + "' and t.year='" \
                    + config.Year + "' and cancelled = 'N' order by t.type, Billno"

            cur.execute(s)
            res = cur.fetchall()
            if len(res) != 0:
                amt = 0
                self.transflag = True
                for r in res:
                    amt += r[4]

                lst = [res[0][1], "", "", amt]
                self.display(lst, type, "C")

        # displaying EGEn
        if type == "Credit":
            s = "select t.code, c.description, t.narration, t.type, t.amount from Transaction"\
                + " as t, customer as c where t.code= c.code and (t.billno like 'CCR%' or t.billno like 'MCR%')"\
                + " and t.code ='EBRO' and t.date='" + str(self.curdate) + "' and t.year='" \
                + config.Year + "' and cancelled = 'N' order by t. code, Billno"
        elif type == "Cash":
            s = "select t.code, c.description, t.narration, t.type, t.amount from Transaction" \
                + " as t,  customer as c where t.code= c.code and (t.billno like 'CCH%' or t.billno like 'MCH%')" \
                + " and t.code ='EBRO' and t.date='" + str(self.curdate) + "' and t.year='" \
                + config.Year + "' and cancelled = 'N' order by t. code, Billno"

        cur.execute(s)
        res = cur.fetchall()

        if len(res) != 0:
            amt = 0
            for r in res:
                amt += r[4]
            lst = [res[0][1], "", "", amt]
            self.display(lst, type, "C")

    def display_entries(self, type):
        # opens the connection and fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        if type == "Cash":
            ttype = "C"
        if type == "Credit":
            ttype = "J"

        s = "select code, narration, type, amount, entryno from entries  " \
            + " where date='" + str(self.curdate) + "' and year='" \
            + config.Year + "' and transtype = '" + ttype + "' order by entryno"
        cur.execute(s)
        res = cur.fetchall()

        for r in res:
            if r[0][0] == "A" or r[0][0] == "L":
                s = "select description from customer where code='" + r[0] + "'"
            elif r[0][0] == "F" or r[0][0] == "P":
                s = "select description from product where code='" + r[0] + "'"
            cur.execute(s)
            des = cur.fetchall()
            if len(des) != 0:
                desc = des[0][0]
            else:
                desc = ""
            lst = [desc, r[1], "", r[3]]
            self.display(lst, type, r[2])

    def display(self, lst, type, transtype):
        self.currow += 1
        a = "{:.2f}".format(lst[3])
        if type == "Credit":
            if transtype == "D":
                self.tree.insert("", index=self.currow, iid=self.currow, values=(lst[0], lst[1], lst[2], a, "", "", ""))
                self.jndb += float(lst[3])
            elif transtype == "C":
                self.tree.insert("", index=self.currow, iid=self.currow, values=(lst[0], lst[1], lst[2], "", a, "", ""))
                self.jncr += float(lst[3])
        elif type == "Cash":
            if transtype == "D":
                self.tree.insert("", index=self.currow, iid=self.currow, values=(lst[0], lst[1], lst[2], "", "", a, ""))
                self.cashdb += float(lst[3])
            elif transtype == "C":
                self.tree.insert("", index=self.currow, iid=self.currow, values=(lst[0], lst[1], lst[2], "", "", "", a))
                self.cashcr += float(lst[3])

    def display_total(self):
        self.currow += 1
        jndb = "{:.2f}".format(self.jndb)
        jncr = "{:.2f}".format(self.jncr)
        cashdb = "{:.2f}".format(self.cashdb)
        cashcr = "{:.2f}".format(self.cashcr)
        self.tree.insert("", index=self.currow, iid=self.currow, values=("", "Total", "", jndb, jncr, cashdb, cashcr))
        self.currow += 1
        if self.cashdb > self.cashcr:
            diff = self.cashdb - self.cashcr
            d = "{:.2f}".format(diff)
            self.tree.insert("", index=self.currow, iid=self.currow,
                             values=("", "Balance for the day", "", "", "", d, ""))
        elif self.cashcr > self.cashdb:
            diff = self.cashcr - self.cashdb
            d = "{:.2f}".format(diff)
            self.tree.insert("", index=self.currow, iid=self.currow,
                             values=("", "Balance for the day", "", "", "", "", d))
        else:
            self.tree.insert("", index=self.currow, iid=self.currow,
                             values=("", "Balance for the day (Nill)", "", "", "", "", ""))

    def print(self, _event=None):
        self.write_pdf()
        # prints the stock pdf file
        win32api.ShellExecute(0, "print", "daybook.pdf", None, ".", 0)

    def write_pdf(self):
        print("")
        pdf = FPDF("L", "mm", "A4")
        pdf.add_page()

        # addding Company Name as center text in line1
        pdf.set_font("helvetica", size=26)
        pdf.cell(0, 8, txt="Sri Narayana Trading Company", ln=1, align='C')
        pdf.cell(0, 8, txt="", ln=1, align='C')

        # adding Accouting year in line2
        pdf.set_font("helvetica", size=16)
        content = "DayBook for the Accounting year " + config.Year
        content = ('{:^75}'.format(content))
        pdf.cell(10, 8, txt=content, ln=1)

        # adding Accouting year in line2
        content = "Date: " + self.strdate.get()
        content = ('{:<75}'.format(content))
        pdf.cell(10, 8, txt=content, ln=1)

        pdf.set_font("helvetica", size=12)
        # displaying table for daybook in pdf
        with pdf.table(col_widths=(45, 30, 15, 18, 18, 18, 18),
                        text_align=("LEFT", "LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"),
                        borders_layout="ALL") as table:
            headings = table.row()
            headings.cell("Account Description", align="C")
            headings.cell("Narration", align="C")
            headings.cell("Quantity", align="C")
            headings.cell("Debit", align="C")
            headings.cell("Credit", align="C")
            headings.cell("Cash Payment", align="C")
            headings.cell("Cash Receipt", align="C")

            # displaying the contents of the table in the pdf from daybook table created
            for data_row in self.tree.get_children():
                value = self.tree.item(data_row)['values']
                if value[0] != "":
                    row = table.row()
                    for datum in value:
                        row.cell(datum)
                else:
                    if value[1] == "Total":
                        no = data_row

        # displaying the total and balance of the table in the pdf from daybook table created
        with pdf.table(col_widths=(45, 30, 15, 18, 18, 18, 18),
                        text_align=("LEFT", "LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"),
                        borders_layout="NO_HORIZONTAL_LINES") as total:
            trow = total.row()
            value = self.tree.item(no)['values']
            for datum in value:
                trow.cell(datum)
            trow = total.row()
            no = int(no) + 1
            value = self.tree.item(str(no))['values']
            for datum in value:
                trow.cell(datum)

        # printing the content to the daybook.pdf
        pdf.output("daybook.pdf")

    def preparing_window(self, tab):
        self.tab = tab
        # creating frame for fields
        field_fra = ttk.LabelFrame(tab, width=2000, height=800)
        field_fra.place(x=10, y=10)

        # adding Company name to frame
        tk.Label(field_fra, text="SRI NARAYANA TRADING COMPANY", bd=4).place(x=550, y=10)
        s = "Account Year " + config.Year
        tk.Label(field_fra, text=s, bd=4).place(x=580, y=40)
        tk.Label(field_fra, text="DayBook", bd=4).place(x=600, y=70)

        # adding Date controls to field frame
        tk.Label(field_fra, text="Date", bd=4).place(x=120, y=120)
        self.date_ent = tk.Entry(field_fra, textvariable=self.strdate)
        self.date_ent.place(x=180, y=120)

        # creating button to select date
        self.seldate_bt = tk.Button(field_fra, text="Select Date", underline=0, width=15,
                                    command=lambda: self.my_window())
        self.seldate_bt.place(x=570, y=100)
        config.Root.bind("<Control-s>", self.my_window)

        self.print_bt = tk.Button(field_fra, text="Print", underline=4, width=15, command=lambda: self.print())
        self.print_bt.place(x=750, y=100)
        config.Root.bind("<Control-t>", self.print)
        close_bt = tk.Button(field_fra, text="Close", underline=2, width=15, command=lambda: self.close())
        close_bt.place(x=870, y=100)
        config.Root.bind("<Control-o>", self.close)

        # creating Navigation buttons
        self.first_bt = tk.Button(field_fra, text="First", underline=0, width=6, command=lambda: self.move_first())
        self.first_bt.place(x=1100, y=100)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(field_fra, text="Prev", underline=0, width=6, command=lambda: self.move_prev())
        self.prev_bt.place(x=1150, y=100)
        config.Root.bind("<Control-p>", self.move_prev)
        self.next_bt = tk.Button(field_fra, text="Next", underline=0, width=6, command=lambda: self.move_next())
        self.next_bt.place(x=1200, y=100)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(field_fra, text="Last", underline=0, width=6, command=lambda: self.move_last())
        self.last_bt.place(x=1250, y=100)
        config.Root.bind("<Control-l>", self.move_last)

        # creating frame for the table
        table_fra = ttk.Frame(field_fra, width=3000, height=100)
        table_fra.place(x=20, y=150)

        # creating table for displaying the daybook
        self.tree = ttk.Treeview(table_fra, height=25)
        self.tree['columns'] = ('Desc', 'Narr', 'Quantity', 'Debit', 'Credit', 'Payment', 'Receipt')
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('Desc', width=300)
        self.tree.column('Narr', width=300)
        self.tree.column('Quantity', width=80, anchor=tk.E)
        self.tree.column('Debit', width=180, anchor=tk.E)
        self.tree.column('Credit', width=180, anchor=tk.E)
        self.tree.column('Payment', width=180, anchor=tk.E)
        self.tree.column('Receipt', width=180, anchor=tk.E)

        self.tree.heading('#0', text='')
        self.tree.heading('Desc', text='Account Description')
        self.tree.heading('Narr', text='Narration')
        self.tree.heading('Quantity', text='Quantity')
        self.tree.heading('Debit', text='Debit')
        self.tree.heading('Credit', text='Credit')
        self.tree.heading('Payment', text='Cash Payment')
        self.tree.heading('Receipt', text='Cash Receipt')

        # adding scroll bar to the daybook table
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.tree.pack(expand=1)

        # disabling the text box that displays the date for which the daybook is displayed
        self.date_ent.configure(state="disabled")
        self.my_window()
