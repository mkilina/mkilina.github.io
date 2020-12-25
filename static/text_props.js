var setupTextEditing = function() {
    var urlParams = new URLSearchParams(window.location.search);
    $.get(`/get_statistics/${urlParams.get('file_id')}`, function(data) {
        const readability = data.readability_score;
        $("#FRE").text(readability);

        const file_id = urlParams.get('file_id');
        $("#filename").text(file_id);
        
        const total = data.total_words;
        $("#totalWords").text(total);

        const unique = data.unique_words;
        $("#uniqueWords").text(unique);

        var barData = {
            labels: ['ECON', 'JUR', 'LING', 'PSYCH', 'HIST', 'SOC', 'YOU'],
            datasets: [{
                fillColor: ['rgba(151,187,205,0.2)', "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,1)"],
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(151,187,205,1)",
                data : [76.6, 87.03, 82.17, 78.13, 91.11, 77.95, readability]
                }]
            }
        var mychart = document.getElementById("chart").getContext("2d");

        steps = 10
        max = 130

        new Chart(mychart).Bar(barData, {
        scaleOverride: true,
        scaleSteps: steps,
        scaleStepWidth: Math.ceil(max / steps),
        scaleStartValue: 30,
        scaleShowVerticalLines: true,
        scaleShowGridLines: true,
        barShowStroke: true,
        scaleShowLabels: true
        }
        );

    });

}

setTimeout(setupTextEditing, 0);