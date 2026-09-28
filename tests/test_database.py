from app.database import Database

def test_database_crud(tmp_path):
    db=Database(tmp_path/"test.db")
    i=db.add("contacts",{"name":"Emergency Contact","relationship":"Family","phone":"123","email":"","notes":""})
    assert db.get("contacts",i)["name"]=="Emergency Contact"
    db.update("contacts",i,{"name":"Updated","relationship":"Family","phone":"456","email":"","notes":""})
    assert db.get("contacts",i)["phone"]=="456"
    db.delete("contacts",i)
    assert db.get("contacts",i) is None
    db.close()

def test_stats(tmp_path):
    db=Database(tmp_path/"stats.db")
    db.add("tasks",{"title":"Insurance renewal","category":"Finance","priority":"High","due_date":"2099-01-01","recurrence":"Yearly","status":"Planned","notes":""})
    assert db.stats()["tasks"]==1
    db.close()
