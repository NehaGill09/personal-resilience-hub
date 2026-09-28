import csv, json
from pathlib import Path
from datetime import datetime
from .database import Database

def snapshot(db: Database):
    return {"generated_at":datetime.now().isoformat(timespec="seconds"),
            "statistics":db.stats(),
            "tasks":db.list_table("tasks"),"documents":db.list_table("documents"),
            "contacts":db.list_table("contacts"),"inventory":db.list_table("inventory"),
            "finances":db.list_table("finances"),"plans":db.list_table("plans")}

def export_json(db,path):
    Path(path).write_text(json.dumps(snapshot(db),indent=2,default=str),encoding="utf-8")
def export_csv(db,path,table):
    rows=db.list_table(table)
    if not rows: Path(path).write_text("",encoding="utf-8"); return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
def export_html(db,path):
    s=db.stats()
    sections=[]
    for table in ("tasks","documents","contacts","inventory","finances","plans"):
        rows=db.list_table(table)
        if not rows: continue
        heads=list(rows[0].keys())
        body="".join("<tr>"+"".join(f"<td>{str(r.get(h,''))}</td>" for h in heads)+"</tr>" for r in rows)
        sections.append(f"<h2>{table.title()}</h2><table><tr>{''.join(f'<th>{h}</th>' for h in heads)}</tr>{body}</table>")
    html=f"""<!doctype html><html><head><meta charset='utf-8'><title>Resilience Hub Report</title>
    <style>body{{font-family:Arial;margin:40px;color:#1f2937}}h1{{color:#0f766e}}table{{border-collapse:collapse;width:100%;margin-bottom:28px}}th,td{{border:1px solid #ddd;padding:7px;font-size:12px;text-align:left}}th{{background:#e6fffa}}</style>
    </head><body><h1>Personal Resilience Hub</h1><p>Generated {s['generated_at']}</p>
    <p>Tasks: {s['tasks']} · Overdue: {s['overdue']} · Expiring documents: {s['expiring']} · Monthly financial load: {s['monthly_essential']}</p>
    {''.join(sections)}</body></html>"""
    Path(path).write_text(html,encoding="utf-8")
