import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector as con
import config


class Product:

    def __init__(self):
        self.tab = None
        self.top = None
        self.rec = self.currec = self.totrec = None
        self.transflag = self.trans = None

        self.add_bt = self.mod_bt = self.del_bt = None
        self.save_bt = self.reset_bt = self.cancel_bt = None
        self.find_bt = self.close_bt = None

        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None

        self.code_ent = self.desc_ent = self.hsncode_ent = self.taxableyes_rd = self.taxableno_rd = None
        self.unit_cbo = self.qtyrecno_rd = self.qtyrecyes_rd = self.ytopqty_ent = None
        self.find_code_ent = None
        self.code_tree = self.selcode_tree = None

        self.strcode = tk.StringVar()
        self.strdesc = tk.StringVar()
        self.strhsncode = tk.StringVar()
        self.strtaxable = tk.StringVar()
        self.strunit = tk.StringVar()
        self.strqtytorec = tk.StringVar()
        self.strytopqty = tk.StringVar()
        self.strfindcode = tk.StringVar()

    def lock_controls(self, flag):
        # locks or unlocks editing controls
        self.code_ent.configure(state=flag)
        self.desc_ent.configure(state=flag)
        self.hsncode_ent.configure(state=flag)
        self.taxableyes_rd.configure(state=flag)
        self.taxableno_rd.configure(state=flag)
        self.unit_cbo.configure(state=flag)
        self.qtyrecyes_rd.configure(state=flag)
        self.qtyrecno_rd.configure(state=flag)
        self.ytopqty_ent.configure(state="disabled")

    def fetch_rec(self, code):
        # opens the connection and fetches the records from Product table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        s = "select * from Product where year='" + config.Year + "' order by code Desc"
        cur.execute(s)
        self.rec = cur.fetchall()
        # clearing fields and table
        self.clear_fields()
        self.clear_table()

        if code == "":
            # displaying first product
            if len(self.rec) > 0:
                self.currec = 0
                self.totrec = len(self.rec)
                # display first record
                self.display_fields()
                self.display_table()
            else:
                # in case of empty table no display
                self.currec = -1
                self.totrec = 0
        else:
            # displaying current product
            self.display_table()
            # setting current record to the code
            for i in range(0, len(self.rec)):
                if self.rec[i][0] == code:
                    self.currec = i
            self.totrec = len(self.rec)
            self.display_fields()

    def display_table(self):
        # displaying all product details in the table
        i = 0
        if self.currec >= 0:
            lst = []
            for row in self.rec:
                lst.clear()
                if row[6] == 0:
                    lst = [row[0], row[1], row[2], row[3], row[4], row[5], ""]
                else:
                    lst = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
                self.code_tree.insert(parent='', index=i, iid="%s" % i, text='', values=lst)
                i = i + 1
            self.code_tree.pack()

    def clear_table(self):
        # clearing the table content
        for row in self.code_tree.get_children():
            self.code_tree.delete(row)

    def display_fields(self):
        # displaying current product details in the form fields
        if self.currec >= 0:
            self.strcode.set(self.rec[self.currec][0])
            self.strdesc.set(self.rec[self.currec][1])
            if self.rec[self.currec][2] == 'N':
                self.strtaxable.set("N")
            elif self.rec[self.currec][2] == 'Y':
                self.strtaxable.set("Y")
            else:
                self.strtaxable.set("A")

            self.strhsncode.set(self.rec[self.currec][3])
            self.strunit.set(self.rec[self.currec][4])

            if self.rec[self.currec][5] == 'N':
                self.strqtytorec.set("N")
            elif self.rec[self.currec][5] == 'Y':
                self.strqtytorec.set("Y")
                self.strytopqty.set(self.rec[self.currec][6])
            else:
                self.strqtytorec.set("A")
                self.strytopqty.set("")
        else:
            # if no records clears the controls
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
            # if not in trans mode and there are one or more records
            # enable modify and delete buttons
            self.mod_bt.configure(state="normal")
            self.del_bt.configure(state="normal")
        else:
            # if in trans mode or there are no records
            # disable modify and delete buttons
            self.mod_bt.configure(state="disabled")
            self.del_bt.configure(state="disabled")
        if not self.transflag and len(self.rec) >= 2:
            # if not in trans mode and there are more records
            # enable find buttons
            self.find_bt.configure(state="normal")
        else:
            # if in trans mode or there are no records
            # disable find buttons
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

    def clear_fields(self):
        # clears the form controls
        self.strcode.set("")
        self.strdesc.set("")
        self.strtaxable.set("A")
        self.strhsncode.set("")
        self.strunit.set("")
        self.strytopqty.set("")
        self.strqtytorec.set("A")

    def add(self, _event=None):
        # preparing for adding records
        if not self.transflag:
            # if not in trans mode
            self.transflag = True
            self.trans = "Add"
            self.trans_mode()
            # disabling taxable, hsncode, qtytorec, ytopqty and unit
            # so that these can be enabled based on the product to be added
            self.taxableyes_rd.configure(state="disabled")
            self.taxableno_rd.configure(state="disabled")
            self.hsncode_ent.configure(state="disabled")
            self.qtyrecyes_rd.configure(state="disabled")
            self.qtyrecno_rd.configure(state="disabled")
            self.ytopqty_ent.configure(state="disabled")
            self.unit_cbo.configure(state="disabled")
            self.code_ent.focus_set()

    def modify(self, _event=None):
        # preparing for modifying records
        if not self.transflag and self.totrec != 0:
            # if not in trans mode
            self.transflag = True
            self.trans = "Mod"
            self.trans_mode()
            self.code_ent.configure(state="disabled")
            if self.strqtytorec.get() == "Y":
                self.ytopqty_ent.configure(state="normal")
            elif self.strqtytorec.get() == "N":
                self.ytopqty_ent.configure(state="disabled")
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
                # disabling taxable, hsncode, qtytorec, ytopqty and unit
                # so that these can be enabled based on the product to be added
                self.taxableyes_rd.configure(state="disabled")
                self.taxableno_rd.configure(state="disabled")
                self.hsncode_ent.configure(state="disabled")
                self.qtyrecyes_rd.configure(state="disabled")
                self.qtyrecno_rd.configure(state="disabled")
                self.ytopqty_ent.configure(state="disabled")
                self.unit_cbo.configure(state="disabled")
                self.code_ent.focus_set()
            elif self.trans == "Mod":
                # displaying original data in case of modify
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
        else:
            ch = self.strcode.get()[:1]
            if ch == "I" or ch == "P":
                # if purchase or sales account of the product
                # check for taxable, hsncode
                if self.strtaxable.get() != "Y" and self.strtaxable.get() != "N":
                    tk.messagebox.showinfo(config.Company_Name, "select Taxable yes or no")
                    self.taxableyes_rd.focus_set()
                    flag = False
                elif self.strtaxable.get() != "N" and self.strhsncode.get() == "":
                    tk.messagebox.showinfo(config.Company_Name, "Specify HSN code")
                    self.hsncode_ent.focus_set()
                    flag = False
            if ch == "P" and flag:
                # if purchase account of that product and if details entered so for are valid
                # check qtytorec and ytopqty
                if self.strqtytorec.get() != "Y" and self.strqtytorec.get() != "N":
                    tk.messagebox.showinfo(config.Company_Name, "select Quantity to record or not")
                    self.qtyrecyes_rd.focus_set()
                    flag = False
                elif self.strqtytorec.get() == "Y":
                    if str(self.strytopqty.get()) == "":
                        tk.messagebox.showinfo(config.Company_Name, "Year top Quantity cannot be blank")
                        self.ytopqty_ent.focus_set()
                        flag = False
                    elif not config.is_float(self.strytopqty.get()):
                        tk.messagebox.showinfo(config.Company_Name, " Invalid Year top Quantity")
                        self.ytopqty_ent.focus_set()
                        flag = False

        return flag

    def save(self, _event=None):
        if self.transflag:
            # checking form fields
            if self.check_fields():
                # saving after form field validation
                if self.strqtytorec.get() == "Y":
                    qtyrec = "Y"
                    qty = self.strytopqty.get()
                elif self.strqtytorec.get() == "N":
                    qtyrec = "N"
                    qty = 0
                else:
                    qtyrec = ""
                    qty = 0

                # opens the connection to save the records in product table
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()
                flag = True
                if self.trans == "Add":
                    # in case of addition checking if the product already exists
                    if config.check_records("Product", "Code", self.strcode.get()):
                        tk.messagebox.showinfo(config.Company_Name, "Product code already exist")
                        self.code_ent.focus_set()
                        flag = False
                    else:
                        # adding product details to the table
                        s = "insert into Product values('" + self.strcode.get() + "','" + self.strdesc.get() + "','" \
                            + self.strtaxable.get() + "', '" + self.strhsncode.get() + "','" + self.strunit.get() + "','" \
                            + qtyrec + "'," + str(qty) + ",'" + config.Year + "')"
                        cur.execute(s)
                        myconn.commit()

                elif self.trans == "Mod":
                    # saving altered product details to the table
                    s = "update Product set Code='" + self.strcode.get() + "', Description='" + self.strdesc.get() \
                        + "',taxable='" + self.strtaxable.get() + "',HSNcode='" + self.strhsncode.get() + "',QtyUnit='"\
                        + self.strunit.get() + "',QtyToRec='" + qtyrec + "',YTopQty=" + str(qty) + ",Year='" \
                        + config.Year + "' where code='" + self.strcode.get() + "'"
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
            # checking if transaction for the product exists
            if config.check_records("Transaction", "code", self.strcode.get()):
                tk.messagebox.showinfo(config.Company_Name, "Transaction for the code exist, so cannot delete it")
            else:
                # getting confirmation from user before deleting
                if tk.messagebox.askokcancel(title=None, message="Delete it?"):
                    s = "Delete from product where Code='" + self.strcode.get() + "' and Year='" + config.Year + "'"

                    # opens the connection to delete Customer
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
            # displaying details of the product selected
            self.currec = int(index[0])
            self.code_tree.selection_set(self.currec)
            self.display_fields()
            self.set_navi()
            self.top.destroy()

    def sel_cancel(self, _event=None):
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

            tk.Label(self.top, text="Product Code", bd=4).place(x=30, y=50)
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

            ok_bt = tk.Button(self.top, text="OK", underline=0, command=lambda: self.sel_ok())
            ok_bt.place(x=150, y=450)
            self.top.bind("<Alt-o>", self.sel_ok)
            cancel_bt = tk.Button(self.top, text="Cancel", underline=0, command=lambda: self.sel_cancel())
            cancel_bt.place(x=200, y=450)
            self.top.bind("<Alt-c>", self.sel_cancel)

            s = "select code, description from product order by code"
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
        # only 4 characters
        # first letter must be I or P or F
        flag = True
        s = ""
        if type == "Main":
            # in case of code validation during addition
            s = self.strcode.get()
        elif type == "Find":
            # in case of code validation during find
            s = self.strfindcode.get()

        lt = len(s)
        s = s.upper()
        for i in range(0, lt):
            # checking each character in the code
            if not ('A' <= s[i] <= 'Z'):
                tk.messagebox.showinfo(config.Company_Name, "only Letters")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                flag = False
                break
            else:
                # checking for first character in the code
                if (i == 0) and (s[i] != 'I' and s[i] != 'P' and s[i] != 'F'):
                    tk.messagebox.showinfo(config.Company_Name, "First Letter should be I or P or F ")
                    s = ""
                    flag = False
                    break

        if len(s) > 4:
            tk.messagebox.showinfo(config.Company_Name, "only 4 letters")
            s = s[:4]
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

    def check_hsncode(self):
        # checking gstno
        # only numbers
        s = self.strhsncode.get()
        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or s[i] == " "):
                tk.messagebox.showinfo(config.Company_Name, "only Numbers")
                s1 = s[:i]
                if i <= (lt-1):
                    s1 = s1 + s[i+1:]
                s = s1
                break
        self.strhsncode.set(s)

    def check_ytopqty(self):
        # checking Ytopqty
        # only numbers and "."
        s = self.strytopqty.get()
        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                tk.messagebox.showinfo(config.Company_Name, "only Numbers")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break
        self.strytopqty.set(s)

    def code_out(self, _event=None):
        if self.transflag:
            ch = self.strcode.get()[:1]
            if ch == "F":
                self.strtaxable.set("N")
                self.strhsncode.set("")
                self.strqtytorec.set("N")
                self.strytopqty.set("")
                self.taxableyes_rd.configure(state="disabled")
                self.taxableno_rd.configure(state="disabled")
                self.hsncode_ent.configure(state="disabled")
                self.qtyrecyes_rd.configure(state="disabled")
                self.qtyrecno_rd.configure(state="disabled")
                self.ytopqty_ent.configure(state="disabled")
                self.strunit.set("")
                self.unit_cbo.configure(state="disabled")
            elif ch == "I" or ch == "P":
                self.strtaxable.set("A")
                self.strhsncode.set("")
                self.taxableyes_rd.configure(state="normal")
                self.taxableno_rd.configure(state="normal")
                self.hsncode_ent.configure(state="normal")
                self.strunit.set("")
                self.unit_cbo.configure(state="normal")
                if ch == "I":
                    self.strqtytorec.set("N")
                    self.strytopqty.set("")
                    self.qtyrecyes_rd.configure(state="disabled")
                    self.qtyrecno_rd.configure(state="disabled")
                    self.ytopqty_ent.configure(state="disabled")
                else:
                    self.strqtytorec.set("A")
                    self.strytopqty.set("")
                    self.qtyrecyes_rd.configure(state="normal")
                    self.qtyrecno_rd.configure(state="normal")
                    self.ytopqty_ent.configure(state="normal")

    def selected(self):
        # selecting product
        item = self.code_tree.selection()
        if item[0] != self.currec:
            self.currec = int(item[0])
            self.clear_fields()
            self.display_fields()
            self.set_navi()

    def sel_qtyrec(self):
        # enabling ytopqty only if qtytorec is "Y"
        if self.strqtytorec.get() == "Y":
            self.ytopqty_ent.configure(state="normal")
            self.ytopqty_ent.focus_set()
        elif self.strqtytorec.get() == "N":
            self.strytopqty.set("")
            self.ytopqty_ent.configure(state="disabled")
            self.unit_cbo.focus_set()

    def preparing_window(self, tab):
        # creating frame for customer
        code_fra = ttk.LabelFrame(tab, width=1100, height=700)
        code_fra.place(x=20, y=20)
        self.tab = tab
        tab.focus_set()

        # creating frame for fields in Form view
        field_fra = ttk.LabelFrame(code_fra, width=1000, height=370)
        field_fra.place(x=20, y=20)

        # adding ProdCode controls to fieldframe
        tk.Label(field_fra, text="Product Code", bd=4).place(x=30, y=50)
        self.code_ent = tk.Entry(field_fra, textvariable=self.strcode)
        self.code_ent.place(x=150, y=50)
        self.code_ent.bind('<KeyRelease>', lambda e: self.check_code("Main"))
        self.code_ent.bind('<FocusOut>', lambda e: self.code_out())

        # adding ProdDesc controls to fieldframe
        tk.Label(field_fra, text="Description", bd=4).place(x=30, y=100)
        self.desc_ent = tk.Entry(field_fra, width=80, textvariable=self.strdesc)
        self.desc_ent.place(x=150, y=100)

        # adding Taxable radio controls to fieldframe
        taxable_fra = ttk.LabelFrame(field_fra, text="Taxable", width=200, height=70)
        taxable_fra.place(x=30, y=150)
        self.taxableyes_rd = tk.Radiobutton(taxable_fra, text="Yes", variable=self.strtaxable, value="Y")
        self.taxableyes_rd.place(x=10, y=10)
        self.taxableno_rd = tk.Radiobutton(taxable_fra, text="No", variable=self.strtaxable, value="N")
        self.taxableno_rd.place(x=100, y=10)

        # adding GstNo controls to fieldframe
        tk.Label(field_fra, text="GstNo", bd=4).place(x=300, y=170)
        self.hsncode_ent = tk.Entry(field_fra, textvariable=self.strhsncode)
        self.hsncode_ent.place(x=420, y=170)
        self.hsncode_ent.bind('<KeyRelease>', lambda e: self.check_hsncode())

        # adding QtyToRec radio controls to fieldframe
        qtytorec_fra = ttk.LabelFrame(field_fra, text="Quantity to record", width=200, height=70)
        qtytorec_fra.place(x=30, y=250)
        self.qtyrecyes_rd = tk.Radiobutton(qtytorec_fra, text="Yes", variable=self.strqtytorec, value="Y",
                                           command=self.sel_qtyrec)
        self.qtyrecyes_rd.place(x=10, y=10)
        self.qtyrecno_rd = tk.Radiobutton(qtytorec_fra, text="No", variable=self.strqtytorec, value="N",
                                          command=self.sel_qtyrec)
        self.qtyrecno_rd.place(x=100, y=10)

        # adding Year top Quantity controls to fieldframe
        tk.Label(field_fra, text="Year Top Quantity", bd=4).place(x=300, y=230)
        self.ytopqty_ent = tk.Entry(field_fra, textvariable=self.strytopqty)
        self.ytopqty_ent.place(x=420, y=230)
        self.ytopqty_ent.bind('<KeyRelease>', lambda e: self.check_ytopqty())

        # adding Quantity Unit controls to fieldframe
        tk.Label(field_fra, text="Quantity Unit", bd=4).place(x=300, y=290)
        self.unit_cbo = ttk.Combobox(field_fra, textvariable=self.strunit)
        self.unit_cbo.place(x=420, y=290)
        self.unit_cbo['values'] = ["Bags", "Unit"]
        self.unit_cbo['state'] = 'readonly'

        # creating action frame with buttons
        action_fra = ttk.LabelFrame(field_fra, width=100, height=320)
        action_fra.place(x=800, y=5)

        # creating add,modify and delete buttons
        self.add_bt = tk.Button(action_fra, underline=0, text="Add", width=6, command=lambda: self.add())
        self.add_bt.place(x=20, y=10)
        # tab.bind("<Control-a>", self.add)
        # self.add_bt.bind("<Button-1>", self.add)
        # self.add_bt.bind("<Control-a>", lambda e: self.add())
        config.Root.bind("<Control-a>", self.add)

        self.mod_bt = tk.Button(action_fra, underline=0, text="Modify", width=6, command=lambda: self.modify())
        self.mod_bt.place(x=20, y=40)
        # tab.bind("<Control-m>", self.modify)
        config.Root.bind("<Control-m>", self.modify)

        self.del_bt = tk.Button(action_fra, underline=0, text="Delete", width=6, command=lambda: self.delete())
        self.del_bt.place(x=20, y=70)
        # tab.bind("<Control-d>", self.delete)
        #config.Root.bind("<Control-d>", self.delete)

        # creating save,reset and cancel buttons
        self.save_bt = tk.Button(action_fra, underline=0, text="Save", width=6, command=lambda: self.save())
        self.save_bt.place(x=20, y=120)
        # tab.bind("<Control-s>", self.save)
        config.Root.bind("<Control-s>", self.save)

        self.reset_bt = tk.Button(action_fra, underline=0, text="Reset", width=6, command=lambda: self.reset())
        self.reset_bt.place(x=20, y=150)
        # tab.bind("<Control-e>", self.reset)
        config.Root.bind("<Control-r>", self.reset)

        self.cancel_bt = tk.Button(action_fra, underline=0, text="Cancel", width=6, command=lambda: self.cancel())
        self.cancel_bt.place(x=20, y=180)
        # tab.bind("<Control-c>", self.cancel)
        config.Root.bind("<Control-c>", self.cancel)

        # creating find and close button
        self.find_bt = tk.Button(action_fra, underline=1, text="Find", width=6, command=lambda: self.find())
        self.find_bt.place(x=20, y=220)
        # tab.bind("<Control-i>", self.find)
        config.Root.bind("<Control-i>", self.find)

        self.close_bt = tk.Button(action_fra, underline=2, text="Close", width=6, command=lambda: self.close())
        self.close_bt.place(x=20, y=250)
        # tab.bind("<Control-o>", self.close)
        config.Root.bind("<Control-o>", self.close)

        # creating Navigation buttons
        self.first_bt = tk.Button(field_fra, underline=0, text="First", width=6, command=lambda: self.move_first())
        self.first_bt.place(x=500, y=20)
        # tab.bind("<Control-f>", self.move_first)
        config.Root.bind("<Control-f>", self.move_first)

        self.prev_bt = tk.Button(field_fra, underline=0, text="Prev", width=6, command=lambda: self.move_previous())
        self.prev_bt.place(x=550, y=20)
        # tab.bind("<Control-p>", self.move_previous)
        config.Root.bind("<Control-p>", self.move_previous)

        self.next_bt = tk.Button(field_fra, text="Next", underline=0, width=6, command=lambda: self.move_next())
        self.next_bt.place(x=600, y=20)
        # tab.bind("<Control-n>", self.move_next)
        config.Root.bind("<Control-n>", self.move_next)

        self.last_bt = tk.Button(field_fra, underline=0, text="Last", width=6, command=lambda: self.move_last())
        self.last_bt.place(x=650, y=20)
        # tab.bind("<Control-l>", self.move_last)
        config.Root.bind("<Control-l>", self.move_last)

        # creating frame for the table
        table_fra = ttk.Frame(code_fra, width=900, height=100)
        table_fra.place(x=20, y=400)
        # creating table using treeview
        self.code_tree = ttk.Treeview(table_fra)
        self.code_tree['columns'] = ('ProdCode', 'Desc', 'Taxable', 'GstNo', 'Unit', 'QtyToRec',  'YTopQty')
        self.code_tree.column('#0', width=0, stretch=False)
        self.code_tree.column('ProdCode', width=100)
        self.code_tree.column('Desc', width=250)
        self.code_tree.column('Taxable', width=100)
        self.code_tree.column('GstNo', width=200)
        self.code_tree.column('Unit', width=100)
        self.code_tree.column('QtyToRec', width=150, anchor=tk.CENTER)
        self.code_tree.column('YTopQty', width=150, anchor=tk.E)

        self.code_tree.heading('#0', text='')
        self.code_tree.heading('ProdCode', text='Code')
        self.code_tree.heading('Desc', text='Description')
        self.code_tree.heading('Taxable', text='Taxable')
        self.code_tree.heading('GstNo', text='HSN Code.')
        self.code_tree.heading('Unit', text='Quantity Unit')
        self.code_tree.heading('QtyToRec', text='Quantity To Record')
        self.code_tree.heading('YTopQty', text='Year Top Quantity')

        self.code_tree.bind('<<TreeviewSelect>>', lambda e: self.selected())
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.code_tree.yview)
        self.code_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.code_tree.pack(expand=1)

        self.transflag = False
        self.trans = ""

        # fetching records from the Acccode table
        self.fetch_rec("")

        self.lock_controls("disabled")
        self.enable_controls()
        self.set_navi()
