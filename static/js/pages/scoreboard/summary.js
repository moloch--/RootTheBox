var flag_chart;
var money_chart;
var game_data;
function team_details(uuid) {
    $.getJSON('/scoreboard/ajax/team?uuid='+uuid, function(data) {
        console.log(data);
    });
}
$(function () {
    $(document).ready(function() {
        /* Options for both graphs*/
        Highcharts.getOptions().colors = $.map(Highcharts.getOptions().colors, function(color) {
            return {
                radialGradient: { cx: 0.5, cy: 0.3, r: 0.7 },
                stops: [
                    [0, color],
                    [1, Highcharts.Color(color).brighten(-0.3).get('rgb')]
                ]
            };
        });
        /* Flag Chart */
        flag_chart = new Highcharts.Chart({
            chart: {
                renderTo: 'pie_flags',
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                backgroundColor:'transparent'
            },
            title: {
                text: '<strong>Flags Captured</strong>',
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            },
            tooltip: {
                pointFormat: '{series.name}: {point.y} flags <strong>{point.percentage}%</strong>',
                percentageDecimals: 1
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        color: '#FFFFFF',
                        connectorColor: '#FFFFFF',
                        formatter: function() {
                            return '<div style="font-size:small;text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;">'+
                                    this.point.name+'</div>';
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Flags Captured',
                data: [
                ]
            }]
        });
    });
});
/* Money Chart */
$(function () {
    $(document).ready(function() {
        money_chart = new Highcharts.Chart({
            chart: {
                renderTo: 'pie_money',
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                backgroundColor:'transparent'
            },
            title: {
                text: '<strong>Bank Account</strong>',
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            },
            tooltip: {
                pointFormat: '{series.name}: ${point.y} <strong>{point.percentage}%</strong>',
                percentageDecimals: 1
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        color: '#FFFFFF',
                        connectorColor: '#FFFFFF',
                        formatter: function() {
                            return '<div style="font-size:small;text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;">'+
                                    this.point.name+'</div>';
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Team Money',
                data: [
                ]
            }]
        });
    });
});

/* Update code */
$(document).ready(function() {
    var ws = new WebSocket($("#ws-connect").val() + "/scoreboard/wsocket/game_data");

    ws.onmessage = function(event) {
        game_data = jQuery.parseJSON(event.data);

        /* Update Money */
        var money_ls = [];
        $.each(game_data, function(index, item) {
            money_ls.push([index.toString(), item.money]);
        });
        money_chart.series[0].setData(money_ls, true);

        /* Update Flags */
        var flag_ls = [];
        $.each(game_data, function(index, item) {
            flag_ls.push([index.toString(), item.flags.length]);
        });
        flag_chart.series[0].setData(flag_ls, true);

        /* Update Table */
        $.get("/scoreboard/ajax/summary", function(table) {
            $("#summary_table").html(table);
            $("a[id^=team-details-button]").click(function() {
                window.location = "/teams#" + $(this).data("uuid");
            });
        });
    };
});