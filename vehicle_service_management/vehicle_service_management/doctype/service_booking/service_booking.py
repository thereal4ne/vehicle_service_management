# Copyright (c) 2026, Albin Jacob and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now


class ServiceBooking(Document):
	def validate(self):
		# running all validations here
		self.validate_vehicle_belongs_to_customer()
		self.validate_booking_date_not_past()
		self.validate_no_conflicting_booking()

	def validate_vehicle_belongs_to_customer(self):
		# get owner of selected vehicle from db
		vehicle_owner=frappe.db.get_value("Customer Vehicle",self.vehicle,"customer")

		# verify vehicle actually belongs to selected customer
		if vehicle_owner and vehicle_owner!=self.customer:
			frappe.throw(f"Vehicle {self.vehicle} belongs to {vehicle_owner}, not {self.customer}")

	def validate_booking_date_not_past(self):
		# prevent booking dates from the past
		if self.booking_date:
			if get_datetime(self.booking_date) < get_datetime(now()):
				frappe.throw("Booking date cannot be in the past!")

	def validate_no_conflicting_booking(self):
		# check if there is another booking for the same vehicle at the same time
		conflict=frappe.db.exists(
			"Service Booking",
			{
				"vehicle":self.vehicle,
				"booking_date":self.booking_date,
				"name":("!=",self.name),
				"status":("not in",["Cancelled","Completed"]),
			},
		)
		if conflict:
			frappe.throw(f"Vehicle {self.vehicle} already has a booking on {self.booking_date}")
