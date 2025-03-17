import tkinter as tk
from tkinter import ttk
import mysql.connector as con
from tkinter import messagebox
from datetime import datetime as dt
import config


class Entries:

    def __init__(self):
        self.tab = None
        self.top = None
        self.rec = self.currec = self.totrec = None
        self.transflag = self.trans = self.type = None

        self.add_bt = self.mod_bt = self.del_bt = None
        self.save_bt = self.reset_bt = self.cancel_bt = None
        self.find_bt = self.close_bt = self.selcus_bt = self.selnarr_bt = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None

        self.no_ent = self.date_ent = self.code_ent = self.desc_ent = self.narr_ent = None
        self.typecr_rd = self.typedb_rd = self.qty_ent = self.amt_ent = self.data_ent = None

        self.entries_tree = self.selentries_tree = None

        self.strno = tk.StringVar()
        self.strdate = tk.StringVar()
        self.strprevdate = tk.StringVar()
        self.strcode = tk.StringVar()
        self.strdesc = tk.StringVar()
        self.strnarr = tk.StringVar()
        self.strtype = tk.StringVar()
        self.seltype = tk.StringVar()
        self.strqty = tk.StringVar()
        self.stramt = tk.StringVar()
        self.strdata = tk.StringVar()
        self.prevno = self.prevdate = None

    def lock_controls(self, flag):
        # locks or unlocks editing controls
        self.date_ent.configure(state=flag)
        self.code_ent.configure(state=flag)
        self.narr_ent.configure(state=flag)
        self.typedb_rd.configure(state=flag)
        self.typecr_rd.configure(state=flag)
        self.qty_ent.configure(state=flag)
        self.amt_ent.configure(state=flag)

    def enable_controls(self):
        # enabling or disabling transaction controls
        if self.transflag:
            st1 = "disabled"
            st2 = "normal"
        else:
            st1 = "normal"
            st2 = "disabled"

        # if in transaction mode enabling save,reset and cancel
        # disabling add, mod, delete, find and close
        # if in normal mode disabling sace,reset and cancel
        # enabling add,mod, delete,find and close
        self.add_bt.configure(state=st1)
        self.close_bt.configure(state=st1)

        self.save_bt.configure(state=st2)
        self.reset_bt.configure(state=st2)
        self.cancel_bt.configure(state=st2)

        if not self.transflag and self.totrec >= 1:
            # if not in trans mode and there are atleast one record
            self.mod_bt.configure(state="normal")
            self.del_bt.configure(state="normal")
        else:
            # if in trans mode or there are no record
            self.mod_bt.configure(state="disabled")
            self.del_bt.configure(state="disabled")

        if not self.transflag and self.totrec >= 2:
            # if not in trans mode and there are more than record
            self.find_bt.configure(state="normal")
        else:
            # if in trans mode and there are only one record or no records
            self.find_bt.configure(state="disabled")

        if self.transflag:
            # if in transmode enabling them so that customer or narration can be selected from the list
            self.selcus_bt.configure(state="normal")
            self.selnarr_bt.configure(state="normal")
        else:
            # if not in transmode disabling them
            self.selcus_bt.configure(state="disabled")
            self.selnarr_bt.configure(state="disabled")

    def disable_navi(self):
        # disabling all navi buttons
        self.first_bt.configure(state="disabled")
        self.prev_bt.configure(state="disabled")
        self.next_bt.configure(state="disabled")
        self.last_bt.configure(state="disabled")

    def set_navi(self):
        # enabling or disabling navi buttons
        if self.totrec == 0 or self.totrec == 1:
            # if only one record or no records
            # disabling navi buttons
            self.disable_navi()
        else:
            if self.currec == 0:
                # if first record is displayed
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.currec == (self.totrec - 1):
                # if last record is displayed
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                # if some middle record is displayed
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def move_first(self, _event=None):
        if (not self.transflag) and (self.totrec != 0) and (self.currec != 0):
            # if not in trans mode and current record is not the first one
            self.currec = 0
            self.entries_tree.selection_set(str(self.currec))
            self.set_navi()

    def move_previous(self, _event=None):
        if (not self.transflag) and (self.totrec != 0) and (self.currec != 0):
            # if not in trans mode and current record not the first one
            self.currec = self.currec - 1
            self.entries_tree.selection_set(str(self.currec))
            self.set_navi()

    def move_next(self, _event=None):
        if (not self.transflag) and (self.totrec != 0) and (self.currec != (self.totrec-1)):
            # if not in trans mode and current record not the last one
            self.currec = self.currec + 1
            self.entries_tree.selection_set(str(self.currec))
            self.set_navi()

    def move_last(self, _event=None):
        if (not self.transflag) and (self.totrec != 0) and (self.currec != (self.totrec - 1)):
            # if not in trans mode and current record not the last one
            self.currec = self.totrec - 1
            self.entries_tree.selection_set(str(self.currec))
            self.set_navi()

    def selected(self):
        # selecting product
        item = self.entries_tree.selection()
        if len(item) > 0:
            if item[0] != self.currec:
                self.currec = int(item[0])
                self.clear_fields()
                self.display_fields(self.currec)
                self.set_navi()

    def generate_entryno(self):
        # opens the connection to get the last entryno from the entries table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        if self.type == "Cash":
            s = "select EntryNo from Entries where Transtype='C' and year='" + config.Year + "' order by EntryNo"
        if self.type == "Journal":
            s = "select EntryNo from Entries where Transtype='J' and year='" + config.Year + "' order by EntryNo"
        cur.execute(s)
        res = cur.fetchall()

        no = 0
        if len(res) > 0:
            no = res[len(res) - 1][0]
        # generating new entryno (last one+1)
        no += 1
        self.prevno = no
        self.strno.set(str(no))

    def generate_date(self):
        if self.prevdate == "":
            # opens the connection to get the last entry date
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()
            s = ""
            if self.type == "Cash":
                s = "select Distinct Date from Entries where TransType = 'C' and year='" + config.Year + "' order by Date"
            elif self.type == "Journal":
                s = "select Distinct Date from Entries where TransType = 'J' and year='" + config.Year + "' order by Date"

            cur.execute(s)
            res = cur.fetchall()

            if len(res) > 0:
                curdate = res[len(res) - 1][0]
            else:
                st = "01-04-" + config.Year[0:4]
                curdate = dt.strptime(st, "%d-%m-%Y")

            self.prevdate = curdate.strftime("%d-%m-%Y")
        self.strdate.set(self.prevdate)

    def add(self, _event=None):
        # preparing for adding records
        if not self.transflag:
            # if not in trans mode
            self.transflag = True
            self.trans = "Add"
            self.trans_mode()
            self.generate_entryno()
            self.generate_date()
            self.date_ent.focus_set()

    def modify(self, _event=None):
        # preparing for modifying records
        if not self.transflag and (self.totrec != 0):
            # if not in trans mode
            self.transflag = True
            self.trans = "Mod"
            self.trans_mode()
            self.code_ent.configure(state="disabled")
            self.date_ent.focus_set()

    def trans_mode(self):
        # preparing for transaction mode
        self.lock_controls("normal")
        self.entries_tree.configure(selectmode="none")
        if self.trans == "Add":
            self.clear_fields()
        self.enable_controls()
        self.disable_navi()

    def reset(self, _event=None):
        # resetting the form controls
        if self.transflag:
            if self.trans == "Add":
                self.clear_fields()
                self.strno.set(self.prevno)
                self.strdate.set(self.prevdate)
            elif self.trans == "Mod":
                self.display_fields(self.currec)

            self.date_ent.focus_set()

    def get_desc(self, type):
        s = ""
        flag = False
        if type == "Details":
            if self.strcode.get() != "":
                code = self.strcode.get()
                c = code[:1]
                print(c)
                if c == "F" or c == "P":
                    s = "select Description from Product where Code='" + code + "' and year = '" + config.Year + "'"
                else:
                    s = "select Description from Customer where Code='" + code + "' and year = '" + config.Year + "'"
                flag = True
        elif type == "Narration":
            if self.strnarr.get() != "":
                s = "select Description from Narration where Code='" + self.strnarr.get() + "'"
                flag = True

        if flag:
            # opens the connection and fetches the records from Customer table
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()
            print(s)
            cur.execute(s)
            res = cur.fetchall()
            print(len(res))
            if len(res) > 0:
                if type == "Details":
                    self.strdesc.set(res[0][0])
                    self.narr_ent.focus_set()
                elif type == "Narration":
                    self.strnarr.set(res[0][0])
                    self.narr_ent.focus_set()
            else:
                if type == "Details":
                    tk.messagebox.showinfo(config.Company_Name, "No information about the Account verify it")
                    self.strdesc.set("")
                    self.code_ent.focus_set()
                elif type == "Narration":
                    tk.messagebox.showinfo(config.Company_Name, "No information about the Narration verify it")
                    self.narr_ent.focus_set()

    def get_det(self, type):
        self.seltype = type
        self.top = tk.Toplevel(config.Root)
        self.top.geometry("500x500")
        x = config.Root.winfo_x()
        y = config.Root.winfo_y()
        self.top.geometry("+%d+%d" % (x + 500, y + 150))
        self.top.wm_transient(config.Root)
        self.top.grab_set()

        # creating frame for the top window
        field_fra = ttk.Frame(self.top, width=500, height=700)
        field_fra.place(x=20, y=10)

        # creating table using treeview
        table_fra = ttk.Frame(field_fra, width=80, height=300)
        table_fra.place(x=20, y=50)
        self.selentries_tree = ttk.Treeview(table_fra, height=17, selectmode="browse")
        if self.seltype == "Details":
            tk.Label(self.top, text="Code", bd=4).place(x=30, y=5)
            self.data_ent = tk.Entry(self.top, textvariable=self.strdata)
            self.data_ent.place(x=150, y=5)
            self.data_ent.bind('<KeyRelease>', lambda e: self.check_code("Code", "Select"))

            self.selentries_tree['columns'] = ('Code', 'Desc')
            self.selentries_tree.column('Code', width=80)
            self.selentries_tree.column('Desc', width=250)
            self.selentries_tree.heading('Code', text='code')
            self.selentries_tree.heading('Desc', text='Description')

        elif self.seltype == "Narration":
            tk.Label(self.top, text="Product Code", bd=4).place(x=30, y=5)
            self.data_ent = tk.Entry(self.top, textvariable=self.strdata)
            self.data_ent.place(x=150, y=5)
            self.data_ent.bind('<KeyRelease>', lambda e: self.check_code("Narration", "Select"))

            self.selentries_tree['columns'] = ('Code', 'Desc')
            self.selentries_tree.column('Code', width=80)
            self.selentries_tree.column('Desc', width=250)
            self.selentries_tree.heading('Code', text='Narration code')
            self.selentries_tree.heading('Desc', text='Description')

        elif self.seltype == "Find":
            tk.Label(field_fra, text="Date", bd=4).place(x=30, y=10)
            self.data_ent = tk.Entry(field_fra, textvariable=self.strdata)
            self.data_ent.place(x=150, y=10)
            self.data_ent.bind('<KeyRelease>', self.check_date)

            self.selentries_tree['columns'] = ('EntryNo', 'Date', 'Code')
            self.selentries_tree.column('EntryNo', width=100)
            self.selentries_tree.column('Date', width=250)
            self.selentries_tree.column('Code', width=80)
            self.selentries_tree.heading('EntryNo', text='Entry No')
            self.selentries_tree.heading('Date', text='Date')
            self.selentries_tree.heading('Code', text='Code')

        self.selentries_tree.column('#0', width=0, stretch=False)
        self.selentries_tree.heading('#0', text='')
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.selentries_tree.yview)
        self.selentries_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.selentries_tree.pack(expand=1)

        tk.Button(self.top, text="OK", underline=0, command=lambda: self.sel_ok()).place(x=200, y=450)
        self.top.bind("<Alt-o>", self.sel_ok)
        tk.Button(self.top, text="Cancel", underline=0, command=lambda: self.sel_cancel()).place(x=250, y=450)
        self.top.bind("<Alt-c>", self.sel_cancel)

        # opens the connection and fetches the records from Customer table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = ""
        if self.seltype == "Find":
            if self.type == "Cash":
                s = "select EntryNo, Date, Code from Entries where TransType = 'C' and year='" + config.Year \
                    + "' order by EntryNo"
            elif self.type == "Journal":
                s = "select EntryNo, Date, Code from Entries where TransType = 'J' and year='" + config.Year \
                    + "' order by EntryNo"
            cur.execute(s)
            res = cur.fetchall()
            row = 0
            if len(res) > 0:
                for r in res:
                    self.selentries_tree.insert(parent='', iid=str(row), index=row, text="",
                                                values=(r[0], r[1].strftime("%d-%m-%Y"), r[2]))
                    row += 1

        elif self.seltype == "Details":
            s = "select Code, Description from Customer order by Code"
            cur.execute(s)
            res = cur.fetchall()
            row = 0
            if len(res) > 0:
                for r in res:
                    self.selentries_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                    row += 1

            s = "select Code, Description from product where code like 'F%' or code like 'P%' order by Code"
            cur.execute(s)
            res = cur.fetchall()
            if len(res) > 0:
                for r in res:
                    self.selentries_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                    row += 1

        elif self.seltype == "Narration":
            s = "select Code, Description from Narration order by Code"
            cur.execute(s)
            res = cur.fetchall()
            row = 0
            if len(res) > 0:
                for r in res:
                    self.selentries_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                    row += 1

        self.strdata.set("")
        self.selentries_tree.selection_set(str(0))
        self.selentries_tree.focus_set()

    def sel_ok(self, _event=None):
        index = self.selentries_tree.focus()
        if len(index) == 0:
            tk.messagebox.showinfo("", "select an item")
        else:
            val = self.selentries_tree.item(index, "values")
            if self.seltype == "Details":
                self.strcode.set(val[0])
                self.strdesc.set(val[1])
                self.code_ent.focus_set()
            elif self.seltype == "Find":
                for row in self.entries_tree.get_children():
                    value = self.entries_tree.item(row, "values")
                    # selecting the row in table containing the customer name entered
                    if val[0] == value[0]:
                        self.entries_tree.selection_set(row)
                        self.entries_tree.see(row)
                        self.entries_tree.focus(row)
                        break
                self.add_bt.focus_set()
            elif self.seltype == "Narration":
                self.strnarr.set(val[1])
                self.narr_ent.focus_set()

            self.top.destroy()

    def sel_cancel(self, _event=None):
        self.top.destroy()

    def check_narr(self, e):
        print(e.keysym)
        if e.keysym == "F2":
            self.strnarr.set(self.prevnarr)
        else:
            self.check_code("Narration", "Main")

    def check_amt(self, e):
        if e.keysym == "F2":
            self.stramt.set(self.prevamt)
        else:
            self.check_float("Amount")

    def check_code(self, data, type):
        # checking code or narration
        # only 4 characters for code and 2 for narration
        flag = True
        s = ""
        if data == "Code" and type == "Main":
            # in case of code validation during addition
            s = self.strcode.get()
            s = s.upper()
        elif data == "Code" and type == "Select":
            # in case of code validation during selection
            s = self.strdata.get()
            s = s.upper()
        if data == "Narration" and type == "Main":
            # in case of Narration validation during addition
            s = self.strnarr.get()
        elif data == "Narration" and type == "Select":
            # in case of Narration validation during selection
            s = self.strdata.get()

        lt = len(s)
        for i in range(0, lt):
            # checking each character in the code
            if data == "Code" and (not (('A' <= s[i] <= 'Z') or ('a' <= s[i] <= 'z'))):
                tk.messagebox.showinfo(config.Company_Name, "only Letters")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                flag = False
                break
            else:
                if data == "Code" and type == "Main":
                    # checking for first character in the code
                    if (i == 0) and (s[i] != 'A' and s[i] != 'L' and s[i] != 'E' and s[i] != 'F' and s[i] != 'P'):
                        tk.messagebox.showinfo(config.Company_Name, "First Letter should be A or L or E or F or P ")
                        s = ""
                        flag = False
                        break

        if flag:
            if data == "Code" and type == "Main" and len(s) > 4:
                tk.messagebox.showinfo(config.Company_Name, "only 4 letters")
                s = s[:4]
                flag = False
            #if data == "Narration" and type == "Select" and len(s) > 2:
                #tk.messagebox.showinfo(config.Company_Name, "only 2 letters")
                #s = s[:2]
                #flag = False

        if type == "Select":
            self.strdata.set(s)
            if flag:
                no = len(s)
                for row in self.selentries_tree.get_children():
                    val = self.selentries_tree.item(row, "values")
                    if val[1][:no] == s:
                        self.selentries_tree.selection_set(row)
                        self.selentries_tree.see(row)
                        self.selentries_tree.focus(row)
                        break

        elif data == "Code" and type == "Main":
            self.strcode.set(s)
            if len(s) != 4:
                self.strdesc.set("")
        elif data == "Narration" and type == "Main":
            self.strnarr.set(s)

    def check_float(self, type):
        # checking quantity, amount of the entries to be numbers and "."
        s = ""
        if type == "Quantity":
            s = self.strqty.get()
        elif type == "Amount":
            s = self.stramt.get()

        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                tk.messagebox.showinfo("", "only Numbers")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break

        if type == "Quantity":
            self.strqty.set(s)
            self.qty_ent.focus_set()
        elif type == "Amount":
            self.stramt.set(s)
            self.amt_ent.focus_set()
    """def check_amt(self):
        # checking amount
        # only numbers and "."
        s = self.stramt.get()
        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                tk.messagebox.showinfo(config.Company_Name, "only Numbers")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break
        self.stramt.set(s)
    """

    def check_date(self, e):
        if e.keysym != "BackSpace" and e.keysym != "Left" and e.keysym != "Right" and e.keysym != "Delete":
            self.strdata.set(config.enter_date(self.strdata.get()))
            self.data_ent.icursor(tk.END)
            s = self.strdata.get()
            no = len(s)
            if no >= 5:
                for row in self.selentries_tree.get_children():
                    val = self.selentries_tree.item(row, "values")
                    # selecting the row in table containing the customer name entered
                    if val[1][:no] == s:
                        self.selentries_tree.selection_set(row)
                        self.selentries_tree.see(row)
                        self.selentries_tree.focus(row)
                        break

    def settype(self,  type):
        print(type)
        self.strtype.set(type)
        ch = self.strcode.get()
        if len(ch) > 0:
            if ch[0] == "P":
                self.qty_ent.focus_set()
            else:
                self.amt_ent.focus_set()
    def check_fields(self):
        flag = False
        if self.strdate.get() == "":
            tk.messagebox.showinfo("", "Specify the Date")
            self.date_ent.focus_set()
        elif not config.validate_dt(self.strdate.get()):
            tk.messagebox.showinfo(config.Company_Name, "Invalid Date")
            self.date_ent.focus_set()
        elif self.strcode.get() == "":
            tk.messagebox.showinfo("", "Specify the Account Code")
            self.code_ent.focus_set()
        elif self.strtype.get() == "A":
            tk.messagebox.showinfo("", "Specify the type of Transaction")
            self.typecr_rd.focus_set()
        elif self.stramt.get() == "":
            tk.messagebox.showinfo("", "Specify the Amount")
            self.amt_ent.focus_set()
        else:
            flag = True

        return flag

    def save(self, _event=None):
        if self.transflag:
            if self.check_fields():
                strdate = dt.strftime(dt.strptime(self.strdate.get(), "%d-%m-%Y"), "%Y-%m-%d")
                flag = True
                # opens the connection and fetches the records from Customer table
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()

                if self.strqty.get() == "":
                    qty = 0
                else:
                    qty = self.strqty.get()

                print(qty)
                if self.trans == "Add":
                    transtype = ""
                    if self.type == "Cash":
                        transtype = "C"
                    elif self.type == "Journal":
                        transtype = "J"

                    """s = "select EntryNo from Entries where date = '" + strdate + "'  and code = '" \
                        + self.strcode.get() + "'"
                    cur.execute(s)
                    res = cur.fetchall()
                    if len(res) > 0:
                        if not tk.messagebox.askyesno(config.Company_Name,
                                        'Entries for that code on that day already exist. Do you want to continue? '):
                            flag = False

                    if flag:
                    """
                    s = ("insert into Entries values(" + self.strno.get() + ",'" + strdate + "','" \
                        + self.strcode.get() + "','" + self.strnarr.get() + "','" + self.strtype.get() + "','" \
                        + transtype + "',"  + str(qty) + "," + str(self.stramt.get()) \
                        + ",'" + config.Year + "')")
                    cur.execute(s)
                    myconn.commit()

                elif self.trans == "Mod":
                    print("Modify")
                    print(self.type)
                    if self.type == "Cash":
                        transtype = "C"
                    if self.type == "Journal":
                        transtype = "J"
                    print(transtype)
                    s = "update Entries set date='" + strdate + "', Code='" + self.strcode.get() + "', Narration='" \
                        + self.strnarr.get() + "', type='" + self.strtype.get() + "', amount= " + str(self.stramt.get()) \
                        + ", Quantity= " + str(qty) + " where EntryNo=" + str(self.strno.get()) + " and transtype ='" \
                        + transtype + "' and year='" + config.Year +"'"

                    cur.execute(s)
                    myconn.commit()

                if flag:
                    self.prevnarr = self.strnarr.get()
                    self.prevamt = self.stramt.get()
                    self.prevdate = self.strdate.get()
                    self.transflag = False
                    self.entries_tree.configure(selectmode="browse")
                    self.fetch_rec(self.strno.get())
                    self.lock_controls("disabled")
                    self.enable_controls()
                    self.set_navi()
                    self.add_bt.focus_set()
                    self.entries_tree.see(self.currec)

    def cancel(self, _event=None):
        if self.transflag:
            self.transflag = False
            self.lock_controls("disabled")
            self.enable_controls()
            self.set_navi()
            if self.totrec == 0:
                self.clear_fields()
            else:
                self.entries_tree.selection_set(str(self.currec))
            self.entries_tree.configure(selectmode="browse")
            self.add_bt.focus_set()

    def delete(self, _event=None):
        if not self.transflag and (self.totrec != 0):
            # getting confirmation from user before deleting
            if tk.messagebox.askokcancel(title=None, message="Delete it?"):
                s = "Delete from Entries where EntryNo = " + self.strno.get() + " and Year='" + config.Year + "'"

                # opens the connection to delete Customer
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()
                cur.execute(s)
                myconn.commit()
                if self.totrec == 1:
                    self.clear_table()
                    self.clear_fields()
                    self.totrec = 0
                else:
                    if self.currec == (self.totrec - 1):
                        val = self.entries_tree.item(self.currec - 1, "values")
                    else:
                        val = self.entries_tree.item(self.currec + 1, "values")

                    self.fetch_rec(val[0])

                # enabling controls after deletion
                self.lock_controls("disabled")
                self.enable_controls()
                self.set_navi()
                self.add_bt.focus_set()

    def find(self, _event=None):
        if not self.transflag and (self.totrec != 0):
            self.get_det("Find")
            self.add_bt.focus_set()

    def close(self, _event=None):
        if not self.transflag:
            self.tab.destroy()

    def clear_fields(self):
        self.strno.set("")
        self.strdate.set("")
        self.strcode.set("")
        self.strdesc.set("")
        self.strnarr.set("")
        self.stramt.set("")
        self.strqty.set("0.0")
        self.strtype.set("A")

    def clear_table(self):
        for row in self.entries_tree.get_children():
            self.entries_tree.delete(row)

    def display_fields(self, no):
        values = self.entries_tree.item(no, "values")
        self.strno.set(values[0])
        self.strdate.set(values[1])
        self.strcode.set(values[2])
        c = values[2][:1]
        s = ""
        if c == "A" or c == "L" or c == "E":
            s = "select Description from customer where code='" + values[2] + "' and year = '" \
                + config.Year + "'"
        elif c == "F" or c == "P":
            print("print product")
            s = "select Description from product where code='" + values[2] + "' and year = '" \
                + config.Year + "'"

        # opens the connection and fetches the records from Customer table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        cur.execute(s)
        res = cur.fetchall()
        if len(res) > 0:
            self.strdesc.set(res[0][0])
        else:
            tk.messagebox.showinfo("", "Description not found verify it")
            self.strdesc.set("")

        self.strnarr.set(values[3])
        if values[4] == 'C':
            self.typecr_rd.select()
            self.typedb_rd.deselect()
        elif values[4] == 'D':
            self.typedb_rd.select()
            self.typecr_rd.deselect()
        self.strqty.set(str(values[5]))
        #self.stramt.set("{:.2f}".format(values[6]))
        self.stramt.set(str(values[6]))

    def fetch_rec(self, no):

        # opens the connection and fetches the records from Entries table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = ""
        if self.type == "Cash":
            s = "select EntryNo, Date, Code, Narration, Type, Quantity, Amount from Entries where TransType = 'C' and year='" \
                + config.Year + "' order by Date, EntryNo"
        elif self.type == "Journal":
            s = "select EntryNo, Date, Code, Narration, Type, Quantity, Amount from Entries where TransType = 'J' and year='" \
                + config.Year + "' order by Date, EntryNo"
        cur.execute(s)
        rec = cur.fetchall()

        # clearing fields and table
        self.clear_fields()
        self.clear_table()

        self.totrec = len(rec)
        print("tot",self.totrec)
        if self.totrec > 0:
            # displaying all entries in the table
            i = 0
            self.currec = 0
            lst = []
            for row in rec:
                lst.clear()
                d = "{:.2f}".format(row[6])
                lst = [row[0], row[1].strftime("%d-%m-%Y"), row[2], row[3], row[4], row[5], d]
                self.entries_tree.insert(parent='', index=i, iid=i, text='', values=lst)
                i = i + 1
                self.prevnarr = row[3]
                self.prevamt = row[6]
                #self.prevdate = row[1].strftime("%d-%m-%Y")
            self.entries_tree.pack()
            print(self.prevdate)
            if no == 0:
                # display last entries
                self.currec = self.totrec - 1
            else:
                i = 0
                for row in rec:
                    if row[0] == int(no):
                        self.currec = i
                        break
                    i += 1

            self.entries_tree.selection_set(str(self.currec))
            self.entries_tree.see(self.currec)

        else:
            # in case of empty table no display
            self.currec = -1
            self.totrec = 0

    def preparing_window(self, tab, type):
        self.tab = tab
        self.type = type
        # creating frame for fields in Form view
        field_fra = ttk.LabelFrame(tab, width=1100, height=350)
        field_fra.place(x=20, y=20)

        # adding Entryno controls to field frame
        tk.Label(field_fra, text="Entry No. ", bd=4).place(x=20, y=20)
        self.no_ent = tk.Entry(field_fra, textvariable=self.strno)
        self.no_ent.place(x=100, y=20)

        # adding Date controls to field frame
        tk.Label(field_fra, text="Date ", bd=4).place(x=280, y=20)
        self.date_ent = tk.Entry(field_fra, textvariable=self.strdate)
        self.date_ent.place(x=370, y=20)

        # adding AccCode controls to field frame
        tk.Label(field_fra, text="Code", bd=4).place(x=20, y=70)
        self.code_ent = tk.Entry(field_fra, textvariable=self.strcode)
        self.code_ent.place(x=100, y=70)
        self.code_ent.bind('<KeyRelease>', lambda e: self.check_code("Code", "Main"))
        #self.code_ent.bind('<Return>', lambda e: self.get_desc("Details"))
        self.code_ent.bind('<FocusOut>', lambda e: self.get_desc("Details"))
        self.selcus_bt = tk.Button(field_fra, text="...", command=lambda: self.get_det("Details"))
        self.selcus_bt.place(x=230, y=70)

        # adding AccDesc controls to field frame
        tk.Label(field_fra, text="Description", bd=4).place(x=280, y=70)
        self.desc_ent = tk.Entry(field_fra, width=80, textvariable=self.strdesc)
        self.desc_ent.place(x=370, y=70)

        # adding Narration controls to field frame
        tk.Label(field_fra, text="Narration", bd=4).place(x=20, y=120)
        self.narr_ent = tk.Entry(field_fra, width=80, textvariable=self.strnarr)
        self.narr_ent.place(x=100, y=120)
        #self.narr_ent.bind('<KeyRelease>', lambda e: self.check_code("Narration", "Main"))
        self.narr_ent.bind('<KeyRelease>', self.check_narr)
        self.narr_ent.bind('<Return>', lambda e: self.get_desc("Narration"))
        self.selnarr_bt = tk.Button(field_fra, text="...", command=lambda: self.get_det("Narration"))
        self.selnarr_bt.place(x=600, y=120)

        # adding type radio controls to fieldframe
        type_fra = ttk.LabelFrame(field_fra, text="Type", width=200, height=80)
        type_fra.place(x=20, y=180)
        self.typedb_rd = tk.Radiobutton(type_fra, text="Debit", underline=0, variable=self.strtype, value="D")
        self.typedb_rd.place(x=10, y=10)
        config.Root.bind("<Alt-D>", lambda e: self.settype("D"))
        self.typecr_rd = tk.Radiobutton(type_fra, text="Credit", underline=0, variable=self.strtype, value='C')
        self.typecr_rd.place(x=100, y=10)
        config.Root.bind("<Alt-C>", lambda e: self.settype("C"))

        # adding Quantity controls to Product transaction frame
        tk.Label(field_fra, text="Quantity", bd=4).place(x=250, y=220)
        self.qty_ent = tk.Entry(field_fra, textvariable=self.strqty)
        self.qty_ent.place(x=350, y=220)
        self.qty_ent.bind('<KeyRelease>', lambda e: self.check_float("Quantity"))

        # adding Amount controls to Product transaction frame
        tk.Label(field_fra, text="Amount", bd=4).place(x=530, y=220)
        self.amt_ent = tk.Entry(field_fra, textvariable=self.stramt)
        self.amt_ent.place(x=600, y=220)
        self.amt_ent.bind('<KeyRelease>', self.check_amt)

        # creating action frame with buttons
        action_fra = ttk.LabelFrame(field_fra, width=100, height=300)
        action_fra.place(x=900, y=2)

        # creating add,modify and delete buttons
        self.add_bt = tk.Button(action_fra, underline=0, text="Add", width=6, command=lambda: self.add())
        self.add_bt.place(x=20, y=5)
        config.Root.bind("<Control-a>", self.add)
        self.mod_bt = tk.Button(action_fra, underline=0, text="Modify", width=6, command=lambda: self.modify())
        self.mod_bt.place(x=20, y=35)
        config.Root.bind("<Control-m>", self.modify)
        self.del_bt = tk.Button(action_fra, underline=0, text="Delete", width=6, command=lambda: self.delete())
        self.del_bt.place(x=20, y=65)
        #config.Root.bind("<Control-d>", self.delete)

        # creating save,reset and cancel buttons
        self.save_bt = tk.Button(action_fra, underline=0, text="Save", width=6, command=lambda: self.save())
        self.save_bt.place(x=20, y=105)
        config.Root.bind("<Control-s>", self.save)
        self.reset_bt = tk.Button(action_fra, underline=0, text="Reset", width=6, command=lambda: self.reset())
        self.reset_bt.place(x=20, y=135)
        config.Root.bind("<Control-r>", self.reset)
        self.cancel_bt = tk.Button(action_fra, underline=0, text="Cancel", width=6, command=lambda: self.cancel())
        self.cancel_bt.place(x=20, y=165)
        config.Root.bind("<Control-c>", self.cancel)

        # creating find and close button
        self.find_bt = tk.Button(action_fra, underline=1, text="Find", width=6, command=lambda: self.find())
        self.find_bt.place(x=20, y=205)
        config.Root.bind("<Control-i>", self.find)
        self.close_bt = tk.Button(action_fra, underline=2, text="Close", width=6, command=lambda: self.close())
        self.close_bt.place(x=20, y=235)
        config.Root.bind("<Control-o>", self.close)

        # creating Navigation buttons
        self.first_bt = tk.Button(field_fra, underline=0, text="First", width=6, command=lambda: self.move_first())
        self.first_bt.place(x=600, y=20)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(field_fra, underline=0, text="Prev", width=6, command=lambda: self.move_previous())
        self.prev_bt.place(x=650, y=20)
        config.Root.bind("<Control-p>", self.move_previous)
        self.next_bt = tk.Button(field_fra, underline=0, text="Next", width=6, command=lambda: self.move_next())
        self.next_bt.place(x=700, y=20)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(field_fra, underline=0, text="Last", width=6, command=lambda: self.move_last())
        self.last_bt.place(x=750, y=20)
        config.Root.bind("<Control-l>", self.move_last)

        # creating frame for the table
        table_fra = ttk.Frame(tab, width=900, height=100)
        table_fra.place(x=20, y=370)
        # creating table using treeview
        self.entries_tree = ttk.Treeview(table_fra,height=22)
        self.entries_tree['columns'] = ('EntryNo', 'Date', 'Code', 'Narr', 'Type', 'Qty', 'Amount')
        self.entries_tree.column('#0', width=0, stretch=False)
        self.entries_tree.column('EntryNo', width=100)
        self.entries_tree.column('Date', width=150)
        self.entries_tree.column('Code', width=150)
        # self.entries_tree.column('Desc', width=250)
        self.entries_tree.column('Narr', width=300)
        self.entries_tree.column('Type', width=100)
        self.entries_tree.column('Qty', width=100)
        self.entries_tree.column('Amount', width=200)

        self.entries_tree.heading('#0', text='')
        self.entries_tree.heading('EntryNo', text='Entry No.')
        self.entries_tree.heading('Date', text='Date')
        self.entries_tree.heading('Code', text=' Account Code')
        # self.entries_tree.heading('Desc', text='Description')
        self.entries_tree.heading('Narr', text='Narration')
        self.entries_tree.heading('Type', text='Type')
        self.entries_tree.heading('Qty', text='Quantity')
        self.entries_tree.heading('Amount', text='Amount')
        self.entries_tree.bind('<<TreeviewSelect>>', lambda e: self.selected())

        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.entries_tree.pack(expand=1)

        self.transflag = False
        self.trans = ""

        # fetching records from the Acccode table
        self.fetch_rec(0)

        if self.totrec >= 1:
            row = self.totrec - 1
            val = self.entries_tree.item(row, "values")
            self.prevdate = val[1]

        self.no_ent.configure(state="disabled")
        self.desc_ent.configure(state="disabled")
        self.lock_controls("disabled")
        self.enable_controls()
        self.set_navi()
