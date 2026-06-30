import frappe
import json

def fix_visitor_system_v3():
    # 1. Add "Specify Purpose" field
    if not frappe.db.exists("DocField", {"parent": "Visitor Log", "fieldname": "specify_purpose"}):
        doc = frappe.get_doc("DocType", "Visitor Log")
        doc.append("fields", {
            "fieldname": "specify_purpose",
            "fieldtype": "Data",
            "label": "Specify Purpose",
            "depends_on": "eval:doc.purpose_of_visit == 'Other'",
            "insert_after": "purpose_of_visit"
        })
        doc.save(ignore_permissions=True)
        print("Added Specify Purpose field.")

    # 2. Fix Client Script for Valid Till EOD and Add Download PDF button
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        // Show the WhatsApp Share button if we have a phone number and it's expected
        if (!frm.is_new() && frm.doc.status === 'Expected') {
            frm.add_custom_button(__('Share Gate Pass (WhatsApp)'), function() {
                if (!frm.doc.phone) {
                    frappe.msgprint(__('Please enter a Phone Number first.'));
                    return;
                }
                
                let text = `Welcome to Shivoham Fabtech Private Limited, ${frm.doc.visitor_name}!\\n\\n`;
                text += `Here is your Secure Gate Pass for your visit:\\n`;
                text += `Pass Code: *${frm.doc.pass_code}*\\n\\n`;
                text += `View & Download Pass: ${window.location.origin}/visitor?token=${frm.doc.secure_token_url}\\n\\n`;
                text += `As per our Security protocol, please show this QR Code to the Security Guard for Entry.`;
                
                let url = `https://api.whatsapp.com/send?phone=${frm.doc.phone}&text=${encodeURIComponent(text)}`;
                window.open(url, '_blank');
            }, __('Actions'));
        }
        
        // Add Download PDF Button so they don't have to search for the Print icon!
        if (!frm.is_new()) {
            frm.add_custom_button(__('Download PDF Pass'), function() {
                let print_url = `/api/method/frappe.utils.print_format.download_pdf?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            }, __('Actions'));
        }
    },
    set_till_today: function(frm) {
        // Fix for the EOD Button
        let today_eod = frappe.datetime.now_date() + ' 23:59:59';
        frm.set_value('valid_till', today_eod);
        frm.refresh_field('valid_till');
        frappe.show_alert({message: __('Valid Till set to end of today'), indicator: 'green'});
    }
});
"""
    script_doc.script = new_script
    script_doc.save(ignore_permissions=True)
    frappe.clear_cache(doctype="Visitor Log")
    print("Fixed EOD Script, Added Specify Purpose, and Added Download PDF button.")

if __name__ == "__main__":
    fix_visitor_system_v3()
