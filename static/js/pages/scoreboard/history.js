var flag_chart;
var money_chart;
var game_data;

/* Highcharts code */
$(document).ready(function() {
    if ($("#timercount_hidescoreboard").length === 0) {
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
                text: '<strong>' + $("#pie_flags").data("name") + '</strong>',
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            },
            tooltip: {
                enable: true,
                formatter: function() {
                    return htmlEncode(this.point.y) + ' flag(s)<br /><strong>' + htmlEncode(this.point.percentage.toFixed(2)) + '%</strong>';
                }
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
                            return '<div style="font-size:small;text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;">' +
                                        htmlEncode(this.point.name) + '</div>';
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Flags Captured',
                data: []
            }]
        });
        /* Money Chart */
        money_chart = new Highcharts.Chart({
            chart: {
                renderTo: 'pie_money',
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                backgroundColor:'transparent'
            },
            title: {
                text: '<strong>' + $("#pie_money").data("name") + '</strong>',
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            },
            tooltip: {
                enabled: true,
                formatter: function() {
                    return $("#pie_money").data("symbol") + htmlEncode(this.point.y) + '<br /><strong>' +
                        htmlEncode(this.point.percentage.toFixed(2)) + '%</strong>';
                }
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
                            return '<div style="font-size:small;text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;">' +
                                        htmlEncode(this.point.name) + '</div>';
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Team Money',
                data: []
            }]
        });
    }
});

var title_val, scale_val, symbol_val;
function setGraphTitle(title) {
    title_val = title;
}
function setGraphScale(scale) {
    scale_val = scale;
}
function setGraphSymbol(symbol) {
    symbol_val = symbol;
}

function extendData(series, axis) {
    var ext = axis.getExtremes();
    var x   = ext.dataMax;
    var y   = series.data[series.data.length -1].y;
    series.addPoint({'x':x, 'y':y, marker: { enabled: true }});
}

