$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let candidate_profile = {
            title: 'candidate_profile',
            steps: [
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
                    'click [data-hint=position]': 'Go at <span class="hint-green">career objective</span> page right now.',
                    showSkip: false
                },
                {
                    'click [data-hint=new-position]': 'Click <span class="hint-green">Add career objective</span>',
                    showSkip: false,
                }
            ]
        };

        let candidate_profile_vacancies = {
            title: 'candidate_profile_vacancies',
            steps: [
                {
                    'click #vacancies': 'Go at <span class="hint-green">VACANCIES</span> page right now.',
                    showSkip: false
                }
            ]
        };


        let $no_pos = $('[data-hint=no-position]');
        if ($no_pos.length > 0) {
            hint_set.push(candidate_profile);
        } else {
            hint_set.push(candidate_profile_vacancies);
        }
    }
});



