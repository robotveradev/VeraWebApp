$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let candidate_profile1 = {
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
                }
            ]
    };
        let career_objective = {
            title: 'career_objective',
            steps: [
                {
                    'click #career_objective': 'Go at <span class="hint-green">career objective</span> page right now.',
                    showSkip: false
                }
            ]
        };
        let add_experience_info = {
            title: 'add_experience_info',
            steps: [
                {
                    'click #add_experience_info': 'Go at <span class="hint-green">experience info</span> page right now.',
                    showSkip: false
                }
            ]
    };
        let add_education_info = {
            title: 'add_education_info',
            steps: [
                {
                    'click #add_education_info': 'Go at <span class="hint-green">education info</span> page right now.',
                    showSkip: false
                }
            ]
    };
         let vacancies = {
            title: 'vacancies',
            steps: [
                {
                    'click #vacancies': 'Go at <span class="hint-green">VACANCIES</span> page right now.',
                    showSkip: false
                }
            ]
    };
         hint_set.push(candidate_profile1);
         if(document.career_objective){
             console.log(document.career_objective);
            hint_set.push(career_objective);
        }
        hint_set.push(add_experience_info, add_education_info, vacancies);
    }
});



