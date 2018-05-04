$(document).ready(function () {
    $('#alert_increase').hide().find('a').on('click', function () {
        $(this).closest('#alert_increase').hide();
    });
    $('.ban-action').on('click', function () {
        $(this).closest('li').toggleClass('disabled');
    });

    $('#pipeline-constructor select').on('change', function () {
        let fee_item = $(this).closest('div').find('input[name="fee"]');
        if ($(this).find(":selected").data('fee')) {
            fee_item.show();
        } else {
            fee_item.hide();
        }
    });

    $('#pipeline_form_submit').on('click', function (e) {
        e.preventDefault();
        let totalFee = 0;
        let allowed_amount = Number($('#allowed').text());
        let lis = $('ul#pipeline-constructor').find('li');
        lis.map(function (i, item) {
            let select = $(item).find('div > div > select');
            if ($(select).val() === null || $(item).hasClass('disabled')) {
                $(item).remove();
            } else {
                let approve = $(item).find('input[type=checkbox]')[0];
                let approve_input = $(item).find('input[name="approve"]')[0];
                let fee = $(item).find('input[name="fee"]')[0];
                $(fee).val($(fee).val() > 0 ? $(fee).val() : 0);
                totalFee += Number($(fee).val());
                if (approve.checked) {
                    $(approve_input).val('True');
                } else {
                    $(approve_input).val('False');
                }
            }
        });
        if (totalFee > allowed_amount) {
            $('#alert_increase').show();
            $('#new_allowed').attr('min', totalFee)
        } else {
            $('#pipeline_form').submit();
        }
    });

    $('#increase_allowed_form').on('submit', function (e) {

        e.preventDefault();

        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (data) {
                console.log('Submission was successful.');
                UIkit.modal('#increase').hide();
                $('#pipeline_form').submit();
            },
            error: function (data) {
                console.log('An error occurred.');
                console.log(data);
            },
        });
    });
});
