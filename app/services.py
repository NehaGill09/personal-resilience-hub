from datetime import date

def required(value, label):
    value=str(value or "").strip()
    if not value: raise ValueError(f"{label} is required.")
    return value

def valid_date(value, label="Date"):
    value=str(value or "").strip()
    if not value: return ""
    try: date.fromisoformat(value)
    except ValueError: raise ValueError(f"{label} must use YYYY-MM-DD.")
    return value

def money(value):
    if value in ("", None): return 0.0
    try: return float(str(value).replace(",",""))
    except ValueError: raise ValueError("Amount must be a valid number.")

def positive(value, label):
    n=money(value)
    if n<0: raise ValueError(f"{label} cannot be negative.")
    return n

def task_payload(title, category, priority, due, recurrence, status, notes):
    return {"title":required(title,"Task title"),"category":category or "General",
            "priority":priority,"due_date":valid_date(due,"Due date"),
            "recurrence":recurrence or "None","status":status,"notes":notes or ""}

def document_payload(name, category, expiry, location, notes):
    return {"name":required(name,"Document name"),"category":category or "Identity",
            "expiry_date":valid_date(expiry,"Expiry date"),"location":location or "","notes":notes or ""}

def inventory_payload(name,item_type,category,quantity,unit,expiry,cost,location,notes):
    q=positive(quantity,"Quantity")
    return {"name":required(name,"Item name"),"item_type":item_type,"category":category or "General",
            "quantity":q,"unit":unit or "unit","expiry_date":valid_date(expiry,"Expiry date"),
            "replacement_cost":positive(cost,"Replacement cost"),"location":location or "","notes":notes or ""}

def financial_payload(name,amount,frequency,essential,due_day,notes):
    try: day=int(due_day or 1)
    except ValueError: raise ValueError("Due day must be a number.")
    if not 1<=day<=31: raise ValueError("Due day must be between 1 and 31.")
    return {"name":required(name,"Expense name"),"amount":positive(amount,"Amount"),
            "frequency":frequency,"essential":1 if essential else 0,"due_day":day,"notes":notes or ""}

def plan_payload(name,scenario,instructions,meeting,last_reviewed,notes):
    return {"name":required(name,"Plan name"),"scenario":scenario or "General",
            "instructions":instructions or "","meeting_point":meeting or "",
            "last_reviewed":valid_date(last_reviewed,"Review date"),"notes":notes or ""}
