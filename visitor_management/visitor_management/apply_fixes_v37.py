import frappe

def fix_status_dropdown():
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        // Dynamically filter the Status dropdown!
        if (frm.is_new()) {
            frm.set_df_property('status', 'options', ['Expected', 'Checked In']);
        } else {
            frm.set_df_property('status', 'options', ['Expected', 'Checked In', 'Checked Out']);
        }
    },
    
    // Bind to the physical form buttons
    btn_open_gate_pass: function(frm) {
        if (frm.is_new()) {
            frappe.msgprint(__('Please save the pass first.'));
            return;
        }
        let print_url = `/printview?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
        window.open(print_url, '_blank');
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
    frappe.clear_cache()
    print("Status Dropdown logic successfully injected!")

if __name__ == "__main__":
    fix_status_dropdown()
