$(document).ready(function() {
	var ws = new WebSocket("ws://192.168.2.47:8888/websocket");
	if (typeof String.prototype.startsWith != 'function') {
		  String.prototype.startsWith = function (str){
		    return this.indexOf(str) == 0;
		  };
	}
	
	ws.onopen = function() {
		//Wait for a notification
		if($('#scoreboard').length){
			ws.send("load plox");
		}
	};
	
	ws.onmessage = function (evt) {
		var message = JSON.parse(evt.data);
		console.log(message);
		if(message['py/object'] == 'libs.Notification.Notification') {
			//Send a Notification
			Notifier.notify(message['message'], message['title'], "data:image/png;base64,"+message['file_contents']);
		} else if(message['py/object'] == 'libs.ScoreUpdate.ScoreUpdate') {
			if($('#scoreboard').length){
				//Update the line chart
				chart.series[getSeriesByName(message['team_name'])].addPoint([parseInt(message['time_stamp']), getCorrectValue(parseInt(message['value']), getSeriesByName(message['team_name']))]);
				//Update the bar chart
				correctData(getSeriesByName(message['team_name']), parseInt(message['team_score']));
				bar_chart.redraw();
			}
		}
		
	};
	
	function getCorrectValue(newestValue, seriesId) {
		if(chart.series[seriesId].data.length > 0) {
			return chart.series[seriesId].data[chart.series[seriesId].data.length-1].config[1] + newestValue;
		} else {
			return newestValue;
		}
	}
	
	function getSeriesByName(teamName) {
		for(var index = 0; index < chart.series.length; index++) {
			if(chart.series[index].name == teamName) {
				return index;
			}
		}
		return -1;
	}
	
	function correctData(teamIndex, newScore) {
		var new_data = [];
		//Copy all of the team scores that are currently being displayed
		for(var index = 0; index < bar_chart.series[0].data.length; index++) {
			 new_data[index] = bar_chart.series[0].data[index].config;
		}
		new_data[teamIndex] = newScore;
		bar_chart.series[0].setData(new_data, false);
	}
	
	function trim(stringToTrim) {
		return stringToTrim.replace(/^\s+|\s+$/g,"");
	}
});