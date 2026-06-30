import frappe

def hide_qr_code_field():
    # We want to hide the 'qr_code' field from the UI because the user doesn't need to see the raw file URL
    # But we CANNOT delete it because the backend relies on it for the print format and web pass!
    
    # Check if it's a Custom Field (it usually is if we appended it later)
    if frappe.db.exists("Custom Field", "Visitor Log-qr_code"):
        frappe.db.set_value("Custom Field", "Visitor Log-qr_code", "hidden", 1)
    else:
        # If it's a core DocField, we update it via Property Setter
        frappe.make_property_setter({
            "doctype": "Visitor Log",
            "doctype_or_field": "DocField",
            "fieldname": "qr_code",
            "property": "hidden",
            "value": 1,
            "property_type": "Check"
        })
        
    frappe.clear_cache()
    print("QR Code field successfully hidden from UI!")

if __name__ == "__main__":
    hide_qr_code_field()
