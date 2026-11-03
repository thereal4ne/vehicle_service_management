# Copyright (c) 2026, Albin Jacob and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ServiceJobCard(Document):
	def validate(self):
		# calculate total cost and check task statuses
		self.calculate_estimated_cost()
		self.validate_task_completion()

	def on_update(self):
		# update service booking status when job card is saved/updated
		self.sync_booking_status()

	def calculate_estimated_cost(self):
		# sum up estimated cost of all child table tasks
		total=0
		for task in self.tasks:
			total+=task.estimated_cost or 0
		self.estimated_cost=total
		if not self.actual_cost:
			self.actual_cost=total

	def validate_task_completion(self):
		if self.status=="Completed":
			# cannot complete job card without any tasks
			if not self.tasks:
				frappe.throw("Cannot completed a job without service tasks")

			# make sure all tasks are completed before completing the job card
			for task in self.tasks:
				if task.status!="Completed":
					frappe.throw(f"Cannot mark a job card as completed '{task.task_name}' is still {task.status}")

	def sync_booking_status(self):
		# automatically sync booking status with job card status
		if not self.service_booking:
			return

		if self.status=="Completed":
			frappe.db.set_value("Service Booking",self.service_booking,"status","Completed")
		elif self.status=="In Progress":
			frappe.db.set_value("Service Booking",self.service_booking,"status","In Progress")
