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
                'next [data-hint=signup-head]': 'For <span class="hint-green">register</span> you must complete fields below.<br/>' +
                'Click <span class="hint-green">NEXT</span> to continue.',
                showSkip: false
            },
            {
                ' [type=submit]': 'Then click <span class="hint-green">SIGN UP</span> to continue.',
                shape: 'circle',
                radius: 50,
                showNext: false,
                skipButton: {text: 'Ok'}
            },
        );
        enjoyhint_instance.set(enjoyhint_script_steps);
        enjoyhint_instance.run();
    }
});
