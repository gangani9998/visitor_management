import frappe
from frappe.utils import now

def fix_mandatory_fields_and_regenerate():
    logs = frappe.get_all("Visitor Log")
    for log in logs:
        doc = frappe.get_doc("Visitor Log", log.name)
        
        if doc.purpose_of_visit:
            if not frappe.db.exists("Purpose of Visit", doc.purpose_of_visit):
                frappe.get_doc({
                    "doctype": "Purpose of Visit",
                    "name": doc.purpose_of_visit
                }).insert(ignore_permissions=True)
                
        # Fill missing mandatory fields on old test records so they don't block saving
        if not doc.valid_from:
            doc.valid_from = now()
        if not doc.valid_till:
            doc.valid_till = now()
            
        if doc.pass_code and doc.secure_token_url:
            doc.save(ignore_permissions=True)
            
    frappe.db.commit()
    print("Messages regenerated and old incomplete test records bypassed safely!")

if __name__ == "__main__":
    fix_mandatory_fields_and_regenerate()
