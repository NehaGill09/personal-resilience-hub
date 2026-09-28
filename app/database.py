import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

DB_PATH = Path("resilience_hub.db")

class Database:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.init_schema()

    def init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks(
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL,
          priority TEXT NOT NULL, due_date TEXT, recurrence TEXT DEFAULT 'None',
          status TEXT NOT NULL, notes TEXT, created_at TEXT, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS documents(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL,
          expiry_date TEXT, location TEXT, notes TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS contacts(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, relationship TEXT,
          phone TEXT, email TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS inventory(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, item_type TEXT NOT NULL,
          category TEXT, quantity REAL DEFAULT 1, unit TEXT, expiry_date TEXT,
          replacement_cost REAL DEFAULT 0, location TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS finances(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, amount REAL NOT NULL,
          frequency TEXT NOT NULL, essential INTEGER DEFAULT 1, due_day INTEGER DEFAULT 1, notes TEXT);
        CREATE TABLE IF NOT EXISTS plans(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, scenario TEXT,
          instructions TEXT, meeting_point TEXT, last_reviewed TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        """)
        self.conn.commit()

    def _now(self): return datetime.now().isoformat(timespec="seconds")
    def _rows(self, table, order="id DESC"):
        return [dict(r) for r in self.conn.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()]

    def list_tasks(self, search="", status="All"):
        q="SELECT * FROM tasks WHERE (title LIKE ? OR category LIKE ? OR notes LIKE ?)"
        args=[f"%{search}%"]*3
        if status!="All": q+=" AND status=?"; args.append(status)
        q+=" ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, due_date IS NULL, due_date"
        return [dict(r) for r in self.conn.execute(q,args)]

    def list_table(self, table): return self._rows(table)

    def add(self, table, data):
        data=dict(data); data.pop("id",None)
        if table=="tasks":
            now=self._now(); data.setdefault("created_at",now); data["updated_at"]=now
        cols=", ".join(data); marks=", ".join("?" for _ in data)
        cur=self.conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", list(data.values()))
        self.conn.commit(); return cur.lastrowid

    def update(self, table, row_id, data):
        data=dict(data); data.pop("id",None)
        if table=="tasks": data["updated_at"]=self._now()
        sets=", ".join(f"{k}=?" for k in data)
        self.conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", list(data.values())+[row_id])
        self.conn.commit()

    def delete(self, table, row_id):
        self.conn.execute(f"DELETE FROM {table} WHERE id=?", (row_id,)); self.conn.commit()

    def get(self, table, row_id):
        r=self.conn.execute(f"SELECT * FROM {table} WHERE id=?",(row_id,)).fetchone()
        return dict(r) if r else None

    def stats(self):
        today=date.today(); end=today+timedelta(days=30)
        tasks=self.conn.execute("SELECT * FROM tasks").fetchall()
        docs=self.conn.execute("SELECT * FROM documents").fetchall()
        inv=self.conn.execute("SELECT * FROM inventory").fetchall()
        open_tasks=sum(1 for r in tasks if r["status"]!="Done")
        due=0; overdue=0
        for r in tasks:
            if r["due_date"] and r["status"]!="Done":
                try:
                    d=date.fromisoformat(r["due_date"])
                    if d<=end: due+=1
                    if d<today: overdue+=1
                except ValueError: pass
        expiring=0
        for r in docs:
            if r["expiry_date"]:
                try:
                    if today<=date.fromisoformat(r["expiry_date"])<=end: expiring+=1
                except ValueError: pass
        supply_expiring=0
        for r in inv:
            if r["expiry_date"]:
                try:
                    if today<=date.fromisoformat(r["expiry_date"])<=end: supply_expiring+=1
                except ValueError: pass
        monthly=0
        for r in self.conn.execute("SELECT * FROM finances WHERE essential=1"):
            amt=float(r["amount"])
            monthly += amt if r["frequency"]=="Monthly" else amt/3 if r["frequency"]=="Quarterly" else amt/12 if r["frequency"]=="Yearly" else amt
        return {"tasks":open_tasks,"total_tasks":len(tasks),"due_30":due,"overdue":overdue,
                "documents":len(docs),"expiring":expiring,"inventory":len(inv),
                "supply_expiring":supply_expiring,"monthly_essential":round(monthly,2)}

    def close(self): self.conn.close()
