
import config
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime as dt
from datetime import timedelta
import mysql.connector as con
from fpdf.fpdf import FPDF
import win32api


class Stock:

    def __init__(self):
        self.top = self.tree = self.tab = self.field_fra = None
        self.enddate_ent = self.stdate_ent = None
        self.stdate = self.enddate = self.curdate = None
        self.sdate = tk.StringVar()
        self.edate = tk.StringVar()
        self.strdate = tk.StringVar()

        self.last_bt = self.next_bt = self.prev_bt = self.first_bt = None
        self.print_bt = self.seldate_bt = None

        self.openqty = 0
        self.salesqty = 0
        self.purchaseqty = 0
        self.transflag = self.diffdate = self.dateflag = None

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
        ok_bt = tk.Button(self.top, text="Ok", underline=0, width=8, command=lambda: self.ok())
        ok_bt.place(x=100, y=140)
        self.top.bind("<Control-o>", self.ok)

        # creating Cancel button
        cancel_bt = tk.Button(self.top, text="Cancel", underline=0, width=8, command=lambda: self.cancel())
        cancel_bt.place(x=210, y=140)
        self.top.bind("<Control-c>", self.cancel)

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
                        self.stdate_ent.focus_set()
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
                # setting navigation buttons acording to the dates
                self.set_navi()
                # displaying stock for the current date
                if self.tree:
                    self.clear_table()
                self.display_stock()
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
            # if stock for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the end date
            self.dateflag = "First"
            # setting current date to the start date
            self.curdate = self.stdate
            self.sdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            self.strdate.set(dt.strftime(self.curdate, "%d-%m-%Y"))
            self.set_navi()
            # clearing the table and displaying stock for the current date(start date)
            self.clear_table()
            self.display_stock()

    def move_prev(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "Last"):
            # if stock for more than 1 day is to be displayed
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
            # clearing the table and displaying stock for the current date(date before)
            self.clear_table()
            self.display_stock()

    def move_next(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "First"):
            # if stock for more than 1 day is to be displayed
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
            # clearing the table and displaying stock for the current date(date after)
            self.clear_table()
            self.display_stock()

    def move_last(self, _event=None):
        if self.diffdate and (self.dateflag == "Middle" or self.dateflag == "First"):
            # if stock for more than 1 day is to be displayed
            # and current date is between start and end date or current date is the start date
            # setting current date to the last date
            self.curdate = self.enddate
            self.dateflag = "Last"
            self.sdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            self.strdate.set(dt.strftime(self.curdate, "%d-%m-%Y"))
            self.set_navi()
            # clearing the table and displaying stock for the current date(end date)
            self.clear_table()
            self.display_stock()

    def clear_table(self):
        # clears stock table
        for row in self.tree.get_children():
            self.tree.delete(row)

    def display_stock(self):
        # displaying stock for the current date
        # creating frame for the table
        table_fra = ttk.Frame(self.field_fra, width=3000, height=100)
        table_fra.place(x=20, y=160)

        # creating table using treeview
        self.tree = ttk.Treeview(table_fra, height=20)
        self.tree['columns'] = ["Product", "Op_Stock", "Purchase", "Sales", "Cl_Stock"]

        # setting width for each column in the table
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column("Product", width=400, anchor=tk.W)
        self.tree.column("Op_Stock", width=250, anchor=tk.E)
        self.tree.column("Purchase", width=250, anchor=tk.E)
        self.tree.column("Sales", width=250, anchor=tk.E)
        self.tree.column("Cl_Stock", width=250, anchor=tk.E)

        # setting heading for each column in the table
        self.tree.heading('#0', text='')
        self.tree.heading("Product", text="Product Name", anchor=tk.CENTER)
        self.tree.heading("Op_Stock", text="Opening Stock", anchor=tk.CENTER)
        self.tree.heading("Purchase", text="Purchase Quantity", anchor=tk.CENTER)
        self.tree.heading("Sales", text="Sales Quantity", anchor=tk.CENTER)
        self.tree.heading("Cl_Stock", text="Closing Stock", anchor=tk.CENTER)

        # attaching scrollbar to the table
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.tree.pack(expand=1)

        # opens the connection  with the database
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        # getting all product code(purchase code) to display the stock for each code
        s = "Select Code, Description, ytopqty from Product where Code like 'P%' and Year = '" + config.Year + "'"
        cur.execute(s)
        prodres = cur.fetchall()

        # contains the date to be displayed in the table
        lst = []
        # to set the index for each row in the table
        i = 1
        for res in prodres:
            lst.clear()
            self.openqty = 0
            self.purchaseqty = 0
            self.salesqty = 0
            # calculating opening stock for the current product for the current date
            self.calculate_openstock(res[0], res[2])
            # calculating total sales and purchase quantity for the current product on the current date
            self.calculate_salespurchase(res[0])
            # calculating the closing stock by adding purchase quantity to the opening stock
            # and deducting sales quantity
            bal = (self.openqty + self.purchaseqty) - self.salesqty
            # adding the transation details of the current product to the list
            desc = res[1].split("(")
            if len(desc) == 1:
                prodname = desc[0]
            else:
                prodname = desc[1][:len(desc[1]) - 1]
            lst = [prodname, self.openqty, self.purchaseqty, self.salesqty, bal]
            # diaplying the list in the table
            self.tree.insert("", index=i, values=lst)
            i += 1

        if not self.transflag:
            # if no transaction has been made on that day
            tk.messagebox.showinfo(config.Company_Name, "No Transactions made on that day")

    def calculate_openstock(self, code, tqty):
        # calculating opening stock for that product
        # opens the connection to fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        # getting purchase transaction("P%", code) and  Sales transaction("I%", icode) for that product
        # till the date before the current date
        icode = "I" + code[1:]
        s = "Select Code, quantity from Transaction where (Code = '" + icode + "' or Code = '" + code + "') and Date < '" \
            + self.sdate.get() + "' and Cancelled = 'N' and Year = '" + config.Year + "' order by code"
        cur.execute(s)
        res = cur.fetchall()

        sqty = 0
        pqty = 0
        for r in res:
            if r[0][:1] == "I":
                sqty = sqty + r[1]
            elif r[0][:1] == "P":
                pqty = pqty + r[1]

        # calculating opening stock by adding purchase quantity withe ytopqty and deducting the sales quantity
        self.openqty = (tqty + pqty) - sqty

    def calculate_salespurchase(self, code):
        # calculating the total purchase quantity and Sales quantity for that product on that date
        # opens the connection to fetches the details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        # getting purchase quantity for that product code from entries table
        s = "Select Code, quantity from Entries where Code = '" + code + "' and Date = '" \
            + self.sdate.get() + "' and Year = '" + config.Year + "' order by code"
        cur.execute(s)
        res = cur.fetchall()

        pqty = 0
        for r in res:
            if not self.transflag:
                self.transflag = True
            pqty = pqty + r[1]
        self.purchaseqty = pqty

        # getting Sales quantity for that product code from Transaction table
        icode = "I" + code[1:]
        s = "Select Code, quantity from Transaction where Code = '" + icode + "' and Date = '" \
            + self.sdate.get() + "' and Cancelled = 'N' and Year = '" + config.Year + "' order by code"
        cur.execute(s)
        res = cur.fetchall()

        sqty = 0
        for r in res:
            if not self.transflag:
                self.transflag = True
            sqty = sqty + r[1]
        self.salesqty = sqty

        # getting purchase quantity for ("P%", code) of that product on the current date
        icode = "P" + code[1:]
        s = "Select Code, quantity from Entries where Code = '" + icode + "' and Date = '" \
            + self.sdate.get() + "' and Year = '" + config.Year + "' order by code"
        cur.execute(s)
        res = cur.fetchall()

        pqty = 0
        for r in res:
            if not self.transflag:
                self.transflag = True
            pqty = pqty + r[1]

        # setting the total Sales and total purchase quantity

        self.purchaseqty = pqty

    def write_pdf(self):
        # creating the report pdf file
        pdf = FPDF("P", "mm", "A4")
        # creating a new pdf page
        pdf.add_page()

        # addding Company Name as center text in line1
        pdf.set_font("helvetica", size=26)
        pdf.cell(0, 8, txt="Sri Narayana Trading Company", ln=1, align='C')
        pdf.cell(0, 8, txt="", ln=1, align='C')

        # adding Accouting year in line2
        pdf.set_font("helvetica", size=16)
        content = "Stock for the Accounting year " + config.Year
        content = ('{:^75}'.format(content))
        pdf.cell(0, 8, txt=content, ln=1, align='C')
        pdf.cell(0, 8, txt="", ln=1, align='C')

        # adding Date in line3
        content = "Date: " + self.strdate.get()
        content = ('{:<75}'.format(content))
        pdf.cell(0, 8, txt=content, ln=1, align="L")
        pdf.cell(0, 8, txt="", ln=1, align='C')

        pdf.set_font("helvetica", size=12)
        with pdf.table(col_widths=(60, 20, 20, 20, 20),
                text_align=("LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"),
                       borders_layout="NO_HORIZONTAL_LINES") as table:
            # printing heading for that table
            headings = table.row()
            headings.cell("Product Name", align='C')
            headings.cell("Opening Stock", align='C')
            headings.cell("Purchase Quantity", align='C')
            headings.cell("Sales Quantity", align='C')
            headings.cell("Closing Stock", align='C')

            # printing table to the pdf file
            for data_row in self.tree.get_children():
                value = self.tree.item(data_row)['values']
                row = table.row()
                for datum in value:
                    row.cell(datum)

        # writes the output of the table to th pdf file named stock.pdf
        pdf.output("stock.pdf")

    def print(self, _event=None):
        self.write_pdf()
        # prints the stock pdf file
        win32api.ShellExecute(0, "print", "stock.pdf", None, ".", 0)

    def close(self, _event=None):
        self.tab.destroy()

    def preparing_window(self, tab):
        self.tab = tab
        # creating frame for fields
        self.field_fra = ttk.Frame(self.tab, width=1450, height=800)
        self.field_fra.place(x=10, y=10)

        # adding Company name to frame
        tk.Label(self.field_fra, text="SRI NARAYANA TRADING COMPANY", bd=4).place(x=550, y=20)
        s = "Account Year " + config.Year
        tk.Label(self.field_fra, text=s, bd=4).place(x=580, y=50)
        tk.Label(self.field_fra, text="Stock", bd=4).place(x=630, y=80)

        # adding Date controls to field frame
        tk.Label(self.field_fra, text="Date", bd=4).place(x=120, y=120)
        date_ent = tk.Entry(self.field_fra, textvariable=self.strdate)
        date_ent.place(x=180, y=120)

        # creating button to select date
        self.seldate_bt = tk.Button(self.field_fra, text="Select Date", underline=0, width=15, command=lambda: self.my_window())
        self.seldate_bt.place(x=370, y=120)
        config.Root.bind("<Control-s>", self.my_window)
        self.print_bt = tk.Button(self.field_fra, text="Print", underline=4, width=15, command=lambda: self.print())
        self.print_bt.place(x=550, y=120)
        config.Root.bind("<Control-t>", self.print)
        close_bt = tk.Button(self.field_fra, text="Close", underline=2, width=15, command=lambda: self.close())
        close_bt.place(x=670, y=120)
        config.Root.bind("<Control-o>", self.close)

        # creating Navigation buttons
        self.first_bt = tk.Button(self.field_fra, text="First", underline=0, width=6, command=lambda: self.move_first())
        self.first_bt.place(x=900, y=120)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(self.field_fra, text="Prev", underline=0, width=6, command=lambda: self.move_prev())
        self.prev_bt.place(x=950, y=120)
        config.Root.bind("<Control-p>", self.move_prev)
        self.next_bt = tk.Button(self.field_fra, text="Next", underline=0, width=6, command=lambda: self.move_next())
        self.next_bt.place(x=1000, y=120)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(self.field_fra, text="Last", underline=0, width=6, command=lambda: self.move_last())
        self.last_bt.place(x=1050, y=120)
        config.Root.bind("<Control-l>", self.move_last)

        date_ent.configure(state="disabled")
        self.diffdate = False
        self.my_window()
