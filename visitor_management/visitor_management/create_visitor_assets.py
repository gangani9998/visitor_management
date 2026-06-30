import frappe

def create_print_format():
    if not frappe.db.exists("Print Format", "Visitor Gate Pass"):
        html = """
        <div style="width: 100%; text-align: center; font-family: Arial, sans-serif; padding: 20px; border: 2px solid #333;">
            <h2><b>{{ frappe.db.get_default('company') or 'COMPANY' }}</b></h2>
            <hr>
            <h3>VISITOR GATE PASS</h3>
            <p><b>Name:</b> {{ doc.visitor_name }}</p>
            <p><b>Vehicle No:</b> {{ doc.vehicle_number or 'N/A' }}</p>
            <p><b>Visiting:</b> {{ doc.person_to_meet }}</p>
            <p><b>Valid Till:</b> {{ doc.get_formatted("valid_till") or 'N/A' }}</p>
            <hr>
            <div style="text-align: center; margin-top: 15px;">
                <h4>PASS CODE: <span style="font-size: 24px; letter-spacing: 2px;">{{ doc.pass_code }}</span></h4>
                {% if doc.qr_code %}
                    <img src="{{ doc.qr_code }}" style="max-width: 150px; border: 1px solid #ccc; padding: 5px;">
                {% endif %}
            </div>
            <hr>
            <div style="font-size: 10px; text-align: left; margin-top: 20px;">
                <b>Safety Rules:</b><br>
                1. Please wear PPE if entering factory zones.<br>
                2. Speed limit is 10km/h on premises.<br>
                3. Please present this pass to security upon exit.
            </div>
        </div>
        """
        doc = frappe.get_doc({
            "doctype": "Print Format",
            "name": "Visitor Gate Pass",
            "doc_type": "Visitor Log",
            "module": "Visitor Management",
            "custom_format": 1,
            "html": html,
            "align_labels_right": 0,
            "show_section_headings": 0
        })
        doc.insert(ignore_permissions=True)
        print("Successfully created Print Format: Visitor Gate Pass.")

def create_workspace():
    if not frappe.db.exists("Workspace", "Security Gate"):
        doc = frappe.get_doc({
            "doctype": "Workspace",
            "name": "Security Gate Dashboard",
            "label": "Security Gate Dashboard",
            "title": "Security Gate Dashboard",
            "type": "Workspace",
            "module": "Visitor Management",
            "is_standard": 1,
            "public": 1,
            "sequence_id": 1.0,
            "icon": "shield",
            "content": '[{"id":"header-1","type":"header","data":{"text":"Security Operations"}},{"id":"shortcut-1","type":"shortcut","data":{"shortcut_name":"Visitor Log","label":"New Check-In"}},{"id":"list-1","type":"list","data":{"list_name":"Currently Inside"}}]'
        })
        
        # Add shortcuts
        doc.append("shortcuts", {
            "type": "DocType",
            "link_to": "Visitor Log",
            "label": "Quick Check-In",
            "format": "Standard",
            "color": "Grey"
        })
        doc.insert(ignore_permissions=True)
        print("Successfully created Workspace: Security Gate.")

if __name__ == "__main__":
    create_print_format()
    create_workspace()
