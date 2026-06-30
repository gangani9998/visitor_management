import frappe

def update_security_passes_label():
    # 1. Update the actual custom field if it's a Custom Field
    custom_field_exists = frappe.db.exists("Custom Field", {"dt": "Visitor Log", "label": "Security Passes (Auto-Generated)"})
    if custom_field_exists:
        frappe.db.set_value("Custom Field", custom_field_exists, "label", "Digital Gate Pass Details")
        
    # 2. Update it if it's part of the core DocType JSON
    doc = frappe.get_doc("DocType", "Visitor Log")
    updated = False
    for field in doc.fields:
        if field.label == "Security Passes (Auto-Generated)":
            field.label = "Digital Gate Pass Details"
            updated = True
            
    if updated:
        doc.save(ignore_permissions=True)
        
    frappe.clear_cache()
    print("Section Break Label successfully updated to 'Digital Gate Pass Details'!")

if __name__ == "__main__":
    update_security_passes_label()
