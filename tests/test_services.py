import pytest
from app.services import valid_date, money, task_payload, financial_payload

def test_valid_date():
    assert valid_date("2026-09-29")=="2026-09-29"
    with pytest.raises(ValueError): valid_date("29/09/2026")

def test_money():
    assert money("12,500")==12500
    with pytest.raises(ValueError): money("abc")

def test_task_required():
    with pytest.raises(ValueError): task_payload("","","Medium","","None","Planned","")

def test_financial_due_day():
    with pytest.raises(ValueError): financial_payload("Rent","100","Monthly",True,32,"")
