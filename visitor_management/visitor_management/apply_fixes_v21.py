import frappe

def fix_button_order():
    # Because we deleted 'actions_section', the buttons lost their anchor and floated to the top.
    # We must explicitly anchor the first button to 'draft_share_message'
    
    fields = [
        {"name": "btn_open_gate_pass", "after": "draft_share_message"},
        {"name": "btn_copy_message", "after": "btn_open_gate_pass"},
        {"name": "btn_share_via_wa", "after": "btn_copy_message"}
    ]
    
    for f in fields:
        # Check if it's a Custom Field
        custom_field = frappe.db.get_value("Custom Field", f"Visitor Log-{f['name']}", "name")
        if custom_field:
            frappe.db.set_value("Custom Field", custom_field, "insert_after", f['after'])
        else:
            # If it's a core DocField, we use Property Setter
            frappe.make_property_setter({
                "doctype": "Visitor Log",
                "doctype_or_field": "DocField",
                "fieldname": f['name'],
                "property": "insert_after",
                "value": f['after'],
                "property_type": "Data"
            })
            
    frappe.clear_cache()
    print("Fixed button order to sit BELOW the Draft Share Message!")

if __name__ == "__main__":
    fix_button_order()
