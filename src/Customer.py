import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector as con
import config


class Customer:

    def __init__(self):
        self.tab = None
        self.top = None
        self.rec = self.currec = self.totrec = None
        self.transflag = self.trans = None

        self.add_bt = self.mod_bt = self.del_bt = None
        self.save_bt = self.reset_bt = self.cancel_bt = None
        self.find_bt = self.close_bt = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None

        self.code_ent = self.desc_ent = self.phone_ent = self.gstno_ent = self.openbal_ent = None
        self.baltypecr_rd = self.baltypedb_rd = self.balyes_rd = self.balno_rd = None
        self.find_desc_ent = None
        self.code_tree = self.selcode_tree = None

        self.strcode = tk.StringVar()
        self.strdesc = tk.StringVar()
        self.strprevcode = tk.StringVar()
        self.strgstno = tk.StringVar()
        self.strphone = tk.StringVar()
        self.strbal = tk.StringVar()
        self.strbaltype = tk.StringVar()
        self.stropenbal = tk.StringVar()
        self.strfinddesc = tk.StringVar()

    def lock_controls(self, flag):
        # locks or unlocks editing controls
        self.code_ent.configure(state=flag)
        self.desc_ent.configure(state=flag)
        self.phone_ent.configure(state=flag)
        self.gstno_ent.configure(state=flag)
        self.balyes_rd.configure(state=flag)
        self.balno_rd.configure(state=flag)
        if self.trans == "Mod" and self.strbal.get() == "Y":
            self.openbal_ent.configure(state="normal")
            self.baltypedb_rd.configure(state="normal")
            self.baltypecr_rd.configure(state="normal")
        else:
            self.openbal_ent.configure(state="disabled")
            self.baltypedb_rd.configure(state="disabled")
            self.baltypecr_rd.configure(state="disabled")

    def fetch_rec(self, code):

        # opens the connection and fetches the records from Customer table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = "select * from Customer where year='" + config.Year + "' order by Description"
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
        # displaying all product in the table
        i = 0
        dbamt = 0
        cramt = 0
        if self.currec >= 0:
            lst = []
            # calculating the total credits and debits of all customer
            for row in self.rec:
                lst.clear()
                if row[5] == "D":
                    lst = [row[0], row[1], row[2], row[3], "{:.2f}".format(row[4]), ""]
                    dbamt += row[4]
                elif row[5] == "C":
                    lst = [row[0], row[1], row[2], row[3], "", "{:.2f}".format(row[4])]
                    cramt += row[4]
                else:
                    lst = [row[0], row[1], row[2], row[3], "", ""]
                self.code_tree.insert(parent='', index=i, iid=i, text='', values=lst)
                i = i + 1

            # displaying the total credit and debits and balance
            lst = ["", "Total", "", "", dbamt, cramt]
            self.code_tree.insert(parent='', index=i, iid=i, text='', values=lst)
            if dbamt > cramt:
                lst = ["", "Balance", "", "", "{:.2f}".format(dbamt - cramt), ""]
            elif dbamt < cramt:
                lst = ["", "Balance", "", "", "", "{:.2f}".format(cramt - dbamt)]
            else:
                lst = ["", "Balance (Nill)", "", "", "", ""]
            i += 1
            self.code_tree.insert(parent='', index=i, iid=i, text='', values=lst)
        self.code_tree.pack()
        self.code_tree.selection_set(self.currec)
        self.code_tree.see(self.currec)

    def clear_table(self):
        # clearing the table content
        for row in self.code_tree.get_children():
            self.code_tree.delete(row)

    def display_fields(self):
        # displaying current customer in the form fields
        if self.currec >= 0:
            self.strcode.set(self.rec[self.currec][0])
            self.strdesc.set(self.rec[self.currec][1])
            self.strphone.set(self.rec[self.currec][2])
            self.strgstno.set(self.rec[self.currec][3])
            if self.rec[self.currec][4] != 0:
                self.stropenbal.set(self.rec[self.currec][4])

            if self.rec[self.currec][5] == 'C':
                self.strbaltype.set("C")
                self.strbal.set("Y")
            elif self.rec[self.currec][5] == 'D':
                self.strbaltype.set("D")
                self.strbal.set("Y")
            else:
                self.strbaltype.set("A")
                self.strbal.set("N")
        else:
            # clearing the fields in case of no records in table
            self.clear_fields()

    def enable_controls(self):
        # enabling or disbling trans controls
        if self.transflag:
            # in trans mode
            st1 = "disabled"
            st2 = "normal"
        else:
            # in non trans mode
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
            elif self.currec == self.totrec - 1:
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

    """def check_transaction(self, code, desc):
        # opens the connection and fetches the records from Customer table
        myconn = con.connect(user='root', password='vellore6', host='127.0.0.1', database='Accounts')
        cur = myconn.cursor()

        s = "Select * from transaction where code like  '" + code + "%' or code like '" + desc + "%'"
        cur.execute(s)
        res = cur.fetchall()
        if len(res) > 0:
            flag = True
        else:
            flag = False

        return flag
    """

    def move_first(self, _event=None):
        if (not self.transflag) and (self.currec != 0):
            # if not in trans mode and current record not the first one
            self.currec = 0
            self.code_tree.selection_set(self.currec)
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
        if (not self.transflag) and (self.currec != (self.totrec - 1)):
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

    def clear_fields(self):
        # clears the form controls
        self.strcode.set("")
        self.strdesc.set("")
        self.strphone.set("")
        self.strgstno.set("")
        self.strbal.set("A")
        self.stropenbal.set("")
        self.strbaltype.set("A")

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
        if not self.transflag and self.totrec != 0:
            # if not in trans mode and there are records in the table
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
                # clearing fields in case of add mode
                self.clear_fields()
                self.code_ent.focus_set()
            elif self.trans == "Mod":
                # displaying original content in case of modify mode
                self.display_fields()
                self.desc_ent.focus_set()

    def check_fields(self):
        # validating form fields
        flag = True
        if self.strcode.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Code cannot be blank")
            self.code_ent.focus_set()
            flag = False
        elif self.strdesc.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Description cannot be blank")
            self.desc_ent.focus_set()
            flag = False
        elif self.strbal.get() != "Y" and self.strbal.get() != "N":
            tk.messagebox.showinfo(config.Company_Name, "specify opening balance required are not")
            self.balyes_rd.focus_set()
            flag = False
        elif self.strbal.get() == "Y" and self.strbaltype.get() != "D" and self.strbaltype.get() != "C":
            tk.messagebox.showinfo(config.Company_Name, "specify opening balance type")
            self.baltypedb_rd.focus_set()
            flag = False
        elif self.strbaltype.get() == "C" or self.strbaltype.get() == "D":
            if str(self.stropenbal.get()) == "":
                tk.messagebox.showinfo(config.Company_Name, "opening balance cannot be blank")
                self.openbal_ent.focus_set()
                flag = False
            elif not config.is_float(self.stropenbal.get()):
                tk.messagebox.showinfo(config.Company_Name, " Invalid opening balance")
                self.openbal_ent.focus_set()
                flag = False
        return flag

    def save(self, _event=None):
        if self.transflag:
            # checking form fields
            if self.check_fields():
                # saving after form field validation
                if self.strbaltype.get() == "C":
                    baltype = "C"
                    bal = "{:.2f}".format(float(self.stropenbal.get()))
                elif self.strbaltype.get() == "D":
                    baltype = "D"
                    bal = "{:.2f}".format(float(self.stropenbal.get()))
                else:
                    baltype = ""
                    bal = 0

                # opens the connection and fetches the records from Customer table
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()

                flag = True
                if self.trans == "Add":
                    # in case of addition checking if the customer already exists
                    if config.check_records("Customer", "Code", self.strcode.get()):
                        tk.messagebox.showinfo(config.Company_Name, "Customer code already exist")
                        flag = False
                    else:
                        # in case of valid new customer add the details to customer table
                        s = "insert into Customer values('" + self.strcode.get() + "','" + self.strdesc.get() + "','" \
                            + self.strphone.get() + "','" + self.strgstno.get() + "'," + str(bal) + ",'" \
                            + baltype + "','" + config.Year + "')"
                        cur.execute(s)
                        myconn.commit()
                elif self.trans == "Mod":
                    # in case modify update the given details to the customer table
                    s = "update Customer set Code='" + self.strcode.get() + "', Description='" + self.strdesc.get() \
                        + "',PhoneNo ='" + self.strphone.get() + "',GstNo='" + self.strgstno.get() + "',OpenBal=" \
                        + str(bal) + ", BalType='" + baltype + "' where Code='" \
                        + self.strcode.get() + "' and Year='" + config.Year + "'"
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
            # checking if transaction for the customer exists
            if config.check_records("Transaction", "Code", self.strcode.get()):
                tk.messagebox.showinfo(config.Company_Name, "Transaction for the code exist, so cannot delete it")
            elif config.check_records("Entries", "code", self.strcode.get()):
                tk.messagebox.showinfo(config.Company_Name, "Transaction for the code exist, so cannot delete it")
            else:
                if tk.messagebox.askokcancel(title=None, message="Delete it?"):
                    # deleting
                    s = "Delete from Customer where Code='" + self.strcode.get() + "' and Year='" + config.Year + "'"
                    # deleting customer details after getting confirmation
                    # opens the connection to delete customer from Customer table
                    myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                    cur = myconn.cursor()
                    cur.execute(s)
                    myconn.commit()

                    if self.totrec == 1:
                        # if only one customer that is deleted
                        # display empty fields
                        self.fetch_rec("")
                    elif self.currec == (self.totrec - 1):
                        # if last customer was deleted displaying the previous one
                        self.fetch_rec(self.rec[self.currec - 1][0])
                    else:
                        # displaying the next customer details
                        self.fetch_rec(self.rec[self.currec + 1][0])

                # enabling controls after deletion
                self.code_tree.selection_set(self.currec)
                self.lock_controls("disabled")
                self.enable_controls()
                self.set_navi()

    def sel_ok(self, _event=None):
        # displaying the details of the customer found out
        index = self.selcode_tree.selection()
        if index == "":
            tk.messagebox.showinfo(config.Company_Name, "select an item")
        else:
            # displaying the product selected
            self.currec = int(index[0])
            self.code_tree.selection_set(self.currec)
            self.code_tree.see(self.currec)
            self.display_fields()
            self.set_navi()
            self.top.destroy()

    def sel_cancel(self, _event=None):
        self.top.destroy()

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

            # opens the connection and fetches the records from Customer table
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()
            s = "select code, description from customer where Year = '" + config.Year + "' order by Description"
            cur.execute(s)
            selrec = cur.fetchall()
            row = 0
            if len(selrec) > 0:
                # displaying list of customer in table
                for r in selrec:
                    self.selcode_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                    row += 1

            # setting focus to the code textbox
            self.strfinddesc.set("")
            self.find_desc_ent.focus()

    def close(self, _event=None):
        if not self.transflag:
            self.tab.destroy()

    def sel_openbal(self):
        # enabling ytopqty only if qtytorec is "Y"
        if self.strbal.get() == "Y":
            self.stropenbal.set("")
            self.baltypedb_rd.configure(state="normal")
            self.baltypecr_rd.configure(state="normal")
            self.openbal_ent.configure(state="normal")
            self.baltypedb_rd.focus_set()
        elif self.strbal.get() == "N":
            self.stropenbal.set("")
            self.strbaltype.set("A")
            self.baltypedb_rd.configure(state="disabled")
            self.baltypecr_rd.configure(state="disabled")
            self.openbal_ent.configure(state="disabled")

    def check_description(self):
        s = self.strdesc.get()
        lt = len(s)
        if lt == 1:
            s = s.upper()
            self.strdesc.set(s)
    def check_code(self):
        # checking customer code
        # only 4 characters
        # first letter must be A or L or E
        s = self.strcode.get()
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
                if (i == 0) and (s[i] != 'A' and s[i] != 'L' and s[i] != 'E'):
                    tk.messagebox.showinfo(config.Company_Name, "First Letter should be A or L or E ")
                    s = ""
                    break

        if len(s) > 4:
            tk.messagebox.showinfo(config.Company_Name, "only 4 letters")
            s = s[:4]

        self.strcode.set(s)

    def check_desc(self):
        # matching product description with the list of customers
        s = self.strfinddesc.get()
        no = len(s)
        print(s)
        for row in self.selcode_tree.get_children():
            print("Hai")
            val = self.selcode_tree.item(row, "values")
            print(val)
            if val[1][:no].upper() == s.upper():
                print("Found")
                self.selcode_tree.selection_set(row)
                self.selcode_tree.see(row)
                break

        self.strfinddesc.set(s)

    def check_phoneno(self):
        # checking phone number
        s = self.strphone.get()
        lt = len(s) - 1
        for i in range(0, lt):
            # checking for only numbers or "-" or " "
            if not ((str(0) <= s[lt] <= str(9)) or s[lt] == "-" or s[lt] == " "):
                tk.messagebox.showinfo(config.Company_Name, "only Numbers")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break
        self.strphone.set(s)

    def check_gstno(self):
        # checking gstno
        # only numbers
        s = self.strgstno.get()
        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or ('A' <= s[i] <= 'Z') or ('a' <= s[i] <= 'z') or s[i] == " "):
                tk.messagebox.showinfo(config.Company_Name, "only Numbers an letters")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break
        self.strgstno.set(s)

    def check_openbal(self):
        # checking open balance
        # only numbers or "."
        s = self.stropenbal.get()
        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                tk.messagebox.showinfo(config.Company_Name, "only Numbers")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break

        self.stropenbal.set(s)

    def selected(self):
        # displaying the details of the selected customer
        item = self.code_tree.selection()
        if item[0] != self.currec:
            self.currec = int(item[0])
            self.clear_fields()
            self.display_fields()
            self.set_navi()

    def preparing_window(self, tab):
        # creating frame for customer
        code_fra = ttk.LabelFrame(tab, width=1100, height=1100)
        code_fra.place(x=20, y=20)
        self.tab = tab
        tab.focus_set()

        # creating frame for fields in Form view
        field_fra = ttk.LabelFrame(code_fra, width=1000, height=350)
        field_fra.place(x=20, y=20)

        # adding Customer Code controls to field frame
        tk.Label(field_fra, text="AccCode", bd=4).place(x=30, y=50)
        self.code_ent = tk.Entry(field_fra, textvariable=self.strcode)
        self.code_ent.place(x=120, y=50)
        self.code_ent.bind('<KeyRelease>', lambda e: self.check_code())

        # adding Customer Description controls to field frame
        tk.Label(field_fra, text="Description", bd=4).place(x=30, y=100)
        self.desc_ent = tk.Entry(field_fra, width=80, textvariable=self.strdesc)
        self.desc_ent.place(x=120, y=100)
        self.desc_ent.bind('<KeyRelease>', lambda e: self.check_description())

        # adding Phone No controls to field frame
        tk.Label(field_fra, text="Phone No", bd=4).place(x=30, y=150)
        self.phone_ent = tk.Entry(field_fra, width=25, textvariable=self.strphone)
        self.phone_ent.place(x=120, y=150)
        self.phone_ent.bind('<KeyRelease>', lambda e: self.check_phoneno())

        # adding Gst No controls to field frame
        tk.Label(field_fra, text="Gst No", bd=4).place(x=300, y=150)
        self.gstno_ent = tk.Entry(field_fra, width=40, textvariable=self.strgstno)
        self.gstno_ent.place(x=380, y=150)
        self.gstno_ent.bind('<KeyRelease>', lambda e: self.check_gstno())

        # adding open balance radio controls to field frame
        bal_fra = ttk.LabelFrame(field_fra, text="Open Balance", width=180, height=70)
        bal_fra.place(x=30, y=220)
        self.balyes_rd = tk.Radiobutton(bal_fra, text="Yes", variable=self.strbal, value="Y",
                                        command=self.sel_openbal)
        self.balyes_rd.place(x=10, y=10)
        self.balno_rd = tk.Radiobutton(bal_fra, text="No", variable=self.strbal, value="N",
                                       command=self.sel_openbal)
        self.balno_rd.place(x=90, y=10)

        # adding open balance type radio controls to field frame
        baltype_fra = ttk.LabelFrame(field_fra, text="Open Balance Type", width=200, height=70)
        baltype_fra.place(x=260, y=220)
        self.baltypedb_rd = tk.Radiobutton(baltype_fra, text="Debit", variable=self.strbaltype, value="D")
        self.baltypedb_rd.place(x=10, y=10)
        self.baltypecr_rd = tk.Radiobutton(baltype_fra, text="Credit", variable=self.strbaltype, value='C')
        self.baltypecr_rd.place(x=100, y=10)

        # adding open balance controls to field frame
        tk.Label(field_fra, text="Open Balance", bd=4).place(x=500, y=250)
        self.openbal_ent = tk.Entry(field_fra, width=25, textvariable=self.stropenbal)
        self.openbal_ent.place(x=600, y=250)
        self.openbal_ent.bind('<KeyRelease>', lambda e: self.check_openbal())

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
        self.first_bt = tk.Button(field_fra, underline=0, text="First", width=6, command=lambda: self.move_first())
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
        table_fra = ttk.Frame(code_fra, width=1500, height=800)
        table_fra.place(x=20, y=400)
        # creating table using treeview
        self.code_tree = ttk.Treeview(table_fra, selectmode="browse", height=20)
        self.code_tree['columns'] = ('AccCode', 'Desc', 'Phone', 'GstNo', 'OpenBaldb', 'OpenBalcr')
        self.code_tree.column('#0', width=0, stretch=False)
        self.code_tree.column('AccCode', width=100)
        self.code_tree.column('Desc', width=250)
        self.code_tree.column('Phone', width=150, anchor=tk.CENTER)
        self.code_tree.column('GstNo', width=150, anchor=tk.CENTER)
        self.code_tree.column('OpenBaldb', width=150, anchor=tk.E)
        self.code_tree.column('OpenBalcr', width=150, anchor=tk.E)

        self.code_tree.heading('#0', text='')
        self.code_tree.heading('AccCode', text='Code')
        self.code_tree.heading('Desc', text='Description')
        self.code_tree.heading('Phone', text='Phone No.')
        self.code_tree.heading('GstNo', text='Gst No.')
        self.code_tree.heading('OpenBaldb', text='Openbalance Debit')
        self.code_tree.heading('OpenBalcr', text='Open Balance Credit')

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
