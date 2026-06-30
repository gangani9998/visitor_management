import frappe
import json

def fix_security_workspace():
    ws_name = "Security Gate Dashboard"
    
    if not frappe.db.exists("Workspace", ws_name):
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "name": ws_name,
            "title": ws_name,
            "module": "Visitor Management",
            "is_standard": 0,
            "public": 1,
        })
        ws.insert(ignore_permissions=True)
    
    ws = frappe.get_doc("Workspace", ws_name)
    
    # Set content with shortcut blocks
    ws.content = json.dumps([
        {"type": "shortcut", "data": {"shortcut_name": "Live Security Dashboard", "col": 4}},
        {"type": "shortcut", "data": {"shortcut_name": "QR Gate Scanner", "col": 4}},
        {"type": "shortcut", "data": {"shortcut_name": "Visitor Log", "col": 4}},
        {"type": "card", "data": {"card_name": "Security Operations", "col": 12}}
    ])
    
    # Clear old shortcuts and links
    ws.shortcuts = []
    ws.links = []
    
    # Add shortcuts - URL type is valid here!
    ws.append("shortcuts", {
        "label": "Live Security Dashboard",
        "type": "URL",
        "url": "/security-dashboard",
        "color": "Green",
        "doc_view": ""
    })
    ws.append("shortcuts", {
        "label": "QR Gate Scanner",
        "type": "URL",
        "url": "/security-scan",
        "color": "Blue",
        "doc_view": ""
    })
    ws.append("shortcuts", {
        "label": "Visitor Log",
        "type": "DocType",
        "link_to": "Visitor Log",
        "color": "Grey",
        "doc_view": "List"
    })
    
    # Add links card
    ws.append("links", {
        "label": "Security Operations",
        "type": "Card Break",
        "hidden": 0
    })
    ws.append("links", {
        "label": "Visitor Log",
        "type": "Link",
        "link_type": "DocType",
        "link_to": "Visitor Log",
        "icon": "users",
        "hidden": 0
    })
    
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    print("Security Gate Dashboard workspace fixed successfully!")

if __name__ == "__main__":
    fix_security_workspace()
