$("td[contenteditable]").on("keypress focusout",evt=>{
	if (evt.type == "keypress") {
		let code = evt.charCode || evt.keyCode;
		if (code != 13 || evt.shiftKey) return true;
	}
	let output = {};
	let id = $(evt.target).closest("tr").data("player");
	if (!isNaN(id)) {
		output = {
			id:id,
			key:evt.target.id,
			data:evt.target.innerText
		};
		console.log(output);
		$.ajax({
			type: "POST",
			url: "http://probsjust.in/organizedcrime",
			data: output,
		});
	}
	if (evt.type == "keypress") return false;
});
