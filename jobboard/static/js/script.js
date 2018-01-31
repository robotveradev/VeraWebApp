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

    $('.cv_switch').on('change', function () {
        $(this).parents('form').submit();
    });
    // $('.datepicker').pickadate({
    //     selectMonths: true, // Creates a dropdown to control month
    //     selectYears: 100, // Creates a dropdown of 60 years to control year,
    //     today: 'Today',
    //     clear: 'Clear',
    //     close: 'Ok',
    //     min: new Date(1950, 1, 1),
    //     max: new Date(2002, 11, 31),
    //     closeOnSelect: false, // Close upon selecting a date,
    //     format: ''
    // });
});
