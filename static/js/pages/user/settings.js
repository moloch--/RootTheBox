/* Add click events */
$(document).ready(function() {
    $(".teamavatarimg").click(function() {
        $("#team_avatar_select").val($(this).attr('value'));
        $("#team-avatar-form").click();
    });

    $(".useravatarimg").click(function() {
        $("#user_avatar_select").val($(this).attr('value'));
        $("#user-avatar-form").click();
    });
});