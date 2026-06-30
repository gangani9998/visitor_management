import frappe

def fix_pdf_and_whatsapp():
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Fix 1: Use Standard Print View to bypass local PDF generation (wkhtmltopdf) errors on Mac
            frm.page.add_inner_button(__('Open Gate Pass'), function() {
                let print_url = `/printview?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            }).addClass('btn-primary').css({'color': 'white', 'background-color': '#1a4f8b'});
            
            if (frm.doc.status === 'Expected') {
                frm.page.add_inner_button(__('Share WhatsApp'), function() {
                    if (!frm.doc.phone) {
                        frappe.msgprint(__('Please enter a Phone Number first.'));
                        return;
                    }
                    
                    // Fix 2: Format phone number with country code for WhatsApp API
                    let phone = frm.doc.phone.replace(/[^0-9]/g, '');
                    if (phone.length === 10) {
                        phone = '91' + phone; // Default to India country code if exactly 10 digits
                    }
                    
                    let text = `Welcome to Shivoham Fabtech Private Limited, ${frm.doc.visitor_name}!\\n\\n`;
                    text += `Here is your Secure Gate Pass:\\n`;
                    text += `Pass Code: *${frm.doc.pass_code}*\\n\\n`;
                    text += `Download Pass: ${window.location.origin}/visitor?token=${frm.doc.secure_token_url}\\n\\n`;
                    text += `Please show this QR Code to the Security Guard for Entry.`;
                    
                    // Force WhatsApp Web to avoid Mac App Deep-Link crashes
                    let url = `https://web.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(text)}`;
                    window.open(url, '_blank');
                }).addClass('btn-success').css({'color': 'white'});
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
    print("Fixed PDF Print URL and WhatsApp Phone logic!")

if __name__ == "__main__":
    fix_pdf_and_whatsapp()
