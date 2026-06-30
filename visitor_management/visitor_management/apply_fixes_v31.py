import frappe

def regenerate_no_emoji_messages():
    logs = frappe.get_all("Visitor Log")
    for log in logs:
        doc = frappe.get_doc("Visitor Log", log.name)
        if doc.pass_code and doc.secure_token_url:
            doc.save(ignore_permissions=True)
            
    frappe.db.commit()
    print("Messages generated without emojis for all passes!")

if __name__ == "__main__":
    regenerate_no_emoji_messages()
