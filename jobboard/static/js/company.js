$(document).ready(function () {
    $('select[name=role]').on('change', function () {
        let $sel = $(this);
        let new_role = $(this).val();
        UIkit.modal.confirm(`Do you want to change member role to ${new_role}?`).then(function () {
            $sel.closest('form')[0].submit();
        }, function () {
            $sel.closest('form')[0].reset();
            console.log('Change role rejected.')
        });
    })
});
