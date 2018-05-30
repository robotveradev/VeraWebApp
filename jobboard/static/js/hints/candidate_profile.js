$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let candidate_profile1 = {
            title: 'candidate_profile1',
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
                    'click #career_objective': 'Go at <span class="hint-green">career objective</span> page right now.',
                    showSkip: false
                }
            ]
    };
        let candidate_profile2 = {
            title: 'candidate_profile2',
            steps: [
                {
                    'click #add_experience_info': 'Go at <span class="hint-green">experience info</span> page right now.',
                    showSkip: false
                }
            ]
    };
        let candidate_profile3 = {
            title: 'candidate_profile3',
            steps: [
                {
                    'click #add_education_info': 'Go at <span class="hint-green">education info</span> page right now.',
                    showSkip: false
                }
            ]
    };
         let candidate_profile4 = {
            title: 'candidate_profile4',
            steps: [
                {
                    'click #vacancies': 'Go at <span class="hint-green">VACANCIES</span> page right now.',
                    showSkip: false
                }
            ]
    };
         hint_set.push(candidate_profile1, candidate_profile2, candidate_profile3, candidate_profile4);
    }
});



