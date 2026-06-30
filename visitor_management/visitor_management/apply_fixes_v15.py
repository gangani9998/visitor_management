import frappe

def fix_message_and_add_copy_button():
    # 1. Update Client Script to add "Copy Message" button
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.page.add_inner_button(__('Open Gate Pass'), function() {
                let print_url = `/printview?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            });
            
            // NEW Copy Button!
            if (frm.doc.draft_share_message) {
                frm.page.add_inner_button(__('Copy Message'), function() {
                    frappe.utils.copy_to_clipboard(frm.doc.draft_share_message);
                    frappe.show_alert({message: __('Message copied to clipboard!'), indicator: 'green'});
                });
            }
            
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
                    // Read the text directly from the draft_share_message field instead of generating it again here!
                    let text = frm.doc.draft_share_message;
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
    
    # 2. Strip * from all existing logs
    logs = frappe.get_all("Visitor Log", fields=["name", "draft_share_message"])
    for log in logs:
        if log.draft_share_message and '*' in log.draft_share_message:
            clean_msg = log.draft_share_message.replace('*', '')
            frappe.db.set_value("Visitor Log", log.name, "draft_share_message", clean_msg)
            
    frappe.db.commit()
    frappe.clear_cache()
    print("Added Copy button and cleaned existing asterisks!")

if __name__ == "__main__":
    fix_message_and_add_copy_button()
