import frappe

def after_install():
    # Execute the doctype and asset creation scripts that were previously run manually
    try:
        from visitor_management.visitor_management.create_visitor_doctype import create_visitor_log
        create_visitor_log()
    except Exception as e:
        print(f"Error creating Visitor Log Doctype: {e}")
        
    try:
        from visitor_management.visitor_management.create_visitor_roles_scripts import create_roles
        create_roles()
    except Exception as e:
        print(f"Error creating Visitor Roles: {e}")

    try:
        from visitor_management.visitor_management.create_visitor_assets import setup_portal
        setup_portal()
    except Exception as e:
        print(f"Error creating Visitor Assets: {e}")

    print("Visitor Management app installed successfully.")
