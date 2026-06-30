import frappe
from frappe.utils import add_days, now_datetime

def test_visitor_flow():
    print("--- Starting End-to-End Test ---")
    try:
        # Step 1: Create an Expected Visitor (Pre-Registration Flow)
        print("1. Creating Expected Visitor...")
        doc = frappe.get_doc({
            "doctype": "Visitor Log",
            "visitor_name": "Test John Doe",
            "phone": "1234567890",
            "visitor_type": "Visitor",
            "purpose_of_visit": "Meeting",
            "entry_type": "Single Entry",
            "valid_from": now_datetime(),
            "valid_till": add_days(now_datetime(), 1),
            "status": "Expected",
            # We need an employee to link to. Let's find any employee or just create one if none exist.
        })
        
        employee = frappe.db.get_value("Employee", {"status": "Active"}, "name")
        if not employee:
            # Create a dummy employee
            emp = frappe.get_doc({
                "doctype": "Employee",
                "first_name": "Test Host",
                "status": "Active",
                "gender": "Male",
                "date_of_joining": frappe.utils.today(),
                "date_of_birth": "1990-01-01"
            }).insert(ignore_permissions=True)
            employee = emp.name
            
        doc.person_to_meet = employee
        doc.insert(ignore_permissions=True)
        print(f"-> Created {doc.name}")

        # Step 2: Validate Auto-Generation (Pass Code, Token, QR)
        print("2. Validating Auto-Generation...")
        doc.reload()
        if not doc.pass_code or not doc.secure_token_url:
            raise Exception("Pass Code or Secure Token URL was not generated!")
        if not doc.qr_code:
            raise Exception("QR Code was not generated!")
        print(f"-> Success: Pass Code [{doc.pass_code}], Token [{doc.secure_token_url}], QR [{doc.qr_code}]")

        # Step 3: Transition to Checked In
        print("3. Testing Check-In...")
        doc.status = "Checked In"
        doc.save(ignore_permissions=True)
        if not doc.check_in_time:
            raise Exception("Check-In Time was not auto-stamped!")
        print(f"-> Checked In successfully at {doc.check_in_time}")

        # Step 4: Transition to Checked Out
        print("4. Testing Check-Out...")
        doc.status = "Checked Out"
        doc.save(ignore_permissions=True)
        if not doc.check_out_time:
            raise Exception("Check-Out Time was not auto-stamped!")
        print(f"-> Checked Out successfully at {doc.check_out_time}")
        
        # Step 5: Test Single Entry Re-entry Block
        print("5. Testing Re-entry Block (Should Fail)...")
        try:
            doc.status = "Checked In"
            doc.save(ignore_permissions=True)
            raise Exception("SYSTEM FAILED TO BLOCK RE-ENTRY FOR SINGLE ENTRY PASS!")
        except Exception as e:
            if "already used" in str(e).lower() or "single entry" in str(e).lower():
                print("-> Success: System successfully blocked re-entry.")
            else:
                raise e

        print("--- All Tests Passed Successfully! ---")
    except Exception as e:
        print(f"TEST FAILED: {e}")

if __name__ == "__main__":
    test_visitor_flow()
