$(document).ready(function () {
    $('.slider').slider({
        indicators: false
    });
    $('.collapsible').collapsible();
    $('select').material_select();
    $('.modal').modal();

    $('.dropdown-button').dropdown({
            inDuration: 300,
            outDuration: 225,
            constrainWidth: false, // Does not change width of dropdown to that of the activator
            hover: false, // Activate on hover
            gutter: 0, // Spacing from edge
            belowOrigin: false, // Displays dropdown below the button
            alignment: 'left', // Displays dropdown with edge aligned to the left of button
            stopPropagation: false // Stops event propagation
        }
    );

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
    $('.tooltipped').tooltip({delay: 50});

    function hide_more(elem) {
        var spec_list = $('#' + elem + ' ul');
        var elem_count = spec_list.children('li').length;
        if (elem_count > 5) {
            $('#' + elem + '_less').remove();
            for (var i = 5; i < elem_count; i++) {
                spec_list.children('li').eq(i).hide();
            }
            spec_list.append('<li id="' + elem + '_more" class="spec-item"><span class="more-link">More...</span><span class="right">' + (elem_count - 5) + '</span></li>');
        }
    }

    function show_more(elem) {
        var spec_list = $('#' + elem + ' ul');
        var elem_count = spec_list.children('li').length;
        if (elem_count > 5) {
            $('#' + elem + '_more').remove();
            for (var i = 5; i < elem_count; i++) {
                spec_list.children('li').eq(i).show();
            }
            spec_list.append('<li id="' + elem + '_less" class="spec-item"><span class="hide-link">Less</span></li>');
        }
    }

    hide_more('specialisation');
    hide_more('salary');
    hide_more('keyword');
    hide_more('industry');

    $(document).on('click', '.more-link', function () {
        show_more($(this).parents('div')[0].id);
    }).on('click', '.hide-link', function () {
        hide_more($(this).parents('div')[0].id);
    });


});