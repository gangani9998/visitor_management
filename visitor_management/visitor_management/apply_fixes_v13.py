import frappe

def revert_button_colors():
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Native Frappe button style (removing raw CSS injections)
            frm.page.add_inner_button(__('Open Gate Pass'), function() {
                let print_url = `/printview?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            });
            
            if (frm.doc.status === 'Expected') {
                frm.page.add_inner_button(__('Share via WA'), function() {
                    if (!frm.doc.phone) {
                        frappe.msgprint(__('Please enter a Phone Number first.'));
                        return;
                    }
                    let phone = frm.doc.phone.replace(/[^0-9]/g, '');
                    let country = frappe.boot.sysdefaults.country || "India";
                    if (phone.length === 10) {
                        if (country === "India") {
                            phone = '91' + phone;
                        } else if (country === "United States") {
                            phone = '1' + phone;
                        } else if (country === "United Arab Emirates") {
                            phone = '971' + phone;
                        }
                    }
                    let text = `Welcome to Shivoham Fabtech Private Limited, ${frm.doc.visitor_name}!\\n\\n`;
                    text += `Here is your Secure Gate Pass:\\n`;
                    text += `Pass Code: *${frm.doc.pass_code}*\\n\\n`;
                    text += `Download Pass: ${window.location.origin}/visitor?token=${frm.doc.secure_token_url}\\n\\n`;
                    text += `Please show this QR Code to the Security Guard for Entry.`;
                    
                    let url = `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
                    window.open(url, '_blank');
                });
            }
        }
    },
    set_till_today: function(frm) {
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
    print("Reverted to native Frappe button styles!")

if __name__ == "__main__":
    revert_button_colors()
