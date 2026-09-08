function expand() {
	for (var i=0; i<expand.arguments.length; i++) {
		var element = document.getElementById(expand.arguments[i]);
		element.style.display = (element.style.display == "none") ? "block" : "none";

	}
}

