var ws = new WebSocket("ws://localhost:8888/websocket");
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
	} else if(evt.data.startsWith("update:")) {
		if($('#scoreboard').length) {
			var teamName = trim(evt.data.substring(evt.data.indexOf("teamName:")+"teamName:".length));
			var series = getSeries(teamName);
			var timestamp = trim(evt.data.substring(evt.data.indexOf("timestamp:")+"timestamp:".length, evt.data.indexOf("|", evt.data.indexOf("timestamp:"))));
			//Find the correct sieries with the updates team name
			//Find the timestamp of the update
			//Find the value of the update
			//push that point
			//chart.series[0].addPoint( [200, 31]);
			console.log(timestamp);
		}
	}
	
};

function getSeries(teamName) {
	for(var index = 0; index < chart.series.length; index++) {
		console.log(chart.series[index].name);
		if(chart.series[index].name == teamName) {
			return index;
		}
	}
	return -1;
}
function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"");
}