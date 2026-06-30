import frappe

def fix_all_print_and_buttons():
    # 1. Update Print Format (Fix Stretching and Add AM/PM)
    print_doc = frappe.get_doc("Print Format", "Visitor Gate Pass")
    
    new_html = """
    {% set default_company = frappe.db.get_single_value("Global Defaults", "default_company") %}
    {% set company_name = default_company %}
    {% set company_logo = frappe.db.get_value("Company", default_company, "company_logo") if default_company else "" %}
    {% set final_purpose = doc.specify_purpose if doc.purpose_of_visit == 'Other' else doc.purpose_of_visit %}
    
    <div style="max-width: 600px; margin: 0 auto; text-align: center; font-family: Arial, sans-serif; padding: 10px; border: 2px solid #333; background: #fff; line-height: 1.2;">
        {% if company_logo %}
            <img src="{{ company_logo }}" style="max-height: 40px; margin-bottom: 5px;">
        {% endif %}
        <h2 style="color: #1a4f8b; margin: 0; padding-top: 5px;"><b>{{ company_name | upper }}</b></h2>
        <hr style="margin: 5px 0;">
        <h4 style="background: #1a4f8b; color: white; padding: 5px; margin: 5px 0;">VISITOR / VENDOR GATE PASS</h4>
        
        <table style="width: 100%; text-align: left; margin-bottom: 10px; font-size: 12px; border-collapse: collapse;">
            <tr>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Name:</b> {{ doc.visitor_name }}</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Phone:</b> {{ doc.phone or 'N/A' }}</td>
            </tr>
            <tr>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Visiting:</b> 
                    {% set emp_name = frappe.db.get_value("Employee", doc.person_to_meet, "employee_name") %}
                    {{ emp_name or doc.person_to_meet }}
                </td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Type:</b> {{ doc.visitor_type }}</td>
            </tr>
            <tr>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Vehicle:</b> {{ doc.vehicle_number or 'N/A' }}</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Purpose:</b> {{ final_purpose }}</td>
            </tr>
            <tr>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Entry Type:</b> {{ doc.entry_type }}</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;"><b>Valid Till:</b> 
                    {% if doc.valid_till %}
                        {{ frappe.utils.format_datetime(doc.valid_till, "dd-MM-yyyy hh:mm a") }}
                    {% else %}
                        N/A
                    {% endif %}
                </td>
            </tr>
        </table>
        
        <div style="text-align: center; margin-top: 5px; margin-bottom: 5px;">
            <h4 style="margin:0;">PASS CODE: <span style="font-size: 20px; letter-spacing: 2px; color: #d9534f;">{{ doc.pass_code }}</span></h4>
            {% if doc.qr_code %}
                <img src="{{ doc.qr_code }}" style="max-width: 120px; border: 1px solid #333; padding: 2px; margin-top: 5px; border-radius: 5px;">
            {% endif %}
            <p style="font-size: 11px; font-weight: bold; margin: 5px 0; color: #1a4f8b;"><i>Please show this pass when entering and exiting for Check-In and Check-Out.</i></p>
        </div>
        
        <div style="font-size: 9.5px; text-align: left; border: 1px solid #ccc; padding: 5px; background: #f9f9f9;">
            <h5 style="color: #1a4f8b; margin: 0 0 3px 0;">Safety & Security Instructions</h5>
            <ol style="padding-left: 15px; margin: 0;">
                <li>Visit only the person / department specified in the pass.</li>
                <li>Photography inside the company premises with a mobile phone or camera is strictly prohibited.</li>
                <li>Ensure company staff escorts you while visiting the plant area.</li>
                <li>Do not touch any switches or equipment.</li>
                <li>Do not seat, stand & wait at any unknown place inside the plant area.</li>
                <li>Personal protective equipment (PPE) must be worn in many areas of our plant for your safety.</li>
                <li>During an emergency siren, leave building via emergency exits and report to assembly point.</li>
                <li>Inside the company premises, the vehicle speed limit is 15 km/hr.</li>
                <li>For entering premises, helmet and valid license are mandatory for two-wheelers.</li>
                <li>For entering premises, seat belt and valid license are mandatory for four-wheelers.</li>
            </ol>
        </div>
    </div>
    """
    print_doc.html = new_html
    print_doc.save(ignore_permissions=True)

    # 2. Update Client Script (Fix WhatsApp Button Style)
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    new_script = """
frappe.ui.form.on('Visitor Log', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.page.add_inner_button(__('Open Gate Pass'), function() {
                let print_url = `/printview?doctype=Visitor Log&name=${frm.doc.name}&format=Visitor Gate Pass&no_letterhead=1`;
                window.open(print_url, '_blank');
            }).css({'color': 'white', 'background-color': '#1a4f8b', 'font-weight': 'bold', 'border': 'none'});
            
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
                }).css({'color': 'white', 'background-color': '#28a745', 'font-weight': 'bold', 'border': 'none'});
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
    print("Fixed Print Layout Size, AM/PM formatting, and Button styling!")

if __name__ == "__main__":
    fix_all_print_and_buttons()
