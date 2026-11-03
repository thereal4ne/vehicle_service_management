import frappe
from frappe import _
from frappe.model.document import Document

class CustomerVehicle(Document):
	def validate(self):
		# basic cleanup and duplicate check before saving
		self.clean_fields()
		self.validate_duplicate_registration()

	def clean_fields(self):
		# convert plate to uppercase and trim extra spaces
		if self.registration_number:
			self.registration_number=self.registration_number.strip().upper()

	def validate_duplicate_registration(self):
		if not self.registration_number:
			return

		# check if another vehicle has the same reg number (exclude self)
		existing=frappe.db.exists("Customer Vehicle",{"registration_number":self.registration_number,"name":("!=",self.name)},)
		if existing:
			frappe.throw(_(f"A vehicle with registration number {self.registration_number} already exists."))
