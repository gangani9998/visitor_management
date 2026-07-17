// Copyright (c) 2026, SFPL and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Log", {
	onload: function(frm) {
		// Auto-set "Valid Till" to End of Day if it is a new form
		if (frm.is_new() && !frm.doc.valid_till) {
			let today = frappe.datetime.get_today();
			frm.set_value('valid_till', today + ' 23:59:59');
		}
	}
});
