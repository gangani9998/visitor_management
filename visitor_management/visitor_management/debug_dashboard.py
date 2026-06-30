import frappe
from frappe.utils import today, get_datetime

def test_dashboard():
    today_date = today()
    print("today_date:", today_date)
    result = frappe.get_all("Visitor Log", filters={
        "valid_from": ["<=", today_date + " 23:59:59"],
        "valid_till": [">=", today_date + " 00:00:00"]
    }, fields=["name", "visitor_name", "status"])
    print("result:", result)

if __name__ == "__main__":
    test_dashboard()
