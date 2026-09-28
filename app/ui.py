import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from datetime import date
from .database import Database
from .services import task_payload, document_payload, inventory_payload, financial_payload, plan_payload
from .reports import export_json, export_csv, export_html

BG="#f4f7f6"; CARD="#ffffff"; TEXT="#173b3a"; ACCENT="#0f766e"; MUTED="#607270"; DANGER="#b42318"

class ResilienceHubApp:
    def __init__(self):
        self.db=Database(); self.root=tk.Tk(); self.root.title("Personal Resilience Hub"); self.root.geometry("1280x800"); self.root.minsize(1100,700)
        self.style=ttk.Style(self.root); self.style.theme_use("clam")
        self.style.configure(".",font=("Segoe UI",10)); self.style.configure("TNotebook",background=BG,borderwidth=0)
        self.style.configure("TNotebook.Tab",padding=(18,9)); self.style.configure("Treeview",rowheight=30,font=("Segoe UI",9))
        self.style.configure("Treeview.Heading",font=("Segoe UI",9,"bold")); self.style.configure("Accent.TButton",font=("Segoe UI",10,"bold"))
        self.build()

    def build(self):
        self.root.configure(bg=BG)
        top=tk.Frame(self.root,bg=TEXT,height=70); top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top,text="Personal Resilience Hub",bg=TEXT,fg="white",font=("Segoe UI",22,"bold")).pack(side="left",padx=24)
        tk.Label(top,text="Plan ahead • protect what matters • stay ready",bg=TEXT,fg="#b9d8d4",font=("Segoe UI",10)).pack(side="left",padx=4)
        ttk.Button(top,text="Export Report",style="Accent.TButton",command=self.export_report).pack(side="right",padx=18)
        self.nb=ttk.Notebook(self.root); self.nb.pack(fill="both",expand=True,padx=18,pady=16)
        self.tabs={}
        self.dashboard=self.make_dashboard(); self.nb.add(self.dashboard,text="  Dashboard  ")
        for key,label in [("tasks","Tasks"),("documents","Documents"),("contacts","Contacts"),("inventory","Home Inventory"),("finances","Finances"),("plans","Emergency Plans")]:
            frame=self.make_table_tab(key); self.nb.add(frame,text=f"  {label}  "); self.tabs[key]=frame
        self.root.protocol("WM_DELETE_WINDOW",self.close); self.refresh_all()

    def make_dashboard(self):
        f=tk.Frame(self.nb,bg=BG); self.cards=tk.Frame(f,bg=BG); self.cards.pack(fill="x",pady=(8,14))
        self.card_vars={}
        for key,title in [("tasks","Open Tasks"),("due_30","Due in 30 Days"),("overdue","Overdue"),("expiring","Docs Expiring"),("monthly_essential","Monthly Financial Load")]:
            c=tk.Frame(self.cards,bg=CARD,highlightthickness=1,highlightbackground="#d9e5e3"); c.pack(side="left",fill="both",expand=True,padx=5)
            tk.Label(c,text=title,bg=CARD,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=14,pady=(12,2))
            v=tk.StringVar(); self.card_vars[key]=v; tk.Label(c,textvariable=v,bg=CARD,fg=ACCENT,font=("Segoe UI",22,"bold")).pack(anchor="w",padx=14,pady=(0,12))
        lower=tk.Frame(f,bg=BG); lower.pack(fill="both",expand=True)
        left=tk.Frame(lower,bg=CARD); left.pack(side="left",fill="both",expand=True,padx=(5,8))
        tk.Label(left,text="Readiness checklist",bg=CARD,fg=TEXT,font=("Segoe UI",13,"bold")).pack(anchor="w",padx=16,pady=14)
        self.dash_tree=ttk.Treeview(left,columns=("priority","due","status"),show="headings")
        for col,title,w in [("priority","Priority",100),("due","Due",120),("status","Status",110)]: self.dash_tree.heading(col,text=title); self.dash_tree.column(col,width=w)
        self.dash_tree.pack(fill="both",expand=True,padx=12,pady=(0,12))
        right=tk.Frame(lower,bg=TEXT,width=320); right.pack(side="right",fill="y",padx=(8,5)); right.pack_propagate(False)
        tk.Label(right,text="Today’s focus",bg=TEXT,fg="white",font=("Segoe UI",15,"bold")).pack(anchor="w",padx=20,pady=(22,8))
        self.focus=tk.StringVar(); tk.Label(right,textvariable=self.focus,bg=TEXT,fg="#cde4e0",justify="left",wraplength=275,font=("Segoe UI",10)).pack(anchor="w",padx=20)
        ttk.Button(right,text="Add a task",command=lambda:self.open_form("tasks")).pack(anchor="w",padx=20,pady=20)
        return f

    def make_table_tab(self,table):
        f=tk.Frame(self.nb,bg=BG); bar=tk.Frame(f,bg=BG); bar.pack(fill="x",pady=(5,10))
        ttk.Button(bar,text=f"+ Add {table[:-1].title()}",command=lambda:self.open_form(table)).pack(side="left")
        ttk.Button(bar,text="Refresh",command=self.refresh_all).pack(side="left",padx=8)
        ttk.Button(bar,text="Delete Selected",command=lambda:self.delete_selected(table)).pack(side="right")
        if table=="tasks":
            self.search=tk.StringVar(); ttk.Entry(bar,textvariable=self.search,width=30).pack(side="right",padx=8); ttk.Label(bar,text="Search",background=BG).pack(side="right")
        cols={
        "tasks":[("title","Task",260),("category","Category",130),("priority","Priority",90),("due_date","Due",110),("status","Status",100)],
        "documents":[("name","Document",220),("category","Category",120),("expiry_date","Expiry",110),("location","Location",180)],
        "contacts":[("name","Name",180),("relationship","Relationship",140),("phone","Phone",150),("email","Email",220)],
        "inventory":[("name","Item",190),("item_type","Type",110),("quantity","Qty",70),("expiry_date","Expiry",110),("location","Location",150)],
        "finances":[("name","Expense",200),("amount","Amount",100),("frequency","Frequency",100),("essential","Essential",90),("due_day","Due Day",80)],
        "plans":[("name","Plan",190),("scenario","Scenario",140),("meeting_point","Meeting Point",180),("last_reviewed","Reviewed",110)]
        }[table]
        tree=ttk.Treeview(f,columns=[c[0] for c in cols],show="headings",selectmode="browse")
        for c,t,w in cols: tree.heading(c,text=t); tree.column(c,width=w)
        tree.pack(fill="both",expand=True)
        tree.bind("<Double-1>",lambda e,t=table:self.edit_selected(t))
        setattr(self,table+"_tree",tree); return f

    def refresh_all(self):
        s=self.db.stats()
        for k,v in self.card_vars.items(): v.set(f"{s[k]:,.2f}" if k=="monthly_essential" else str(s[k]))
        for table in self.tabs: self.refresh_table(table)
        for x in self.dash_tree.get_children(): self.dash_tree.delete(x)
        for r in self.db.list_tasks()[:12]:
            if r["status"]!="Done": self.dash_tree.insert("", "end",values=(r["priority"],r["due_date"] or "—",r["status"]))
        if s["overdue"]: msg=f"{s['overdue']} task(s) are overdue. Start there."
        elif s["due_30"]: msg=f"{s['due_30']} task(s) are due within 30 days."
        elif s["expiring"]: msg=f"{s['expiring']} document(s) expire within 30 days."
        else: msg="No urgent items detected. Add your key documents, contacts, supplies and plans to build your baseline."
        self.focus.set(msg)

    def refresh_table(self,table):
        tree=getattr(self,table+"_tree"); rows=self.db.list_tasks(self.search.get() if table=="tasks" else "") if table=="tasks" else self.db.list_table(table)
        tree.delete(*tree.get_children())
        maps={
        "tasks":["title","category","priority","due_date","status"],
        "documents":["name","category","expiry_date","location"],
        "contacts":["name","relationship","phone","email"],
        "inventory":["name","item_type","quantity","expiry_date","location"],
        "finances":["name","amount","frequency","essential","due_day"],
        "plans":["name","scenario","meeting_point","last_reviewed"]}
        for r in rows: tree.insert("", "end",iid=str(r["id"]),values=[r.get(k,"") for k in maps[table]])

    def delete_selected(self,table):
        tree=getattr(self,table+"_tree"); sel=tree.selection()
        if not sel: messagebox.showinfo("Select an item","Choose a row first."); return
        if messagebox.askyesno("Confirm deletion","Delete the selected item?"):
            self.db.delete(table,int(sel[0])); self.refresh_all()

    def edit_selected(self,table):
        tree=getattr(self,table+"_tree"); sel=tree.selection()
        if sel: self.open_form(table,int(sel[0]))

    def fields_for(self,table,row):
        defs={
        "tasks":[("title","Title"),("category","Category"),("priority","Priority"),("due_date","Due date (YYYY-MM-DD)"),("recurrence","Recurrence"),("status","Status"),("notes","Notes")],
        "documents":[("name","Name"),("category","Category"),("expiry_date","Expiry date"),("location","Storage location"),("notes","Notes")],
        "contacts":[("name","Name"),("relationship","Relationship"),("phone","Phone"),("email","Email"),("notes","Notes")],
        "inventory":[("name","Name"),("item_type","Type"),("category","Category"),("quantity","Quantity"),("unit","Unit"),("expiry_date","Expiry date"),("replacement_cost","Replacement cost"),("location","Location"),("notes","Notes")],
        "finances":[("name","Expense name"),("amount","Amount"),("frequency","Frequency"),("essential","Essential (yes/no)"),("due_day","Due day (1-31)"),("notes","Notes")],
        "plans":[("name","Plan name"),("scenario","Scenario"),("instructions","Instructions"),("meeting_point","Meeting point"),("last_reviewed","Last reviewed"),("notes","Notes")]}[table]
        return defs

    def open_form(self,table,row_id=None):
        row=self.db.get(table,row_id) if row_id else {}
        win=tk.Toplevel(self.root); win.title(("Edit " if row_id else "Add ")+table[:-1].title()); win.geometry("560x620"); win.transient(self.root); win.grab_set()
        frm=tk.Frame(win,bg=BG); frm.pack(fill="both",expand=True,padx=20,pady=18); vars={}
        for key,label in self.fields_for(table,row):
            tk.Label(frm,text=label,bg=BG,fg=TEXT).pack(anchor="w",pady=(6,2))
            if key=="notes" or key in ("instructions",):
                w=tk.Text(frm,height=4,width=60); w.insert("1.0",str(row.get(key,""))); w.pack(fill="x"); vars[key]=w
            else:
                var=tk.StringVar(value=str(row.get(key,""))); w=ttk.Entry(frm,textvariable=var); w.pack(fill="x"); vars[key]=var
        def value(k):
            w=vars[k]; return w.get("1.0","end-1c") if isinstance(w,tk.Text) else w.get()
        def save():
            try:
                if table=="tasks": data=task_payload(value("title"),value("category"),value("priority"),value("due_date"),value("recurrence"),value("status"),value("notes"))
                elif table=="documents": data=document_payload(value("name"),value("category"),value("expiry_date"),value("location"),value("notes"))
                elif table=="inventory": data=inventory_payload(value("name"),value("item_type"),value("category"),value("quantity"),value("unit"),value("expiry_date"),value("replacement_cost"),value("location"),value("notes"))
                elif table=="finances": data=financial_payload(value("name"),value("amount"),value("frequency"),value("essential").lower() in ("yes","y","true","1"),value("due_day"),value("notes"))
                elif table=="plans": data=plan_payload(value("name"),value("scenario"),value("instructions"),value("meeting_point"),value("last_reviewed"),value("notes"))
                else: data={k:value(k) for k,_ in self.fields_for(table,row)}
                if row_id: self.db.update(table,row_id,data)
                else: self.db.add(table,data)
                win.destroy(); self.refresh_all()
            except ValueError as e: messagebox.showerror("Check your entry",str(e),parent=win)
        ttk.Button(frm,text="Save",style="Accent.TButton",command=save).pack(side="right",pady=18)
        ttk.Button(frm,text="Cancel",command=win.destroy).pack(side="right",padx=8,pady=18)

    def export_report(self):
        path=filedialog.asksaveasfilename(defaultextension=".html",filetypes=[("HTML report","*.html"),("JSON backup","*.json")])
        if not path:return
        try:
            if path.lower().endswith(".json"): export_json(self.db,path)
            else: export_html(self.db,path)
            messagebox.showinfo("Export complete",f"Saved to:\n{path}")
        except Exception as e: messagebox.showerror("Export failed",str(e))

    def close(self): self.db.close(); self.root.destroy()
    def run(self): self.root.mainloop()
