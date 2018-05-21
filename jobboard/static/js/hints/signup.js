$(document).ready(function () {

    let pass = localStorage.getItem('signup');
    if (pass !== '0') {
        let enjoyhint_instance = new EnjoyHint({
            onStart: function () {
                $('#id_username').blur();
                $('form').on('keydown', function (e) {
                    if (e.which === 13) {
                        return false;
                    }
                });
            },
            onSkip: function () {
                localStorage.setItem('signup', '0')
            }
        });
        let enjoyhint_script_steps = [];
        if ($('.uk-text-danger').length > 0) {
            enjoyhint_script_steps.push({
                'next .uk-text-danger': 'Ooops, looks like there is some errors in signup progress. Lets try again.<br/>' +
                'Click <span class="hint-green">NEXT</span> to continue.',
                showSkip: false
            })
        }


        enjoyhint_script_steps.push(
            {
                'next form': 'To <span class="hint-green">register</span> you must complete fields below.<br/>' +
                'Click <span class="hint-green">NEXT</span> to continue.',
                showSkip: false
            },
            {
                'key #id_username': 'Enter you <span class="hint-green">username.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
                onBeforeStart: function () {
                    $('#id_username').focus();
                }
            },
            {
                'key #id_password': 'Enter you <span class="hint-green">password.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'key #id_password_confirm': 'Repeat you <span class="hint-green">password</span> one more time.<br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'key #id_email': 'And your <span class="hint-green">email.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'click [type=submit]': 'Click the button <span class="hint-green">SIGN UP</span> for register.',
                shape: 'circle',
                radius: 50,
                showSkip: false
            },
        );

        enjoyhint_instance.set(enjoyhint_script_steps);
        enjoyhint_instance.run();
    }
});