function drawBotGraph(state) {
    var chart = new Highcharts.Chart({
        chart: {
            renderTo: 'history-graph',
            type: 'line',
            backgroundColor:'transparent',
            zoomType: 'x',
        },
        title: {
                text: $("#history-graph").data("name"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: $("#history-graph").data("xaxis"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 14px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            }
        },
        yAxis: {
            title: {
                text: $("#history-graph").data("yaxis"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 14px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            }
        },
        tooltip: {
            enabled: true,
            formatter: function() {
                return '<strong>' + htmlEncode(this.series.name) + '</strong><br />' + htmlEncode(this.y) + ' bot(s)';
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true
                },
                enableMouseTracking: true
            }
        },
        colors: ['#4572A7', '#AA4643', '#89A54E', '#80699B', '#3D96AE', '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92'],
        series: state,
    });
    for (item in chart.series) {
        extendData(chart.series[item], chart.xAxis[0]);
    }
    return chart;
}

function drawMoneyGraph(state) {
    var chart = new Highcharts.Chart({
        chart: {
            renderTo: 'history-graph',
            type: 'line',
            backgroundColor:'transparent',
            zoomType: 'x',
        },
        title: {
                text: title_val,
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: $("#history-graph").data("xaxis"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 14px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            }
        },
        yAxis: {
            title: {
                text: scale_val,
                style: {
                    color: '#FFFFFF',
                    font: 'bold 14px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            }
        },
        tooltip: {
            enabled: true,
            formatter: function() {
                return '<strong>' + htmlEncode(this.series.name) + '</strong><br /> ' + htmlEncode(symbol_val) + htmlEncode(this.y);
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true
                },
                enableMouseTracking: true
            }
        },
        colors: ['#4572A7', '#AA4643', '#89A54E', '#80699B', '#3D96AE', '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92'],
        series: state,
    });
    for (item in chart.series) {
        extendData(chart.series[item], chart.xAxis[0]);
    }
    return chart;
}

function drawFlagGraph(state) {

    var chart = new Highcharts.Chart({
        chart: {
            renderTo: 'history-graph',
            type: 'line',
            backgroundColor:'transparent',
            zoomType: 'x',
        },
        title: {
                text: $("#pie-flags").data("name"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
        },
        xAxis: {
            gridLineColor: "#888",
            type: 'datetime',
            title: {
                text: $("#history-graph").data("xaxis"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 14px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            }
        },
        yAxis: {
            gridLineColor: "#888",
            title: {
                text: $("#pie-flags").data("name"),
                style: {
                    color: '#FFFFFF',
                    font: 'bold 14px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            }
        },
        tooltip: {
            enabled: true,
            formatter: function() {
                return '<strong>' + htmlEncode(this.series.name) + '</strong><br />' + htmlEncode(this.y) + ' flag(s)';
            }
        },
        colors: ['#4572A7', '#AA4643', '#89A54E', '#80699B', '#3D96AE', '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92'],
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true
                },
                enableMouseTracking: true
            }
        },
        series: state,
    });
    for (item in chart.series) {
        extendData(chart.series[item], chart.xAxis[0]);
    }
    return chart;
}

function getSeriesIndexByName(state, teamName) {
    for(var index = 0; index < state.length; index++) {
        if (state[index].name == teamName) {
            return index;
        }
    }
    return undefined;
}

/* Called if the graph is currently displayed */
function liveUpdate(chart, update) {
    for (var teamname in updates) {
        teamdata = updates[teamName]
        for(index = 0; index < teamdata.length; ++index) {
            update = teamdata[index]
            timestamp = update['timestamp'] * 1000;
            teamname = update['team_name'];
            value = update['value'];
            seriesIndex = getSeriesIndexByName(chart.series, teamname);
            if (index !== undefined) {
                var shift = (30 <= chart.series[index].data.length);
                var scores = [timestamp, value];
                chart.series[index].addPoint(scores, true, shift);
            } else {
                create_series = {
                    name: teamname,
                    data: [
                        [timestamp, value],
                    ]
                }
                chart.addSeries(create_series);
            }
        }
    }
}

function updateState(state, updates) {
    for (var teamName in updates) {
        teamdata = updates[teamName]
        for(index = 0; index < teamdata.length; ++index) {
            update = teamdata[index]
            timestamp = update['timestamp'] * 1000;
            teamname = update['team_name'];
            value = update['value'];
            seriesIndex = getSeriesIndexByName(state, teamname);
            if (seriesIndex !== undefined) {
                // Add to existing series' data array
                state[seriesIndex].data.push([timestamp, value]);
            } else {
                //console.log("Create flag series: " + teamname);
                newSeries = {
                    name: teamname,
                    data: [
                        [timestamp, value],
                    ]
                }
                state.push(newSeries);
            }
        }
    }
}

function initializeSocket(top) {
    $("body").css("cursor", "progress");
    window.history_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/game_history?top=" + top);
    var chart = undefined;
    var flagState = []; // List of Highchart series
    var moneyState = [];
    var botState = [];
    var liveUpdateCallback = undefined;

    history_ws.onopen = function() {
        $("#activity-monitor").removeClass("fa-eye-slash");
        $("#activity-monitor").addClass("fa-refresh fa-spin");
    }

    history_ws.onclose = function() {
        $("#activity-monitor").removeClass("fa-refresh fa-spin");
        $("#activity-monitor").addClass("fa-eye-slash");
    }

    history_ws.onmessage = function (evt) {
        if (evt.data === "pause") {
            location.reload();
        } else {
            msg = jQuery.parseJSON(evt.data);
            if ('error' in msg) {
                console.log("ERROR: " + msg.toString());
            } else if ('history' in msg) {
                /* Default graph is flags, init that first */
                updateState(flagState, msg['history']['flag_count']);
                chart = drawFlagGraph(flagState);
                liveUpdateCallback = liveUpdate;
                /* Init other states */
                updateState(moneyState, msg['history']['score_count']);
                updateState(botState, msg['history']['bot_count']);
            } else if ('update' in msg) {
                /* Update graph states */
                updateState(flagState, msg['update']['flag_count']);
                updateState(moneyState, msg['update']['score_count']);
                updateState(botState, msg['update']['bot_count']);
                /* Update the live chart */
                liveUpdateCallback(chart, msg['update']);
            }
            $("body").css("cursor", "default");
        }
    };
    $("#flags-history-button").off();
    $("#flags-history-button").click(function() {
        chart = drawFlagGraph(flagState);
        liveUpdateCallback = liveUpdate;
    });
    $("#money-history-button").off();
    $("#money-history-button").click(function() {
        chart = drawMoneyGraph(moneyState);
        liveUpdateCallback = liveUpdate;
    });
    $("#bots-history-button").off();
    $("#bots-history-button").click(function() {
        chart = drawBotGraph(botState);
        liveUpdateCallback = liveUpdate;
    });
    
}

$(document).ready(function() {
    if ($("#timercount_hidescoreboard").length > 0) {
        $.get("/scoreboard/ajax/timer", function(distance) {
            distance = distance * 1000;
            setTimer(distance, "_hidescoreboard");
        });
        window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/pause_score");
        scoreboard_ws.onmessage = function(event) {
            if (event.data !== "pause") {
                location.reload();
            }
        }
    } else {
        initializeSocket(10);
        $("#datapoints").change(function(){
            initializeSocket(this.value);
        });
        if ($("#timercount").length > 0) {
            $.get("/scoreboard/ajax/timer", function(distance) {
                distance = distance * 1000;
                setTimer(distance, "");
            });
        }
        window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/game_data");
        scoreboard_ws.onmessage = function(event) {
            if (event.data === "pause") {
                location.reload();
            } else {
                game_data = jQuery.parseJSON(event.data);

                /* Update Money */
                let i = 0;
                var money_ls = [];
                $.each(game_data, function(index, item) {
                    money_ls.push([index.toString(), item.money]);
                    i = i+1;
                    if (i > 9) {
                        return false;
                    }
                });
                money_chart.series[0].setData(money_ls, true);
    
                /* Update Flags */
                i = 0;
                var flag_ls = [];
                $.each(game_data, function(index, item) {
                    flag_ls.push([index.toString(), item.flags.length]);
                    i = i+1;
                    if (i > 9) {
                        return false;
                    }
                });
                flag_chart.series[0].setData(flag_ls, true);
                
            }
        };

        $("#graphtext").click(function(){
            $("#pie_graphs").toggle();
            if ($("#pie_graphs").is(":visible")) {
                $("#graphtext").html('<i class="fa fa-caret-down graphtoggle"></i>&nbsp;&nbsp;Charts&nbsp;');
            } else {
                $("#graphtext").html('<i class="fa fa-caret-up graphtoggle"></i>&nbsp;&nbsp;Charts&nbsp;');
            }
        });
    }
});

function padDigits(number, digits) {
    return Array(Math.max(digits - String(number).length + 1, 0)).join(0) + number;
}
  
function setTimer(distance, id) {
    // Update the count down every 1 second
    var x = setInterval(function() {
        // Time calculations for days, hours, minutes and seconds
        var hours = Math.max(0,Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)));
        var minutes = Math.max(0,Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)));
        var seconds = Math.max(0,Math.floor((distance % (1000 * 60)) / 1000));

        // Display the result in the element with id="demo"
        var hourval = "";
        if (hours > 0) {
            hourval = hours + "h ";
        }
        $("#timercount" + id).text(hourval + padDigits(minutes,2) + "m " + padDigits(seconds,2) + "s ");

        // If the count down is finished, write some text
        if (distance <= 0) {
            clearInterval(x);
            $("#timercount" + id).text("EXPIRED");
        }
        distance = distance - 1000;
    }, 1000);
}