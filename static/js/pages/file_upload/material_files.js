$(document).ready(function() {
    data = {'_xsrf': getCookie("_xsrf")}
    $.post('/materials', data, function(response) {
        $('#container').jstree({
            'core' : {
              'data' : $.parseJSON(response)["children"]
            }
        });
    });
});
