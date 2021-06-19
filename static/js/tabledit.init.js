var regex = /.*csrftoken=([^;.]*).*$/ ;
var xCSRFToken = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
$.ajaxSetup({
	headers: {
		"X-CSRFToken":xCSRFToken
	},
});
$(document).ready(!function(t){"use strict";function o(){}o.prototype.init=function(){t("#inline-editable").Tabledit({
	url: 'http://127.0.0.1:8000/goals/',
	inputClass:"form-control form-control-sm table",
	editButton:false,
	deleteButton:false,
	hideIdentifier: true,
	columns:{
		identifier:[0,"id"],
		editable:[[2, 'life'], [3, 'study'], [4, 'interest']]
	},
})},t.EditableTable=new o,t.EditableTable.Constructor=o}(window.jQuery),function(){"use strict";window.jQuery.EditableTable.init();}())
;

$(document).ready(!function(t){"use strict";function o(){}o.prototype.init=function(){t("#show-table").Tabledit({
	url: '#',
	inputClass:"form-control form-control-sm table",
	editButton:false,
	deleteButton:false,
	hideIdentifier: true,
	columns:{
		identifier:[0,"id"],
		editable:[]
	},
})},t.EditableTable=new o,t.EditableTable.Constructor=o}(window.jQuery),function(){"use strict";window.jQuery.EditableTable.init()}());
$.ajaxSetup({
		headers: {
			"X-CSRFToken":xCSRFToken
		},
	});
;