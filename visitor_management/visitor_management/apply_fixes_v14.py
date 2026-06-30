import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def add_draft_message_field():
    # Because Visitor Log is a custom DocType in a custom App, it's generally best to add it as a normal field
    # But doing it via Custom Field is safest and quickest dynamically without wiping data!
    create_custom_field("Visitor Log", {
        "fieldname": "draft_share_message",
        "label": "Draft Share Message",
        "fieldtype": "Small Text",
        "insert_after": "gate_pass_qr_code",
        "read_only": 1,
        "description": "Auto-generated copyable message for WhatsApp, Email, or Teams."
    })
    
    # Run a quick update to populate it for existing docs
    logs = frappe.get_all("Visitor Log")
    for log in logs:
        doc = frappe.get_doc("Visitor Log", log.name)
        if doc.pass_code and doc.secure_token_url:
            # Re-trigger save to let controller populate it
            doc.save(ignore_permissions=True)
            
    frappe.db.commit()
    frappe.clear_cache()
    print("Added Draft Share Message field successfully!")

if __name__ == "__main__":
    add_draft_message_field()
