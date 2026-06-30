import frappe

def regenerate_tight_messages():
    logs = frappe.get_all("Visitor Log")
    for log in logs:
        doc = frappe.get_doc("Visitor Log", log.name)
        if doc.pass_code and doc.secure_token_url:
            doc.save(ignore_permissions=True)
            
    frappe.db.commit()
    print("Messages generated with tight layout and Visitor Passcode!")

if __name__ == "__main__":
    regenerate_tight_messages()
