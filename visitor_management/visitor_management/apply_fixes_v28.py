import frappe

def regenerate_final_wording_messages():
    logs = frappe.get_all("Visitor Log")
    for log in logs:
        doc = frappe.get_doc("Visitor Log", log.name)
        if doc.pass_code and doc.secure_token_url:
            # Triggering a save will run validate() and generate the newly combined message
            doc.save(ignore_permissions=True)
            
    frappe.db.commit()
    print("Final worded messages generated for all passes!")

if __name__ == "__main__":
    regenerate_final_wording_messages()
