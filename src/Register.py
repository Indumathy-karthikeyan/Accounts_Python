import config
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime as dt
from datetime import timedelta
import mysql.connector as con
from fpdf.fpdf import FPDF
import win32api


class Register:

    def __init__(self):

        self.stdate_ent = self.enddate_ent = None
        self.cash_fra = self.credit_fra = None
        self.cashsumtree = self.cashprodtree = self.creditsumtree= self.creditprodtree = None
        self.cashsumscroll = self.cashprodscroll = self.creditsumscroll = self.creditprodscroll = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None
        self.seldate_bt = self.print_bt = None
        self.top = self.tree = None
        self.sdate = tk.StringVar()
        self.edate = tk.StringVar()
        self.strdate = tk.StringVar()
        self.strcurdate = tk.StringVar()
        self.stdate = self.enddate = self.curdate = None
        self.transflag = self.diffdate = None
        self.prodflag = self.totalcol = None

    def my_window(self, _event=None):
        self.top = tk.Toplevel(config.Root)
        self.top.geometry("400x200")
        x = config.Root.winfo_x()
        y = config.Root.winfo_y()
        self.top.geometry("+%d+%d" % (x + 500, y + 250))
        self.top.wm_transient(config.Root)
        self.top.grab_set()

        # adding Start date
        #self.sdate.set("1-4-2022")
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
        self.top.bind("<Alt-o>", self.ok)

        # creating Cancel button
        cancel_bt = tk.Button(self.top, text="Cancel", underline=0, width=8, command=lambda: self.cancel())
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

        flag = False
        if self.sdate.get() == "":
            tk.messagebox.showinfo("", "Specify start Date")
            self.stdate_ent.focus_set()
        elif not config.validate_dt(self.sdate.get()):
            tk.messagebox.showinfo(config.Company_Name, "Invalid start Date")
            self.stdate_ent.focus_set()
        else:
            self.stdate = dt.strptime(dt.strftime(dt.strptime(self.sdate.get(), "%d-%m-%Y"), "%Y-%m-%d"),"%Y-%m-%d")
            self.curdate = self.stdate
            self.strcurdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
            if self.edate.get() != "":
                if not config.validate_dt(self.edate.get()):
                    tk.messagebox.showinfo(config.Company_Name, "Invalid end Date")
                    self.enddate_ent.focus_set()
                else:
                    flag = True
                    self.enddate = dt.strptime(dt.strftime(dt.strptime(self.edate.get(), "%d-%m-%Y"), "%Y-%m-%d"),"%Y-%m-%d")
                    if self.stdate == self.enddate:
                        self.diffdate = False
                    else:
                        self.diffdate = True
            else:
                flag = True
                self.diffdate = False


            if flag:
                self.strdate.set(dt.strftime(dt.strptime(self.sdate.get(), "%d-%m-%Y"), "%d-%m-%Y"))
                self.top.destroy()
                self.set_navi()
                self.display()

    def cancel(self, _event=None):
        self.top.destroy()

    def display(self):
        self.clear_table()
        self.prodflag = [False, False]
        self.totalcol = [0, 0]
        self.get_prodinfo("Cash", self.cash_fra)
        self.get_prodinfo("Credit", self.credit_fra)

        if not self.creditsumtree and not self.cashsumtree:
            self.print_bt.configure(state="disabled")
        else:
            self.print_bt.configure(state="normal")

    def get_prodinfo(self, type, fra):
        # getting prodinfo from transaction
        # opens the connection and fetches the records from Transaction table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        # setting bill pattern to search in case of cash or credit transaction for both sales and purchase
        code1 = ""
        code2 = ""
        prodcode = ""
        if type == "Cash" and self.regtype == "Sales":
            # in case of cash Sales pattern for billno is either "CCH%" or "MCH%"
            code1 = "CCH%"
            code2 = "MCH%"
        elif type == "Credit" and self.regtype == "Sales":
            # in case of credit Sales pattern for billno is either "CCR%" or "MCR%"
            code1 = "CCR%"
            code2 = "MCR%"
        elif type == "Cash" and self.regtype == "Purchase":
            # in case of cash purchase pattern for billno is either "PCH%"
            code1 = "PCH%"
        elif type == "Credit" and self.regtype == "Purchase":
            # in case of credit purchase pattern for billno is either "PCR%"
            code1 = "PCR%"

        # in case of sales pattern for product code is "I%"
        prodcode = "I%"
        # getting transactions based on the pattern on that particular date
        s = "select distinct code from transaction where (BillNo like '" + code1 + "' or BillNo like '" + code2 \
            + "') and (code like '" + prodcode + "') and (date = '" + self.strcurdate.get() + "') and (year = '" \
            + config.Year + "') and cancelled='N' order by code"

        cur.execute(s)
        prodres = cur.fetchall()

        # list to store product info
        prodlst = []
        # list to store info of all transactions made for all products
        translst = []

        for res in prodres:
            # intializing product list with product name
            prodlst.append([res[0], 0, 0])

        taxlst = ["LCST", "LSST", "LIST", "EBRO"]
        for i in range(0,4):
            if self.regtype == "Sales":
                # getting transactions of tax based on the pattern on that particular date
                s = "select distinct code from transaction where (BillNo like '" + code1 + "' or BillNo like '" + code2 \
                    + "') and (code like '" + taxlst[i] + "') and (date = '" + self.strcurdate.get() + "') and (year = '" \
                    + config.Year + "') and cancelled='N' order by code"
            elif self.regtype == "Purchase":
                # getting transactions of tax based on the pattern on that particular date
                s = "select distinct code from transaction where (BillNo like '" + code1 + "') and (code like '" \
                    + taxlst[i] + "') and (date = '" + self.strcurdate.get() + "') and (year = '" \
                    + config.Year + "') and cancelled='N' order by code"

            cur.execute(s)
            taxres = cur.fetchall()
            for res in taxres:
                # intializing product list with LCST if tax exists
                prodlst.append([res[0], 0, 0])
        """
        # getting tax info LSST based on the pattern on that particular date
        s = "select distinct code from transaction where (BillNo like '" + code1 + "' or BillNo like '" + code2 \
            + "') and (code like 'LSST') and (date = '" + self.curdate + "') and (year = '" \
            + config.Year + "') order by code"
        cur.execute(s)
        taxres = cur.fetchall()
        for res in taxres:
            # intializing product list with LSST if tax exists
            prodlst.append([res[0], 0, 0])

        # getting tax info LIST based on the pattern on that particular date
        s = "select distinct code from transaction where (BillNo like '" + code1 + "' or BillNo like '" + code2 \
            + "') and (code like 'LIST') and (date = '" + self.curdate + "') and (year = '" \
            + config.Year + "') order by code"
        cur.execute(s)
        taxres = cur.fetchall()
        for res in taxres:
            # intializing product list with LIST if tax exists
            prodlst.append([res[0], 0, 0])
        """
        # getting total no of product transacted on that day including tax
        totprod = len(prodlst)
        # total no of rows for the table that displays the summary of transaction
        totrow = 0
        if totprod == 0:
            #if no transaction are made for that day( no product info)
            if type == "Cash":
                s = "No Cash Transaction are made  on that day"
                self.cashlabel = tk.Label(self.cash_fra, text=s, bd=4)
                self.cashlabel.place(x=600, y=100)
            if type == "Credit":
                s = "No Credit Transaction are made  on that day"
                self.creditlabel = tk.Label(self.credit_fra, text=s, bd=4)
                self.creditlabel.place(x=600, y=100)

        else:
            if type == "Cash":
                if self.cashlabel:
                    self.cashlabel.destroy()
            if type == "Credit":
                if self.creditlabel:
                    self.creditlabel.destroy()
            for curprodno in range(0, totprod):
                # getting transactions for each item in the prodlst
                if self.regtype == "Sales":
                    # getting transactions of tax based on the pattern on that particular date
                    s = "select code, Quantity, Amount from Transaction where (BillNo like '" + code1 + "' or BillNo like '" \
                        + code2 + "') and (code = '" + prodlst[curprodno][0] + "') and (date = '" + self.strcurdate.get() \
                        + "') and (year = '" + config.Year + "') and cancelled='N' order by code"
                elif self.regtype == "Purchase":
                    # getting transactions of tax based on the pattern on that particular date
                    s = "select code, Quantity, Amount from Transaction where (BillNo like '" + code1 + "' ) and (code = '" \
                        + prodlst[curprodno][0] + "') and (date = '" + self.strcurdate.get() \
                        + "') and (year = '" + config.Year + "') and cancelled='N' order by code"

                #s = "Select code, Quantity, Amount from Transaction where code = '" + prodlst[curprodno][0] + "' and " \
                #    + "(BillNo like '" + code1 + "' or BillNo like '" + code2 + "') and year ='" + config.Year \
                #    + "' and Date = '" + self.curdate + "'"
                cur.execute(s)
                res = cur.fetchall()
                no = len(res)

                if no > totrow:
                    # if no of transaction for that product is more than the total row set for the summary table
                    for j in range(totrow, no):
                        ss = []
                        for k in range(0, totprod):
                            ss.append("")
                        translst.append(ss)
                    totrow = no

                totamt = 0
                totqty = 0
                for i in range(0, no):

                    if res[i][1]:
                        print("Hai")
                        s = "{:>3.2f}  {:>15.2f}".format(res[i][1], res[i][2])
                        totqty += res[i][1]
                    else:
                        s = "{:>3}  {:>15.2f}".format("", res[i][2])
                    translst[i][curprodno] = s
                    #totqty += res[i][1]
                    totamt += res[i][2]

                prodlst[curprodno][1] = totqty
                prodlst[curprodno][2] = totamt

            self.display_bill(type, totprod, prodlst)
            self.display_prod(type, translst, prodlst)

    def display_bill(self, type, totprod, prodlst):
        # opens the connection and fetches the records from AccDet table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = ""
        if type == "Cash":
            s = "select BillNo, Amount, EntryNo from transaction where (BillNo like 'CCH%' or BillNo like 'MCH%') " \
                + " and type = 'D'" + " and (date = '" + self.strcurdate.get() + "') and (year = '" + config.Year \
                + "') and cancelled='N' order by EntryNo"
        elif type == "Credit":
            s = "select BillNo, code, Amount, EntryNo  from transaction where (BillNo like 'CCR%' or BillNo like 'MCR%') and " \
                + "type = 'D' and (date = '" + self.strcurdate.get() + "') and (year = '" + config.Year \
                + "')  and cancelled='N' order by EntryNo"

        cur.execute(s)
        billres = cur.fetchall()
        totbill = len(billres)
        totrow = 0

        billlst = []
        prodno = []
        no = 0
        if totbill >= totprod:
            doubleflag = False
            totrow = totbill
        else:
            doubleflag = True
            diff = totprod - totbill
            if diff <= totbill:
                totrow = totbill
                prodno = [totbill, diff]
            else:
                no = totprod // 2
                if (totprod % 2) != 0:
                    no += 1
                totrow = no
                prodno = [no, totprod-no]

        for j in range(0, totrow):
            if doubleflag:
                if type == "Cash":
                    billlst.append(["", "", "", "", "", "", "", "", ""])
                elif type == "Credit":
                    billlst.append(["", "", "", "", "", "", "", "", "", ""])
            else:
                if type == "Cash":
                    billlst.append(["", "", "", "", "", ""])
                elif type == "Credit":
                    billlst.append(["", "", "", "", "", "", ""])

        totbillamt = 0
        col = 0
        for j in range(0, totbill):
            billlst[j][0] = billres[j][0]
            if type == "Cash":
                billlst[j][1] = str(billres[j][1]).format(":>15.2f")
                totbillamt += billres[j][1]
                col = 3
            elif type == "Credit":
                billlst[j][1] = billres[j][1]
                billlst[j][2] = str(billres[j][2]).format(":>15.2f")
                totbillamt += billres[j][2]
                col = 4

        k = 0
        totqty = [0, 0]
        totamt = [0, 0]
        for j in range(0, totprod):
            if j < totrow:
                billlst[k][col] = prodlst[j][0]
                billlst[k][col + 1] = str(prodlst[j][1]).format(":>3")
                billlst[k][col + 2] = str(prodlst[j][2]).format(":>15.2f")
                totqty[0] += prodlst[j][1]
                totamt[0] += prodlst[j][2]
                if j == (totrow-1):
                    k = -1
            else:
                billlst[k][col + 3] = prodlst[j][0]
                billlst[k][col + 4] = str(prodlst[j][1]).format(":>3")
                billlst[k][col + 5] = str(prodlst[j][2]).format(":>15.2f")
                totqty[1] += prodlst[j][1]
                totamt[1] += prodlst[j][2]

            k += 1
        if type == "Cash":
            fra = self.cash_fra
            self.prodflag[0] = doubleflag
        else:
            fra = self.credit_fra
            self.prodflag[1] = doubleflag
        # creating frame for the table
        table_fra = ttk.Frame(fra, width=3000, height=100)
        table_fra.place(x=20, y=10)

        # creating table using treeview
        tree = ttk.Treeview(table_fra, height=15)
        if type == "Cash" and not doubleflag:
            tree['columns'] = ["Bill", "Totamt", "", "Product", "Qty", "Amount"]
        elif type == "Cash" and doubleflag:
            tree['columns'] = ["Bill", "Totamt", "", "Product", "Qty", "Amount", "Product1", "Qty1", "Amount1"]
        elif type == "Credit" and not doubleflag:
            tree['columns'] = ["Bill", "Code", "Totamt", "", "Product", "Qty", "Amount"]
        elif type == "Credit" and doubleflag:
            tree['columns'] = ["Bill", "Code", "Totamt", "", "Product", "Qty", "Amount", "Product1", "Qty1", "Amount1"]
        tree.column("Bill", width=100, anchor=tk.W)
        tree.column("Totamt", width=200, anchor=tk.E)
        tree.column("Product", width=200, anchor=tk.CENTER)
        tree.column("Qty", width=100, anchor=tk.E)
        tree.column("Amount", width=200, anchor=tk.E)
        tree.column('#0', width=0, stretch=False)
        tree.column("", width=10, anchor=tk.E)

        if type == "Credit":
            tree.column("Code", width=100, anchor=tk.W)

        if doubleflag:
            tree.column("Product1", width=200, anchor=tk.CENTER)
            tree.column("Qty1", width=100, anchor=tk.E)
            tree.column("Amount1", width=200, anchor=tk.E)

        tree.heading("Bill", text="Bill No", anchor=tk.CENTER)
        tree.heading("Totamt", text="Total Amount", anchor=tk.CENTER)
        tree.heading("Product", text="Product Code", anchor=tk.CENTER)
        tree.heading("Qty", text="Quantity", anchor=tk.CENTER)
        tree.heading("Amount", text="Amount", anchor=tk.CENTER)
        tree.heading('#0', text='')
        tree.heading("", text="", anchor=tk.E)

        if type == "Credit":
            tree.heading("Code", text="Customer Code", anchor=tk.CENTER)

        if doubleflag:
            tree.heading("Product1", text="Product Code", anchor=tk.CENTER)
            tree.heading("Qty1", text="Quantity", anchor=tk.CENTER)
            tree.heading("Amount1", text="Amount", anchor=tk.CENTER)

        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=tree.yview)
        tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        tree.pack(expand=1)

        for j in range(0, totrow):
            tree.insert("", index=j, iid=str(j), values=billlst[j])

        tree.insert("", index=totrow, values=[""])
        ss = []
        if type == "Cash" and doubleflag:
            ss = ["", "{:>15.2f}".format(totbillamt), "", "", totqty[0], "{:>15.2f}".format(totamt[0]), "", totqty[1], "{:>15.2f}".format(totamt[1])]
        elif type == "Cash" and not doubleflag:
            ss = ["Total", "{:>15.2f}".format(totbillamt), "", "", totqty[0], "{:>15.2f}".format(totamt[0])]
        elif type == "Credit" and doubleflag:
            ss = ["", "", "{:>15.2f}".format(totbillamt), "", "", totqty[0], "{:>15.2f}".format(totamt[0]), "", totqty[1], "{:>15.2f}".format(totamt[1])]
        elif type == "Credit" and not doubleflag:
            ss = ["Total", "", "{:>15.2f}".format(totbillamt), "", "", totqty[0], "{:>15.2f}".format(totamt[0])]

        tree.insert("", index=totrow+1, iid=totrow + 1, values=ss)

        if doubleflag:
            qty = totqty[0] + totqty[1]
            amt = "{:>15.2f}".format(totamt[0] + totamt[1])
            if type == "Cash":
                ss = ["Total", totbillamt, "", "", "", "", "", qty, amt]
            else:
                ss = ["Total", "", totbillamt, "", "", "", "", "", qty, amt]
            tree.insert("", index=totrow+2, iid=totrow + 2, values=ss)

        if type == "Cash":
            self.cashsumtree = tree
            self.cashsumscroll = treescroll
        if type == "Credit":
            self.creditsumtree = tree
            self.creditsumscroll = treescroll

    def display_prod(self, type, translst, prodlst):
        totcol = 7
        totrow = len(translst)
        totprod = len(prodlst)

        if totprod < totcol:
            totcol = totprod
            colwidth = 200 + (totprod * 50)
        else:
            colwidth = 200

        if type == "Cash":
            fra = self.cash_fra
            yvalue = 400
            self.totalcol[0] = totcol
        else:
            fra = self.credit_fra
            yvalue = 450
            self.totalcol[1] = totcol

        # creating frame for the table
        table_fra = ttk.Frame(fra, width=3000, height=100)
        table_fra.place(x=20, y=350)

        # creating table using treeview
        tree = ttk.Treeview(table_fra, height=15)
        ss = []
        for i in range(0, totcol):
            ss.append(prodlst[i][0])

        tree['columns'] = ss

        tree.column('#0', width=0, stretch=False)
        for i in range(0, totcol):
            tree.column(prodlst[i][0], width=colwidth, anchor=tk.W)

        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=tree.yview)
        tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        tree.pack(expand=1)

        times = totprod // 7
        if (totprod % 7) != 0:
            times += 1

        currow = 1
        col = totcol
        for curtimes in range(0, times):
            row = 0
            c = 0
            stcol = curtimes * totcol
            for j in range(0, col):
                c = 0
                for k in range(0, totrow):
                    if translst[k][stcol+j] == "":
                        break
                    else:
                        c = k + 1
                if c > row:
                    row = c
            ss = []
            for i in range(0, col):
                ss.append(prodlst[stcol+i][0])
            for i in range(col, totcol):
                ss.append(" ")

            tree.insert("", index=currow, values=ss)
            ss.clear()
            for k in range(0, row):
                for j in range(0, col):
                    ss.append(translst[k][stcol+j])
                currow += 1
                for i in range(col, totcol):
                    ss.append(" ")
                tree.insert("", index=currow, values=ss)
                ss.clear()
            currow += 1
            for i in range(0, totcol):
                ss.append(" ")
            tree.insert("", index=currow, values=ss)
            ss.clear()
            currow += 1
            for i in range(0, col):
                s = "{:>3}  {:>15.2f}".format(prodlst[stcol+i][1], prodlst[stcol+i][2])
                ss.append(s)
            for i in range(col, totcol):
                ss.append(" ")

            tree.insert("", index=currow, values=ss)
            currow += 1
            ss.clear()
            for i in range(0, totcol):
                ss.append(" ")
            tree.insert("", index=currow, values=ss)
            currow += 1
            col = totprod - 7

        if type == "Cash":
            self.cashprodtree = tree
            self.cashprodscroll = treescroll
        if type == "Credit":
            self.creditprodtree = tree
            self.creditprodscroll = treescroll

    def set_navi(self):
        if not self.diffdate:
            self.first_bt.configure(state="disabled")
            self.prev_bt.configure(state="disabled")
            self.next_bt.configure(state="disabled")
            self.last_bt.configure(state="disabled")
        else:
            if self.curdate == self.stdate:
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.curdate == self.enddate:
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def move_first(self, _event=None):
        self.curdate = self.stdate
        self.strcurdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
        self.strdate.set(dt.strftime(dt.strptime(self.strcurdate.get(), "%Y-%m-%d"), "%d-%m-%Y"))
        self.set_navi()
        self.clear_table()
        self.display()

    def move_prev(self, _event=None):
        self.curdate = self.curdate - timedelta(days=1)
        self.strcurdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
        self.strdate.set(dt.strftime(dt.strptime(self.strcurdate.get(), "%Y-%m-%d"), "%d-%m-%Y"))
        self.set_navi()
        self.clear_table()
        self.display()

    def move_next(self, _event=None):
        self.curdate = self.curdate + timedelta(days=1)
        self.strcurdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
        self.strdate.set(dt.strftime(dt.strptime(self.strcurdate.get(), "%Y-%m-%d"), "%d-%m-%Y"))
        self.set_navi()
        self.clear_table()
        self.display()

    def move_last(self, _event=None):
        self.curdate = self.enddate
        self.strcurdate.set(dt.strftime(self.curdate, "%Y-%m-%d"))
        self.strdate.set(dt.strftime(dt.strptime(self.strcurdate.get(), "%Y-%m-%d"), "%d-%m-%Y"))
        self.set_navi()
        self.clear_table()
        self.display()

    def clear_table(self):
        # clears product table
        if self.cashsumtree:
            self.cashsumtree.destroy()
            self.cashsumscroll.destroy()
        if self.cashprodtree:
            self.cashprodtree.destroy()
            self.cashprodscroll.destroy()
        if self.creditsumtree:
            self.creditsumtree.destroy()
            self.creditsumscroll.destroy()
        if self.creditprodtree:
            self.creditprodtree.destroy()
            self.creditprodscroll.destroy()

    def print(self, _event=None):
        self.write_pdf()
        #win32api.ShellExecute(0, "print", "stock.pdf", None, ".", 0)

    def write_pdf(self):
        pdf = config.MyPDF("L", "mm", "A4")
        pdf.add_page()

        content = ""
        # adding Accouting year in line2


        # adding Accouting year in line2
        content = "Date: " + self.strdate.get()
        content = ('{:<73}'.format(content))
        if self.regtype == "Sales":
            content += "Sales Register"
        elif self.regtype == "Purchase":
            content += "Purchase Register"
        pdf.set_font("helvetica", size=16)
        pdf.cell(10, 8, txt=content, ln=1)

        s = ""
        if self.regtype == "Sales":
            s = "Sales"
        elif self.regtype == "Purchase":
            s = "Purchase"

        if self.cashsumtree:
            pdf.cell(0, 8, txt="Cash "+s, ln=1)
            self.write_bill("Cash", pdf)
            pdf.cell(0, 8, txt=" ", ln=1)
            self.write_prod("Cash", pdf)
            pdf.cell(0, 8, txt=" ", ln=1)
        if self.creditsumtree:
            pdf.cell(0, 8, txt="Credit " + s, ln=1)
            self.write_bill("Credit", pdf)
            pdf.cell(0, 8, txt=" ", ln=1)
            self.write_prod("Credit", pdf)

        pdf.output("Register.pdf")

    def write_bill(self, type, pdf):
        pdf.set_font("helvetica", size=12)
        # displaying table for daybook in pdf
        width = []
        align = []
        doubelflag= False
        if type == "Cash":
            if self.prodflag[0]:
                width = [15, 25, 5, 25, 25, 25, 25, 25, 25]
                align = ["LEFT", "RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT"]
            else:
                width = [15, 25, 5, 25, 25, 25]
                align = ["LEFT", "RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT"]

            tree = self.cashsumtree
            doubleflag = self.prodflag[0]
        elif type == "Credit":
            if self.prodflag[1]:
                width = [15, 20, 25, 5, 25, 25, 25, 25, 25, 25]
                align = ["LEFT", "LEFT", "RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT"]
            else:
                width = [15, 20, 25, 5, 25, 25, 25]
                align = ["LEFT", "LEFT", "RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT"]
            tree = self.creditsumtree
            doubleflag = self.prodflag[1]

        with pdf.table(col_widths=width, text_align=align, borders_layout="ALL") as table:
            headings = table.row()
            headings.cell("Bill No", align="C")
            if type == "Credit":
                headings.cell("Customer Code", align="C")
            headings.cell("Total Amount", align="C")
            headings.cell("", align="C")
            headings.cell("Product Code", align="C")
            headings.cell("Quantity", align="C")
            headings.cell("Amount", align="C")

            if doubleflag:
                headings.cell("Product Code ", align="C")
                headings.cell("Quantity", align="C")
                headings.cell("Amount", align="C")

            no = ""
            # displaying the contents of the table in the pdf from daybook table created
            for data_row in tree.get_children():
                value = tree.item(data_row)['values']
                if value[0] != "Total" and value[0] != "":
                    row = table.row()
                    for datum in value:
                        row.cell(datum)
                else:
                    #if value[1] == "Total":
                    no = data_row

        # displaying the total and balance of the table in the pdf from daybook table created
        with pdf.table(col_widths=width, text_align=align, borders_layout="NO_HORIZONTAL_LINES") as total:
            value = tree.item(no)['values']
            trow = total.row()
            for datum in value:
                trow.cell(datum)

    def write_prod(self, type, pdf):
        pdf.set_font("helvetica", size=12)
        # displaying table for daybook in pdf
        width = []
        align = []
        tree = None
        if type == "Cash":
            tree = self.cashprodtree
            for i in range(0, self.totalcol[0]):
                width.append(50)
                #tree = self.cashprodtree
                align.append("LEFT")
        elif type == "Credit":
            for i in range(0, self.totalcol[1]):
                width.append(50)
                tree = self.creditprodtree
                align.append("LEFT")

        with pdf.table(col_widths=width, text_align=align,
                      borders_layout="ALL") as table:
            headings = table.row()
            for i in range(0, self.totalcol[1]):
                val = "Product " + str(i)
                headings.cell(val, align="C")

            no = ""
            # displaying the contents of the table in the pdf from daybook table created
            for data_row in tree.get_children():
                value = tree.item(data_row)['values']
                if not value:
                    value = []
                    if type == "Cash":
                        for j in range(0, self.totalcol[0]):
                            value.append("")
                    if type == "Credit":
                        for j in range(0, self.totalcol[1]):
                            value.append("")

                row = table.row()
                for datum in value:
                    row.cell(datum)

    def close(self, _event=None):
        self.tab.destroy()

    def preparing_window(self, tab, type):
        self.regtype = type
        self.tab = tab

        reg_tab = ttk.Notebook(self.tab)
        reg_tab.place(x=10, y=100)

        cash_tab = ttk.Frame(reg_tab, width=1550, height=750)
        reg_tab.add(cash_tab, text="Cash     ")
        credit_tab = ttk.Frame(reg_tab, width=1550, height=750)
        reg_tab.add(credit_tab, text="Credit     ")

        # creating frame for fields
        self.cash_fra = ttk.Frame(cash_tab, width=1500, height=700)
        self.cash_fra.place(x=10, y=10)

        # creating frame for fields
        self.credit_fra = ttk.Frame(credit_tab, width=1500, height=700)
        self.credit_fra.place(x=10, y=10)

        # adding labels to cash and credit tabs to display messages
        # when no transactions are made for that day
        s = "No Cash Transaction are made  on that day"
        self.cashlabel = tk.Label(self.cash_fra, text=s, bd=4)
        s = "No Credit Transaction are made  on that day"
        self.creditlabel = tk.Label(self.credit_fra, text=s, bd=4)
        #self.creditlabel.pack(x=600, y=100)

        # adding Company name to Cash frame
        tk.Label(self.tab, text="SRI NARAYANA TRADING COMPANY", bd=4).place(x=570, y=1)

        s = "Sales Register for Accounting Year " + config.Year
        tk.Label(self.tab, text=s, bd=4).place(x=550, y=25)

        # adding Date controls to Cash frame
        tk.Label(self.tab, text="Date", bd=4).place(x=120, y=60)
        date_ent = tk.Entry(self.tab, textvariable=self.strdate)
        date_ent.place(x=180, y=60)
        date_ent.configure(state="disabled")

        # creating button to select date
        self.seldate_bt = tk.Button(self.tab, underline=0, text="Select Date", width=15, command=lambda: self.my_window())
        self.seldate_bt.place(x=370, y=60)
        config.Root.bind("<Control-s>", self.my_window)
        self.print_bt = tk.Button(self.tab, text="Print", underline=4, width=15, command=lambda: self.print())
        self.print_bt.place(x=500, y=60)
        config.Root.bind("<Control-t>", self.print)
        close_bt = tk.Button(self.tab, text="Close", underline=0, width=15, command=lambda: self.close())
        close_bt.place(x=620, y=60)
        config.Root.bind("<Control-o>", self.close)

        # creating Navigation buttons
        self.first_bt = tk.Button(self.tab, text="First", underline=0, width=6, command=lambda: self.move_first())
        self.first_bt.place(x=900, y=60)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(self.tab, text="Prev", underline=0, width=6, command=lambda: self.move_prev())
        self.prev_bt.place(x=950, y=60)
        config.Root.bind("<Control-p>", self.move_prev)
        self.next_bt = tk.Button(self.tab, text="Next", underline=0, width=6, command=lambda: self.move_next())
        self.next_bt.place(x=1000, y=60)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(self.tab, text="Last", underline=0, width=6, command=lambda: self.move_last())
        self.last_bt.place(x=1050, y=60)
        config.Root.bind("<Control-l>", self.move_last)

        self.my_window()

