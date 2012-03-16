var ws = new WebSocket("ws://172.16.1.20:8888/notification");
ws.onopen = function() {
  //Wait for a notification
};
ws.onmessage = function (evt) {
   humane.info(evt.data);
};