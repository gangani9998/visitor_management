import frappe

def force_apply_visitor_form_fixes():
    # Because these fields are Custom Fields, Property Setter won't work on them!
    # We must explicitly update the tabCustom Field rows in the database.
    
    fixes = [
        {"fieldname": "valid_from", "property": "reqd", "value": 1},
        {"fieldname": "valid_till", "property": "reqd", "value": 1},
        {"fieldname": "purpose_of_visit", "property": "fieldtype", "value": "Autocomplete"},
        {"fieldname": "specify_purpose", "property": "hidden", "value": 1}
    ]
    
    for fix in fixes:
        custom_field = frappe.db.get_value("Custom Field", f"Visitor Log-{fix['fieldname']}", "name")
        if custom_field:
            frappe.db.set_value("Custom Field", custom_field, fix['property'], fix['value'])
            
    # Also verify the Client Script was updated correctly
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    old_script = script_doc.script
    status_filter_code = """
        if (frm.is_new()) {
            frm.set_df_property('status', 'options', 'Expected\\nChecked In');
        } else {
            frm.set_df_property('status', 'options', 'Expected\\nChecked In\\nChecked Out');
        }
    """
    
    if "frm.set_df_property('status'" not in old_script:
        new_script = old_script.replace("refresh: function(frm) {", f"refresh: function(frm) {{\n{status_filter_code}")
        script_doc.script = new_script
        script_doc.save(ignore_permissions=True)
        
    frappe.db.commit()
    frappe.clear_cache()
    print("Forced Custom Field logic updated successfully!")

if __name__ == "__main__":
    force_apply_visitor_form_fixes()
