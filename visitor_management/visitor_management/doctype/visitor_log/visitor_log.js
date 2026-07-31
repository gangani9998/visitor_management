// Copyright (c) 2026, SFPL and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Log", {
	onload: function(frm) {
		// Auto-set "Valid Till" to End of Day if it is a new form
		if (frm.is_new() && !frm.doc.valid_till) {
			let today = frappe.datetime.get_today();
			frm.set_value('valid_till', today + ' 23:59:59');
		}
	},
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.status === "Checked Out" && frm.doc.entry_type === "Single Entry") {
            frm.set_read_only();
            frm.disable_save();
            frm.set_intro(__('This Single Entry pass is Checked Out and has expired. It is now Read-Only.'), 'red');
            return;
        } else {
            frm.set_intro('');
        }
        if (frm.is_new()) {
            frm.set_df_property('status', 'options', ['Expected', 'Checked In']);
        } else {
            frm.set_df_property('status', 'options', ['Expected', 'Checked In', 'Checked Out']);
        }
        frm.trigger('entry_type');
    },
    
    entry_type: function(frm) {
        if (frm.doc.entry_type === "Single Entry") {
            frm.set_df_property('entries', 'hidden', 1);
        } else {
            frm.set_df_property('entries', 'hidden', 0);
        }
    },
    
    btn_open_gate_pass: function(frm) {
        if (frm.is_new() || !frm.doc.secure_token_url) {
            frappe.msgprint(__('Please save the pass first.'));
            return;
        }
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
