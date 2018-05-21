$(document).ready(function () {
    let pass = localStorage.getItem('candidate_profile');
    if (pass !== '0') {
        let enjoyhint_instance = new EnjoyHint({
            onSkip: function () {
                localStorage.setItem('candidate_profile', '0')
            }
        });

        let enjoyhint_script_steps = [
            {
                'next [data-hint=profile_head]': '<span class="hint-green">Congratulations!</span><br/>' +
                'You have <span class="hint-green">successfully</span> created a profile in the <span class="hint-green">Vera Oracle system</span>, ' +
                'and soon all the features of the portal will be available to you.',
                showSkip: false
            },
            {
                'next [data-hint=main_info]': 'You can see main profile info, like <span class="hint-green">first name, ' +
                '</span><span class="hint-green">last name, </span><span class="hint-green">middle name </span> ' +
                'and <span class="hint-green">tax number.</span>',
                showSkip: false
            },
            {
                'next [data-hint=contract_address]': '<span class="hint-green">Your own contract address.</span><br/>' +
                'If it\'s spinner here right now - your contract does not ready yet, and address will be here soon =)',
                showSkip: false
            },
            {
                'next [data-hint=balance]': 'And <span class="hint-green">your balance</span> in  <span class="hint-green">Vera Coin</span> here',
                showSkip: false,
            },
            {
                'next [data-hint=status_change]': 'Later in this place you will see the current <span class="hint-green">status</span> of ' +
                'your <span class="hint-green">contract</span> in the system,<br/>' +
                'also you can independently <span class="hint-green">change the status</span> of your contract.',
                showSkip: false,
            },
            {
                'click #vacancies': 'Go at <span class="hint-green">vacancies</span> page right now.',
                showSkip: false
            }
        ];

        enjoyhint_instance.set(enjoyhint_script_steps);
        enjoyhint_instance.run();
    }
});




