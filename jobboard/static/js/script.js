$(document).ready(function () {
    $('.slider').slider({
        indicators: false
    });
    $('.collapsible').collapsible();
    $('select').material_select();
    $('.modal').modal();

    var time_block = $("#time_to_block");
    var time_per_block = time_block.data('per-block');
    setInterval(function () {
        var time = Number(time_block.text()) + 1;
        if (time <= time_per_block - 1) {
            time_block.text(time);
        } else {
            time_block.text(0);
        }
    }, 1000);
});
