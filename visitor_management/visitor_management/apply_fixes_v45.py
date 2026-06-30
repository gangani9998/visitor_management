import frappe

def transition_to_web_link():
    # 1. Update the Client Script to open the Web Link instead of Print Format
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (frm.is_new()) {
            frm.set_df_property('status', 'options', ['Expected', 'Checked In']);
        } else {
            frm.set_df_property('status', 'options', ['Expected', 'Checked In', 'Checked Out']);
        }
    },
    
    btn_open_gate_pass: function(frm) {
        if (frm.is_new() || !frm.doc.secure_token_url) {
            frappe.msgprint(__('Please save the pass first.'));
            return;
        }
        // Open the Web View Link directly!
        let url = window.location.origin + "/visitor?token=" + frm.doc.secure_token_url;
        window.open(url, '_blank');
    },
    
    btn_copy_message: function(frm) {
        if (!frm.doc.draft_share_message) {
            frappe.msgprint(__('No message generated yet. Please save the pass first.'));
            return;
        }
        frappe.utils.copy_to_clipboard(frm.doc.draft_share_message);
    },
    
    btn_share_via_wa: function(frm) {
        if (!frm.doc.phone) {
            frappe.msgprint(__('Please enter a Phone Number first.'));
            return;
        }
        if (!frm.doc.draft_share_message) {
            frappe.msgprint(__('No message generated yet. Please save the pass first.'));
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
        let text = frm.doc.draft_share_message;
        let url = `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
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
    
    # 2. Delete the obsolete Print Format from the system
    if frappe.db.exists("Print Format", "Visitor Gate Pass"):
        frappe.delete_doc("Print Format", "Visitor Gate Pass", ignore_permissions=True, force=1)
        
    frappe.clear_cache()
    print("Transitioned 'Open Gate Pass' button to the Web Link and deleted old Print Format!")

if __name__ == "__main__":
    transition_to_web_link()
