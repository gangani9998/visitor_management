import frappe
import json

def update_section_label():
    # 1. Update the actual custom field if it's a Custom Field
    custom_field_exists = frappe.db.exists("Custom Field", {"dt": "Visitor Log", "label": "Access & Validity Logic"})
    if custom_field_exists:
        frappe.db.set_value("Custom Field", custom_field_exists, "label", "Access & Validity")
        
    # 2. Update it if it's part of the core DocType JSON
    doc = frappe.get_doc("DocType", "Visitor Log")
    updated = False
    for field in doc.fields:
        if field.label == "Access & Validity Logic":
            field.label = "Access & Validity"
            updated = True
            
    if updated:
        doc.save(ignore_permissions=True)
        
    frappe.clear_cache()
    print("Section Break Label successfully updated to 'Access & Validity'!")

if __name__ == "__main__":
    update_section_label()
