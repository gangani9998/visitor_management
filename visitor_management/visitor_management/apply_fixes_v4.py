import frappe

def reorder_fields():
    doc = frappe.get_doc("DocType", "Visitor Log")
    
    # Extract the fields we want to move
    specify_purpose = None
    set_till_today = None
    
    new_fields = []
    
    # Find and remove them from their current bad positions
    for f in doc.fields:
        if f.fieldname == "specify_purpose":
            specify_purpose = f
        elif f.fieldname == "set_till_today":
            set_till_today = f
            
    if specify_purpose:
        doc.fields.remove(specify_purpose)
    if set_till_today:
        doc.fields.remove(set_till_today)
        
    # Reconstruct the list, inserting at the EXACT physical position
    for f in doc.fields:
        new_fields.append(f)
        if f.fieldname == "purpose_of_visit" and specify_purpose:
            new_fields.append(specify_purpose)
        elif f.fieldname == "valid_till" and set_till_today:
            new_fields.append(set_till_today)
            
    doc.fields = new_fields
    doc.save(ignore_permissions=True)
    frappe.clear_cache(doctype="Visitor Log")
    print("Re-ordered fields perfectly!")

def update_client_script():
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Add Download PDF Button directly to the top bar (no group)
            frm.add_custom_button(__('Download PDF Pass'), function() {
                let print_url = `/api/method/frappe.utils.print_format.download_pdf?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            }).addClass('btn-primary'); // Make it blue and obvious!
            
            // Add WhatsApp button directly to top bar
            if (frm.doc.status === 'Expected') {
                frm.add_custom_button(__('Share via WhatsApp'), function() {
                    if (!frm.doc.phone) {
                        frappe.msgprint(__('Please enter a Phone Number first.'));
                        return;
                    }
                    let text = `Welcome to Shivoham Fabtech Private Limited, ${frm.doc.visitor_name}!\\n\\n`;
                    text += `Here is your Secure Gate Pass:\\n`;
                    text += `Pass Code: *${frm.doc.pass_code}*\\n\\n`;
                    text += `Download Pass: ${window.location.origin}/visitor?token=${frm.doc.secure_token_url}\\n\\n`;
                    text += `Please show this QR Code to the Security Guard for Entry.`;
                    
                    let url = `https://api.whatsapp.com/send?phone=${frm.doc.phone}&text=${encodeURIComponent(text)}`;
                    window.open(url, '_blank');
                });
            }
        }
    },
    set_till_today: function(frm) {
        // Set the value safely using Frappe's datetime utility
        let today = frappe.datetime.get_today(); 
        frm.set_value('valid_till', today + ' 23:59:59')
            .then(() => {
                frappe.show_alert({message: __('Valid Till set to end of today'), indicator: 'green'});
            });
    }
});
"""
    script_doc.script = new_script
    script_doc.save(ignore_permissions=True)
    print("Updated Client Script with top-level buttons and fixed EOD.")

if __name__ == "__main__":
    reorder_fields()
    update_client_script()
