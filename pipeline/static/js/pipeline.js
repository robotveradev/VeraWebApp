$(document).ready(function () {
    $('#form-horizontal-select').on('change', function () {
        let must_app = $(this).children('option:selected').data('appr');
        $('[name=approvable]').prop('disabled', must_app).prop('checked', must_app);
    });

    let $status = $('input[name=status]');

    if ($status.length > 0) {
        $status.on('change', function () {
            UIkit.modal.confirm('Change vacancy status? This may take some time.').then(function () {
                $('#change_vacancy_status')[0].submit();
            }, function () {
                console.log('Rejected.');
            });

        })
    }
});
