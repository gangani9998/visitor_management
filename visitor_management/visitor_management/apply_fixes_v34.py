import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def apply_visitor_form_fixes():
    # 1. Make Valid From and Valid Till mandatory (reqd = 1)
    # 2. Change Purpose of Visit to Autocomplete so users can type anything OR select from list
    # 3. Hide 'specify_purpose' since Autocomplete makes it obsolete
    
    fixes = [
        {"fieldname": "valid_from", "property": "reqd", "value": 1, "property_type": "Check"},
        {"fieldname": "valid_till", "property": "reqd", "value": 1, "property_type": "Check"},
        {"fieldname": "purpose_of_visit", "property": "fieldtype", "value": "Autocomplete", "property_type": "Select"},
        {"fieldname": "specify_purpose", "property": "hidden", "value": 1, "property_type": "Check"}
    ]
    
    for fix in fixes:
        frappe.make_property_setter({
            "doctype": "Visitor Log",
            "doctype_or_field": "DocField",
            "fieldname": fix["fieldname"],
            "property": "property",
            "value": fix["value"],
            "property_type": fix["property_type"]
        })
        
    # Also update the Client Script to restrict the Status dropdown for New documents
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    old_script = script_doc.script
    
    # We will inject the status filtering into the refresh function
    status_filter_code = """
        if (frm.is_new()) {
            frm.set_df_property('status', 'options', 'Expected\\nChecked In');
        } else {
            frm.set_df_property('status', 'options', 'Expected\\nChecked In\\nChecked Out');
        }
    """
    
    if "frm.set_df_property('status'" not in old_script:
        # Inject right after refresh: function(frm) {
        new_script = old_script.replace("refresh: function(frm) {", f"refresh: function(frm) {{\n{status_filter_code}")
        script_doc.script = new_script
        script_doc.save(ignore_permissions=True)
        
    frappe.clear_cache()
    print("Form logic updated successfully!")

if __name__ == "__main__":
    apply_visitor_form_fixes()
