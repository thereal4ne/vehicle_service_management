import frappe


# 1. API to create a booking
@frappe.whitelist()
def create_booking(customer, vehicle, booking_date, service_type, notes=None):
	# Check mandatory parameters
	if not customer or not vehicle or not booking_date or not service_type:
		frappe.throw("Customer, vehicle, booking date, and service type are all required!")

	# Check permission
	if not frappe.has_permission("Service Booking", "create"):
		frappe.throw("You do not have permission to create a booking!", frappe.PermissionError)

	# Create and save document
	doc = frappe.get_doc({
		"doctype": "Service Booking",
		"customer": customer,
		"vehicle": vehicle,
		"booking_date": booking_date,
		"service_type": service_type,
		"notes": notes
	})
	doc.insert()
	return doc


# 2. API to get booking details
@frappe.whitelist()
def get_booking(booking_id):
	if not booking_id:
		frappe.throw("Please provide a booking_id!")

	# Check if record exists
	if not frappe.db.exists("Service Booking", booking_id):
		frappe.throw(f"Service Booking {booking_id} not found!", frappe.DoesNotExistError)

	doc = frappe.get_doc("Service Booking", booking_id)
	return doc


# 3. API to update booking status
@frappe.whitelist()
def update_booking_status(booking_id, status):
	if not booking_id or not status:
		frappe.throw("Both booking_id and status are required!")

	# Check valid status
	allowed_statuses = ["Draft", "Confirmed", "In Progress", "Completed", "Cancelled"]
	if status not in allowed_statuses:
		frappe.throw(f"Invalid status! Allowed statuses are: {allowed_statuses}")

	# Fetch and update
	doc = frappe.get_doc("Service Booking", booking_id)
	doc.status = status
	doc.save()
	return doc
