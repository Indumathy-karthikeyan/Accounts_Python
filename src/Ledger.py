import config
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import timedelta
from datetime import datetime as dt
import mysql.connector as con
import win32api
from fpdf.fpdf import FPDF


class Ledger:

    def __init__(self):

        self.tree = self.top = self.tab = self.res = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None
        self.seldate_bt = self.print_bt = self.find_bt = None
        self.stdate_ent = self.enddate_ent = self.strcurdate = self.code_ent = self.desc_ent = self.selcode_ent = None

        self.cramt = self.dbamt = self.baltype = None
        self.transflag = self.codeflag = None

        self.currec = self.totrec = self.currow = self.curdate = self.diffcode = self.enddate = self.stdate = None

        self.selcode = tk.StringVar()
        self.strcode = tk.StringVar()
        self.strfinddesc = tk.StringVar()
        self.strdesc = tk.StringVar()
        self.sdate = tk.StringVar()
        self.edate = tk.StringVar()
        self.strdate = tk.StringVar()

    def my_window(self, _event=None):
        self.top = tk.Toplevel(config.Root)
        self.top.geometry("400x300")
        x = config.Root.winfo_x()
        y = config.Root.winfo_y()
        self.top.geometry("+%d+%d" % (x + 500, y + 250))
        self.top.wm_transient(config.Root)
        self.top.grab_set()

        # adding Start date
        self.sdate.set("")
        self.edate.set("")
        self.selcode.set("")
        tk.Label(self.top, text="Code :", width=8, bd=4).place(x=60, y=40)
        self.selcode_ent = tk.Entry(self.top, width=25, textvariable=self.selcode)
        self.selcode_ent.place(x=150, y=40)
        self.selcode_ent.bind("<KeyRelease>", self.check_code)
        tk.Label(self.top, text="Start Date :", width=8, bd=4).place(x=60, y=90)
        self.stdate_ent = tk.Entry(self.top, width=25, textvariable=self.sdate)
        self.stdate_ent.place(x=150, y=90)
        self.stdate_ent.bind("<KeyRelease>", self.enter_stdate)
        # adding End date
        tk.Label(self.top, text="End Date :", width=8, bd=4).place(x=60, y=150)
        self.enddate_ent = tk.Entry(self.top, width=25, textvariable=self.edate)
        self.enddate_ent.place(x=150, y=150)
        self.enddate_ent.bind("<KeyRelease>", self.enter_enddate)

        # creating ok button
        ok_bt = tk.Button(self.top, text="Ok", underline=0, width=10, command=lambda: self.ok())
        ok_bt.place(x=100, y=210)
        self.top.bind("<Alt-o>", self.ok)

        # creating Cancel button
        cancel_bt = tk.Button(self.top, text="Cancel", underline=0, width=10, command=lambda: self.cancel())
        cancel_bt.place(x=210, y=210)
        self.top.bind("<Alt-c>", self.cancel)

        self.selcode_ent.focus_set()

    def check_code(self, _event=None):
        # checking customer code
        # only 4 characters
        # first letter must be A or L or E
        s = self.selcode.get()
        lt = len(s)
        s = s.upper()
        for i in range(0, lt):
            if not ('A' <= s[i] <= 'Z'):
                tk.messagebox.showinfo(config.Company_Name, "only Letters")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break
            else:
                if (i == 0) and (s[i] != 'A' and s[i] != 'L' and s[i] != 'E' and s[i] != 'P' and s[i] != 'I'
                                 and s[i] != 'F'):
                    tk.messagebox.showinfo(config.Company_Name, "First Letter should be A or L or E or P or I or F")
                    s = ""
                    break

        if len(s) > 4:
            tk.messagebox.showinfo(config.Company_Name, "only 4 letters")
            s = s[:4]

        self.selcode.set(s)

    def enter_stdate(self, e):
        if (e.keysym != "BackSpace" and e.keysym != "Left" and e.keysym != "Right" and e.keysym != "Delete"
                and e.keysym != "Tab"):
            self.sdate.set(config.enter_date(self.sdate.get()))
            self.stdate_ent.icursor(tk.END)

    def enter_enddate(self, e):
        if (e.keysym != "BackSpace" and e.keysym != "Left" and e.keysym != "Right" and e.keysym != "Delete"
                and e.keysym != "Tab"):
            self.edate.set(config.enter_date(self.edate.get()))
            self.enddate_ent.icursor(tk.END)

    def ok(self, _event=None):

        # validating start date entered
        if self.selcode.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Enter the Accounting code")
            self.selcode_ent.focus_set()
        elif self.sdate.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Enter the starting date")
            self.stdate_ent.focus_set()
        else:
            if not config.validate_dt(self.sdate.get()):
                tk.messagebox.showinfo(config.Company_Name, "Invalid start date")
                self.stdate_ent.focus_set()
            else:
                # if valid start date
                # converting start date to "yy-mm-dd" format for doing query in the database
                self.stdate = dt.strftime(dt.strptime(self.sdate.get(), "%d-%m-%Y"), "%Y-%m-%d")

                # validating end date entered
                if self.edate.get() != "":
                    if not config.validate_dt(self.edate.get()):
                        tk.messagebox.showinfo(config.Company_Name, "Invalid end date")
                        self.enddate_ent.focus_set()
                    else:
                        # if valid end date
                        # converting end date to "yy-mm-dd" format for doing query in the database
                        self.enddate = dt.strftime(dt.strptime(self.edate.get(), "%d-%m-%Y"), "%Y-%m-%d")
                else:
                    self.enddate = dt.strftime(dt.strptime(self.stdate, "%Y-%m-%d"), "%Y-%m-%d")

                # opens the connection and fetches the details
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()

                # getting the code details of the specified code
                ch = self.selcode.get()[0]
                table = ""
                if ch == "A" or ch == "L" or ch == "E":
                    table = "Customer"
                elif ch == "P" or ch == "I" or ch == "F":
                    table = "Product"
                s = "Select Code, Description from " + table + " where code like '" + self.selcode.get() + "%' and  "\
                    + "year = '" + config.Year + "' order by code"
                cur.execute(s)
                self.res = cur.fetchall()

                if self.tree:
                    self.clear_table()
                # closing the date window
                self.top.destroy()

                # displaying daybook for the current date
                if len(self.res) > 0:
                    self.currec = 0
                    self.totrec = len(self.res)
                    if self.totrec > 1:
                        self.diffcode = True
                        self.find_bt.configure(state="normal")
                    else:
                        self.diffcode = False
                        self.find_bt.configure(state="disabled")
                    self.display_ledger()
                    self.print_bt.configure(state="normal")
                    self.transflag = False

                else:
                    self.currec = -1
                    self.totrec = 0
                    self.diffcode = False
                    self.find_bt.configure(state="disabled")
                    self.print_bt.configure(state="disabled")
                    tk.messagebox.showinfo(config.Company_Name, "No code for the specified pattern")

                # setting navigation buttons according to the dates
                self.set_navi()

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
        # setting navigation buttons acording to the no of account code
        print("Inside navi",self.currec)
        if self.totrec == 0 or self.totrec == 1:
            # if only start date is entered
            self.first_bt.configure(state="disabled")
            self.prev_bt.configure(state="disabled")
            self.next_bt.configure(state="disabled")
            self.last_bt.configure(state="disabled")
        else:
            if self.currec == 0:
                # if current record is the first record
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.currec == (self.totrec - 1):
                # if current record is the last record
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                # if current record is between first and last record
                # enable all navigation buttons
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def move_first(self, _event=None):
        if self.diffcode and (self.totrec > 1) and self.currec != 0:
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the end date
            self.currec = 0
            self.set_navi()
            # clearing the table and displaying daybook for the current date(start date)
            self.clear_table()
            self.display_ledger()

    def move_prev(self, _event=None):
        if self.diffcode and (self.totrec > 1) and self.currec != 0:
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the end date
            # setting current date to the previous date
            self.currec -= 1
            self.set_navi()
            # clearing the table and displaying daybook for the current date(date before)
            self.clear_table()
            self.display_ledger()

    def move_next(self, _event=None):
        if self.diffcode and (self.totrec > 1) and (self.currec != (self.totrec - 1)):
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the start date
            # setting current date to the next date
            self.currec += 1
            self.set_navi()
            # clearing the table and displaying daybook for the current date(date after)
            self.clear_table()
            self.display_ledger()

    def move_last(self, _event=None):
        if self.diffcode and (self.totrec > 1) and (self.currec != (self.totrec - 1)):
            # if daybook for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the start date
            # setting current date to the last date

            self.currec = self.totrec - 1
            self.set_navi()
            # clearing the table and displaying daybook for the current date(end date)
            self.clear_table()
            self.display_ledger()

    def clear_table(self):
        # clears daybook table
        for row in self.tree.get_children():
            self.tree.delete(row)

    def print(self, _event=None):
        self.write_pdf()
        # prints the stock pdf file
        win32api.ShellExecute(0, "print", "Ledger.pdf", None, ".", 0)

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
        content = "Ledger for the Accounting year " + config.Year
        content = ('{:^75}'.format(content))
        pdf.cell(10, 8, txt=content, ln=1)

        # adding Accouting year in line2
        content = "Description: e4  z " + self.strdesc.get()
        content = ('{:<75}'.format(content))
        pdf.cell(10, 8, txt=content, ln=1)

        pdf.set_font("helvetica", size=12)
        # displaying table for daybook in pdf
        with pdf.table(col_widths=(45, 30, 15, 18, 18, 18, 18),
                text_align=("LEFT", "LEFT", "RIGHT", "RIGHT",  "RIGHT"),
                       borders_layout="ALL") as table:
            headings = table.row()
            headings.cell("Date", align="C")
            headings.cell("Narration", align="C")
            headings.cell("Quantity", align="C")
            headings.cell("Debit", align="C")
            headings.cell("Credit", align="C")

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
                    text_align=("LEFT", "LEFT", "RIGHT", "RIGHT", "RIGHT"),
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
        pdf.output("Ledger.pdf")

    def get_prevbalance(self):
        # calculating openning balance for the current date
        db = 0
        cr = 0

        # opens the connection to fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        ch = self.res[self.currec][0][0]
        if ch == "A" or ch == "L":
            s = ("select Code, OpenBal, BalType from Customer where code = '" + self.res[self.currec][0]
                + "' and year = '" + config.Year + "'")

            cur.execute(s)
            res = cur.fetchall()

            if len(res) > 0:
                if res[0][2] == "C":
                    cr += float(res[0][1])
                elif res[0][2] == "D":
                    db += float(res[0][1])

        # getting sales transaction upto previous date to calculate openning balance
        # getting all Manual and Computer Cash Transaction from Transaction table
        s = "select Code, Type, Amount from Transaction where Date <'" + str(self.curdate) \
            + "' and code = '" + self.res[self.currec][0] + "' and year = '" + config.Year \
            + "' and cancelled = 'N' order by BillNo"

        cur.execute(s)
        res = cur.fetchall()

        if len(res) > 0:
            # calculating sum of cash Sales amount
            for r in res:
                if r[1] == "C":
                    cr += float(r[2])
                elif r[1] == "D":
                    db += float(r[2])

        # getting transaction from entries upto previous date to calculate openning balance
        # s = "select Code, Type, Amount from Entries where Date <'" + str(self.curdate) + "' and TransType = 'C'"\
        #    + " and year = '" + config.Year + "'"
        s = "select Code, Type, Amount from Entries where Date <'" + str(self.curdate) + "' and code= '"\
            + self.res[self.currec][0] + "' and year = '" + config.Year + "'"
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
            self.cramt = bal
            self.dbamt = 0
        elif db > cr:
            # in case if debit is more calculate balance set type to debit
            bal = db - cr
            self.baltype = "D"
            self.dbamt = bal
            self.cramt = 0
        else:
            # in case both are equal nill balance
            bal = db - cr
            self.baltype = ""
            self.dbamt = 0
            self.cramt = 0

        self.currow = 0
        # displaying opening balance
        amt = "{:.2f}".format(bal)
        self.currow = 0
        if self.baltype == "":
            self.tree.insert("", index=self.currow, values=["", "Opening Balance of the day (Nill)"])
        elif self.baltype == "D":
            self.tree.insert("", index=self.currow, values=["", "Opening Balance of the day", "", str(amt), ""])
        elif self.baltype == "C":
            self.tree.insert("", index=self.currow, values=["", "Opening Balance of the day", "", "", str(amt)])

    def display_ledger(self):

        # opens the connection and fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        code = self.res[self.currec][0]
        self.curdate = dt.strptime(self.stdate, "%Y-%m-%d").date()
        edate = dt.strptime(self.enddate, "%Y-%m-%d").date()

        self.strcode.set(self.res[self.currec][0])
        self.strdesc.set(self.res[self.currec][1])

        self.get_prevbalance()
        self.currow += 1
        flag = False
        while self.curdate <= edate:
            s = ("select Date, Narration, type, Quantity, amount, BillNo from transaction  where code= '" + code
                 + "' and Date = '" + str(self.curdate) + "' and Year='" + config.Year + "' order by BillNo")
            cur.execute(s)
            transrec = cur.fetchall()
            for rec in transrec:
                d = "{:.2f}".format(rec[4])
                if rec[2] == "D":
                    self.tree.insert("", index=self.currow, values=[self.curdate, rec[1], rec[3], d, ""])
                    self.dbamt += float(rec[4])
                elif rec[2] == "C":
                    self.tree.insert("", index=self.currow, values=[self.curdate, rec[1], rec[3], "", d])
                    self.cramt += float(rec[4])
                flag = True

                self.currow += 1
            s = ("select Date, Narration, type, Quantity, amount, EntryNo from entries  where code= '" + code
                 + "' and Date = '" + str(self.curdate) + "' and Year='" + config.Year + "' order by EntryNo ")
            cur.execute(s)
            entryrec = cur.fetchall()
            for rec in entryrec:
                d = "{:.2f}".format(rec[4])
                if rec[2] == "D":
                    self.tree.insert("", index=self.currow, values=[self.curdate, rec[1], rec[3], d, ""])
                    self.dbamt += float(rec[4])
                elif rec[2] == "C":
                    self.tree.insert("", index=self.currow, values=[self.curdate, rec[1], rec[3], "", d])
                    self.cramt += float(rec[4])
                flag = True

                self.currow += 1

            self.curdate = self.curdate + timedelta(days=1)

        self.display_total()

        if not flag:
            tk.messagebox.showinfo(config.Company_Name, "No transaction for the specified date for that code")

    def display_total(self):
        self.currow += 1
        dbamt = "{:.2f}".format(self.dbamt)
        cramt = "{:.2f}".format(self.cramt)
        self.tree.insert("", index=self.currow, iid=self.currow, values=("", "", "", "", ""))
        self.currow += 1
        self.tree.insert("", index=self.currow, iid=self.currow, values=("", "Total", "", dbamt, cramt))
        self.currow += 1
        if self.dbamt > self.cramt:
            diff = self.dbamt - self.cramt
            d = "{:.2f}".format(diff)
            self.tree.insert("", index=self.currow, iid=self.currow,
                             values=("", "Balance for the day", "", d, ""))
        elif self.cramt > self.dbamt:
            diff = self.cramt - self.dbamt
            d = "{:.2f}".format(diff)
            self.tree.insert("", index=self.currow, iid=self.currow,
                             values=("", "Balance for the day", "", "", d))
        else:
            self.tree.insert("", index=self.currow, iid=self.currow,
                             values=("", "Balance for the day (Nill)", "", "", ""))

    def check_desc(self):
        # matching product description with the list of customers
        s = self.strfinddesc.get()
        no = len(s)
        for row in self.selcode_tree.get_children():
            val = self.selcode_tree.item(row, "values")
            if val[1][:no].upper() == s.upper():
                self.selcode_tree.selection_set(row)
                self.selcode_tree.see(row)
                break

        self.strfinddesc.set(s)

    def find(self, _event=None):
        if not self.transflag:
            # creating a new window to list all the customer for searching
            self.top = tk.Toplevel(config.Root)
            self.top.geometry("500x500")
            x = config.Root.winfo_x()
            y = config.Root.winfo_y()
            self.top.geometry("+%d+%d" % (x + 500, y + 150))
            self.top.wm_transient(config.Root)
            self.top.grab_set()

            # creating frame for the top window
            top_fra = ttk.Frame(self.top, width=500, height=500)
            top_fra.place(x=10, y=10)

            # adding entry box to type customer name to search for to the top frame
            tk.Label(top_fra, text="Customer description", bd=4).place(x=30, y=10)
            self.find_desc_ent = tk.Entry(top_fra, textvariable=self.strfinddesc)
            self.find_desc_ent.place(x=180, y=10)
            self.find_desc_ent.bind('<KeyRelease>', lambda e: self.check_desc())

            # creating table to list the customer names
            table_fra = ttk.Frame(top_fra, width=80, height=300)
            table_fra.place(x=20, y=50)
            self.selcode_tree = ttk.Treeview(table_fra, height=17, selectmode="browse")
            self.selcode_tree['columns'] = ('Code', 'Desc')
            self.selcode_tree.column('#0', width=0, stretch=False)
            self.selcode_tree.column('Code', width=100)
            self.selcode_tree.column('Desc', width=350)

            self.selcode_tree.heading('#0', text='')
            self.selcode_tree.heading('Code', text='Code')
            self.selcode_tree.heading('Desc', text='Description')
            treescroll = ttk.Scrollbar(table_fra)
            treescroll.configure(command=self.selcode_tree.yview)
            self.selcode_tree.configure(yscrollcommand=treescroll.set)
            treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
            self.selcode_tree.pack(expand=1)

            # creating ok and cancel button
            ok_bt = tk.Button(top_fra, text="OK", width=8, underline=0, command=lambda: self.sel_ok())
            ok_bt.place(x=180, y=430)
            self.top.bind("<Alt-o>", self.sel_ok)
            cancel_bt = tk.Button(top_fra, text="Cancel", width=8, underline=0, command=lambda: self.sel_cancel())
            cancel_bt.place(x=250, y=430)
            self.top.bind("<Alt-c>", self.sel_cancel)

            # opens the connection and fetches the details
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()

            # getting the code details of the specified code
            ch = self.selcode.get()[0]
            table = ""
            if ch == "A" or ch == "L" or ch == "E":
                table = "Customer"
            elif ch == "P" or ch == "I" or ch == "F":
                table = "Product"
            s = "Select Code, Description from " + table + " where code like '" + self.selcode.get() + "%' and  " \
                + "year = '" + config.Year + "' order by Description"
            cur.execute(s)
            res = cur.fetchall()
            row = 0
            if len(self.res) > 0:
                # displaying list of customer in table
                for r in res:
                    self.selcode_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                    row += 1

            # setting focus to the code textbox
            self.strfinddesc.set("")
            self.find_desc_ent.focus()

    def sel_ok(self, _event=None):
        # displaying the details of the customer found out
        index = self.selcode_tree.selection()
        if index == "":
            tk.messagebox.showinfo(config.Company_Name, "select an item")
        else:
            item = self.selcode_tree.item(index)
            val = item['values']
            # displaying the product selected
            row = 0
            for r in self.res:
                if r[0] == val[0]:
                    self.currec = row
                row += 1

            self.set_navi()
            self.top.destroy()
            # clearing the table and displaying daybook for the current date(start date)
            self.clear_table()
            self.display_ledger()

    def sel_cancel(self, _event=None):
        self.top.destroy()

    def preparing_window(self, tab):
        self.tab = tab
        # creating frame for fields
        field_fra = ttk.LabelFrame(tab, width=2000, height=800)
        field_fra.place(x=10, y=10)

        # adding Company name to frame
        tk.Label(field_fra, text="SRI NARAYANA TRADING COMPANY", bd=4).place(x=550, y=10)
        s = "Account Year " + config.Year
        tk.Label(field_fra, text=s, bd=4).place(x=580, y=40)
        tk.Label(field_fra, text="Ledger", bd=4).place(x=600, y=70)

        # adding code and description controls to field frame
        tk.Label(field_fra, text="Code", bd=4).place(x=20, y=100)
        self.code_ent = tk.Entry(field_fra, textvariable=self.strcode, width=12)
        self.code_ent.place(x=70, y=100)
        tk.Label(field_fra, text="Description", bd=4).place(x=150, y=100)
        self.desc_ent = tk.Entry(field_fra, textvariable=self.strdesc, width=75)
        self.desc_ent.place(x=220, y=100)

        # creating Navigation buttons
        self.first_bt = tk.Button(field_fra, text="First", underline=0, width=10, command=lambda: self.move_first())
        self.first_bt.place(x=1050, y=100)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(field_fra, text="Prev", underline=0, width=10, command=lambda: self.move_prev())
        self.prev_bt.place(x=1130, y=100)
        config.Root.bind("<Control-p>", self.move_prev)
        self.next_bt = tk.Button(field_fra, text="Next", underline=0, width=10, command=lambda: self.move_next())
        self.next_bt.place(x=1210, y=100)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(field_fra, text="Last", underline=0, width=10, command=lambda: self.move_last())
        self.last_bt.place(x=1290, y=100)
        config.Root.bind("<Control-l>", self.move_last)

        # creating frame for the table
        table_fra = ttk.Frame(field_fra, width=3000, height=100)
        table_fra.place(x=20, y=150)

        # creating table for displaying the daybook
        self.tree = ttk.Treeview(table_fra, height=25)
        self.tree['columns'] = ('Date', 'Narr', 'Quantity', 'Debit', 'Credit')
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('Date', width=100)
        self.tree.column('Narr', width=500)
        self.tree.column('Quantity', width=100, anchor=tk.E)
        self.tree.column('Debit', width=200, anchor=tk.E)
        self.tree.column('Credit', width=200, anchor=tk.E)

        self.tree.heading('#0', text='')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Narr', text='Narration')
        self.tree.heading('Quantity', text='Quantity')
        self.tree.heading('Debit', text='Debit')
        self.tree.heading('Credit', text='Credit')

        # adding scroll bar to the daybook table
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.tree.pack(expand=1)

        field1_fra = ttk.LabelFrame(field_fra, width=130, height=300)
        field1_fra.place(x=1200, y=200)

        # creating button to select date
        self.seldate_bt = tk.Button(field1_fra, text="Select Date", underline=0, width=10,
                                    command=lambda: self.my_window())
        self.seldate_bt.place(x=20, y=50)
        config.Root.bind("<Control-s>", self.my_window)

        self.find_bt = tk.Button(field1_fra, text="Find", underline=1, width=10,
                                 command=lambda: self.find())
        self.find_bt.place(x=20, y=100)
        config.Root.bind("<Control-i>", self.find)
        self.print_bt = tk.Button(field1_fra, text="Print", underline=4, width=10, command=lambda: self.print())
        self.print_bt.place(x=20, y=150)
        config.Root.bind("<Control-t>", self.print)
        close_bt = tk.Button(field1_fra, text="Close", underline=2, width=10, command=lambda: self.close())
        close_bt.place(x=20, y=200)
        config.Root.bind("<Control-o>", self.close)

        # disabling the text box that displays the code and description for which the ledger is displayed
        self.code_ent.configure(state="disabled")
        self.desc_ent.configure(state="disabled")
        self.my_window()
