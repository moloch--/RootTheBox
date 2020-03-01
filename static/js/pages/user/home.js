var skills_chart;
/* Highcharts code */
$(document).ready(function() {
    /* Skill Chart */
    if ($("#spider_skills").length > 0) {
        skill_chart = new Highcharts.Chart({
            chart: {
                renderTo: 'spider_skills',
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                backgroundColor:'transparent',
                polar: true,
                type: 'line',
                marginTop: 55
            },
            title: {
                text: '<strong>' + $("#spider_skills").data("name") + '</strong>',
                style: {
                    color: '#FFFFFF',
                    font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
                    'text-shadow': '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black',
                },
            },
            tooltip: {
                shared: true,
                pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>'
            },    
            xAxis: {
                categories: "",
                tickmarkPlacement: 'on',
                lineWidth: 0
            },
            yAxis: {
                gridLineInterpolation: 'polygon',
                lineWidth: 0,
                min: 0
            },
            legend: {
                enabled: false,
                align: 'right',
                verticalAlign: 'top',
                y: 70,
                layout: 'vertical'
            },
            series: [{
                name: 'Skill Progress',
                type: 'area',
                data: [5,6,8],
                pointPlacement: 'on'
            }],
        });
    }
});

/* Update code */
$(document).ready(function() {
    if ($("#spider_skills").length > 0) {
        skill_chart.xAxis[0].setCategories($.parseJSON(categories));
        /* Update Graph */
        $.get("/scoreboard/ajax/skills?uuid=" + $("#spider_skills").data("uuid"), function(skillvalues) {
            skill_chart.series[0].setData($.parseJSON(skillvalues), true);
        });
    }
});