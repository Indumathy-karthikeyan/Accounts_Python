import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime as dt
import mysql.connector as con
import math
from fpdf.fpdf import FPDF
import win32api

import config


class Transaction:

    def __init__(self):
        self.tab = None
        self.top = None
        self.rec = self.totrec = self.currec = self.prodtotrow = self.prodcurrec = self.prodrow = None
        self.bill_type = self.type = None

        self.transflag = self.prodtransflag = self.trans = self.prodtrans = self.emptyflag = self.gstflag = None

        self.billno_ent = self.cuscode_ent = self.cusdesc_ent = self.name1_ent = self.name2_ent = self.data_ent = None
        self.date_ent = self.narr_ent = self.gstno_ent = self.totamt_ent = self.Intra_rd = self.Inter_rd = self.prevBill = None
        self.selnarr_bt = self.selcus_bt = None

        self.strname1 = tk.StringVar()
        self.strname2 = tk.StringVar()
        self.strcuscode = tk.StringVar()
        self.strcusdesc = tk.StringVar()
        self.strnarr = tk.StringVar()
        self.strgstno = tk.StringVar()
        self.strgtype = tk.StringVar()
        self.strbillno = tk.StringVar()
        self.strdate = tk.StringVar()
        self.strtotamt = tk.StringVar()
        self.taxable = tk.StringVar()
        self.strgsttype = tk.StringVar()
        self.strdata = tk.StringVar()
        self.seltype = tk.StringVar()
        self.printtype = tk.StringVar()

        self.totaldiff = None
        self.prev_gsttype = None
        self.first_bt = self.prev_bt = self.next_bt = self.last_bt = None
        self.add_bt = self.mod_bt = self.del_bt = None
        self.save_bt = self.reset_bt = self.cancel_bt = self.find_bt = self.print_bt = self.close_bt = None

        self.prodcode_ent = self.proddesc_ent = self.ratequt_rd = self.rateunit_rd = None
        self.prodrate_ent = self.prodwt_ent = self.prodqty_ent = self.prodamt_ent = self.prodhsn_ent = None

        self.strprodcode = tk.StringVar()
        self.strproddesc = tk.StringVar()
        self.strhsncode = tk.StringVar()
        self.strratetype = tk.StringVar()
        self.strprodrate = tk.StringVar()
        self.strprodwt = tk.StringVar()
        self.strprodqty = tk.StringVar()
        self.strprodamt = tk.StringVar()

        self.selprod_bt = None
        self.prodadd_bt = self.prodmod_bt = self.proddel_bt = None
        self.prodsave_bt = self.prodreset_bt = self.prodcancel_bt = self.calgst_bt = None

        self.prodfirst_bt = self.prodprev_bt = self.prodnext_bt = self.prodlast_bt = None

        self.prod_tree = self.prodlst = self.code_tree = None

    def clear_form(self, type):
        # clearing the entire form
        if type == "Bill":
            # clearing customer details
            if self.transflag:
                # in case of trans mode clearing only certain fields
                self.clear_fields("Few")
            else:
                # if not trans mode clearing all fields
                self.clear_fields("All")
        # clearing product details in fields and in table
        self.clear_prod()
        self.clear_table()
        # resetting variables to intial values
        self.prodlst = []
        self.prodcurrec = -1
        self.prodtotrow = 0
        self.prodrow = 0
        self.prev_gsttype = ""

    def clear_fields(self, type):
        if type == "All":
            # in case entire details has to eb cleared
            self.strbillno.set("")
            self.strdate.set("")
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            # clearing customer code and name in case of credit bill
            self.strcuscode.set("")
            self.strcusdesc.set("")
            self.strnarr.set("")
        elif self.bill_type == "Computer Cash Bill":
            # clearing name in case of Computer cash bill
            self.strname1.set("")
            self.strname2.set("")

        # clearing rest of the customer fields
        self.strgstno.set("")
        self.strgtype.set("A")
        self.strtotamt.set("")

    def clear_prod(self):
        # clearing product details
        self.strprodcode.set("")
        self.strproddesc.set("")
        self.taxable.set("")
        self.strhsncode.set("")
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            self.strprodrate.set("")
            self.strratetype.set("A")
            self.strprodwt.set("")
        self.strprodqty.set("")
        self.strprodamt.set("")

    def clear_table(self):
        # clearing the product table
        for row in self.prod_tree.get_children():
            self.prod_tree.delete(row)

    def lock_controls(self, flag):
        # locking bill controls
        self.date_ent.configure(state=flag)
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            self.cuscode_ent.configure(state=flag)
            self.narr_ent.configure(state=flag)
        elif self.bill_type == "Computer Cash Bill":
            self.name1_ent.configure(state=flag)
            self.name2_ent.configure(state=flag)

        self.Inter_rd.configure(state=flag)
        self.Intra_rd.configure(state=flag)

    def lock_prodcontrols(self, flag):
        self.prodcode_ent.configure(state=flag)
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            self.prodrate_ent.configure(state=flag)
            self.ratequt_rd.configure(state=flag)
            self.rateunit_rd.configure(state=flag)
            self.prodwt_ent.configure(state=flag)
        self.prodqty_ent.configure(state=flag)
        self.prodamt_ent.configure(state=flag)

    def enable_controls(self):
        if self.transflag:
            state1 = "normal"
            state2 = "disabled"
        else:
            state1 = "disabled"
            state2 = "normal"

        self.add_bt.configure(state=state2)
        self.close_bt.configure(state=state2)
        self.save_bt.configure(state=state1)
        self.reset_bt.configure(state=state1)
        self.cancel_bt.configure(state=state1)
        if self.bill_type != "Manual Cash Bill":
            self.selcus_bt.configure(state=state1)
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            self.selnarr_bt.configure(state=state1)

        if self.transflag:
            self.del_bt.configure(state=state2)
            self.mod_bt.configure(state=state2)
            self.print_bt.configure(state=state2)
            self.find_bt.configure(state=state2)
        else:
            if self.totrec >= 2:
                self.find_bt.configure(state=state2)
            else:
                self.find_bt.configure(state=state1)

            if self.totrec >= 1:
                print("more records")
                self.del_bt.configure(state=state2)
                self.mod_bt.configure(state=state2)
                self.print_bt.configure(state=state2)
            else:
                print(self.transflag)
                self.del_bt.configure(state=state1)
                self.mod_bt.configure(state=state1)
                self.print_bt.configure(state=state1)

    def enable_prodcontrols(self):
        # enabling or disabling prod trans controls
        if (not self.transflag) and (not self.prodtransflag):
            self.prodadd_bt.configure(state="disabled")
            self.prodmod_bt.configure(state="disabled")
            self.proddel_bt.configure(state="disabled")
            self.prodsave_bt.configure(state="disabled")
            self.prodreset_bt.configure(state="disabled")
            self.prodcancel_bt.configure(state="disabled")
            self.calgst_bt.configure(state="disabled")
            self.selprod_bt.configure(state="disabled")
        else:
            if self.prodtransflag:
                self.prodadd_bt.configure(state="disabled")
                self.prodsave_bt.configure(state="normal")
                self.prodreset_bt.configure(state="normal")
                self.prodcancel_bt.configure(state="normal")
                self.selprod_bt.configure(state="normal")
            else:
                self.prodadd_bt.configure(state="normal")
                self.prodsave_bt.configure(state="disabled")
                self.prodreset_bt.configure(state="disabled")
                self.prodcancel_bt.configure(state="disabled")
                self.selprod_bt.configure(state="disabled")

            if self.transflag and (not self.prodtransflag) and self.prodrow >= 1:
                self.calgst_bt.configure(state="normal")
            else:
                self.calgst_bt.configure(state="disabled")

            if (not self.prodtransflag) and (self.prodrow >= 1):
                self.prodmod_bt.configure(state="normal")
                self.proddel_bt.configure(state="normal")
            else:
                self.prodmod_bt.configure(state="disabled")
                self.proddel_bt.configure(state="disabled")

    def disable_navi(self):
        # disabling all navi buttons
        self.first_bt.configure(state="disabled")
        self.prev_bt.configure(state="disabled")
        self.next_bt.configure(state="disabled")
        self.last_bt.configure(state="disabled")

    def set_navi(self):
        # enabling or enabling bill navi buttons
        if self.totrec == 0 or self.totrec == 1:
            # if no bill exists
            self.disable_navi()
        else:
            # if bill exists
            if self.currec == 0:
                # if current bill is the first one
                self.first_bt.configure(state="disabled")
                self.prev_bt.configure(state="disabled")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")
            elif self.currec == (self.totrec - 1):
                # if current bill is the last one
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="disabled")
                self.last_bt.configure(state="disabled")
            else:
                # if current bill is in middle
                self.first_bt.configure(state="normal")
                self.prev_bt.configure(state="normal")
                self.next_bt.configure(state="normal")
                self.last_bt.configure(state="normal")

    def disable_prodnavi(self):
        # disabling all product navi buttons
        self.prodfirst_bt.configure(state="disabled")
        self.prodprev_bt.configure(state="disabled")
        self.prodnext_bt.configure(state="disabled")
        self.prodlast_bt.configure(state="disabled")

    def set_prodnavi(self):
        # enabling or diabling product navi buttons
        if self.prodrow == 0 or self.prodrow == 1:
            # if no product records
            self.disable_prodnavi()
        else:
            # product record exists
            if self.prodcurrec == 0:
                # if current product is the first one
                self.prodfirst_bt.configure(state="disabled")
                self.prodprev_bt.configure(state="disabled")
                self.prodnext_bt.configure(state="normal")
                self.prodlast_bt.configure(state="normal")
            elif self.prodcurrec == (self.prodrow - 1):
                # if current product is the last one
                self.prodfirst_bt.configure(state="normal")
                self.prodprev_bt.configure(state="normal")
                self.prodnext_bt.configure(state="disabled")
                self.prodlast_bt.configure(state="disabled")
            else:
                # if current product is in the middle
                self.prodfirst_bt.configure(state="normal")
                self.prodprev_bt.configure(state="normal")
                self.prodnext_bt.configure(state="normal")
                self.prodlast_bt.configure(state="normal")

    def set_bill(self, trans_mode):
        if trans_mode:
            # if in trans mode unlocking edit controls and disabling navibuttons
            self.lock_controls("normal")
            self.disable_navi()
        else:
            # if not in trans mode ulocking edit controls and enabling navibuttons
            self.lock_controls("disabled")
            self.set_navi()

        self.enable_controls()

    def set_prod(self, trans_mode):
        if trans_mode:
            # if in trans mode unlocking edit controls and disabling navibuttons
            self.lock_prodcontrols("normal")
            self.disable_prodnavi()
        else:
            # if not in trans mode locking edit controls and enabling navibuttons
            self.lock_prodcontrols("disabled")
            self.set_prodnavi()

        self.enable_prodcontrols()

    def set_transmode(self, flag):
        if flag:
            if self.trans == "Add":
                self.lock_controls("Normal")
        else:
            self.lock_controls("disabled")
            self.lock_prodcontrols("disabled")
            self.enable_controls()
            self.enable_prodcontrols()
            if self.totrec == 0 or self.totrec == 1:
                self.disable_navi()
                self.disable_prodnavi()
            else:
                self.set_navi()
                self.set_prodnavi()

    def display_table(self):
        # displaying product table from the prodlst
        i = 0
        amt = 0
        self.gstflag = False
        #print("display table")
        #print(self.prodlst)
        for row in self.prodlst:
            if row[0] != 'EBRO':

                if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    amt += float(row[8])
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                      values=(row[1], row[3], row[4], row[6], row[7], row[8]))
                elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    amt += float(row[5])
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                      values=(row[1], row[3], row[4], row[5]))

                if row[0] == "LIST" or row[0] == "LCST" or row[0] == "LSST":
                    self.gstflag = True
            else:

                if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                          values=("", "", "", "", "", ""))
                    i += 1
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                          values=("Total", "", "", "", "", "{:.2f}".format(amt)))
                    i += 1
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                          values=(row[1], row[3], row[4], row[6], row[7], row[8]))
                elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                          values=("", "", "", ""))
                    i += 1
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                          values=("Total", "", "", "{:.2f}".format(amt)))
                    i += 1
                    self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                          values=(row[1], row[3], row[4], row[5]))

            if row[0] == "LIST":
                self.strgsttype = "Inter"
            if row[0] == "LCST":
                self.strgsttype = "Intra"
            i = i + 1

        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            self.prod_tree.insert(parent='', index=i, iid=i, text='', values=("", "", "", "", "", ""))
            i += 1
            self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                values=("Grand Total", "", "", "", "", self.strtotamt.get()))
        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
            self.prod_tree.insert(parent='', index=i, iid=i, text='', values=("", "", "", ""))
            i += 1
            self.prod_tree.insert(parent='', index=i, iid=i, text='',
                                  values=("Grand Total", "", "", self.strtotamt.get()))

        self.prod_tree.pack()

    def display_prod(self):
        # printing product details in product fields
        self.strprodcode.set(self.prodlst[self.prodcurrec][0])
        self.strproddesc.set(self.prodlst[self.prodcurrec][1])
        self.strhsncode.set(self.prodlst[self.prodcurrec][3])
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            if self.prodlst[self.prodcurrec][4] != 0:
                self.strprodrate.set(self.prodlst[self.prodcurrec][4])
            if self.prodlst[self.prodcurrec][5] == 'Qut' or self.prodlst[self.prodcurrec][5] == 'Kg':
                self.strratetype.set("Kg")
            elif self.prodlst[self.prodcurrec][5] == 'Unit':
                self.strratetype.set("Unit")
            else:
                self.strratetype.set("A")
            if self.prodlst[self.prodcurrec][7] != 0:
                self.strprodwt.set(self.prodlst[self.prodcurrec][7])
            if self.prodlst[self.prodcurrec][6] != 0:
                self.strprodqty.set(self.prodlst[self.prodcurrec][6])
            self.strprodamt.set(self.prodlst[self.prodcurrec][8])
        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
            if self.prodlst[self.prodcurrec][4] != 0:
                self.strprodqty.set(self.prodlst[self.prodcurrec][4])
            self.strprodamt.set(self.prodlst[self.prodcurrec][5])

    def move_first(self, _event=None):
        if (not self.transflag) and (self.currec != 0) and (not self.emptyflag):
            # if not in trans mode and current record is not the first one
            self.currec = 0
            self.fetch_bill()
            self.set_navi()
            self.set_prodnavi()

    def move_previous(self, _event=None):
        if (not self.transflag) and (self.currec != 0) and (not self.emptyflag):
            # if not in trans mode and current record is not the first one
            self.currec = self.currec - 1
            self.fetch_bill()
            self.set_navi()
            self.set_prodnavi()

    def move_next(self, _event=None):
        if (not self.transflag) and (self.currec != (self.totrec - 1)) and (not self.emptyflag):
            # if not in trans mode and current record is not the last one
            self.currec = self.currec + 1
            self.fetch_bill()
            self.set_navi()
            self.set_prodnavi()

    def move_last(self, _event=None):
        if (not self.transflag) and (self.currec != (self.totrec - 1)) and (not self.emptyflag):
            # if not in trans mode and current record is not the last one
            self.currec = self.totrec - 1
            self.fetch_bill()
            self.set_navi()
            self.set_prodnavi()

    def move_prodfirst(self, _event=None):
        if (not self.transflag and not self.prodtransflag and (not self.emptyflag)) or\
                (self.transflag and not self.prodtransflag and (self.prodrow != 0) and (self.prodcurrec != 0)):
            # if not in product trans mode and current record is not the first one
            self.prodcurrec = 0
            self.set_prodnavi()
            self.display_prod()

    def move_prodprevious(self, _event=None):
        if (not self.transflag and not self.prodtransflag and (not self.emptyflag)) or \
                (self.transflag and not self.prodtransflag and (self.prodrow != 0) and (self.prodcurrec != 0)):
            # if not in product trans mode and current record is not the first one
            self.prodcurrec = self.prodcurrec - 1
            self.set_prodnavi()
            self.display_prod()

    def move_prodnext(self, _event=None):
        #print(self.transflag, self.prodtransflag, self.emptyflag)
        #print(self.prodtotrow, self.prodrow, self.prodcurrec)
        if (not self.transflag and (not self.prodtransflag) and (not self.emptyflag)) or \
                (self.transflag and not self.prodtransflag and (self.prodrow != 0) and
                (self.prodcurrec != (self.prodrow - 1))):
            # if not in product trans mode and current record is not the last one
            self.prodcurrec = self.prodcurrec + 1
            self.set_prodnavi()
            self.display_prod()

    def move_prodlast(self, _event=None):
        if (not self.transflag and not self.prodtransflag and (not self.emptyflag)) or \
                (self.transflag and not self.prodtransflag and (self.prodrow != 0) and
                 (self.prodcurrec != (self.prodrow - 1))):
            # if not in product trans mode and current record is not the last one
            self.prodcurrec = self.prodrow - 1
            self.set_prodnavi()
            self.display_prod()

    def check_code(self, data, type):
        # checking customer code or product code or narration
        # only 4 characters for code and 2 for narration
        flag = True
        s = ""
        if data == "Customer" and type == "Main":
            # in case of addtion validating Customer code
            s = self.strcuscode.get()
            s = s.upper()
        elif data == "Customer" and type == "Select":
            # in case of selection validating Customer name
            s = self.strdata.get()
        elif data == "Product" and type == "Main":
            # in case of addtion validating Product code
            s = self.strprodcode.get()
            s = s.upper()
        elif data == "Product" and type == "Select":
            # in case of selection validating product code
            s = self.strdata.get()
            s = s.upper()
        if data == "Narration" and type == "Main":
            # in case of addtion validating Narration code
            s = self.strnarr.get()
        elif data == "Narration" and type == "Select":
            # in case of selection validating Narration code
            s = self.strdata.get()
        elif data == "Find" and type == "Select":
            # in case of find validating billno
            s = self.strdata.get()
            s = s.upper()
        lt = len(s)
        for i in range(0, lt):
            # checking each character in the code
            if (data != "Narration" and data != "Find") and (not (('A' <= s[i] <= 'Z') or ('a' <= s[i] <= 'z'))):
                # checking other details except narration for only letters
                tk.messagebox.showinfo(config.Company_Name, "only Letters")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                flag = False
                break
            else:
                # if only letters for other details except narration
                if data == "Customer" and type == "Main":
                    # checking for first character in the customer code
                    if (i == 0) and (s[i] != 'A' and s[i] != 'L'):
                        tk.messagebox.showinfo(config.Company_Name, "First Letter should be A or L")
                        s = ""
                        flag = False
                        break
                elif data == "Product":
                    # checking for first character in the product code
                    if (i == 0) and (s[i] != 'I' and s[i] != 'F'):
                        tk.messagebox.showinfo(config.Company_Name, "First Letter should be I or F ")
                        s = ""
                        flag = False
                        break
                elif data == "Find" and (not ('0' <= s[i] <= '9')):
                    tk.messagebox.showinfo(config.Company_Name, "Only numbers")
                    s = ""
                    flag = False
                    break


        if flag:
            if ((data == "Customer" and type == "Main") or data == "Product") and len(s) > 4:
                # checking customer or product code allowing only 4 characters
                tk.messagebox.showinfo(config.Company_Name, "only 4 letters")
                s = s[:4]
                flag = False

        if type == "Select":
            # in case of selection
            self.strdata.set(s.upper())
            print(s)
            if data == "Find":
                if self.bill_type == "Computer Cash Bill":
                    s = "CCH" + s
                if self.bill_type == "Manual Cash Bill":
                    s = "MCH" + s
                if self.bill_type == "Computer Credit Bill":
                    s = "CCR" + s
                if self.bill_type == "Manual Credit Bill":
                    s = "MCR" + s

                print(s)
            if flag:
                no = len(s)
                for row in self.code_tree.get_children():
                    val = self.code_tree.item(row, "values")
                    if data == "Customer" or data == "Find":
                        # selecting the row in table containing the customer name entered
                        if val[1][:no].upper() == s.upper():
                            self.code_tree.selection_set(row)
                            self.code_tree.see(row)
                            self.code_tree.focus(row)
                            print("focus",self.code_tree.focus())
                            break
                    else:
                        # selecting the row in table containing the product code or narration code or billno entered
                        if val[0][:no] == s:
                            self.code_tree.selection_set(row)
                        break
        elif data == "Customer" and type == "Main":
            self.strcuscode.set(s)
            if len(s) != 4:
                # if invalid customer code clearing the customer description field
                self.strcusdesc.set("")
        elif data == "Product" and type == "Main":
            self.strprodcode.set(s)
            if len(s) != 4:
                # if invalid product code clearing the product description field
                self.strproddesc.set("")
        elif data == "Narration" and type == "Main":
            self.strnarr.set(s)

    def get_det(self, type, _event=None):
        # displaying a window to show table enabling user to select from the list
        self.top = tk.Toplevel(config.Root)
        self.top.geometry("500x500")
        x = config.Root.winfo_x()
        y = config.Root.winfo_y()
        self.top.geometry("+%d+%d" % (x + 500, y + 150))
        self.top.wm_transient(config.Root)
        self.top.grab_set()

        self.seltype = type
        # creating frame for the top window
        field_fra = ttk.Frame(self.top, width=500, height=700)
        field_fra.place(x=20, y=10)

        # creating table using treeview
        table_fra = ttk.Frame(field_fra, width=80, height=300)
        table_fra.place(x=20, y=50)
        self.code_tree = ttk.Treeview(table_fra, height=17, selectmode="browse")

        if self.seltype == "Customer":
            # in case of customer displaying code, description and gstno
            # so that user can pick the customer
            tk.Label(field_fra, text="Code", bd=4).place(x=30, y=5)
            self.data_ent = tk.Entry(field_fra, textvariable=self.strdata)
            self.data_ent.place(x=150, y=5)
            self.data_ent.bind('<KeyRelease>', lambda e: self.check_code("Customer", "Select"))

            self.code_tree['columns'] = ('Code', 'Desc', 'GstNo')
            self.code_tree.column('#0', width=0, stretch=False)
            self.code_tree.column('Code', width=100)
            self.code_tree.column('Desc', width=220)
            self.code_tree.column('GstNo', width=100)
            self.code_tree.heading('#0', text='')
            self.code_tree.heading('Code', text='Customer code')
            self.code_tree.heading('Desc', text='Description')
            self.code_tree.heading('GstNo', text='Gst No.')

        elif self.seltype == "Product":
            # in case of product displaying code, description and gstno and taxable
            # so that user can pick the customer
            tk.Label(field_fra, text="Code", bd=4).place(x=30, y=5)
            self.data_ent = tk.Entry(field_fra, textvariable=self.strdata)
            self.data_ent.place(x=150, y=5)
            self.data_ent.bind('<KeyRelease>', lambda e: self.check_code("Product", "Select"))

            self.code_tree['columns'] = ('Code', 'Desc', 'GstNo', 'Taxable')
            self.code_tree.column('#0', width=0, stretch=False)
            self.code_tree.column('Code', width=100)
            self.code_tree.column('Desc', width=150)
            self.code_tree.column('GstNo', width=110)
            self.code_tree.column('Taxable', width=70)
            self.code_tree.heading('#0', text='')
            self.code_tree.heading('Code', text='Product code')
            self.code_tree.heading('Desc', text='Description')
            self.code_tree.heading('GstNo', text='Gst No.')
            self.code_tree.heading('Taxable', text='Taxable')

        elif self.seltype == "Narration":
            # in case of narration displaying code, description
            # so that user can pick the narration
            tk.Label(field_fra, text="Code", bd=4).place(x=30, y=5)
            self.data_ent = tk.Entry(field_fra, textvariable=self.strdata)
            self.data_ent.place(x=150, y=5)
            self.data_ent.bind('<KeyRelease>', lambda e: self.check_code("Narration", "Select"))
            self.code_tree['columns'] = ('Code', 'Desc')
            self.code_tree.column('#0', width=0, stretch=False)
            self.code_tree.column('Code', width=80)
            self.code_tree.column('Desc', width=350)
            self.code_tree.heading('Code', text='Code')
            self.code_tree.heading('Desc', text='Description')

        elif self.seltype == "Find":
            # in case of find displaying date, billno and customer code
            # so that user can pick the billno
            tk.Label(field_fra, text="Bill No", bd=4).place(x=30, y=5)
            self.data_ent = tk.Entry(field_fra, textvariable=self.strdata)
            self.data_ent.place(x=150, y=5)
            self.data_ent.bind('<KeyRelease>', lambda e: self.check_code("Find", "Select"))

            wd = 0
            if self.bill_type == "Manual Cash Bill":
                # in case of manual cash bill display only date and billno
                self.code_tree['columns'] = ('Date', 'Bill No')
                wd = 100
            else:
                self.code_tree['columns'] = ('Date', 'Bill No', 'Code')
                wd = 80
                self.code_tree.column('Code', width=180)
                self.code_tree.heading('Code', text='Customer')

            self.code_tree.column('Date', width=wd)
            self.code_tree.column('Bill No', width=wd)
            self.code_tree.heading('Date', text='Date')
            self.code_tree.heading('Bill No', text='Bill No.')

        self.code_tree.column('#0', width=0, stretch=False)
        self.code_tree.heading('#0', text='')
        # attaching scrollbar to the table
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.code_tree.yview)
        self.code_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.code_tree.pack(expand=1)

        # displaying ok and cancel buttons
        tk.Button(self.top, text="OK", underline=0, command=lambda: self.sel_ok()).place(x=200, y=450)
        self.top.bind("<Alt-o>", self.sel_ok)
        tk.Button(self.top, text="Cancel", underline=0, command=lambda: self.sel_cancel()).place(x=250, y=450)
        self.top.bind("<Alt-c>", self.sel_cancel)

        # getting information from the table based on the selection type
        s = ""
        if self.seltype == "Customer":
            s = "select code, description,gstno from customer where code like 'A%' or code like 'L%' and year = '"\
                    + config.Year + "' order by description"
        elif self.seltype == "Product":
            s = "select code, description,HSNCode,taxable from product where code like 'I%' and year = '"\
                    + config.Year + "' order by code"
        elif self.seltype == "Narration":
            s = "select code, description from Narration"
        elif self.seltype == "Find":
            if self.bill_type == "Computer Cash Bill":
                s = "select Date, BillNo, Code, entryno from Transaction where BillNo like 'CCH%' and code not like 'EBRO' " \
                    + " and type = 'D' and year = '" + config.Year + "' order by Date, EntryNo"
            elif self.bill_type == "Manual Cash Bill":
                s = "select Date, BillNo, Code, entryno from Transaction where BillNo like 'MCH%' and code not like 'EBRO' " \
                    + " and type = 'D' and year = '" + config.Year + "' order by Date, EntryNo"
            elif self.bill_type == "Computer Credit Bill":
                s = "select Date, BillNo, Code, entryno from Transaction where BillNo like 'CCR%' and code not like 'EBRO' " \
                    + " and type = 'D' and year = '" + config.Year + "' order by Date, EntryNo"
            elif self.bill_type == "Manual Credit Bill":
                s = "select Date, BillNo, Code, entryno from Transaction where BillNo like 'MCR%' and code not like 'EBRO' " \
                    + " and type = 'D' and year = '" + config.Year + "' order by Date, EntryNo"

        # opens the connection to fetches the list of values to be displayed in the table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        cur.execute(s)
        res = cur.fetchall()
        row = 0
        if len(res) > 0:
            for r in res:
                if type == "Customer":
                    self.code_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1], r[2]))
                elif type == "Product":
                    self.code_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1], r[2], r[3]))
                elif type == "Narration":
                    self.code_tree.insert(parent='', iid=str(row), index=row, text="", values=(r[0], r[1]))
                elif type == "Find":
                    if self.bill_type == "Manual Cash Bill":
                        self.code_tree.insert(parent='', iid=str(row), index=row, text="",
                                              values=(dt.strftime(r[0], "%d-%m-%Y"), r[1]))
                    elif self.bill_type == "Computer Cash Bill":
                        name = r[2].split("+")
                        s = name[0] + " " + name[1]
                        self.code_tree.insert(parent='', iid=str(row), index=row, text="",
                                              values=(dt.strftime(r[0], "%d-%m-%Y"), r[1], s))
                    else:
                        s = r[2]
                        self.code_tree.insert(parent='', iid=str(row), index=row, text="",
                                          values=(dt.strftime(r[0], "%d-%m-%Y"), r[1], s))

                row += 1

        self.strdata.set("")
        self.code_tree.selection_set(str(0))
        self.code_tree.focus_set()

    def sel_ok(self, _event=None):
        # getting the index of the selected item
        index = self.code_tree.focus()
        if index == "":
            # in case no item is selected
            tk.messagebox.showinfo(config.Company_Name, "select an item")
        else:
            # setting the values of the selected item in respected fields
            val = self.code_tree.item(index, "values")
            if self.seltype == "Customer":
                if self.bill_type == "Computer Cash Bill":
                    self.strname1.set(val[1])
                if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
                    self.strcuscode.set(val[0])
                    self.strcusdesc.set(val[1])
                self.strgstno.set(val[2])
                if self.strgstno.get() != "":
                    # setting the gst type according the gst no of the customer
                    s = self.strgstno.get()
                    if s[:2] == "33":
                        # if gstno starts with 33 set gsttype to Intra state
                        self.strgtype.set("Intra")
                    else:
                        # set gsttype to Interstate
                        self.strgtype.set("Inter")
                elif self.strgstno.get() == "":
                    # if no gst no set gsttype to default value Intra state
                    self.strgtype.set("Intra")
            elif self.seltype == "Product":
                self.strprodcode.set(val[0])
                self.strproddesc.set(val[1])
                self.strhsncode.set(val[2])
                self.taxable.set(val[3])
                if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    self.prodrate_ent.focus_set()
                if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    self.prodqty_ent.focus_set()
            elif self.seltype == "Narration":
                self.strnarr.set(val[1])
            elif self.seltype == "Find":

                self.strdate.set(dt.strftime(dt.strptime(val[0], "%d-%m-%Y"), "%d-%m-%Y"))
                self.strbillno.set(val[1])
                i = 0
                for row in self.rec:

                    if row[0] == val[1]:
                        self.currec = i
                        break
                    i += 1
                self.fetch_bill()
            self.top.destroy()

    def sel_cancel(self, _event=None):
        self.top.destroy()

    def get_desc(self, seltype):
        # to get the description of the code entered
        s = ""
        flag = False
        if seltype == "Customer":
            if self.strcuscode.get() != "":
                s = "select Description,GstNo from Customer where Code='" + self.strcuscode.get() + "' and Year = '"\
                    + config.Year + "'"
                flag = True
        elif seltype == "Product":
            if self.strprodcode.get() != "":
                s = "select Description,HSNCode,taxable from Product where Code='" + self.strprodcode.get() \
                    + "' and Year = '" + config.Year + "'"
                flag = True
        elif seltype == "Narration":
            if self.strnarr.get() != "":
                s = "select Description from Narration where Code='" + self.strnarr.get() + "'"
                flag = True

        if flag:
            # opens the connection to fetch the description of the code
            myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
            cur = myconn.cursor()
            cur.execute(s)
            res = cur.fetchall()

            if len(res) > 0:
                # if description for the code entered exists
                # displaying it in the respective controls based on the selection type
                if seltype == "Customer":
                    # in case of customer selection displaying description, gstno and gsttype
                    self.strcusdesc.set(res[0][0])
                    if res[0][1]:
                        self.strgstno.set(res[0][1])
                        # setting the gst type according the gst no of the customer
                        s = self.strgstno.get()
                        if s[:2] == "33":
                            # if gstno starts with 33 set gsttype to Intra state
                            self.strgtype.set("Intra")
                        else:
                            # set gsttype to Interstate
                            self.strgtype.set("Inter")
                    else:
                        self.strgstno.set("")
                        # if no gst no set gsttype to default value Intra state
                        self.strgtype.set("Intra")
                elif seltype == "Product":
                    # in case of product selection displaying description, hsncode and taxability of that product
                    self.strproddesc.set(res[0][0])
                    if res[0][1]:
                        self.strhsncode.set(res[0][1])
                    else:
                        self.strhsncode.set("")
                    self.taxable.set(res[0][2])
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        self.prodrate_ent.focus_set()
                    elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                        self.prodqty_ent.focus_set()
                elif seltype == "Narration":
                    # in case of narration displaying the description
                    self.strnarr.set(res[0][0])
                    self.narr_ent.focus_set()

                #if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    #self.prodqty_ent.focus_set()
                #elif self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    #self.prodrate_ent.focus_set()

            else:
                # displaying respective message as information of the code does not exist
                if self.seltype == "Customer":
                    tk.messagebox.showinfo(config.Company_Name, "No information about the customer verify it")
                    self.strcuscode.set("")
                    self.cuscode_ent.focus_set()
                elif self.seltype == "Product":
                    tk.messagebox.showinfo(config.Company_Name, "No information about the Product verify it")
                    self.strprodcode.set("")
                    self.prodcode_ent.focus_set()
                elif self.seltype == "Narration":
                    tk.messagebox.showinfo(config.Company_Name, "No information about the Narrarion verify it")
                    self.strnarr.set("")
                    self.narr_ent.focus_set()

    def generate_billno(self):
        # generates new billno based on the type of bill in case of addition
        s = ""
        if self.bill_type == "Computer Cash Bill":
            s = "select Distinct BillNo, EntryNo from Transaction where BillNo Like 'CCH%' and Year='" + config.Year \
                + "' order by EntryNo"
        elif self.bill_type == "Manual Cash Bill":
            s = "select Distinct BillNo, EntryNo from Transaction where BillNo Like 'MCH%' and Year='" + config.Year \
                + "' order by EntryNo"
        elif self.bill_type == "Computer Credit Bill":
            s = "select Distinct BillNo, EntryNo from Transaction where BillNo Like 'CCR%' and Year='" + config.Year \
                + "' order by EntryNo"
        elif self.bill_type == "Manual Credit Bill":
            s = "select Distinct BillNo, EntryNo from Transaction where BillNo Like 'MCR%' and Year='" + config.Year \
                + "' order by EntryNo"

        # opens the connection to fetch last billno
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        cur.execute(s)
        res = cur.fetchall()

        if len(res) > 0:
            # additing one to existing bill no
            no = res[len(res) - 1][0]
            n = int(no[3:]) + 1
        else:
            # in case of no bill setting current billno to 1
            n = 1

        # setting the prefix based on the billtype to newly generated billno
        no = ""
        if self.bill_type == "Computer Cash Bill":
            no = "CCH" + str(n)
        elif self.bill_type == "Manual Cash Bill":
            no = "MCH" + str(n)
        elif self.bill_type == "Computer Credit Bill":
            no = "CCR" + str(n)
        elif self.bill_type == "Manual Credit Bill":
            no = "MCR" + str(n)

        self.strbillno.set(no)

    def generate_date(self):
        # setting the date for the new bill to the date of the last bill based on the type
        billno = ""

        if self.bill_type == "Computer Cash Bill":
            billno = "CCH%"
        elif self.bill_type == "Manual Cash Bill":
            billno = "MCH%"
        elif self.bill_type == "Computer Credit Bill":
            billno = "CCR%"
        elif self.bill_type == "Manual Credit Bill":
            billno = "MCR%"
        s = "select Distinct date from Transaction  where BillNo like '" + billno + "' and year = '" \
            + config.Year + "' order by date"

        # opens the connection to fetch the date of the last bill
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        cur.execute(s)
        res = cur.fetchall()

        if len(res) > 0:
            # getting the last bill date
            newdt = res[len(res) - 1][0]
            self.strdate.set(newdt.strftime("%d-%m-%Y"))
        else:
            # setting the new bill date to the first day of the accounting year
            newdt = "01-04-" + config.Year[0:4]
            self.strdate.set(newdt)

    def add(self, _event=None):
        # preparing for adding Bill
        if not self.transflag:
            # if not in trans mode
            self.transflag = True
            self.prodtransflag = False
            self.trans = "Add"
            # clearing the entire form
            self.clear_form("Bill")
            self.set_bill(True)
            self.set_prod(False)
            # generating billno and date for the new bill
            self.generate_billno()
            self.generate_date()
            # setting the gstype to default value Intra state
            self.strgtype.set("Intra")
            self.date_ent.focus_set()
            self.gstflag = False

    def modify(self, _event=None):
        # preparing for modifying records
        if not self.transflag and not self.emptyflag:
            # if not in trans mode
            self.transflag = True
            self.prodtransflag = False
            self.trans = "Mod"
            self.prevBill = self.currec
            #print("modify",self.prevBill)
            # preparing for bill modification
            self.set_bill(True)
            self.set_prod(False)
            self.date_ent.focus_set()

        # setting previous gst type according to the gst type of the current bill before modification
        self.prev_gsttype = ""
        for r in self.prodlst:
            if r[0] == "LIST" or r[0] == "LCST":
                self.prev_gsttype = r[0]

        if self.prev_gsttype == "LIST":
            self.strgtype.set("Inter")
        else:
            self.strgtype.set("Intra")

    def delete(self, _event=None):
        if not self.emptyflag and not self.transflag:
            # cancelling the current bill
            if tk.messagebox.askyesno(config.Company_Name, "Cancel the Bill"):
                s = "Update Transaction set Cancelled = 'Y' where BillNo = '" + self.strbillno.get() + "'"
                # opens the connection to update the cancelation status of the current bill
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()
                cur.execute(s)
                myconn.commit()

                self.clear_form("Bill")
                # moving to the next bill based on the position of the deleted bill
                if self.currec == 0 and self.totrec == 1:
                    # if cancelled bill was the only bill
                    # setting that no bill exists
                    self.currec = -1
                    self.totrec = 0
                elif self.currec == (self.totrec-1):
                    # if the cancelled bill was the last bill
                    # moving the previous bill
                    self.currec -= 1
                    self.fetch_rec(self.rec[self.currec][0])
                    self.fetch_bill()
                else:
                    # if the cancelled bill was in the middle
                    # moving to the next bill
                    self.fetch_rec(self.rec[self.currec][0])
                    self.fetch_bill()
                self.set_bill(False)
                self.set_prod(False)

    def addtotable(self):
        # opens the connection to add the current bill info to the table after validating all info
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        if self.trans == "Mod":
            # in case of modify add the bill details already entered and add the bill as new one
            s = "Delete from transaction where BillNo = '" + self.strbillno.get() + "'"
            cur.execute(s)
            intentryno = self.preventryno
        elif self.trans == "Add":
            # generating the new entry no for the bill to be added
            s = "select distinct EntryNo from Transaction order by EntryNo"
            cur.execute(s)
            res = cur.fetchall()
            if len(res) > 0:
                intentryno = res[len(res) - 1][0] + 1
            else:
                intentryno = 1
        # converting the date of the new bill to the format to be stored in the table
        strdate = dt.strftime(dt.strptime(self.strdate.get(), "%d-%m-%Y"), "%Y-%m-%d")

        code = ""
        if self.bill_type == "Computer Cash Bill":
            # concatenating the names entered in 2 fields as code
            code = self.strname1.get() + " + " + self.strname2.get()
        elif self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            code = self.strcuscode.get()

        # setting narration based on the type of bill
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            narr = self.strnarr.get()
        else:
            # since cash bill has no narration field
            narr = ""

        # adding customer details of the bill to the table
        s = "insert into Transaction (EntryNo,BillNo,Date,Code,Narration,Type,Amount,Cancelled,Year) values(" \
            + str(intentryno) + ", '" + self.strbillno.get() + "','" + strdate + "','" + code + "','" + narr \
            + "','D'," + str(self.strtotamt.get()) + ",'N','" + config.Year + "')"
        cur.execute(s)

        #print(self.prodlst)
        # adding product details of the bill from the product table to the transaction table in database
        for rec in self.prodlst:
            if rec[0][:1] == "I" or rec[0][:1] == "L" or rec[0][:1] == "E":

                #if rec[0][:1] == "E":
                    #ttype = "D"
                #else:
                    #ttype = "C"
                # only details of the product, tax and roundoff to be added
                if rec[0] == "LIST" or rec[0] == "LCST" or rec[0] == "LSST" or rec[0] == "EBRO":
                    # if tax or roundoff info
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        amt = rec[8]
                    if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                        amt = rec[5]

                    s = "insert into Transaction (EntryNo, BillNo, Date, Code, Type,Amount, Cancelled, Year) " \
                        + "values(" + str(intentryno) + ",'" + self.strbillno.get() + "','" + strdate + "','" \
                        + rec[0] + "','C'," + str(amt) + ",'N','" + config.Year + "')"

                else:

                    # if product info that is sales account of the product
                    wt = 0.0
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        if rec[7] != "":
                            wt = rec[7]
                        s = "insert into Transaction values(" + str(intentryno) + ",'" + self.strbillno.get() \
                            + "','" + strdate + "','" + rec[0] + "', ' ', 'C'," + str(rec[4]) + ",'" \
                            + rec[5] + "'," + str(rec[6]) + "," + str(wt) + "," + str(rec[8]) + ",'N','" \
                            + config.Year + "')"
                    elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                        s = "insert into Transaction(Entryno, Billno, Date, Code, Type, Quantity, Amount, Cancelled, Year)" \
                                + " values(" + str(intentryno) + ",'" + self.strbillno.get() \
                                + "','" + strdate + "','" + rec[0] + "', 'C'," + str(rec[4])  \
                                + "," + str(rec[5]) + ",'N','" + config.Year + "')"

                cur.execute(s)
        self.currec += 1
        myconn.commit()

    def check_bill(self):
        # checking customer info entered
        flag = False
        if self.bill_type == "Computer Cash Bill" and self.strname1.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Name cannot be blank")
        elif (self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill") \
                and self.strcuscode.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Select the customer")
            self.cuscode_ent.focus_set()
        elif self.prodtransflag:
            # if product information entered has not been saved
            tk.messagebox.showinfo(config.Company_Name, "Save the product")
        elif self.prodrow == 0:
            # if no product information has been provided
            tk.messagebox.showinfo(config.Company_Name, "No product information")
        else:
            flag = True

        return flag

    def save(self, _event=None):
        if self.transflag and not self.prodtransflag:
            if self.check_bill():
                # if all information has been provided
                self.cal_gst()
                if tk.messagebox.askokcancel(config.Company_Name, "Save Bill"):

                    # adding the entire bill to the transaction table
                    self.addtotable()

                    # setting the form after addition
                    self.clear_form("Bill")
                    self.fetch_rec("")
                    if self.trans == "Mod":
                        self.currec = self.prevBill
                    self.fetch_bill()
                    self.transflag = False
                    self.trans = ""
                    self.set_bill(False)
                    self.set_prod(False)

    def reset(self, _event=None):
        if self.transflag and not self.prodtransflag:
            # clearing the entire bill
            self.clear_form("Bill")
            if self.trans == "Add":
                # generating date for the new bill in case of additon
                self.generate_date()
            else:
                # displaying the original content of the current bill to be modified
                self.fetch_bill()
                #self.strgtype.set(self.prev_gsttype)

            self.set_bill(True)
            self.set_prod(False)

    def cancel(self, _event=None):
        if self.transflag and not self.prodtransflag:
            # cancelling the transaction and setting the bill to the original form
            self.transflag = False
            self.prodtransflag = False
            self.trans = ""
            self.prodtrans = ""
            if self.totrec == 0:
                self.clear_form("Bill")
            else:
                self.fetch_bill()

            self.set_bill(False)
            self.set_prod(False)

    def prod_add(self, _event=None):
        if self.transflag and (not self.prodtransflag):
            # preparing for adding new product
            self.prodtransflag = True
            self.prodtrans = "Add"
            self.clear_prod()
            self.set_prod(True)
            self.taxable.set("")
            self.prodcode_ent.focus_set()
            self.prod_tree.configure(selectmode="none")

    def prod_modify(self, _event=None):
        if self.transflag and (not self.prodtransflag) and (self.prodrow > 0):
            #print("Inside mod")
            ch = self.strprodcode.get()[:1]
            flag = True
            if ch == "L" or ch == "E":
                if not tk.messagebox.askokcancel(config.Company_Name, "Want to change the data?"):
                    flag = False
                    self.prod_cancel()

            if flag:
                self.prodtransflag = True
                self.prodtrans = "Mod"
                self.set_prod(True)
                self.prodcode_ent.focus_set()

    def check_prod(self):
        # validating prodcut details entered
        flag = True
        if self.strprodcode.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "select product")
            self.prodcode_ent.focus_set()
            flag = False
        elif self.strproddesc.get() == "":
            tk.messagebox.showinfo(config.Company_Name, "Invalid product description")
            self.prodcode_ent.focus_set()
            flag = False
        if flag:
            if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                if self.strprodrate.get() == "":
                    tk.messagebox.showinfo(config.Company_Name, "Specify rate of product")
                    self.prodrate_ent.focus_set()
                    flag = False
                elif not config.is_float(self.strprodrate.get()):
                    tk.messagebox.showinfo(config.Company_Name, " Invalid Rate")
                    self.prodrate_ent.focus_set()
                    flag = False
                elif self.strratetype.get() == "A":
                    tk.messagebox.showinfo(config.Company_Name, "Specify rate type")
                    self.ratequt_rd.focus_set()
                    flag = False
                elif (self.strratetype.get() == "Qut" or self.strratetype.get() == "Kg") and self.strprodwt.get() == "":
                    tk.messagebox.showinfo(config.Company_Name, "Specify the weight")
                    self.prodwt_ent.focus_set()
                    flag = False
        if flag:
            if self.strprodqty.get() == "":
                tk.messagebox.showinfo(config.Company_Name, "Specify the quantity")
                self.prodqty_ent.focus_set()
                flag = False
            elif not config.is_float(self.strprodqty.get()):
                tk.messagebox.showinfo(config.Company_Name, " Invalid Quantity")
                self.prodqty_ent.focus_set()
                flag = False

            elif self.strprodamt.get() == "":
                tk.messagebox.showinfo("", "Specify the Amount")
                self.prodamt_ent.focus_set()
                flag = False
            elif not config.is_float(self.strprodamt.get()):
                tk.messagebox.showinfo(config.Company_Name, " Invalid Amount")
                self.prodamt_ent.focus_set()
                flag = False

        if flag:
            # if valid product details are provided check the customer info
            if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
                #  Check if customer has been selected
                if self.strcuscode.get() == "":
                    tk.messagebox.showinfo(config.Company_Name, "Select the customer first")
                    self.cuscode_ent.focus_set()
                    flag = False
            elif self.bill_type == "Computer Cash Bill":
                #  Check if customer has been selected
                if self.strname1.get() == "":
                    tk.messagebox.showinfo(config.Company_Name, "Select the customer first")
                    self.name1_ent.focus_set()
                    flag = False

        if flag:
            # check gst no of the customer
            if self.strgtype.get() != "Inter" and self.strgtype.get() != "Intra":
                tk.messagebox.showinfo(config.Company_Name, "Select the gst type")
                self.Inter_rd.focus_set()
                flag = False
        return flag

    def check_float(self, type):
        # checking rate, quantiy, wt, amount of the product to be numbers and "."
        s = ""
        if type == "Rate":
            s = self.strprodrate.get()
        if type == "Quantity":
            s = self.strprodqty.get()
        if type == "Weight":
            s = self.strprodwt.get()
        if type == "Amount":
            s = self.strprodamt.get()

        lt = len(s)
        for i in range(0, lt):
            if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                tk.messagebox.showinfo("", "only Numbers")
                s1 = s[:i]
                if i <= (lt - 1):
                    s1 = s1 + s[i + 1:]
                s = s1
                break
        if type == "Rate":
            self.strprodrate.set(s)
            self.prodrate_ent.focus_set()
        if type == "Quantity":
            self.strprodqty.set(s)
            self.prodqty_ent.focus_set()
        if type == "Weight":
            self.strprodwt.set(s)
            self.prodwt_ent.focus_set()
        if type == "Amount":
            self.strprodamt.set(s)
            self.prodamt_ent.focus_set()

    """def check_prodqty(self):
        if self.prodtransflag:
            s = self.strprodqty.get()
            lt = len(s)
            for i in range(0, lt):
                if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                    tk.messagebox.showinfo("", "only Numbers")
                    s1 = s[:i]
                    if i <= (lt - 1):
                        s1 = s1 + s[i + 1:]
                    s = s1
                    break
            self.strprodqty.set(s)

    def check_prodwt(self):
        if self.prodtransflag:
            s = self.strprodwt.get()
            lt = len(s)
            for i in range(0, lt):
                if not ((str(0) <= s[i] <= str(9)) or s[i] == "."):
                    tk.messagebox.showinfo("", "only Numbers")
                    s1 = s[:i]
                    if i <= (lt - 1):
                        s1 = s1 + s[i + 1:]
                    s = s1
                    break

            self.strprodwt.set(s)
    """
    def cal_tot(self):
        sum = 0.0
        # calculating the sum of amount of all products
        for r in range(0, self.prodrow):
            if self.prodlst[r][0] != "EBRO":
                #print(self.prodlst[r])
                if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    sum += float(self.prodlst[r][8])
                if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    sum += float(self.prodlst[r][5])


        s = int(sum)
        #n = math.ceil(int(sum)/10)*10
        if sum != s:
            #diffamt = sum - s
            diffamt = s - sum
            lst = []
            flag = False
            for r in range(0, len(self.prodlst)):
                if self.prodlst[r][0] == "EBRO":
                    flag = True
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        self.prodlst[r][8] = diffamt
                    if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                        self.prodlst[r][5] = diffamt

            if not flag:
                if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    lst = ["EBRO", "Bill Round Off", "", "", "", "A", "", "", "{:.2f}".format(diffamt)]
                if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    lst = ["EBRO", "Bill Round Off", "", "", "", "{:.2f}".format(diffamt)]
                self.prodlst.append(lst)

        # setting the bill total to the amount calculated
        self.strtotamt.set(str(s))

    def del_gst(self):
        # deleting gst information from the prodlst
        r = 0
        for row in range(0, self.prodrow):
            if self.prodlst[r][0] == "LIST" or self.prodlst[r][0] == "LCST" or self.prodlst[r][0] == "LSST":
                self.prodlst.pop(r)
            elif self.prodlst[r][0] == "" or self.prodlst[r][0] == "EBRO":
                self.prodlst.pop(r)
            else:
                r += 1
        # setting total prod row to the no of items in the prodlst
        self.prodrow = len(self.prodlst)
        if self.prodrow == 0:
            self.prodcurrec = -1
        else:
            self.prodcurrec = self.prodrow - 1

    def cal_gst(self, _event=None):
        flag = True
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            #  Check if customer has been selected
            if self.strcuscode.get() == "":
                tk.messagebox.showinfo(config.Company_Name, "Select the customer first")
                flag = False
        elif self.bill_type == "Computer Cash Bill":
            #  Check if customer has been selected
            if self.strname1.get() == "":
                tk.messagebox.showinfo(config.Company_Name, "Select the customer first")
                flag = False

        if flag:
            # check gst no of the customer
            if self.strgtype.get() != "Inter" and self.strgtype.get() != "Intra":
                tk.messagebox.showinfo(config.Company_Name, "Select the gst type")
                flag = False

        if flag:
            # get total amount of all taxable product
            total = 0.0
            for p in self.prodlst:
                # check if product is taxable
                ch = p[0][0]
                if ch != "L" and ch != "E":
                    if p[2] == "Y":
                        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                            total += float(p[8])
                        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                            total += float(p[5])

            if total != 0:
                #print("GST",self.gstflag)
                if self.gstflag:
                #if total == 0:
                    self.del_gst()

                gsttype = ""
                if self.strgtype.get() == "Inter":
                    gsttype = "LIST"
                elif self.strgtype.get() == "Intra":
                    gsttype = "LCST"

                # opens the connection to fetch the  percentage of tax from the Gst table
                myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
                cur = myconn.cursor()
                s = "Select * from Gst order by stdate"
                cur.execute(s)
                gstres = cur.fetchall()

                if len(gstres) < 0:
                    tk.messagebox.showerror(config.Company_Name, "NO Gst details available")
                    return False
                else:
                    # getting the latest gst tax from the Gst table
                    curgst = len(gstres) - 1
                    # delete previous gst calculated
                    if self.gstflag:
                        self.del_gst()
                    self.prev_gsttype = gsttype
                    self.gstflag = True

                    if gsttype == "LIST":
                        # Calculate IGST tax and add to the product grid
                        amt = total * (float(gstres[curgst][1]) / 100)
                        self.prodrow += 1
                        gstval = "IGST " + str(gstres[curgst][1]) + "%"
                        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                            lst = ["LIST", gstval, "", "", "", "A", "", "", "{:.2f}".format(amt)]
                        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                            lst = ["LIST", gstval, "", "", "", "{:.2f}".format(amt)]
                        self.prodlst.append(lst)

                    elif gsttype == "LCST":
                        # Calculate CGST tax and add to the product grid
                        amt = total * (float(gstres[curgst][2]) / 100)
                        self.prodrow += 1
                        gstval = "CGST " + str(gstres[curgst][2])  + "%"
                        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                            lst = ["LCST", gstval, "", "", "", "A", "", "", "{:.2f}".format(amt)]
                        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                            lst = ["LCST", gstval, "", "", "", "{:.2f}".format(amt)]

                        self.prodlst.append(lst)
                        # Calculate SGST tax and add to the product grid
                        amt = total * (float(gstres[curgst][3]) / 100)
                        self.prodrow += 1
                        gstval = "SGST " + str(gstres[curgst][3]) + "%"
                        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                            lst = ["LSST", gstval, "", "", "", "A", "", "", "{:.2f}".format(amt)]
                        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                            lst = ["LSST", gstval, "", "", "", "{:.2f}".format(amt)]

                        self.prodlst.append(lst)
            else:
                if self.gstflag:
                    self.del_gst()
                    self.gstflag = False
            # calculating the total of the product and gst
            self.cal_tot()
            self.clear_table()
            self.display_table()
            self.display_prod()
            self.set_prodnavi()

    def cal_amt(self):
        # calculating the amount of each product based on ratetype
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            if self.strratetype.get() == "Unit":
                # if rate type is unit amount is calculated using rate and quanity
                if self.strprodrate.get() != "" and self.strprodqty.get() != "":
                    amt = float(self.strprodrate.get()) * float(self.strprodqty.get())
                    self.strprodamt.set(str(amt))
            if self.strratetype.get() == "Qut" or self.strratetype.get() == "Kg":
                # if rate type is Quintal amount is calculated using rate and weight
                if self.strprodrate.get() != "" and self.strprodwt.get() != "":
                    amt = float(self.strprodrate.get()) * float(self.strprodwt.get())
                    self.strprodamt.set(str(amt))

    def prod_delete(self, _event=None):
        # deleting info the current product
        if self.transflag and (not self.prodtransflag) and (self.prodrow > 0):
            # if in transmode and not in prodtransmode  and some prod info exists
            if tk.messagebox.askyesno(config.Company_Name, "Delete the product"):
                if self.prodlst[self.prodcurrec][0] == "LIST" or self.prodlst[self.prodcurrec][0] == "LCST" \
                        or self.prodlst[self.prodcurrec][0] == "LSST" or self.prodlst[self.prodcurrec][0] == "" \
                        or self.prodlst[self.prodcurrec][0] == "EBRO":
                    tk.messagebox.showinfo(config.Company_Name, "Cannot delete tax information")
                else:
                    self.prodlst.pop(self.prodcurrec)
                    #self.prodtotrow -= 1
                    self.prodrow -= 1
                    self.prodcurrec = self.prodrow -1
                    if self.prodrow <= 0 or (self.gstflag and self.prodrow == 2):
                        # clearing product controls if no prod info exists
                        self.del_gst()
                        self.clear_table()
                        self.clear_prod()
                        self.strtotamt.set("")
                        self.prodtotrow = 0
                        self.prodcurrec = -1
                    else:
                        # calculating new gst for the existing product
                        if self.gstflag:
                            self.cal_gst()
                        self.cal_tot()
                        self.clear_table()
                        self.clear_prod()
                        self.display_prod()
                        self.display_table()

                    self.enable_prodcontrols()
                    self.set_prodnavi()

    def prod_save(self, _event=None):
        if self.transflag and self.prodtransflag:
            # if in transmode and prodtransmode
            save_flag = False
            if self.check_prod():
                # Saving after valid product info is given
                save_flag = True
                if self.prodtrans == "Add":
                    for r in self.prodlst:
                        if r[0] == self.strprodcode.get():
                            save_flag = tk.messagebox.askyesno(config.Company_Name, "Product already added continue Yes or No")

                    lst = []
                    if save_flag:
                        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                            lst = [self.strprodcode.get(), self.strproddesc.get(), self.taxable.get(),
                                   self.strhsncode.get(), float(self.strprodrate.get()), self.strratetype.get(),
                                   self.strprodqty.get(), self.strprodwt.get(), self.strprodamt.get()]
                        if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                            lst = [self.strprodcode.get(), self.strproddesc.get(), self.taxable.get(),
                                   self.strhsncode.get(), self.strprodqty.get(), self.strprodamt.get()]

                        r = 0
                        for r in range(0, self.prodrow):
                            if self.prodlst[r][0][0] == "L":
                                break
                        self.prodrow += 1
                        self.prodlst.insert(r, lst)
                        self.prodtotrow += 1
                        self.prodcurrec = self.prodrow - 1
                    else:
                        # if product already exist and deos not want to save
                        self.prodcode_ent.focus_set()

                elif self.prodtrans == "Mod":
                    # updating product info given to the list
                    self.prodlst[self.prodcurrec][0] = self.strprodcode.get()
                    self.prodlst[self.prodcurrec][1] = self.strproddesc.get()
                    self.prodlst[self.prodcurrec][3] = self.strhsncode.get()
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        self.prodlst[self.prodcurrec][4] = self.strprodrate.get()
                        self.prodlst[self.prodcurrec][5] = self.strratetype.get()
                        self.prodlst[self.prodcurrec][7] = self.strprodwt.get()
                        self.prodlst[self.prodcurrec][6] = self.strprodqty.get()
                        self.prodlst[self.prodcurrec][8] = self.strprodamt.get()
                    else:
                        self.prodlst[self.prodcurrec][4] = self.strprodqty.get()
                        self.prodlst[self.prodcurrec][5] = self.strprodamt.get()
                    #self.clear_table()
                    #self.display_table()

                if save_flag:
                    #self.trans)
                    if self.trans == "Mod":
                        print("recalculatin gst")
                        # if product info has been saved calculate new gst
                        self.cal_gst()
                    self.prod_tree.configure(selectmode="browse")

                    # setting the controls after addtion of product info
                    self.lock_prodcontrols("disabled")
                    self.prodtransflag = False
                    self.prodtrans = ""

                    #print("ebfore")
                    #print(self.prodlst)
                    # calculating the total of the product and gst
                    self.cal_tot()
                    self.clear_table()
                    self.display_table()
                    self.display_prod()

                    self.enable_prodcontrols()
                    self.set_prodnavi()
                    #print("after")
                    #print(self.prodlst)

    def prod_reset(self, _event=None):
        if self.transflag and self.prodtransflag:
            # if in transmode or prodtransmode
            if self.prodtrans == "Add":
                # in case of add clearing product fields
                self.clear_prod()
                self.prodcode_ent.focus_set()
            else:
                # in case of modify displaying original info of the current product
                self.display_prod()
                self.prodcode_ent.focus_set()

    def prod_cancel(self, _event=None):
        if self.transflag and self.prodtransflag:
            # if in transmode and prodtransmode
            self.prodtransflag = False
            if self.prodtrans == "Add":
                if self.prodtotrow > 0:
                    # in case if already product exists display the last one
                    self.display_prod()
                else:
                    # in case if no product info exists clear all the fields
                    self.clear_prod()
                    self.clear_table()
                    self.prodlst.clear()
            elif self.prodtrans == "Mod":
                # in case of modify display the original data
                self.display_prod()

            # setting the controls after cancelling the transaction
            self.prodtrans = ""
            self.enable_prodcontrols()
            self.lock_prodcontrols("disabled")
            self.set_prodnavi()

            self.prod_tree.configure(selectmode="browse")

    def fetch_rec(self, type):
        # get bill details from Transaction table
        billno = ""
        # getting the billno based on the type of transaction

        if self.bill_type == "Computer Cash Bill":
            billno = "CCH%"
        elif self.bill_type == "Manual Cash Bill":
            billno = "MCH%"
        elif self.bill_type == "Computer Credit Bill":
            billno = "CCR%"
        elif self.bill_type == "Manual Credit Bill":
            billno = "MCR%"

        # in case of sales get billno of all sales transaction made for that accounting year
        #s = "select  billno, EntryNo from Transaction where BillNo Like '" + billno + "' and code not like 'E%' and Type='D' and Cancelled = 'N'" \
            #+ " and Year='" + config.Year + "' order by EntryNo"
        s = "select  billno, EntryNo from Transaction where BillNo Like '" + billno + "' and Type='D' and Cancelled = 'N'" \
            + " and Year='" + config.Year + "' order by EntryNo"
        # opens the connection to fetch billno from transaction table
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        cur.execute(s)
        self.rec = cur.fetchall()

        # getting the total no of bills of that type
        self.totrec = len(self.rec)
        #print("total",self.totrec)
        #print(self.rec[self.totrec-1][0])
        if self.totrec != 0:
            # if bills of that transaction type exists
            if type == "Last":
                # if last bill is to be display set current bill to last one
                self.currec = self.totrec - 1
            self.emptyflag = False
        else:
            # if no bills of that transaction type exists
            # set current bill and emptyflag accordingly
            self.currec = -1
            self.emptyflag = True

    def fetch_bill(self):
        # get details of the current billno from Transaction
        s = ""
        if (self.bill_type == "Manual Cash Bill") or (self.bill_type == "Computer Cash Bill"):
            #s = "select date, code, amount, entryno from Transaction where BillNo = '" + self.rec[self.currec][0] + "' and Type='D'" \
                #+ " and code not like 'E%' and Year='" + config.Year + "'"
            s = "select date, code, amount, entryno from Transaction where BillNo = '" + self.rec[self.currec][0] + "' and Type='D'" \
                + " and Year='" + config.Year + "'"
        elif (self.bill_type == "Manual Credit Bill") or (self.bill_type == "Computer Credit Bill"):
            #s = "select t.date,t.code,c.description,c.gstno,t.narration,t.amount, t.entryno from Transaction as t," \
                #+ " customer as c where BillNo ='" + self.rec[self.currec][0] + "' and t.code not like 'E%' and t.code=c.code and Type='D' and t.Year='" \
                #+ config.Year + "'"
            s = "select t.date,t.code,c.description,c.gstno,t.narration,t.amount, t.entryno from Transaction as t," \
                + " customer as c where BillNo ='" + self.rec[self.currec][
                    0] + "' and t.code=c.code and Type='D' and t.Year='" \
                + config.Year + "'"

        # opens the connection to fetch the details of the current bill
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()
        cur.execute(s)
        rec = cur.fetchall()

        # displaying bill,date and amount
        self.strbillno.set(self.rec[self.currec][0])
        self.strdate.set(dt.strftime(rec[0][0], "%d-%m-%Y"))
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            # if credit bill display the customer code,description,narration and amount
            self.strcuscode.set(rec[0][1])
            self.strcusdesc.set(rec[0][2])
            self.strgstno.set(rec[0][3])
            self.strnarr.set(rec[0][4])
            self.strtotamt.set(rec[0][5])
            self.preventryno = rec[0][6]
        elif self.bill_type == "Computer Cash Bill" or self.bill_type == "Manual Cash Bill":
            self.strtotamt.set(rec[0][2])
            self.preventryno = rec[0][3]
            if self.bill_type == "Computer Cash Bill":
                # if computer cash bill spliting names
                no = rec[0][1].find("+")
                self.strname1.set(rec[0][1][:no - 1])
                self.strname2.set(rec[0][1][no + 2:])

        # fetching the product details of that bill
        # and setting the form according to that
        self.fetch_prod("")
        self.set_bill(False)

    def fetch_prod(self, code):
        # fetching  and the product details of current bill
        self.clear_form("Prod")

        # fetching all products and putting in prodlst to be displayed in table and fields area
        # opens the connection to fetch product details
        myconn = con.connect(user='root', password=config.Pwd, host='127.0.0.1', database=config.Db_Name)
        cur = myconn.cursor()

        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            # fetching product details of that bill
            s = "select t.Code, p.Description, p.Taxable, p.HSNcode, t.Rate, t.Ratetype, t.Quantity,t.wt,t.Amount from " \
                + "Transaction as t ,product as p where BillNo='" + str(self.rec[self.currec][0]) + "' " \
                + "and t.code like 'I%' and t.code=p.code and t.Year='" + config.Year + "' " \
                + "and Type='C' order by t.code"
        elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
            # fetching product details of that bill
            s = "select t.Code, p.Description, p.Taxable, p.HSNcode, t.Quantity,t.Amount from " \
                + "Transaction as t ,product as p where BillNo='" + str(self.rec[self.currec][0]) + "' " \
                + "and t.code like 'I%' and t.code=p.code and t.Year='" + config.Year + "' " \
                + "and Type='C' order by t.code"

        cur.execute(s)
        prodres = cur.fetchall()

        # check prod info for that bill
        if len(prodres) == 0:
            tk.messagebox.showinfo(config.Company_Name, "No product info for that bill. check it")
        else:
            # appending all product details to the list for display
            for row in prodres:
                desc = row[1].split("(")
                if len(desc) == 1:
                    prodname=desc[0]
                else:
                    prodname = desc[1][:len(desc[1])-1]
                if self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                    self.prodlst.append([row[0], prodname,  row[2], row[3], row[4], row[5]])
                elif self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                    self.prodlst.append([row[0], prodname,  row[2], row[3], row[4], row[5], row[6], row[7], row[8]])
            # getting the total no of products
            self.prodrow = len(self.prodlst)

            # fetching Gst details of that bill
            s = "select t.code,c.description,t.amount from Transaction as t ,Customer as c where BillNo='" \
                + str(self.rec[self.currec][0]) + "' " + "and t.code like 'L%' and t.code=c.code and t.Year='" \
                + config.Year + "' " + "and Type='C' order by t.code"

            cur.execute(s)
            prodres = cur.fetchall()
            # check gst info for that bill
            if len(prodres) != 0:
                # appending all gst details to the list for display
                for row in prodres:
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        lst = [row[0], row[1], "",  "", "", "", "", "", row[2]]
                    elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                        lst = [row[0], row[1], "", "", "", row[2]]
                    self.prodlst.append(lst)
                    self.prodrow += 1
                    if row[0] == "LIST":
                        self.strgtype.set("Inter")
                    elif row[0] == "LCST" or row[0] == "LSST":
                        self.strgtype.set("Intra")
            else:
                # set gsttype to null if no gst info exists
                self.strgtype.set("A")

            # fetching EBRO details of that bill
            s = "select t.code,c.description,t.amount from Transaction as t ,Customer as c where BillNo='" \
                + str(self.rec[self.currec][0]) + "' " \
                + "and t.code='EBRO' and t.code=c.code and t.Year='" + config.Year + "' " \
                + " order by t.code"
            cur.execute(s)
            prodres = cur.fetchall()

            # check EBRO info for that bill
            if len(prodres) != 0:
                # appending all EBRO details to the list for display
                for row in prodres:
                    if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                        lst = [row[0], row[1], "",  "", "", "", "", "", row[2]]
                    elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
                        lst = [row[0], row[1], "", "", "", row[2]]
                    #lst = [row[0], row[1], "", "", "", "", "", "", row[2]]
                    self.prodlst.append(lst)
                    self.prodrow += 1

            if code == "":
                # fetching first product
                self.prodcurrec = 0
            else:
                # setting current record to a particular product
                for i in range(0, len(self.prodlst)):
                    if self.prodlst[i][0] == code:
                        self.prodcurrec = i
            # self.prodtotrow = len(self.prodlst)
            # displaying product details in table and fields
            self.display_table()
            self.display_prod()

        self.set_prod(False)

    def print(self, _event=None):
        if not self.emptyflag and not self.transflag:
            # if not in transmode and not emptyflag
            self.top = tk.Toplevel(config.Root)
            self.top.geometry("400x200")
            x = config.Root.winfo_x()
            y = config.Root.winfo_y()
            self.top.geometry("+%d+%d" % (x + 500, y + 150))
            self.top.wm_transient(config.Root)
            self.top.grab_set()

            # adding rate radio controls to product transaction frame
            print_fra = ttk.LabelFrame(self.top, text="Bill Type", width=300, height=150)
            print_fra.place(x=40, y=20)
            original_rd = tk.Radiobutton(print_fra, text="Original", variable=self.printtype, value="Original")
            original_rd.place(x=10, y=10)
            duplicate_rd = tk.Radiobutton(print_fra, text="Duplicate", variable=self.printtype, value='Duplicate')
            duplicate_rd.place(x=150, y=10)
            oridup_rd = tk.Radiobutton(print_fra, text="Original & Duplicate", variable=self.printtype,
                                       value="Original & Duplicate")
            oridup_rd.place(x=50, y=50)

            tk.Button(self.top, text="OK", underline=0, command=lambda: self.print_ok()).place(x=150, y=120)
            self.top.bind("<Alt-o>", self.print_ok)
            tk.Button(self.top, text="Cancel", underline=0, command=lambda: self.print_cancel()).place(x=200, y=120)
            self.top.bind("<Alt-c>", self.print_cancel)
            self.printtype.set("A")

    def print_ok(self, _event=None):
        # printing cash or credit bill
        printtype = self.printtype.get()
        print(printtype)
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Manual Cash Bill":
            if printtype == "Original & Duplicate":
                self.cash_bill("Duplicate")
                win32api.ShellExecute(0, "print", "cash_bill.pdf", None, ".", 0)
                self.cash_bill("Original")
                win32api.ShellExecute(0, "print", "cash_bill.pdf", None, ".", 0)
            else:
                self.cash_bill(printtype)
                win32api.ShellExecute(0, "print", "cash_bill.pdf", None, ".", 0)

        elif self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            if printtype == "Original & Duplicate":
                self.credit_bill("Duplicate")
                win32api.ShellExecute(0, "print", "credit_bill.pdf", None, ".", 0)
                self.credit_bill("Original")
                win32api.ShellExecute(0, "print", "credit_bill.pdf", None, ".", 0)
            else:
                self.credit_bill(printtype)
                win32api.ShellExecute(0, "print", "credit_bill.pdf", None, ".", 0)
        self.top.destroy()

    def print_cancel(self, _event=None):
        self.top.destroy()

    def cash_bill(self,printtype):
        # setting paper size of the pdf file
        pdf = config.BillPDF("P", "mm", "A5")
        pdf.add_page()

        pdf.cell(0, 2, txt="  ", ln=1, align="C")
        pdf.set_font("helvetica", size=10, style="B")
        content = "CASH BILL (" + printtype + ")"
        pdf.cell(0, 5, txt=content, ln=1, align="C")

        # adding billno and date in line 5
        billno = self.strbillno.get()
        content = "No. " + billno[:3] + " / " + billno[3:] + " / " + config.Year
        content = ('{:<80}'.format(content))
        content = content + "Date: " + self.strdate.get()
        pdf.set_font("helvetica", size=10)
        pdf.cell(0, 8, txt=content, ln=1)

        # adding customer name and gstno in line 7,8 and 9
        # printing name1
        strtmp = self.strname1.get()
        content = "To: " + strtmp
        pdf.cell(0, 5, txt=content, ln=1)
        # printing name2
        content = "     " + self.strname2.get()
        pdf.cell(0, 5, txt=content, ln=1)
        # printing gstno of the customer
        strtmp = self.strgstno.get()
        print(strtmp)
        content = "Customer GSTIN: " + strtmp
        pdf.cell(0, 5, txt=content, ln=1)
        self.write_pdftable(pdf)
        pdf.output("cash_bill.pdf")

    def write_pdftable(self, pdf):
        pdf.set_font("helvetica", size=10)
        # adding table to display the product details in the bill
        with pdf.table(width=120, col_widths=(30, 10, 12, 14, 14, 18),
            text_align=("LEFT", "CENTER", "RIGHT", "RIGHT", "RIGHT", "RIGHT"),
                borders_layout="NO_HORIZONTAL_LINES") as table:
            headings = table.row()
            headings.cell("Description of goods")
            headings.cell("HSN Code")
            headings.cell("Rate")
            headings.cell("Qty")
            headings.cell("Wt")
            headings.cell("Amount")
            for value in self.prodlst:
                lst = [value[1], value[3], value[4], value[6], value[7], value[8]]
                row = table.row()
                for data in lst:
                    row.cell(str(data))

        with pdf.table(width=120, col_widths=(30, 10, 12, 14, 14, 18),
                 text_align=("LEFT", "CENTER", "RIGHT", "RIGHT", "RIGHT", "RIGHT"), borders_layout="NO_HORIZONTAL_LINES") as total:
            for data_row in self.prod_tree.get_children():
                value = self.prod_tree.item(data_row)['values']
                if value[0] == "Grand Total":
                    trow = total.row()
                    for datum in value:
                        trow.cell(datum)

    def credit_bill(self, printtype):
        # setting paper size of the pdf file
        pdf = config.BillPDFWithFooter("P", "mm", "A5")
        pdf.add_page()

        pdf.cell(0, 2, txt="  ", ln=1, align="C")
        pdf.set_font("helvetica", size=10, style="B")
        content = "CREDIT BILL (" + printtype + ")"
        pdf.cell(0, 5, txt=content, ln=1, align="C")

        # adding billno and date in line 5
        billno = self.strbillno.get()
        content = "No. " + billno[:3] + " / " + billno[3:] + " / " + config.Year
        content = ('{:<80}'.format(content))
        content = content + "Date: " + self.strdate.get()
        pdf.set_font("helvetica", size=10)
        pdf.cell(0, 8, txt=content, ln=1, align="L")

        # adding customer name and gstno in line 7,8 and 9
        # printing name1
        strtmp = self.strcusdesc.get()
        content = "To: " + strtmp
        pdf.cell(10, 5, txt=content, ln=1, align="L")
        # printing gstno of the customer
        strtmp = self.strgstno.get()
        content = "Customer GSTIN: " + strtmp
        pdf.cell(10, 5, txt=content, ln=1, align="L")
        self.write_pdftable(pdf)

        pdf.cell(0, 8, txt="", ln=1, align="C")
        pdf.cell(0, 8, txt="", ln=1, align="C")
        strtmp = "Signature of the Seller"
        content = ('{:<47}'.format(strtmp))
        content = content + "Signature of the Buyer"
        pdf.set_font("helvetica", size=14)
        pdf.cell(10, 8, txt=content, ln=1, align="L")
        pdf.output("credit_bill.pdf")

    def close(self, _event=None):
        if not self.transflag:
            self.tab.destroy()

    def find(self, _event=None):
        if not self.emptyflag and not self.transflag:
            self.get_det("Find")

    def preparing_window(self, tab, bill_type):

        self.tab = tab
        self.bill_type = bill_type

        # creating frame for bill
        #bill_fra = ttk.LabelFrame(tab, width=2100, height=880)
        #bill_fra.place(x=5, y=5)
        # creating frame for fields in Form view
        field_fra = ttk.LabelFrame(tab, width=1450, height=880)
        field_fra.place(x=10, y=10)

        if self.bill_type == "Manual Cash Bill":
            yaxis = 100
        else:
            yaxis = 70

        # adding billno and date
        # adding BillNo controls to field frame
        tk.Label(field_fra, text="Bill No.", bd=4).place(x=30, y=yaxis)
        self.billno_ent = tk.Entry(field_fra, textvariable=self.strbillno)
        self.billno_ent.place(x=130, y=yaxis)

        # adding Date controls to field frame
        tk.Label(field_fra, text="Date", bd=4).place(x=270, y=yaxis)
        self.date_ent = tk.Entry(field_fra, textvariable=self.strdate)
        self.date_ent.place(x=350, y=yaxis)

        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            # adding customer code, desc, narration and amount if credit sales
            # adding CusCode controls to field frame
            tk.Label(field_fra, text="Customer Code", bd=4).place(x=30, y=120)
            self.cuscode_ent = tk.Entry(field_fra, width=15, textvariable=self.strcuscode)
            self.cuscode_ent.place(x=130, y=120)
            self.cuscode_ent.bind('<FocusOut>', lambda e: self.get_desc("Customer"))
            self.cuscode_ent.bind('<KeyRelease>', lambda e: self.check_code("Customer", "Main"))
            self.selcus_bt = tk.Button(field_fra, text="...", command=lambda: self.get_det("Customer"))
            self.selcus_bt.place(x=230, y=120)

            # adding CusDesc controls to field frame
            tk.Label(field_fra, text=" Description", bd=4).place(x=270, y=120)
            self.cusdesc_ent = tk.Entry(field_fra, width=80, textvariable=self.strcusdesc)
            self.cusdesc_ent.place(x=350, y=120)

            # adding Gst No controls to field frame
            tk.Label(field_fra, text="Gst No.", bd=4).place(x=850, y=120)
            self.gstno_ent = tk.Entry(field_fra, width=30, textvariable=self.strgstno)
            self.gstno_ent.place(x=900, y=120)

            # adding Narration controls to field frame
            tk.Label(field_fra, text="Narration", bd=4).place(x=30, y=180)
            self.narr_ent = tk.Entry(field_fra, width=60, textvariable=self.strnarr)
            self.narr_ent.place(x=130, y=180)
            self.narr_ent.bind('<Return>', lambda e: self.get_desc("Narration"))
            self.narr_ent.bind('<KeyRelease>', lambda e: self.check_code("Narration", "Main"))
            self.selnarr_bt = tk.Button(field_fra, text="...", command=lambda: self.get_det("Narration"))
            self.selnarr_bt.place(x=500, y=180)

            # adding TotAmt controls to field frame
            tk.Label(field_fra, text="Total", bd=4).place(x=530, y=180)
            self.totamt_ent = tk.Entry(field_fra, textvariable=self.strtotamt)
            self.totamt_ent.place(x=600, y=180)
        else:
            # in case of cash sales
            # adding Name controls to field frame in case of Computer cash sales
            if self.bill_type == "Computer Cash Bill":
                tk.Label(field_fra, text="Name", bd=4).place(x=30, y=120)
                self.name1_ent = tk.Entry(field_fra, width=75, textvariable=self.strname1)
                self.name1_ent.place(x=130, y=120)
                self.selcus_bt = tk.Button(field_fra, text="...", command=lambda: self.get_det("Customer"))
                self.selcus_bt.place(x=600, y=120)
                self.name2_ent = tk.Entry(field_fra, width=75, textvariable=self.strname2)
                self.name2_ent.place(x=130, y=180)

                # adding TotAmt controls to field frame
                tk.Label(field_fra, text="Total", bd=4).place(x=650, y=180)
                self.totamt_ent = tk.Entry(field_fra, textvariable=self.strtotamt)
                self.totamt_ent.place(x=720, y=180)
            else:
                # adding TotAmt controls to field frame
                tk.Label(field_fra, text="Total", bd=4).place(x=30, y=150)
                self.totamt_ent = tk.Entry(field_fra, textvariable=self.strtotamt)
                self.totamt_ent.place(x=130, y=150)

        x = 0
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Manual Cash Bill":
            x = 650
        elif self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            x = 1150
        # adding gst type radio controls for purchase transaction frame
        gst_fra = ttk.LabelFrame(field_fra, text="Gst Type", width=200, height=70)
        gst_fra.place(x=x, y=100)

        self.Inter_rd = tk.Radiobutton(gst_fra, text="Inter State", variable=self.strgtype, value="Inter")
        self.Inter_rd.place(x=10, y=10)
        self.Intra_rd = tk.Radiobutton(gst_fra, text="Intra State", variable=self.strgtype, value='Intra')
        self.Intra_rd.place(x=100, y=10)

        # creating Navigation buttons
        self.first_bt = tk.Button(field_fra, underline=0, text="First", width=6, command=lambda: self.move_first())
        self.first_bt.place(x=800, y=50)
        config.Root.bind("<Control-f>", self.move_first)
        self.prev_bt = tk.Button(field_fra, underline=0, text="Prev", width=6, command=lambda: self.move_previous())
        self.prev_bt.place(x=850, y=50)
        config.Root.bind("<Control-p>", self.move_previous)
        self.next_bt = tk.Button(field_fra, underline=0, text="Next", width=6, command=lambda: self.move_next())
        self.next_bt.place(x=900, y=50)
        config.Root.bind("<Control-n>", self.move_next)
        self.last_bt = tk.Button(field_fra, underline=0, text="Last", width=6, command=lambda: self.move_last())
        self.last_bt.place(x=950, y=50)
        config.Root.bind("<Control-l>", self.move_last)

        # creating frame for fields in Form view
        prod_fra = ttk.LabelFrame(field_fra, width=1400, height=500)
        prod_fra.place(x=20, y=230)

        # creating frame for the product table
        table_fra = ttk.Frame(prod_fra, width=500, height=5000)
        table_fra.place(x=780, y=20)

        # creating table using treeview for product
        self.prod_tree = ttk.Treeview(table_fra, height=20)
        # setting the column of the table
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            self.prod_tree['columns'] = ('Product', 'HSN', 'Rate', 'Quantity', 'Weight', 'Amount')
        elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
            self.prod_tree['columns'] = ('Product', 'HSN', 'Quantity', 'Amount')

        # setting the width of the columns in the table
        self.prod_tree.column('#0', width=0, stretch=False)
        self.prod_tree.column('Product', width=170)
        self.prod_tree.column('HSN', width=70, anchor=tk.E)
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            self.prod_tree.column('Rate', width=80, anchor=tk.E)
            self.prod_tree.column('Weight', width=70, anchor=tk.E)
        self.prod_tree.column('Quantity', width=70, anchor=tk.E)
        self.prod_tree.column('Amount', width=120, anchor=tk.E)
        # setting the heading for the columns
        self.prod_tree.heading('#0', text='')
        self.prod_tree.heading('Product', text='Product')
        self.prod_tree.heading('HSN', text='HSN Code')
        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
            self.prod_tree.heading('Rate', text='Rate')
            self.prod_tree.heading('Weight', text='Weight')
        self.prod_tree.heading('Quantity', text='Quantity')
        self.prod_tree.heading('Amount', text='Amount')

        # attaching scrollbar to the product table
        treescroll = ttk.Scrollbar(table_fra)
        treescroll.configure(command=self.prod_tree.yview)
        self.prod_tree.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.prod_tree.pack(expand=1)

        # creating frame for Product transaction in Product Frame
        prodtrans_fra = ttk.LabelFrame(prod_fra, width=750, height=400)
        prodtrans_fra.place(x=20, y=20)

        # creating Product Navigation buttons
        self.prodfirst_bt = tk.Button(prodtrans_fra, underline=0, text="First", width=6, command=lambda: self.move_prodfirst())
        self.prodfirst_bt.place(x=500, y=20)
        config.Root.bind("<Alt-f>", self.move_prodfirst)
        self.prodprev_bt = tk.Button(prodtrans_fra, underline=0, text="Prev", width=6, command=lambda: self.move_prodprevious())
        self.prodprev_bt.place(x=550, y=20)
        config.Root.bind("<Alt-p>", self.move_prodprevious)
        self.prodnext_bt = tk.Button(prodtrans_fra, underline=0, text="Next", width=6, command=lambda: self.move_prodnext())
        self.prodnext_bt.place(x=600, y=20)
        config.Root.bind("<Alt-n>", self.move_prodnext)
        self.prodlast_bt = tk.Button(prodtrans_fra, underline=0, text="Last", width=6, command=lambda: self.move_prodlast())
        self.prodlast_bt.place(x=650, y=20)
        config.Root.bind("<Alt-l>", self.move_prodlast)

        # adding ProdCode controls to Product transaction frame
        tk.Label(prodtrans_fra, text="Product Code", bd=4).place(x=20, y=50)
        self.strprodcode = tk.StringVar()
        self.prodcode_ent = tk.Entry(prodtrans_fra, width=15, textvariable=self.strprodcode)
        self.prodcode_ent.place(x=120, y=50)
        self.prodcode_ent.bind('<FocusOut>', lambda e: self.get_desc("Product"))
        self.prodcode_ent.bind('<KeyRelease>', lambda e: self.check_code("Product", "Main"))
        self.selprod_bt = tk.Button(prodtrans_fra, text="...", command=lambda: self.get_det("Product"))
        self.selprod_bt.place(x=220, y=50)

        if self.bill_type == "Computer Cash Bill" or self.bill_type == "Computer Credit Bill":
                #adding ProdDesc controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Description", bd=4).place(x=260, y=50)
            self.strproddesc = tk.StringVar()
            self.proddesc_ent = tk.Entry(prodtrans_fra, width=60, textvariable=self.strproddesc)
            self.proddesc_ent.place(x=340, y=50)

            # adding HSN code controls to Product transaction frame
            tk.Label(prodtrans_fra, text="HSN Code", bd=4).place(x=20, y=100)
            self.strhsncode = tk.StringVar()
            self.prodhsn_ent = tk.Entry(prodtrans_fra, width=40, textvariable=self.strhsncode)
            self.prodhsn_ent.place(x=120, y=100)

            # adding Rate controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Rate", bd=4).place(x=20, y=150)
            self.prodrate_ent = tk.Entry(prodtrans_fra, textvariable=self.strprodrate)
            self.prodrate_ent.place(x=120, y=150)
            self.prodrate_ent.bind('<Return>', lambda e: self.cal_amt())
            self.prodrate_ent.bind('<KeyRelease>', lambda e: self.check_float("Rate"))

            # adding rate radio controls to product transaction frame
            rate_fra = ttk.LabelFrame(prodtrans_fra, text="Rate Type", width=300, height=70)
            rate_fra.place(x=400, y=100)
            self.strratetype = tk.StringVar()
            self.ratequt_rd = tk.Radiobutton(rate_fra, text="Rate per Kg", variable=self.strratetype, value="Kg")
            self.ratequt_rd.place(x=10, y=10)
            self.rateunit_rd = tk.Radiobutton(rate_fra, text="Rate per Unit", variable=self.strratetype, value='Unit')
            self.rateunit_rd.place(x=150, y=10)

            # adding Quantity controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Quantity", bd=4).place(x=20, y=200)
            self.prodqty_ent = tk.Entry(prodtrans_fra, width=20, textvariable=self.strprodqty)
            self.prodqty_ent.place(x=120, y=200)
            self.prodqty_ent.bind('<Return>', lambda e: self.cal_amt())
            self.prodqty_ent.bind('<KeyRelease>', lambda e: self.check_float("Quantity"))

            # adding Weight controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Weight", bd=4).place(x=270, y=200)
            self.prodwt_ent = tk.Entry(prodtrans_fra, width=20, textvariable=self.strprodwt)
            self.prodwt_ent.place(x=340, y=200)
            self.prodwt_ent.bind('<Return>', lambda e: self.cal_amt())
            self.prodwt_ent.bind('<KeyRelease>', lambda e: self.check_float("Weight"))

            # adding Amount controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Amount", bd=4).place(x=490, y=200)
            self.prodamt_ent = tk.Entry(prodtrans_fra, textvariable=self.strprodamt)
            self.prodamt_ent.place(x=560, y=200)
            self.prodamt_ent.bind('<KeyRelease>', lambda e: self.check_float("Amount"))
        elif self.bill_type == "Manual Cash Bill" or self.bill_type == "Manual Credit Bill":
            # adding ProdDesc controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Description", bd=4).place(x=20, y=100)
            self.strproddesc = tk.StringVar()
            self.proddesc_ent = tk.Entry(prodtrans_fra, width=60, textvariable=self.strproddesc)
            self.proddesc_ent.place(x=120, y=100)

            # adding HSN code controls to Product transaction frame
            tk.Label(prodtrans_fra, text="HSN Code", bd=4).place(x=20, y=150)
            self.strhsncode = tk.StringVar()
            self.prodhsn_ent = tk.Entry(prodtrans_fra, width=40, textvariable=self.strhsncode)
            self.prodhsn_ent.place(x=120, y=150)

            # adding Quantity controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Quantity", bd=4).place(x=20, y=200)
            self.prodqty_ent = tk.Entry(prodtrans_fra, width=20, textvariable=self.strprodqty)
            self.prodqty_ent.place(x=120, y=200)
            self.prodqty_ent.bind('<Return>', lambda e: self.cal_amt())
            self.prodqty_ent.bind('<KeyRelease>', lambda e: self.check_float("Quantity"))

            # adding Amount controls to Product transaction frame
            tk.Label(prodtrans_fra, text="Amount", bd=4).place(x=300, y=200)
            self.prodamt_ent = tk.Entry(prodtrans_fra, textvariable=self.strprodamt)
            self.prodamt_ent.place(x=360, y=200)
            self.prodamt_ent.bind('<KeyRelease>', lambda e: self.check_float("Amount"))

        # creating action frame with buttons
        prodaction_fra = ttk.LabelFrame(prodtrans_fra, width=700, height=80)
        prodaction_fra.place(x=20, y=250)

        # creating add,modify and delete buttons
        self.prodadd_bt = tk.Button(prodaction_fra, underline=0, text="Add", width=10, command=lambda: self.prod_add())
        self.prodadd_bt.place(x=20, y=10)
        config.Root.bind("<Alt-a>", self.prod_add)
        self.prodmod_bt = tk.Button(prodaction_fra, underline=0, text="Modify", width=10, command=lambda: self.prod_modify())
        self.prodmod_bt.place(x=100, y=10)
        config.Root.bind("<Alt-m>", self.prod_modify)
        self.proddel_bt = tk.Button(prodaction_fra, underline=0, text="Delete", width=10, command=lambda: self.prod_delete())
        self.proddel_bt.place(x=180, y=10)
        #config.Root.bind("<Alt-d>", self.prod_delete)

        # creating save,reset and cancel buttons
        self.prodsave_bt = tk.Button(prodaction_fra, underline=0, text="Save", width=10, command=lambda: self.prod_save())
        self.prodsave_bt.place(x=280, y=10)
        config.Root.bind("<Alt-s>", self.prod_save)
        self.prodreset_bt = tk.Button(prodaction_fra, underline=0, text="Reset", width=10, command=lambda: self.prod_reset())
        self.prodreset_bt.place(x=360, y=10)
        config.Root.bind("<Alt-r>", self.prod_reset)
        self.prodcancel_bt = tk.Button(prodaction_fra, underline=0, text="Cancel", width=10, command=lambda: self.prod_cancel())
        self.prodcancel_bt.place(x=440, y=10)
        config.Root.bind("<Alt-c>", self.prod_cancel)

        # creating button to calculate Gst
        self.calgst_bt = tk.Button(prodaction_fra, underline=10, text=" Calculate Gst", width=15, command=lambda: self.cal_gst())
        self.calgst_bt.place(x=540, y=10)
        config.Root.bind("<Alt-g>", self.cal_gst)

        # adding all transaction(add,modify and delete)
        # creating action frame with buttons for Purchase
        trans_fra = ttk.LabelFrame(field_fra, width=850, height=80)
        trans_fra.place(x=300, y=750)

        # creating add,modify and delete buttons
        self.add_bt = tk.Button(trans_fra, underline=0, text="Add", width=10, command=lambda: self.add())
        self.add_bt.place(x=40, y=10)
        config.Root.bind("<Control-a>", self.add)
        self.mod_bt = tk.Button(trans_fra, underline=0, text="Modify", width=10, command=lambda: self.modify())
        self.mod_bt.place(x=120, y=10)
        config.Root.bind("<Control-m>", self.modify)
        self.del_bt = tk.Button(trans_fra, underline=0, text="Delete", width=10, command=lambda: self.delete())
        self.del_bt.place(x=200, y=10)
        #config.Root.bind("<Control-d>", self.delete)

        # creating save,reset and cancel buttons
        self.save_bt = tk.Button(trans_fra, underline=0, text="Save", width=10, command=lambda: self.save())
        self.save_bt.place(x=310, y=10)
        config.Root.bind("<Control-s>", self.save)
        self.reset_bt = tk.Button(trans_fra, underline=0, text="Reset", width=10, command=lambda: self.reset())
        self.reset_bt.place(x=390, y=10)
        config.Root.bind("<Control-r>", self.reset)
        self.cancel_bt = tk.Button(trans_fra, underline=0, text="Cancel", width=10, command=lambda: self.cancel())
        self.cancel_bt.place(x=470, y=10)
        config.Root.bind("<Control-c>", self.cancel)

        # creating find and close button
        self.find_bt = tk.Button(trans_fra, underline=1, text="Find", width=10, command=lambda: self.find())
        self.find_bt.place(x=580, y=10)
        config.Root.bind("<Control-i>", self.find)
        self.print_bt = tk.Button(trans_fra, underline=4, text="Print", width=10, command=lambda: self.print())
        self.print_bt.place(x=660, y=10)
        config.Root.bind("<Control-t>", self.print)
        self.close_bt = tk.Button(trans_fra, underline=2, text="Close", width=10, command=lambda: self.close())
        self.close_bt.place(x=740, y=10)
        config.Root.bind("<Control-o>", self.close)

        # Setting TransFlag and TransType
        self.transflag = False
        self.trans = ""

        # Setting Product TransFlag and TransType
        self.prodtransflag = False
        self.prodtrans = ""

        # setting current record number
        self.totrec = 0
        self.currec = -1
        self.prodrow = 0
        self.prodcurrec = 0

        # disabling controls that need not be accessed
        if self.bill_type == "Computer Credit Bill" or self.bill_type == "Manual Credit Bill":
            self.cusdesc_ent.configure(state="disabled")
            self.gstno_ent.configure(state="disabled")
        self.proddesc_ent.configure(state="disabled")
        self.prodhsn_ent.configure(state="disabled")
        self.billno_ent.configure(state="disabled")
        self.totamt_ent.configure(state="disabled")
        self.prod_tree.configure(selectmode="none")

        # fetching records from the Acccode table
        self.transflag = False
        self.prodtransflag = False
        self.prodlst = []

        self.fetch_rec("Last")

        if self.totrec != 0:
            self.fetch_bill()
        else:
            self.set_bill(False)
            self.set_prod(False)
            self.clear_form("Bill")
