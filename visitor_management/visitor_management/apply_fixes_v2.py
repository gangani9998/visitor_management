import frappe
import json

def fix_visitor_system():
    # 1. Fix Check-out Time visibility (Clear cache so it applies)
    frappe.db.set_value("DocField", {"parent": "Visitor Log", "fieldname": "check_out_time"}, "depends_on", "eval:doc.status == 'Checked Out'")
    frappe.db.set_value("DocField", {"parent": "Visitor Log", "fieldname": "check_in_time"}, "depends_on", "eval:doc.status == 'Checked In' || doc.status == 'Checked Out'")
    frappe.clear_cache(doctype="Visitor Log")

    # 2. Update WhatsApp Message
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
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
    },
    set_till_today: function(frm) {
        let today = frappe.datetime.get_today() + ' 23:59:59';
        frm.set_value('valid_till', today);
        frappe.show_alert({message: __('Valid Till set to end of today'), indicator: 'green'});
    }
});
"""
    script_doc.script = new_script
    script_doc.save(ignore_permissions=True)

    # 3. Update Print Format (Safety Rules & More Details)
    print_doc = frappe.get_doc("Print Format", "Visitor Gate Pass")
    new_html = """
    <div style="width: 100%; text-align: center; font-family: Arial, sans-serif; padding: 20px; border: 2px solid #333; background: #fff;">
        <h2 style="color: #1a4f8b; margin-bottom: 5px;"><b>SHIVOHAM</b></h2>
        <h4 style="margin-top: 0px; color: #555;">Fabtech private limited</h4>
        <hr>
        <h3 style="background: #1a4f8b; color: white; padding: 10px;">VISITOR / VENDOR GATE PASS</h3>
        
        <table style="width: 100%; text-align: left; margin-bottom: 20px; font-size: 14px;">
            <tr>
                <td style="padding: 5px;"><b>Name:</b> {{ doc.visitor_name }}</td>
                <td style="padding: 5px;"><b>Phone:</b> {{ doc.phone or 'N/A' }}</td>
            </tr>
            <tr>
                <td style="padding: 5px;"><b>Visiting:</b> {{ doc.person_to_meet }}</td>
                <td style="padding: 5px;"><b>Type:</b> {{ doc.visitor_type }}</td>
            </tr>
            <tr>
                <td style="padding: 5px;"><b>Vehicle No:</b> {{ doc.vehicle_number or 'N/A' }}</td>
                <td style="padding: 5px;"><b>Purpose:</b> {{ doc.purpose_of_visit }}</td>
            </tr>
            <tr>
                <td style="padding: 5px;"><b>Entry Type:</b> {{ doc.entry_type }}</td>
                <td style="padding: 5px;"><b>Valid Till:</b> {{ doc.get_formatted("valid_till") or 'N/A' }}</td>
            </tr>
        </table>
        
        <hr>
        <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
            <h4>PASS CODE: <span style="font-size: 24px; letter-spacing: 2px; color: #d9534f;">{{ doc.pass_code }}</span></h4>
            {% if doc.qr_code %}
                <img src="{{ doc.qr_code }}" style="max-width: 160px; border: 2px solid #333; padding: 5px; border-radius: 10px;">
            {% endif %}
            <p style="font-size: 12px; margin-top: 10px;"><i>Please show this QR Code to the Security Guard for Entry</i></p>
        </div>
        <hr>
        
        <div style="font-size: 11px; text-align: left; margin-top: 20px; border: 1px solid #ccc; padding: 10px; background: #f9f9f9;">
            <h4 style="color: #1a4f8b; margin-top: 0px;">Safety & Security Instructions</h4>
            <ol style="padding-left: 15px; margin-bottom: 0px;">
                <li style="margin-bottom: 4px;">Please register at the security gate while coming in. After finishing the job, take the signature of the person visiting and deposit the visitor pass back to the security officer.</li>
                <li style="margin-bottom: 4px;">Visit only the person / department specified in the visitor pass.</li>
                <li style="margin-bottom: 4px;">Photography inside the company premises with a mobile phone or a camera is strictly prohibited.</li>
                <li style="margin-bottom: 4px;">Please ensure that company staff escorts you while visiting the plant area.</li>
                <li style="margin-bottom: 4px;">Do not touch any switches or equipment.</li>
                <li style="margin-bottom: 4px;">Please do not seat, stand & wait at any unknown place inside the plant area.</li>
                <li style="margin-bottom: 4px;">Personal protective equipment (PPE) must be worn in many areas of our plant for your own safety.</li>
                <li style="margin-bottom: 4px;">During an emergency siren, leave the building via emergency exits and report to the assembly point.</li>
                <li style="margin-bottom: 4px;">Inside the company premises, the vehicle speed limit is 15 km/hr.</li>
                <li style="margin-bottom: 4px;">For entering the company premises, a helmet and a valid license are mandatory for two-wheeler riders.</li>
                <li>For entering the company premises, a seat belt and valid license are mandatory for four-wheeler drivers.</li>
            </ol>
        </div>
    </div>
    """
    print_doc.html = new_html
    print_doc.save(ignore_permissions=True)

    # 4. Fix Workspace List Error
    ws_doc = frappe.get_doc("Workspace", "Security Gate Dashboard")
    # In newer Frappe, the list block data requires explicitly providing the doctype name or block name properly.
    content = [
        {"id":"header-1","type":"header","data":{"text":"Security Operations"}},
        {"id":"shortcut-1","type":"shortcut","data":{"shortcut_name":"Visitor Log","label":"New Check-In"}},
        {"id":"list-1","type":"list","data":{"list_name":"Currently Inside","document_type":"Visitor Log"}}
    ]
    ws_doc.content = json.dumps(content)
    ws_doc.save(ignore_permissions=True)
    frappe.clear_cache()
    print("All fixes applied successfully!")

if __name__ == "__main__":
    fix_visitor_system()
