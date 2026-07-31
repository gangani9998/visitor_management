# Copyright (c) 2026, SFPL and contributors
# For license information, please see license.txt

import frappe
import uuid
import qrcode
import io
from frappe.model.document import Document
import random
from frappe.utils import now_datetime, get_url, random_string

def generate_unambiguous_passcode(length=6):
	# Exclude visually ambiguous characters: 0, O, 1, I, L, 8, B
	alphabet = "2345679ACDEFGHJKMNPQRSTUVWXYZ"
	return "".join(random.choice(alphabet) for _ in range(length))


class VisitorLog(Document):
	def validate(self):
		# 1. Generate unambiguous 6-character Pass Code on first save
		if not self.pass_code:
			self.pass_code = generate_unambiguous_passcode(6)

		# 2. Generate Secure Token URL on first save
		if not self.secure_token_url:
			self.secure_token_url = str(uuid.uuid4().hex)

		# 3. Validation Logic
		from frappe.utils import get_datetime
		if self.valid_from and self.valid_till:
			valid_from_dt = get_datetime(self.valid_from)
			valid_till_dt = get_datetime(self.valid_till)
			if valid_from_dt > valid_till_dt:
				frappe.throw("Error: 'Valid From' time cannot be after 'Valid Till' time.")

		# 4. Status Routing Logic
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc and self.entry_type == "Single Entry":
				# Prevent bypassing expiration via Expected or any other status once Checked Out
				if old_doc.status == "Checked Out" and self.status != "Checked Out":
					frappe.throw("Error: Code already used. Single Entry pass is expired.")
				# Also prevent checking in if a check_out_time was already stamped
				if self.status == "Checked In" and (self.check_out_time or old_doc.check_out_time):
					frappe.throw("Error: Code already used. Single Entry pass is expired.")
			
		# Auto-stamp check-in / check-out times based on status transition
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc:
				if old_doc.status != "Checked In" and self.status == "Checked In":
					self.check_in_time = now_datetime()
					self.check_out_time = None
					self.append("entries", {
						"check_in_time": self.check_in_time,
						"vehicle_number": self.vehicle_number,
						"vehicle_photo": self.vehicle_photo
					})
				elif old_doc.status != "Checked Out" and self.status == "Checked Out":
					self.check_out_time = now_datetime()
					if self.entries:
						for row in reversed(self.entries):
							if not row.check_out_time:
								row.check_out_time = self.check_out_time
								break

		# 6. Auto-generate Draft Share Message
		if self.pass_code and self.secure_token_url:
			from frappe.utils import get_datetime, format_datetime
			
			company_name = frappe.db.get_single_value("Global Defaults", "default_company") or "Our Company"
			message = f"Dear {self.visitor_name} Ji,\n\n"
			
			if self.valid_from and self.valid_till:
				dt_from = get_datetime(self.valid_from)
				dt_till = get_datetime(self.valid_till)
				
				day = dt_from.day
				ordinal = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
				formatted_date = f"{day}{ordinal} of {dt_from.strftime('%B %Y')}"
				
				v_from_str = format_datetime(self.valid_from, "dd-MM-yyyy hh:mm a")
				v_till_str = format_datetime(self.valid_till, "dd-MM-yyyy hh:mm a")
				
				if dt_from.date() == dt_till.date():
					v_from_time = format_datetime(self.valid_from, "hh:mm a")
					v_till_time = format_datetime(self.valid_till, "hh:mm a")
					message += f"Your upcoming visit to {company_name} has been scheduled for the {formatted_date}.\n"
					message += f"Your Gate Pass has been successfully generated and is valid from {v_from_time} to {v_till_time}.\n\n"
				else:
					message += f"Your upcoming visit to {company_name} has been scheduled.\n"
					message += f"Your Gate Pass has been successfully generated and is valid from {v_from_str} to {v_till_str}.\n\n"
			else:
				message += f"Your upcoming visit to {company_name} has been scheduled.\n"
				message += f"Your Gate Pass has been successfully generated.\n\n"
			v_type = self.visitor_type if self.visitor_type else "Visitor"
			message += f"{v_type} Passcode: {self.pass_code}\n\n"
			message += f"{get_url()}/visitor?token={self.secure_token_url}\n\n"
			message += f"Please click the secure link above to open your Digital Gate Pass, which contains your scannable QR Code and present this to the Security Guard upon arrival for quick entry and Exit."
			self.draft_share_message = message

	def on_update(self):
		# 5. Generate QR Code Image if not exists
		if self.pass_code and not self.qr_code:
			qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
			qr.add_data(self.pass_code)
			qr.make(fit=True)
			img = qr.make_image(fill_color="black", back_color="white")
			
			img_byte_arr = io.BytesIO()
			img.save(img_byte_arr, format='PNG')
			file_content = img_byte_arr.getvalue()
			
			file_name = f"QR_{self.pass_code}.png"
			
			# Create File document securely
			saved_file = frappe.get_doc({
				"doctype": "File",
				"file_name": file_name,
				"attached_to_doctype": "Visitor Log",
				"attached_to_name": self.name,
				"attached_to_field": "qr_code",
				"is_private": 0,
				"content": file_content
			})
			saved_file.insert(ignore_permissions=True)
			
			# We need to set the qr_code field to the file url and save again
			frappe.db.set_value("Visitor Log", self.name, "qr_code", saved_file.file_url, update_modified=False)
