$(document).ready(function () {
    let $fee = $('input[name=fee]');
    let $appr = $('input[name=approvable]');
    let $act_type = $('select[name=action_type]');
    let $changes_button = $('button#save_action_changes');

    let initial = {
        fee: Number($fee.val()),
        appr: $appr[0].checked,
        type: $act_type.val(),
    };

    $fee.on('keydown', function () {
        setTimeout(function () {
            set_save_button()
        }, 100);
    });

    $appr.on('change', function () {
        setTimeout(function () {
            set_save_button()
        }, 100);
    });

    $act_type.on('change', () => {
        setTimeout(function () {
            set_save_button()
        }, 100);
    });

    set_save_button = () => {
        check_values() && $changes_button.show() || $changes_button.hide();
    };

    check_values = () => {
        let nothing_changed =
            $fee.val() == initial.fee &&
            $appr[0].checked == initial.appr &&
            $act_type.val() == initial.type;
        return !nothing_changed;
    };

    $('input[type=range]').on('change', function () {
        $.ajax({
            url: '/quiz/exam/' + $('input[name=e_id]').val() + '/update/grade/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                passing_grade: $(this).val()
            },
            success: function (data) {
                if (data === 'True') {
                    UIkit.notification({
                        message: 'Passing grade successfully updated!',
                        status: 'success',
                        pos: 'top-right',
                        timeout: 3000
                    });
                } else {
                    UIkit.notification({
                        message: 'Some problems while update passing grade...',
                        status: 'danger',
                        pos: 'top-right',
                        timeout: 3000
                    });
                }
            }
        });
    }).on('input', function () {
        $('#passing_grade').text($(this).val());
    });

    $('#change-action').on('submit', function (e) {
        check_values() || e.preventDefault();
    })
});
