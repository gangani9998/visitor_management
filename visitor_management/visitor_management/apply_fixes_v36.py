import frappe
import json
import os

def create_link_doctype_and_fix_core():
    # 1. Create the 'Purpose of Visit' DocType
    if not frappe.db.exists("DocType", "Purpose of Visit"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Purpose of Visit",
            "module": "Visitor Management",
            "custom": 1,
            "autoname": "Prompt",
            "fields": [
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Data",
                    "reqd": 0
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1
                },
                {
                    "role": "All",
                    "read": 1, "write": 1, "create": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        
        # Insert defaults
        for purpose in ["Meeting", "Interview", "Delivery", "Vendor", "Industry Visit"]:
            if not frappe.db.exists("Purpose of Visit", purpose):
                frappe.get_doc({"doctype": "Purpose of Visit", "name": purpose}).insert(ignore_permissions=True)
                
    # 2. Modify the core Visitor Log DocType directly!
    visitor_log = frappe.get_doc("DocType", "Visitor Log")
    
    for field in visitor_log.fields:
        if field.fieldname == "valid_from":
            field.reqd = 1
        elif field.fieldname == "valid_till":
            field.reqd = 1
        elif field.fieldname == "purpose_of_visit":
            field.fieldtype = "Link"
            field.options = "Purpose of Visit"
        elif field.fieldname == "specify_purpose":
            field.hidden = 1
            field.reqd = 0 # Ensure it doesn't block saves if hidden
            
    visitor_log.save(ignore_permissions=True)
    
    # 3. Inject the Client Script again, ensuring it runs
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    # Let's ensure the status filter is in the refresh method cleanly
    if "frm.set_df_property('status'" not in script_doc.script:
        new_script = script_doc.script.replace("refresh: function(frm) {", "refresh: function(frm) {\n        if (frm.is_new()) { frm.set_df_property('status', 'options', 'Expected\\nChecked In'); } else { frm.set_df_property('status', 'options', 'Expected\\nChecked In\\nChecked Out'); }")
        script_doc.script = new_script
        script_doc.save(ignore_permissions=True)
        
    frappe.db.commit()
    frappe.clear_cache()
    print("Core DocType updated and Link field created successfully!")

if __name__ == "__main__":
    create_link_doctype_and_fix_core()
