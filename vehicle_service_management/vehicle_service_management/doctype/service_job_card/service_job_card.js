// Copyright (c) 2026, Albin Jacob and contributors
// For license information, please see license.txt

frappe.ui.form.on("Service Job Card", {
	validate(frm) {
		calculate_total(frm);
	}
});

frappe.ui.form.on("Job Card Task", {
	estimated_cost(frm) {
		calculate_total(frm);
	},
	tasks_remove(frm) {
		calculate_total(frm);
	}
});

function calculate_total(frm) {
	let total = 0;
	(frm.doc.tasks || []).forEach(task => {
		total += flt(task.estimated_cost);
	});
	frm.set_value("estimated_cost", total);
	if (!frm.doc.actual_cost || frm.doc.actual_cost === 0) {
		frm.set_value("actual_cost", total);
	}
}
