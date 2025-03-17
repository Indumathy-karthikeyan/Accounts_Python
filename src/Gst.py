import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector as con
import config
from calendar import month_name
# from datetime import datetime as dt


class Gst:

    def __init__(self):

        self.top = None
        self.cur = self.myconn = None
        self.rec = self.currec = self.totrec = None
        self.transflag = self.trans = None

        self.field_fra = None

        self.add_bt = self.mod_bt = self.del_bt = None
        self.save_bt = self.reset_bt = self.cancel_bt = None
        self.find_bt = self.close_bt = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None

        self.date_ent = self.igst_ent = self.cgst_ent = self.sgst_Ent = None
        self.gst_tree = self.selgst_tree = None

        self.strigst = tk.StringVar()
        self.strdate = tk.StringVar()
        self.prevdate = tk.StringVar()
        self.strcgst = tk.StringVar()
        self.strsgst = tk.StringVar()

    def lock_controls(self, flag):
        # locks or unlocks editing controls
        self.date_ent.configure(state=flag)
        self.igst_ent.configure(state=flag)
        self.cgst_ent.configure(state=flag)
        self.sgst_Ent.configure(state=flag)

    def fetch_rec(self, stdate):

        # opens the connection and fetches the records from Customer table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = "select * from Gst order by stdate"
        cur.execute(s)
        self.rec = cur.fetchall()

        # clearing fields and table
        self.clear_fields()
        self.clear_table()

        if stdate == "":
            if len(self.rec) > 0:
                # display first record
                self.currec = 0
                self.totrec = len(self.rec)
                self.display_fields()
                self.display_table()
            else:
                # in case of empty table no display
                self.currec = -1
                self.totrec = 0
        else:
            # setting current record to the code
            for i in range(0, len(self.rec)):
                if self.rec[i][0] == stdate:
                    self.currec = i
            self.totrec = len(self.rec)
            # displaying current details
            self.display_fields()
            self.display_table()

    def display_table(self):
        i = 0
        if self.currec >= 0:
            lst = []
            for row in self.rec:
                lst.clear()
                lst = [row[0],  row[1], row[2], row[3]]
                self.gst_tree.insert(parent='', index=i, iid=i, text='', values=lst)
                i = i + 1
            self.gst_tree.pack()

    def clear_table(self):
        for row in self.gst_tree.get_children():
            self.gst_tree.delete(row)

    def display_fields(self):
        if self.currec >= 0:
            self.strdate.set(self.rec[self.currec][0])
            self.strigst.set(self.rec[self.currec][1])
            self.strcgst.set(self.rec[self.currec][2])
            self.strsgst.set(self.rec[self.currec][3])
        else:
            self.clear_fields()

    def enable_controls(self):
        print(self.transflag)
        if self.transflag:
            print("hai")
            st1 = "disabled"
            st2 = "normal"
        else:
            st1 = "normal"
            st2 = "disabled"

        self.add_bt.configure(state=st1)

        self.save_bt.configure(state=st2)
        self.reset_bt.configure(state=st2)
        self.cancel_bt.configure(state=st2)

        if not self.transflag and len(self.rec) >= 1:
            self.mod_bt.configure(state="normal")
            self.del_bt.configure(state="normal")
        else:
            self.mod_bt.configure(state="disabled")
            self.del_bt.configure(state="disabled")
        if not self.transflag and len(self.rec) >= 2:
            self.find_bt.configure(state="normal")
        else:
            self.find_bt.configure(state="disabled")

    def disable_navi(self):
        self.first_bt.configure(state="disabled")
        self.prev_bt.configure(state="disabled")
        self.next_bt.configure(state="disabled")
        self.last_bt.configure(state="disabled")

    def set_navi(self):
        if len(self.rec) == 0 or len(self.rec) == 1:
            self.disable_navi()
        else:
            print(self.totrec)
            if self.currec == 0:
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.currec == self.totrec - 1:
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def move_first(self):
        self.currec = 0
        self.set_navi()
        self.display_fields()

    def move_previous(self):
        self.currec = self.currec - 1
        self.set_navi()
        self.display_fields()

    def move_next(self):
        self.currec = self.currec + 1
        self.set_navi()
        self.display_fields()

    def move_last(self):
        self.currec = self.totrec - 1
        self.set_navi()
        self.display_fields()

    def clear_fields(self):
        self.strdate.set("")
        self.strigst.set("")
        self.strcgst.set("")
        self.strsgst.set("")

    def seldate(self):
        day_fra = ttk.LabelFrame(self.field_fra, width=500, height=70)
        day_fra.place(x=120, y=80)
        tk.Label(day_fra, text="Day", bd=4).place(x=5, y=5)
        ed = tk.StringVar()
        day_Cb = ttk.Combobox(day_fra, width=10, textvariable=ed)
        day_Cb.place(x=40, y=5)
        day_Cb["values"] = [i for i in range(1, 32)]

        # adding End month
        tk.Label(day_fra, text="Month", bd=4).place(x=150, y=5)
        em = tk.StringVar()
        endmonth_Cb = ttk.Combobox(day_fra, width=20, textvariable=em)
        endmonth_Cb.place(x=200, y=5)
        endmonth_Cb["values"] = [month_name[m][0:3] for m in range(1, 13)]

        # adding end year
        tk.Label(day_fra, text="Year", bd=4).place(x=350, y=5)
        ey = tk.StringVar()
        endyear_Cb = ttk.Combobox(day_fra, width=10, textvariable=ey)
        endyear_Cb.place(x=400, y=5)
        endyear_Cb["values"] = [config.Year[0:4], config.Year[5:]]

    def add(self):
        self.transflag = True
        self.trans = "Add"
        self.trans_mode()
        self.seldate()

    def modify(self):
        self.transflag = True
        self.trans = "Mod"
        self.trans_mode()

    def trans_mode(self):
        self.lock_controls("normal")
        self.gst_tree.configure(selectmode="none")
        if self.trans == "Add":
            self.clear_fields()
        self.enable_controls()
        self.disable_navi()

    def reset(self):
        if self.trans == "Add":
            self.clear_fields()
        else:
            self.display_fields()

    def check_fields(self):
        flag = True
        if self.strdate.get() == "":
            tk.messagebox.showinfo("", "Start date cannot be blank")
            flag = False
            # self.date_ent.
        elif self.strigst.get() == "":
            tk.messagebox.showinfo("", "I.G.S.Tax cannot be blank")
            flag = False
        elif self.strcgst.get() == "":
            tk.messagebox.showinfo("", "C.G.S.Tax cannot be blank")
            flag = False
        elif self.strsgst.get() == "":
            tk.messagebox.showinfo("", "S.G.S.Tax cannot be blank")
            flag = False
        return flag

    def save(self):
        if self.check_fields():
            s = tk.StringVar()
            if self.trans == "Add":
                s = "insert into Customer values('" + self.strdate.get() + "','" + self.strigst.get() + "','" \
                    + self.strcgst.get() + "','" + self.strsgst.get() + "'"
            elif self.trans == "Mod":
                s = "update Customer set stdate='" + self.strdate.get() + "', IGST='" + self.strigst.get() \
                    + "',CGST ='" + self.strcgst.get() + "',SGST='" + self.strsgst.get() + "' where stdate='" \
                    + self.prevdate.get() + "'"

            # opens the connection and fetches the records from Customer table
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()

            cur.execute(s)
            myconn.commit()
            self.fetch_rec(self.strdate.get())
            self.transflag = False
            self.lock_controls("disabled")
            self.enable_controls()
            self.set_navi()
            self.gst_tree.configure(selectmode="browse")

    def cancel(self):
        self.transflag = False
        self.lock_controls("disabled")
        self.enable_controls()
        self.set_navi()
        self.display_fields()
        self.clear_table()
        self.display_table()
        self.gst_tree.configure(selectmode="browse")

    def delete(self):
        if tk.messagebox.askokcancel(title=None, message="Delete it?"):
            s = "Delete from Gst where stdate='" + self.strdate.get() + "'"

            # opens the connection and fetches the records from Customer table
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()
            cur.execute(s)
            myconn.commit()
            print("tot", self.totrec)
            if self.totrec == 1:
                self.fetch_rec("")
            elif self.currec == (self.totrec - 1):
                self.fetch_rec(self.rec[self.currec-1][0])
            else:
                self.fetch_rec(self.rec[self.currec+1][0])

            self.gst_tree.selection_set(self.currec)
            self.lock_controls("disabled")
            self.enable_controls()
            self.set_navi()

    def sel_ok(self):
        index = self.selgst_tree.focus()
        if index == "":
            tk.messagebox.showinfo("", "select an item")
        else:
            print("index", index)
            self.currec = int(index)
            self.display_fields()
            self.set_navi()
            self.top.destroy()

    def find(self):
        self.top = tk.Toplevel(config.root)
        self.top.geometry("500x500")
        x = config.root.winfo_x()
        y = config.root.winfo_y()
        self.top.geometry("+%d+%d" % (x + 500, y + 150))
        self.top.wm_transient(config.root)
        self.top.grab_set()

        # creating table using treeview
        self.selgst_tree = ttk.Treeview(self.top, height=20, selectmode="browse")
        self.selgst_tree['columns'] = 'Date'
        self.selgst_tree.column('#0', width=0, stretch=False)
        self.selgst_tree.column('Date', width=250)

        self.selgst_tree.heading('#0', text='')
        self.selgst_tree.heading('Date', text='Start date')
        self.selgst_tree.place(x=30, y=10)

        tk.Button(self.top, text="OK", command=lambda: self.sel_ok()).place(x=200, y=450)
        tk.Button(self.top, text="Cancel", command=lambda: self.top.destroy()).place(x=250, y=450)

        s = "select stdate from Gst order by stdate"
        # opens the connection and fetches the records from Customer table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        cur.execute(s)
        selrec = cur.fetchall()

        if len(selrec) > 0:
            for row in range(0, len(selrec)):
                self.selgst_tree.insert(parent='', iid=str(row), index=row, text="", values=(selrec[0]))

    def selected(self):
        if self.gst_tree.focus() != "":
            self.currec = int(self.gst_tree.focus())
            self.clear_fields()
            self.display_fields()
            self.set_navi()

    def preparing_window(self, tab):
        # creating frame for customer
        code_fra = ttk.LabelFrame(tab, width=1100, height=700)
        code_fra.place(x=20, y=20)
        # creating frame for fields in Form view
        self.field_fra = ttk.LabelFrame(code_fra, width=1000, height=350)
        self.field_fra.place(x=20, y=20)
        
        # adding AccCode controls to field frame
        tk.Label(self.field_fra, text="Start Date:", bd=4).place(x=30, y=100)
        self.date_ent = tk.Entry(self.field_fra, textvariable=self.strdate)
        self.date_ent.place(x=120, y=100)
        
        # adding IGS Tax controls to field frame
        tk.Label(self.field_fra, text="I.G.S.Tax", bd=4).place(x=30, y=200)
        self.igst_ent = tk.Entry(self.field_fra, textvariable=self.strigst)
        self.igst_ent.place(x=120, y=200)

        # adding CGS Tax controls to field frame
        tk.Label(self.field_fra, text="C.G.S.Tax", bd=4).place(x=270, y=200)
        self.cgst_ent = tk.Entry(self.field_fra, textvariable=self.strcgst)
        self.cgst_ent.place(x=340, y=200)

        # adding SGS Tax controls to field frame
        tk.Label(self.field_fra, text="S.G.S.Tax", bd=4).place(x=490, y=200)
        self.sgst_Ent = tk.Entry(self.field_fra, textvariable=self.strsgst)
        self.sgst_Ent.place(x=560, y=200)

        # creating action frame with buttons
        action_fra = ttk.LabelFrame(self.field_fra, width=100, height=320)
        action_fra.place(x=800, y=5)

        # creating add,modify and delete buttons
        self.add_bt = tk.Button(action_fra, text="Add", width=6, command=lambda: self.add())
        self.add_bt.place(x=20, y=10)
        self.mod_bt = tk.Button(action_fra, text="Modify", width=6, command=lambda: self.modify())
        self.mod_bt.place(x=20, y=40)
        self.del_bt = tk.Button(action_fra, text="Delete", width=6, command=lambda: self.delete())
        self.del_bt.place(x=20, y=70)

        # creating save,reset and cancel buttons
        self.save_bt = tk.Button(action_fra, text="Save", width=6, command=lambda: self.save())
        self.save_bt.place(x=20, y=120)
        self.reset_bt = tk.Button(action_fra, text="Reset", width=6, command=lambda: self.reset())
        self.reset_bt.place(x=20, y=150)
        self.cancel_bt = tk.Button(action_fra, text="Cancel", width=6, command=lambda: self.cancel())
        self.cancel_bt.place(x=20, y=180)

        # creating find and close button
        self.find_bt = tk.Button(action_fra, text="Find", width=6, command=lambda: self.find())
        self.find_bt.place(x=20, y=220)
        self.close_bt = tk.Button(action_fra, text="Close", width=6, command=lambda: tab.destroy())
        self.close_bt.place(x=20, y=250)

        # creating Navigation buttons
        self.first_bt = tk.Button(self.field_fra, text="<<", width=6, command=lambda: self.move_first())
        self.first_bt.place(x=500, y=20)
        self.prev_bt = tk.Button(self.field_fra, text="<", width=6, command=lambda: self.move_previous())
        self.prev_bt.place(x=550, y=20)
        self.next_bt = tk.Button(self.field_fra, text=">", width=6, command=lambda: self.move_next())
        self.next_bt.place(x=600, y=20)
        self.last_bt = tk.Button(self.field_fra, text=">>", width=6, command=lambda: self.move_last())
        self.last_bt.place(x=650, y=20)

        # creating frame for the table
        table_fra = ttk.Frame(code_fra, width=1500, height=800)
        table_fra.place(x=20, y=400)
        # creating table using treeview
        self.gst_tree = ttk.Treeview(table_fra, selectmode="browse")
        self.gst_tree['columns'] = ('Date', 'I.G.S.T', 'C.G.S.T', 'S.G.S.T')
        self.gst_tree.column('#0', width=0, stretch=False)
        self.gst_tree.column('Date', width=100)
        self.gst_tree.column('I.G.S.T', width=250)
        self.gst_tree.column('C.G.S.T', width=150, anchor=tk.E)
        self.gst_tree.column('S.G.S.T', width=150, anchor=tk.E)

        self.gst_tree.heading('#0', text='')
        self.gst_tree.heading('Date', text='Date')
        self.gst_tree.heading('I.G.S.T', text='I.G.S.Tax')
        self.gst_tree.heading('C.G.S.T', text='C.G.S.Tax')
        self.gst_tree.heading('S.G.S.T', text='S.G.S.Tax')

        self.gst_tree.bind('<<TreeviewSelect>>', lambda e: self.selected())
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.gst_tree.yview)
        self.gst_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.gst_tree.pack(expand=1)

        self.transflag = False
        self.trans = ""

        # fetching records from the Customer table
        self.fetch_rec("")

        self.lock_controls("disabled")
        self.enable_controls()
        self.set_navi()
