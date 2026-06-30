import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def apply_ui_tweaks():
    # 1. Hide Check-Out Time on New documents
    frappe.db.set_value("DocField", {"parent": "Visitor Log", "fieldname": "check_out_time"}, "depends_on", "eval:doc.status == 'Checked Out'")
    frappe.db.set_value("DocField", {"parent": "Visitor Log", "fieldname": "check_in_time"}, "depends_on", "eval:doc.status != 'Expected'")
    
    # 2. Add 'Set Till Today' button if it doesn't exist
    if not frappe.db.exists("DocField", {"parent": "Visitor Log", "fieldname": "set_till_today"}):
        doc = frappe.get_doc("DocType", "Visitor Log")
        
        # Find index of valid_till to insert after
        idx = 0
        for i, field in enumerate(doc.fields):
            if field.fieldname == "valid_till":
                idx = i
                break
                
        doc.append("fields", {
            "fieldname": "set_till_today",
            "fieldtype": "Button",
            "label": "Set Till EOD Today",
            "insert_after": "valid_till"
        })
        
        # re-sort the fields based on insert_after is handled nicely if we just save
        doc.save(ignore_permissions=True)
        print("Added 'Set Till Today' button to Visitor Log.")

    # 3. Update Client Script to handle the button
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    if "set_till_today: function(frm)" not in script_doc.script:
        new_script = script_doc.script + """
frappe.ui.form.on('Visitor Log', {
    set_till_today: function(frm) {
        // Set to end of day today
        let today = frappe.datetime.get_today() + ' 23:59:59';
        frm.set_value('valid_till', today);
        frappe.show_alert({message: __('Valid Till set to end of today'), indicator: 'green'});
    }
});
"""
        script_doc.script = new_script
        script_doc.save(ignore_permissions=True)
        print("Updated Client Script with Set Till Today logic.")

    frappe.db.commit()

if __name__ == "__main__":
    apply_ui_tweaks()
