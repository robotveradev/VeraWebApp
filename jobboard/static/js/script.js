$(document).ready(function () {

    $('.cv_switch').on('change', function () {
        $(this).parents('form').submit();
    });

    function hide_more(elem) {
        let spec_list = $('#' + elem + ' ul');
        let elem_count = spec_list.children('li').length;
        if (elem_count > 5) {
            $('#' + elem + '_less').remove();
            for (let i = 5; i < elem_count; i++) {
                spec_list.children('li').eq(i).hide();
            }
            spec_list.append('<li id="' + elem + '_more" class="spec-item"><span class="more-link">More</span></li>');
        }
    }

    function show_more(elem) {
        let spec_list = $('#' + elem + ' ul');
        let elem_count = spec_list.children('li').length;
        if (elem_count > 5) {
            $('#' + elem + '_more').remove();
            for (let i = 5; i < elem_count; i++) {
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

    $('#check_agent').on('click', function (event) {
        let address_input = $('#agent_address');
        let agent_address = address_input.val();
        if (agent_address === '') {
            address_input.focus();
            address_input.addClass('uk-form-danger');
            return false;
        } else {
            $.ajax({
                url: '/check_agent/',
                type: 'post',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    agent_address: agent_address
                },
                complete: function (x, q) {
                    if (x.status === 400) {
                        address_input.focus();
                        address_input.addClass('uk-form-danger');
                    }
                },
                success: function (data) {
                    address_input.removeClass('uk-form-danger').addClass('uk-form-success');
                    let link_item = $('#grant_revoke_link');
                    let elem = '';
                    let link = '';
                    let action = '';
                    link_item.show();
                    if (data === 'False') {
                        link = '/agent/grant/?address=';
                        elem = 'Address ' + agent_address + ' not is agent.';
                        action = 'grant';
                    } else if (data === 'True') {
                        link = '/agent/revoke/?address=';
                        elem = 'Address ' + agent_address + ' is agent.';
                        action = 'revoke';
                    } else {
                        elem = 'The address ' + agent_address + ' is agent and cannot be revoked from oracle system.';
                        action = 'oracle contract';
                        link_item.hide();
                    }
                    $('#grant_revoke_title').text(action + ' agent');
                    link_item.attr('href', link + agent_address).text(action);
                    $('#agent_status').html(elem);
                    UIkit.modal('#grant_revoke_agent').show();
                }
            })
        }
    });

    $('textarea:not(.simple)').htmlarea({
        toolbar: ["bold", "italic", "underline", "|", "p", "h1", "h2", "h3", "h4", "h5", "h6", "|", "indent", "outdent", "|", "orderedList", "unorderedList", "horizontalrule", "|", "justifyLeft", "justifyCenter", "justifyRight"]
    });
    $('.jHtmlArea').parent('div').addClass('jHtml-textarea');

    $('.select-all').on('click', function () {
        $(this).closest('li').find('input').each(function (i, item) {
            if (!$(item).is(':disabled')) {
                $(item).attr('checked', true);
            }
        });
    });

    $('input[name="test_answer"]').closest('div').find('a').on('click', function () {
        let question_id = $(this).data('question-id');
        let answer = $(this).closest('div').find('input').val();
        if (answer === '') {
            UIkit.notification({
                message: 'Please specify the answer text',
                status: 'primary',
                pos: 'top-right',
                timeout: 3000
            });
        } else {
            $.ajax({
                url: '/quiz/process/answer/',
                type: 'POST',
                context: $(this),
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    que_id: question_id,
                    ans: answer
                },
                success: function () {
                    location.reload();
                }
            })
        }
        return false;
    });

    $('.toggle-icon').on('click', function () {

        "chevron-down" === $(this).attr("data-uk-icon") ? $(this).attr("data-uk-icon", "chevron-up") : $(this).attr("data-uk-icon", "chevron-down");
    })
});





