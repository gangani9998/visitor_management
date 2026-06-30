import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def add_remark_field():
    if not frappe.db.exists("Custom Field", "Visitor Log-remark"):
        create_custom_field("Visitor Log", {
            "fieldname": "remark",
            "label": "Remark",
            "fieldtype": "Small Text",
            "insert_after": "btn_open_gate_pass",  # Place it at the very bottom
            "reqd": 0,
            "hidden": 0,
            "allow_on_submit": 1 # Often remarks need to be edited even after submission
        })
        frappe.clear_cache()
        print("Remark field added successfully!")
    else:
        print("Remark field already exists.")

if __name__ == "__main__":
    add_remark_field()
