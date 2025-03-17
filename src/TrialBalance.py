import config
import tkinter as tk
from tkinter import ttk
from calendar import month_name
from datetime import timedelta
import mysql.connector as con


class TrialBalance:
    def __init__(self):
        self.row = None
        self.tree = None
        self.type = None
        self.dbamt = self.cramt = self.balamt = self.baltype = None

    def display_trialbalance(self):
        # opens the connection and fetches the records from AccDet table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        s = ""
        self.totdbamt = 0
        self.totcramt = 0

        balamt = 0

        if self.type == "A&L":
            s = "Select code,Description,openbal,baltype from customer where (code like 'A%' or code like 'L%')"\
                + " and Year = '" + config.Year + "' order by code"
        elif self.type == "Nominal":
            s = "Select code, Description, Qtytorec, ytopqty from product where (code like 'P%' or code like 'I%' or" \
                + " code like 'F%') and Year = '" + config.Year + "' order by code"

        cur.execute(s)
        res = cur.fetchall()
        print("len",len(res))
        for r in res:
            self.dbamt = 0
            self.cramt = 0
            self.qty = 0

            if self.type == "A&L":
                if r[3] == "C":
                    self.cramt += r[2]
                elif r[3] == "D":
                    self.dbamt += r[2]
            elif self.type == "Nominal":
                #s = "Select code, type, quantity, amount from transaction where code ='" + r[0] + "' and Year = '" \
                    #+ config.Year + "' and cancelled = 'N'"
                #col = 3
                if r[0][0] == "P":
                    self.qty += r[3]

            self.display(r, "Transaction")
            self.display(r, "Entries")

        if self.type == "Nominal":
            s = "Select code, Description from customer where code like 'E%' and Year = '" \
                + config.Year + "' order by code"

            cur.execute(s)
            res = cur.fetchall()
            # print(len(res))
            for r in res:
                self.dbamt = 0
                self.cramt = 0
                self.qty=0
                self.display(r, "Entries")

        print()
        print(self.totdbamt,self.totcramt)
        self.tree.insert("", index=self.row+1,
                         values=("", "", "", ""))
        self.tree.insert("", index=self.row+3,
                         values=("Total", "", "{:.2f}".format(self.totdbamt),"{:.2f}".format(self.totcramt)))
        if self.totdbamt > self.totcramt:
            balamt = self.totdbamt - self.totcramt
            self.tree.insert("", index=self.row+3, values=("Balance", "", "{:.2f}".format(balamt), ""))
        elif self.totdbamt < self.totcramt:
            balamt = self.totcramt - self.totdbamt
            self.tree.insert("", index=self.row+4, values=("Balance", "", "", "{:.2f}".format(balamt)))
        else:
            self.tree.insert("", index=self.row+4, values=("Nill Balance", "", "", ""))

    def display(self, r, tbname):
        # opens the connection and fetches the records from AccDet table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        s = ""
        #qty = 0.0
        #dbamt = 0.0
        #cramt = 0.0
        #bal = 0.0
        col = 0
        print(tbname)
        if tbname == "Transaction":
            if self.type == "A&L":
                s = "Select code, type, amount from transaction where code ='" + r[0] + "' and Year = '" + config.Year \
                    + "' and cancelled = 'N'"
                col = 2
            elif self.type == "Nominal":
                s = "Select code, type, quantity, amount from transaction where code ='" + r[0] + "' and Year = '" \
                    + config.Year + "' and cancelled = 'N'"
                col = 3
        elif tbname == "Entries":
            s = "Select code, type, quantity, amount from Entries where code ='" + r[0] + "' and Year = '" + config.Year + "'"
            col = 3

        cur.execute(s)
        res = cur.fetchall()
        #print(res)

        for curres in res:
            print("code",r[0])
            if self.type == "Nominal":
                if r[0][:1] == "P" or r[0][:1] == "I":
                    print(curres)
                    self.qty += curres[2]
            if curres[1] == "C":
                self.cramt += curres[col]
            elif curres[1] == "D":
                self.dbamt += curres[col]

        if tbname == "Entries":
            bal = 0
            print(r[0]," Qty", self.qty, self.dbamt, self.cramt)
            if self.dbamt > self.cramt:
                bal = self.dbamt - self.cramt
                self.totdbamt += bal
                lst = [r[1], self.qty,"{:.2f}".format(bal), ""]
            elif self.dbamt < self.cramt:
                bal = self.cramt - self.dbamt
                self.totcramt += bal
                lst = [r[1], self.qty, "", "{:.2f}".format(bal)]
            else:
                lst = [r[1], self.qty, "", ""]

            if self.dbamt != 0.0 or self.cramt != 0.0:
                #lst = [r[1], self.qty, self.dbamt, self.cramt]
                self.tree.insert("", index=self.row, values=lst)
                self.row += 1


    def preparing_window(self, tab, type):

        self.type = type
        # creating frame for fields
        field_fra = ttk.LabelFrame(tab, width=2000, height=800)
        field_fra.place(x=10, y=10)

        # adding Company name to frame
        tk.Label(field_fra, text="SRI NARAYANA TRADING COMPANY", bd=4).place(x=550, y=20)
        s = "TrialBalance for the Year " + config.Year
        tk.Label(field_fra, text=s, bd=4).place(x=550, y=50)

        # creating button to select date

        close_bt = tk.Button(field_fra, text="Close", width=15, command=lambda: tab.destroy())
        close_bt.place(x=1000, y=100)

        # creating frame for the table
        table_fra = ttk.Frame(field_fra, width=1500, height=2000)
        table_fra.place(x=100, y=150)

        # creating table using treeview
        self.tree = ttk.Treeview(table_fra,height=22)
        self.tree['columns'] = ('Name', 'Quantity', 'Debit', 'Credit')
        self.tree.column('#0', width=0, stretch=False)

        self.tree.column('Name', width=600)
        self.tree.column('Quantity', width=120, anchor=tk.E)
        self.tree.column('Debit', width=250, anchor=tk.E)
        self.tree.column('Credit', width=250, anchor=tk.E)

        self.tree.heading('#0', text='')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Quantity', text='Quantity')
        self.tree.heading('Debit', text='Amount Debit')
        self.tree.heading('Credit', text='Amount Credit')

        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.tree.pack(expand=1)

        self.row = 0

        self.display_trialbalance()

