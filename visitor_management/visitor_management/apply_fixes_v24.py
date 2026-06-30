import frappe

def reorder_buttons_to_user_spec():
    # The user wants this specific order:
    # 1. Copy Message
    # 2. Share via WA
    # 3. Open Gate Pass
    
    fields = [
        {"name": "btn_copy_message", "after": "draft_share_message"},
        {"name": "btn_share_via_wa", "after": "btn_copy_message"},
        {"name": "btn_open_gate_pass", "after": "btn_share_via_wa"}
    ]
    
    for f in fields:
        custom_field = frappe.db.get_value("Custom Field", f"Visitor Log-{f['name']}", "name")
        if custom_field:
            frappe.db.set_value("Custom Field", custom_field, "insert_after", f['after'])
        else:
            frappe.make_property_setter({
                "doctype": "Visitor Log",
                "doctype_or_field": "DocField",
                "fieldname": f['name'],
                "property": "insert_after",
                "value": f['after'],
                "property_type": "Data"
            })
            
    frappe.clear_cache()
    print("Buttons successfully reordered to User spec!")

if __name__ == "__main__":
    reorder_buttons_to_user_spec()
