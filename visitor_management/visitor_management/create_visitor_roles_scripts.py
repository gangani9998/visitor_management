import frappe

def setup_visitor_system():
    # 1. Create Security Guard Role
    if not frappe.db.exists("Role", "Security Guard"):
        frappe.get_doc({
            "doctype": "Role",
            "role_name": "Security Guard",
            "desk_access": 1
        }).insert(ignore_permissions=True)
        print("Created Security Guard Role")

    # Grant permissions specifically to Security Guard for Visitor Log
    # Security Guards should ONLY have Read/Write/Create, NO Delete, NO Export
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": "Visitor Log",
        "role": "Security Guard",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 0,
        "export": 0,
        "report": 0
    }).insert(ignore_permissions=True)
    
    # 2. Create Client Script for WhatsApp Sharing
    if not frappe.db.exists("Client Script", "Visitor Log WhatsApp Share"):
        script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.status === 'Expected') {
            frm.add_custom_button(__('Share Gate Pass (WhatsApp)'), function() {
                if (!frm.doc.phone) {
                    frappe.msgprint(__('Please enter a Phone Number first.'));
                    return;
                }
                
                let text = `Hello ${frm.doc.visitor_name}!\\n\\n`;
                text += `Here is your Secure Gate Pass for your visit to our factory:\\n`;
                text += `Pass Code: *${frm.doc.pass_code}*\\n\\n`;
                text += `View & Download Pass: ${window.location.origin}/visitor?token=${frm.doc.secure_token_url}`;
                
                let url = `https://api.whatsapp.com/send?phone=${frm.doc.phone}&text=${encodeURIComponent(text)}`;
                window.open(url, '_blank');
            }, __('Actions'));
        }
    }
});
"""
        frappe.get_doc({
            "doctype": "Client Script",
            "dt": "Visitor Log",
            "name": "Visitor Log WhatsApp Share",
            "module": "Visitor Management",
            "script": script
        }).insert(ignore_permissions=True)
        print("Created Client Script for WhatsApp Share")
        
    frappe.db.commit()

if __name__ == "__main__":
    setup_visitor_system()
