$(document).ready(function () {

   /* Popovers */
   $("#level-number").popover({ placement: 'right', trigger: 'focus' });
   $("#buyout").popover({ placement: 'right', trigger: 'focus' });
   $("#game_level-reward").popover({ placement: 'right', trigger: 'focus' });
   $("#game_level-type").popover({ placement: 'right', trigger: 'focus' });
   $("#game_level-name").popover({ placement: 'right', trigger: 'focus' });

   $("#game_level-type").change(function () {
      if (this.value === "none" || this.value === "hidden") {
         $("#buyoutcost").hide();
      } else if (this.value === "buyout") {
         $("#buyoutlabel").text("Unlock Cost");
         $("#game_level-buyout").attr('max', '');
         $("#buyout").attr('data-original-title', 'Unlock Cost');
         $("#buyout").attr('data-content', 'Cost to open this level and see flags [0-9]+');
         $("#buyoutcost").show();
      } else if (this.value === "progress") {
         $("#buyoutlabel").text("% Complete of Prior Level");
         $("#game_level-buyout").attr('max', 100);
         $("#buyout").attr('data-original-title', '% Complete of Prior Level');
         $("#buyout").attr('data-content', 'This level will unlock automatically after this percentage of prior level is completed (value 0-100).');
         $("#buyoutcost").show();
      } else if (this.value === "points") {
         $("#buyoutlabel").text("Points Required");
         $("#game_level-buyout").attr('max', '');
         $("#buyout").attr('data-original-title', 'Points Required');
         $("#buyout").attr('data-content', 'This level will unlock automatically after the score reaches this amount.');
         $("#buyoutcost").show();
      }
   });
});