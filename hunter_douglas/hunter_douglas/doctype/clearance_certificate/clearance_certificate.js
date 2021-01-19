// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Clearance Certificate', {
	refresh: function(frm) {

	},
	onload:function(frm){
		var List =
		[{dept:"Immediate Superior",item:"Handing over report"},
		 {dept:"Own Dept",item:"Books, Manual, Records, Customer Correspondence Files, Catalogues, Drawings, Tools, Instruments, Customer Contacts Etc."},
		 {dept:"Personnel",item:"Bonds / Undertaking (For Persons sent for training at Company’s expenses)"},
		 {dept:"Administration",item:"Car, Mobile Number, Telephone, Co.owned House(with/without furniture /fittings),Identity Cards,Credit Cards,Calculators, Camera  ETC"},
		 {dept:"IT Department",item:"Lap Top, Mouse, Codes, Bags, Data Card, Pen drive ETC"},
		 {dept:"Corporate Accounts",item:"Loans, Advances, Imprest / Any other amount/excessive paid amount  to be recovered"},
		 {dept:"Regand Branch Accounts",item:"Loans, Advances, Imprest / Any other amount to be recovered"},
		 {dept:"Income Tax Invest Proof for the year",item:""}
		]
	frm.clear_table('clearance');
	$.each(List,function(i,d)	{
		let row = frm.add_child('clearance',{
		department :d.dept,
		items:d.item
	})
}),
	refresh_field("clearance");
		
		}
	
});
