import frappe

def fix_all_ui_issues():
    # 1. FIX THE LAYOUT BY RE-INDEXING FIELDS
    doc = frappe.get_doc("DocType", "Visitor Log")
    
    # Extract fields
    specify_purpose = next((f for f in doc.fields if f.fieldname == "specify_purpose"), None)
    set_till_today = next((f for f in doc.fields if f.fieldname == "set_till_today"), None)
    
    if specify_purpose: doc.fields.remove(specify_purpose)
    if set_till_today: doc.fields.remove(set_till_today)
    
    new_fields = []
    
    for f in doc.fields:
        new_fields.append(f)
        if f.fieldname == "purpose_of_visit" and specify_purpose:
            new_fields.append(specify_purpose)
        elif f.fieldname == "valid_till" and set_till_today:
            new_fields.append(set_till_today)
            
    # CRITICAL: Re-assign the fields back to doc and force the idx update!
    doc.fields = new_fields
    for i, field in enumerate(doc.fields):
        field.idx = i + 1
        
    doc.save(ignore_permissions=True)
    frappe.clear_cache(doctype="Visitor Log")

    # 2. FIX THE BUTTONS & SCRIPTS
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Using page.add_inner_button forces the button to appear on the top right bar visibly!
            frm.page.add_inner_button(__('Download PDF Pass'), function() {
                let print_url = `/api/method/frappe.utils.print_format.download_pdf?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            }).addClass('btn-primary').css({'color': 'white', 'background-color': '#1a4f8b'});
            
            if (frm.doc.status === 'Expected') {
                frm.page.add_inner_button(__('Share WhatsApp'), function() {
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
                }).addClass('btn-success').css({'color': 'white'});
            }
        }
    },
    set_till_today: function(frm) {
        // Fix EOD setting
        let today = frappe.datetime.get_today(); 
        frm.set_value('valid_till', today + ' 23:59:59');
        frm.refresh_field('valid_till');
        frappe.show_alert({message: __('Valid Till set to end of today'), indicator: 'green'});
    }
});
"""
    script_doc.script = new_script
    script_doc.save(ignore_permissions=True)
    frappe.clear_cache()
    print("Fixed layout (updated idx) and updated buttons (using page.add_inner_button)!")

if __name__ == "__main__":
    fix_all_ui_issues()
