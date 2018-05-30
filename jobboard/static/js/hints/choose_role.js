$(document).ready(function () {
    let pass = localStorage.getItem('choose_role');
    if (pass !== '0') {

    }
});
let enjoyhint_instance = new EnjoyHint({
    onStart: function () {
        $('form').on('keydown', function (e) {
            if (e.which === 13) {
                return false;
            }
        }).on('submit', function () {
            localStorage.setItem('choose_role', '0')
        });
    },
    onSkip: function () {
        localStorage.setItem('choose_role', '0')
    }
});

let enjoyhint_script_steps = [
    {
        'next .uk-legend': 'Oooops! <span class="hint-green">I completely forgot! </span><br/>' +
        'Before you get into the <span class="hint-green">profile</span>, you need to choose the role of the ' +
        '<span class="hint-green">candidate</span> or <span class="hint-green">employer.</span><br/>' +
        'Click <span class="hint-green">NEXT</span> button to continue.',
        showSkip: false
    },
    {
        'click [data-hint=roles]': 'Click one of <span class="hint-green">candidate</span> or <span class="hint-green">employer</span> tab to choose it.<br/>' +
        '&emsp;<span class="hint-green">hint:</span><br/>' +
        '&emsp;&emsp;if you are looking for an employee - select the <span class="hint-green">employer</span> tab,<br/>' +
        '&emsp;&emsp;otherwise if you are looking for a job - select the <span class="hint-green">candidate</span> tab',
        showSkip: false
    },
];

$('[data-hint=roles] > li').on('click', function () {
    let role = $(this).data('role');
    if (role === 'candidate') {
        enjoyhint_script_steps.push(
            {
                'next [data-hint=fields_candidate]': 'You choose <span class="hint-green">candidate</span> role.<br/>' +
                'Now you must complete some fields.<br/>' +
                'Click <span class="hint-green">NEXT</span> button to continue.',
                showSkip: false
            },
            {
                'key #first_name': 'Enter you <span class="hint-green">first name.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
                onBeforeStart: function () {
                    $('#first_name').focus();
                }
            },
            {
                'key #last_name': 'Enter you <span class="hint-green">last name.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'key #middle_name': 'Enter you <span class="hint-green">middle name.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'key #tax_number': 'And you <span class="hint-green">tax number</span> here<br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'click [data-hint=personal_data_candidate]': 'You must accept this for continue.',
                showSkip: false,
            },
            {
                'click [data-hint=send_but_candidate]': '<span class="hint-green">Looks right!</span><br/>' +
                'Now click <span class="hint-green">SEND</span> button to continue!',
                shape: 'circle',
                radius: 50,
                showSkip: false
            }
        )
    } else if (role === 'employer') {
        enjoyhint_script_steps.push(
            {
                'next [data-hint=fields_employer]': 'You choose <span class="hint-green">employer</span> role.<br/>' +
                'Now you must complete some fields.<br/>' +
                'Click <span class="hint-green">NEXT</span> button to continue.',
                showSkip: false
            },
            {
                'key #first_name_employer': 'Enter your <span class="hint-green">first name.</span><br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
                onBeforeStart: function () {
                    $('#first_name_employer').focus();
                }
            },
            {
                'key #last_name_employer': 'And you <span class="hint-green">middle name</span> here.<br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'key #middle_name_employer': 'And you <span class="hint-green">tax number</span> here.<br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'key #tax_number_employer': 'And you <span class="hint-green">tax number</span> here.<br/>' +
                'Click <span class="hint-green">TAB</span> button to continue.',
                keyCode: 9,
                showSkip: false,
            },
            {
                'click [data-hint=personal_data_employer]': 'You must accept this for continue.',
                showSkip: false,
            },
            {
                'click [data-hint=send_but_employer]': '<span class="hint-green">Looks right!</span><br/>' +
                'Now click <span class="hint-green">SEND</span> button to continue!',
                shape: 'circle',
                radius: 50,
                showSkip: false
            }
        )
    }
});


enjoyhint_instance.set(enjoyhint_script_steps);
enjoyhint_instance.run();
