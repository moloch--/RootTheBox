var ws = new WebSocket("ws://localhost:8888/notification");
if (typeof String.prototype.startsWith != 'function') {
	  String.prototype.startsWith = function (str){
	    return this.indexOf(str) == 0;
	  };
}

ws.onopen = function() {
  //Wait for a notification
};

ws.onmessage = function (evt) {
	if(evt.data.startsWith("notification:")) {
		var title = evt.data.substring(evt.data.indexOf("title:")+"title:".length, evt.data.indexOf("|"));
		var message = evt.data.substring(evt.data.indexOf("message:")+"message:".length, evt.data.indexOf("|", evt.data.indexOf("message:")));
		var icon = evt.data.substring(evt.data.indexOf("icon:")+"icon:".length);
		Notifier.notify(message, title, "data:image/png;base64,"+icon);
	}
	
};