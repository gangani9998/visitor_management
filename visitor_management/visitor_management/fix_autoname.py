import frappe

def fix_autoname():
    doc = frappe.get_doc("DocType", "Visitor Log")
    doc.autoname = "VIS-.YYYY.-.#####"
    doc.naming_rule = "Expression (old style)"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Fixed autoname!")

if __name__ == "__main__":
    fix_autoname()
