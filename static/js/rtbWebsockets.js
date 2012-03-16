var ws = new WebSocket("ws://localhost:8888/notification");
ws.onopen = function() {
  //Wait for a notification
};
ws.onmessage = function (evt) {
   humane.info(evt.data);
};