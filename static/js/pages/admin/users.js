function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function getDetails(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);

    data = {'uuid': uuid, '_xsrf': getCookie("_xsrf")};
    $.post('/admin/ajax/' + obj, data, function(response) {
        $.each(response, function(key, value) {
            //console.log("#" + obj + "-" + key + " => " + value);
            var selection = $("#" + obj + "-" + key);
            if(selection.is("select")) {
                selection.val(value).change();
            } else {
                selection.val(value);
            }
            if (key === "avatar") {
                $("#" + obj + "-avatarimg").attr("src", "/avatars/" + value);
            }
        });
    }, 'json');
}

function readURL(input, type) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#' + type + '-avatarimg').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

$(document).ready(function() {

    /* Team */
    $("a[id^=edit-team-button]").click(function() {
        getDetails("team", $(this).data("uuid"));
    });

    $("#edit-team-submit").click(function() {
        $("#edit-team-form").submit();
    });

    /* User */
    $("a[id^=edit-user-button]").click(function() {
        getDetails("user", $(this).data("uuid"));
        $("#user-team-uuid").val($(this).data("team-uuid"));
        bank_hash = $(this).data("hash-algorithm");
        if (bank_hash == undefined) {
            $("#banking-group").hide();
        } else {
            $("#banking-group").show();
            $("#user-hash-algorithm").val($(this).data("hash-algorithm"));
        }
    });

    $( "#user-expire" ).datepicker();

    $("#edit-user-submit").click(function() {
        $("#edit-user-form").submit();
    });

    $("a[id^=delete-user-button]").click(function() {
        $("#delete-user-uuid").val($(this).data("uuid"));
    });

    $("#delete-user-submit").click(function() {
        $("#delete-user-form").submit();
    });

    $("a[id^=delete-team-button]").click(function() {
        $("#delete-team-uuid").val($(this).data("uuid"));
    });

    $("#delete-team-submit").click(function() {
        $("#delete-team-form").submit();
    });

    $("a[id^=lock-user-button]").click(function() {
        $("#lock-user-uuid").val($(this).data("uuid"));
        $("#lock-user-form").submit();
    });

    $("#edit-scores-submit").click(function(){
        $("#edit-scores-form").submit();
    });

    /* Other */
    $("a[id^=reveal-hash-button]").click(function() {
        alert($(this).data("bank-hash"));
    });

    $(".teamavatarimg").click(function() {
        var image = $(this).attr('value');
        $("#team-avatarimg").attr('src', "/avatars/" + htmlEncode(image));
        $("#team-file-avatar").val("");
        $("#team-avatar").val(image);
        $("#team-avatar-form").click();
    });

    $(".useravatarimg").click(function() {
        var image = $(this).attr('value');
        $("#user-avatarimg").attr('src', "/avatars/" + htmlEncode(image));
        $("#user-file-avatar").val("");
        $("#user-avatar").val(image);
        $("#user-avatar-form").click();
    });
    $("#user-file-avatar").change(function(){
        $("#user-avatar").val("");
        readURL(this, "user");
    });

    $("#team-file-avatar").change(function(){
        $("#team-avatar").val("");
        readURL(this, "team");
    });

    $("#useruploadbutton").click(function(){
        $("#user-file-avatar").click();
    });

    $("#teamuploadbutton").click(function(){
        $("#team-file-avatar").click();
    });
});
