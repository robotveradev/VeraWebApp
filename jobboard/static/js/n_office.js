$(document).ready(function () {

    let input_elem = '<div class="uk-margin">' +
        '<label class="uk-form-label" for="new_office">New office address' +
        '</label>' +
        '<div class="uk-form-controls">' +
        '<input class="uk-input address" id="new_office" maxlength="255" placeholder="New office address" type="text">' +
        '<span style="font-size: 0.7rem" class="uk-text-meta">Enter the address of the new office, and click Enter button</span>' +
        '</div>' +
        '</div>';

    let new_office = function () {
        let office_choice_field = $('#id_office').closest('div.uk-margin');
        office_choice_field.after(input_elem);
        $('#new_office').on('keydown', function (e) {
            if (e.which === 13) {
                let company = $('#id_company');
                if (company.val() === '') {
                    UIkit.notification({message: 'Please, select a company first', pos: 'top-right'});
                    company.focus();
                } else {
                    $.ajax({
                        url: '/company/' + company.val() + '/office/new/',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val(),
                            address: $(this).val(),
                        },
                        success: function (d) {
                            $('#id_office').append('<option value="' + d.id + '" selected>' + d.label + '</option>');
                            $('#new_office').val('');
                        },
                        error: function (e) {
                            UIkit.notification({message: 'Error saving new office', pos: 'top-right'});
                        }
                    });
                }
            }
        });
    };
    new_office();

    function cl(val) {
        console.log(val);
    }
});
