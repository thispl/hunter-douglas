frappe.pages['internal-chat'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Internal Chat',
		single_column: true
	});
	$(frappe.render_template("internal_chat")).appendTo(page.body.addClass("no-border"));
}