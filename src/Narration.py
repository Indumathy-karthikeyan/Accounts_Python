import tkinter as tk
from tkinter import ttk
import mysql.connector as con
from tkinter import messagebox
import config


class Narration:

    def __init__(self):
        self.tab = None
        self.top = None
        self.rec = self.currec = self.totrec = None
        self.transflag = self.trans = None

        self.add_bt = self.mod_bt = self.del_bt = None
        self.save_bt = self.reset_bt = self.cancel_bt = None
        self.find_bt = self.close_bt = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None
        self.code_ent = self.desc_ent = self.find_code_ent = None

        self.code_tree = self.selcode_tree = None

        self.strcode = tk.StringVar()
        self.strdesc = tk.StringVar()
        self.strfindcode = tk.StringVar()

    def lock_controls(self, flag):
        # locks or unlocks editing controls
        self.code_ent.configure(state=flag)
        self.desc_ent.configure(state=flag)

    def fetch_rec(self, code):
        # opens the connection and fetches the records from AccDet table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = "select * from Narration order by code"
        cur.execute(s)
        self.rec = cur.fetchall()

        # clearing fields and table
        self.clear_fields()
        self.clear_table()

        if code == "":
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
                if self.rec[i][0] == code:
                    self.currec = i
            self.totrec = len(self.rec)
            # displaying current details
            self.display_fields()
            self.display_table()

    def display_table(self):
        # displaying all narration in the table
        i = 0
        if self.currec >= 0:
            lst = []
            for row in self.rec:
                lst.clear()
                lst = [row[0], row[1]]
                self.code_tree.insert(parent='', index=i, iid=i, text='', values=lst)
                i = i + 1
            self.code_tree.pack()

    def clear_fields(self):
        # clears the form controls
        self.strcode.set("")
        self.strdesc.set("")

    def clear_table(self):
        # clearing the table content
        for row in self.code_tree.get_children():
            self.code_tree.delete(row)

    def display_fields(self):
        # displaying current narration in the form fields
        if self.currec >= 0:
            self.strcode.set(self.rec[self.currec][0])
            self.strdesc.set(self.rec[self.currec][1])

    def enable_controls(self):
        # enabling or disbling trans controls
        if self.transflag:
            st1 = "disabled"
            st2 = "normal"
        else:
            st1 = "normal"
            st2 = "disabled"

        self.add_bt.configure(state=st1)
        self.close_bt.configure(state=st1)

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
        # diabling all navi buttons
        self.first_bt.configure(state="disabled")
        self.prev_bt.configure(state="disabled")
        self.next_bt.configure(state="disabled")
        self.last_bt.configure(state="disabled")

    def set_navi(self):
        # enabling or diabling navi buttons based on the position of current record
        if len(self.rec) == 0 or len(self.rec) == 1:
            # if no records or only one record
            self.disable_navi()
        else:
            if self.currec == 0:
                # if current record is the first one
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.currec == (self.totrec-1):
                # if current record is in the last one
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                # if current record is the middle one
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def move_first(self, _event=None):
        if (not self.transflag) and (self.currec != 0):
            # if not in trans mode and current record is not the first one
            self.currec = 0
            self.code_tree.selection_set(str(self.currec))
            self.set_navi()
            self.display_fields()

    def move_previous(self, _event=None):
        if (not self.transflag) and (self.currec != 0):
            # if not in trans mode and current record not the first one
            self.currec = self.currec - 1
            self.code_tree.selection_set(str(self.currec))
            self.set_navi()
            self.display_fields()

    def move_next(self, _event=None):
        if (not self.transflag) and (self.currec != (self.totrec-1)):
            # if not in trans mode and current record not the last one
            self.currec = self.currec + 1
            self.code_tree.selection_set(str(self.currec))
            self.set_navi()
            self.display_fields()

    def move_last(self, _event=None):
        if (not self.transflag) and (self.currec != (self.totrec - 1)):
            # if not in trans mode and current record not the last one
            self.currec = len(self.rec) - 1
            self.code_tree.selection_set(str(self.currec))
            self.set_navi()
            self.display_fields()

    def add(self, _event=None):
        # preparing for adding records
        if not self.transflag:
            # if not in trans mode
            self.transflag = True
            self.trans = "Add"
            self.trans_mode()
            self.code_ent.focus_set()

    def modify(self, _event=None):
        # preparing for modifying records
        if not self.transflag:
            # if not in trans mode
            self.transflag = True
            self.trans = "Mod"
            self.trans_mode()
            self.code_ent.configure(state="disabled")
            self.desc_ent.focus_set()

    def trans_mode(self):
        # preparing for transaction mode
        self.lock_controls("normal")
        self.code_tree.configure(selectmode="none")
        if self.trans == "Add":
            self.clear_fields()
        self.enable_controls()
        self.disable_navi()

    def reset(self, _event=None):
        # resetting the form controls
        if self.transflag:
            if self.trans == "Add":
                self.clear_fields()
                self.code_ent.focus_set()
            elif self.trans == "Mod":
                self.display_fields()
                self.desc_ent.focus_set()

    def check_fields(self):
        # validating form fields
        flag = True
        if self.strcode.get() == "":
            tk.messagebox.showinfo("", "Code cannot be blank")
            self.code_ent.focus_set()
            flag = False
        elif self.strdesc.get() == "":
            tk.messagebox.showinfo("", "Description cannot be blank")
            self.desc_ent.focus_set()
            flag = False

        return flag

    def save(self, _event=None):
        if self.transflag:
            # checking form fields
            if self.check_fields():
                # saving after form field validation
                # opens the connection to save the record in narration table
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()

                flag = True
                if self.trans == "Add":
                    # in case of addition checking if the narration already exists
                    if config.check_records("Narration", "Code", self.strcode.get()):
                        tk.messagebox.showinfo(config.Company_Name, "Narration code already exist")
                        self.code_ent.focus_set()
                        flag = False
                    else:
                        s = "insert into Narration values('" + self.strcode.get() + "','" + self.strdesc.get() + "')"
                        cur.execute(s)
                        myconn.commit()

                elif self.trans == "Mod":
                    s = "update Narration set Description='" + self.strdesc.get() + "' where Code='" \
                        + self.strcode.get() + "'"
                    cur.execute(s)
                    myconn.commit()

                if flag:
                    # enabling controls after saving the transaction
                    self.fetch_rec(self.strcode.get())
                    self.transflag = False
                    self.lock_controls("disabled")
                    self.enable_controls()
                    self.set_navi()
                    self.code_tree.configure(selectmode="browse")
                    self.code_tree.selection_set(self.currec)
                    self.add_bt.focus_set()

    def cancel(self, _event=None):
        if self.transflag:
            # enabling controls after cancelling the trasaction
            self.transflag = False
            self.lock_controls("disabled")
            self.enable_controls()
            self.set_navi()
            self.display_fields()
            self.clear_table()
            self.display_table()
            self.code_tree.configure(selectmode="browse")
            self.code_tree.selection_set(self.currec)
            self.add_bt.focus_set()

    def delete(self, _event=None):
        if not self.transflag:
            if tk.messagebox.askokcancel(title=None, message="Delete it?"):
                s = "Delete from Narration where Code='" + self.strcode.get() + "'"

                # opens the connection to delete narration
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()
                cur.execute(s)
                myconn.commit()
                if self.totrec == 1:
                    self.fetch_rec("")
                elif self.currec == (self.totrec - 1):
                    self.fetch_rec(self.rec[self.currec - 1][0])
                else:
                    self.fetch_rec(self.rec[self.currec + 1][0])

                # enabling controls after deletion
                self.code_tree.selection_set(self.currec)
                self.lock_controls("disabled")
                self.enable_controls()
                self.set_navi()

    def sel_ok(self, _event=None):
        index = self.selcode_tree.selection()
        if index == "":
            tk.messagebox.showinfo(config.Company_Name, "select an item")
        else:
            # displaying the product selected
            self.currec = int(index[0])
            self.code_tree.selection_set(self.currec)
            self.display_fields()
            self.set_navi()
            self.top.destroy()

    def find(self, _event=None):
        if not self.transflag:
            # creating a new window to list all the product for finding a particular one
            self.top = tk.Toplevel(config.Root)
            self.top.geometry("400x500")
            x = config.Root.winfo_x()
            y = config.Root.winfo_y()
            self.top.geometry("+%d+%d" % (x + 500, y + 150))
            self.top.wm_transient(config.Root)
            self.top.grab_set()

            tk.Label(self.top, text="Narration Code", bd=4).place(x=30, y=50)
            self.find_code_ent = tk.Entry(self.top, textvariable=self.strfindcode)
            self.find_code_ent.place(x=150, y=50)
            self.find_code_ent.bind('<KeyRelease>', lambda e: self.check_code("Find"))

            # creating table using treeview
            self.selcode_tree = ttk.Treeview(self.top, height=15, selectmode="browse")
            self.selcode_tree['columns'] = ('Code', 'Desc')
            self.selcode_tree.column('#0', width=0, stretch=False)
            self.selcode_tree.column('Code', width=50)
            self.selcode_tree.column('Desc', width=300)

            self.selcode_tree.heading('#0', text='')
            self.selcode_tree.heading('Code', text='Code')
            self.selcode_tree.heading('Desc', text='Description')
            treescroll = ttk.Scrollbar(self.top)
            treescroll.configure(command=self.selcode_tree.yview)
            self.selcode_tree.configure(yscrollcommand=treescroll.set)
            treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
            self.selcode_tree.place(x=30, y=100)

            tk.Button(self.top, text="OK", command=lambda: self.sel_ok()).place(x=150, y=450)
            tk.Button(self.top, text="Cancel", command=lambda: self.top.destroy()).place(x=200, y=450)

            s = "select code, description from Narration order by code"
            # opens the connection and fetches the records from Customer table
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()
            cur.execute(s)
            selrec = cur.fetchall()
            row = 0
            if len(selrec) > 0:
                for r in selrec:
                    self.selcode_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                    row += 1

            # setting focus to the code textbox
            self.strfindcode.set("")
            self.find_code_ent.focus()

    def close(self, _event=None):
        if not self.transflag:
            self.tab.destroy()

    def check_code(self, type):
        # checking product code
        # only 3 characters
        flag = True
        s = ""
        if type == "Main":
            # in case of code validation during addition
            s = self.strcode.get()
        elif type == "Find":
            # in case of code validation during find
            s = self.strfindcode.get()

        lt = len(s)
        for i in range(0, lt):
            # checking each character in the code
            if not (('A' <= s[i] <= 'Z') or ('a' <= s[i] <= 'z')):
                tk.messagebox.showinfo(config.Company_Name, "only Letters")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                flag = False
                break
        if len(s) > 3:
            tk.messagebox.showinfo(config.Company_Name, "only 3 letters")
            s = s[:3]
            flag = False

        if type == "Main":
            self.strcode.set(s)
        elif type == "Find":
            if flag:
                no = len(s)
                for row in self.selcode_tree.get_children():
                    val = self.selcode_tree.item(row, "values")
                    if val[0][:no] == s:
                        self.selcode_tree.selection_set(row)
                        break

            self.strfindcode.set(s)

    def selected(self):
        # selecting product
        item = self.code_tree.selection()
        if item[0] != self.currec:
            self.currec = int(item[0])
            self.clear_fields()
            self.display_fields()
            self.set_navi()

    def preparing_window(self, tab):
        # creating frame for Narration
        code_fra = ttk.LabelFrame(tab, width=1100, height=700)
        code_fra.place(x=20, y=20)
        self.tab = tab
        tab.focus_set()

        # creating frame for fields in Form view
        field_fra = ttk.LabelFrame(code_fra, width=1000, height=350)
        field_fra.place(x=20, y=20)

        # adding NarrCode controls to fieldframe
        tk.Label(field_fra, text="Narration Code", bd=4).place(x=30, y=100)
        self.strcode = tk.StringVar()
        self.code_ent = tk.Entry(field_fra, textvariable=self.strcode)
        self.code_ent.place(x=150, y=100)
        self.code_ent.bind('<KeyRelease>', lambda e: self.check_code("Main"))

        # adding Narrarion Desc controls to fieldframe
        tk.Label(field_fra, text="Description", bd=4).place(x=30, y=180)
        self.strdesc = tk.StringVar()
        self.desc_ent = tk.Entry(field_fra, width=80, textvariable=self.strdesc)
        self.desc_ent.place(x=150, y=180)

        # creating action frame with buttons
        action_fra = ttk.LabelFrame(field_fra, width=100, height=320)
        action_fra.place(x=800, y=5)

        # creating add,modify and delete buttons
        self.add_bt = tk.Button(action_fra, underline=0, text="Add", width=6, command=lambda: self.add())
        self.add_bt.place(x=20, y=10)
        config.Root.bind("<Control-a>", self.add)
        self.mod_bt = tk.Button(action_fra, underline=0, text="Modify", width=6, command=lambda: self.modify())
        self.mod_bt.place(x=20, y=40)
        config.Root.bind("<Control-m>", self.modify)
        self.del_bt = tk.Button(action_fra, underline=0, text="Delete", width=6, command=lambda: self.delete())
        self.del_bt.place(x=20, y=70)
        #config.Root.bind("<Control-d>", self.delete)

        # creating save,reset and cancel buttons
        self.save_bt = tk.Button(action_fra, underline=0, text="Save", width=6, command=lambda: self.save())
        self.save_bt.place(x=20, y=120)
        config.Root.bind("<Control-s>", self.save)
        self.reset_bt = tk.Button(action_fra, underline=0, text="Reset", width=6, command=lambda: self.reset())
        self.reset_bt.place(x=20, y=150)
        config.Root.bind("<Control-r>", self.reset)
        self.cancel_bt = tk.Button(action_fra, underline=0, text="Cancel", width=6, command=lambda: self.cancel())
        self.cancel_bt.place(x=20, y=180)
        config.Root.bind("<Control-c>", self.cancel)

        # creating find and close button
        self.find_bt = tk.Button(action_fra, underline=1, text="Find", width=6, command=lambda: self.find())
        self.find_bt.place(x=20, y=220)
        config.Root.bind("<Control-i>", self.find)
        self.close_bt = tk.Button(action_fra, underline=2, text="Close", width=6, command=lambda: self.close())
        self.close_bt.place(x=20, y=250)
        config.Root.bind("<Control-o>", self.close)

        # creating Navigation buttons
        self.first_bt = tk.Button(field_fra, underline=0,  text="First", width=6, command=lambda: self.move_first())
        self.first_bt.place(x=500, y=20)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(field_fra, underline=0, text="Prev", width=6, command=lambda: self.move_previous())
        self.prev_bt.place(x=550, y=20)
        config.Root.bind("<Control-p>", self.move_previous)
        self.next_bt = tk.Button(field_fra, underline=0, text="Next", width=6, command=lambda: self.move_next())
        self.next_bt.place(x=600, y=20)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(field_fra, underline=0, text="Last", width=6, command=lambda: self.move_last())
        self.last_bt.place(x=650, y=20)
        config.Root.bind("<Control-l>", self.move_last)

        # creating frame for the table
        table_fra = ttk.Frame(code_fra, width=900, height=100)
        table_fra.place(x=20, y=400)
        # creating table using treeview
        self.code_tree = ttk.Treeview(table_fra)
        self.code_tree['columns'] = ('NarrCode', 'Desc')
        self.code_tree.column('#0', width=0, stretch=False)
        self.code_tree.column('NarrCode', width=200)

        self.code_tree.heading('#0', text='')
        self.code_tree.heading('NarrCode', text='Narration Code')
        self.code_tree.heading('Desc', text='Description')

        self.code_tree.bind('<<TreeviewSelect>>', lambda e: self.selected())
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.code_tree.yview)
        self.code_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.code_tree.pack(expand=1)

        self.transflag = False
        self.trans = ""

        # fetching records from the Customer table
        self.fetch_rec("")

        self.lock_controls("disabled")
        self.enable_controls()
        self.set_navi()
