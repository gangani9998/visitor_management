import frappe

def fix_link_validation_and_regenerate():
    logs = frappe.get_all("Visitor Log")
    for log in logs:
        doc = frappe.get_doc("Visitor Log", log.name)
        
        # If the purpose of visit doesn't exist in the new database, create it!
        if doc.purpose_of_visit:
            if not frappe.db.exists("Purpose of Visit", doc.purpose_of_visit):
                frappe.get_doc({
                    "doctype": "Purpose of Visit",
                    "name": doc.purpose_of_visit
                }).insert(ignore_permissions=True)
                
        if doc.pass_code and doc.secure_token_url:
            doc.save(ignore_permissions=True)
            
    frappe.db.commit()
    print("Messages regenerated and missing DB links safely created!")

if __name__ == "__main__":
    fix_link_validation_and_regenerate()
