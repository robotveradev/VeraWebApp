$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let profile_complete = {
            title: 'profile_complete',
            steps: [
                {
                    'key input[name=photo]': '<span class="hint-green">Please</span> chose <span class="hint-green">your photo</span> from your <span class="hint-green">computer</span> files.<br/>' +
                    'According to statistics, this increases the attractiveness of the resume by 50%.<br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_birth_date_month': '<span class="hint-green">Please</span> enter <span class="hint-green">your birthday month </span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_birth_date_day': '<span class="hint-green">Please</span> enter <span class="hint-green">your birthday date </span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_birth_date_year': '<span class="hint-green">Please</span> enter <span class="hint-green">your birthday year </span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_sex': '<span class="hint-green">Please</span> chose <span class="hint-green">your gender</span><br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_address': '<span class="hint-green">Please</span> enter <span class="hint-green">your address </span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },

                {
                    'key #id_relocation': '<span class="hint-green">Please</span> answer, <span class="hint-green">do you</span> ready <span class="hint-green">for</span> relocation?<br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_official_journey': '<span class="hint-green">Please</span> answer, <span class="hint-green">do you</span> ready <span class="hint-green">for</span>  official journey?<br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_specialisations': '<span class="hint-green">Please</span> chose <span class="hint-green">your specialisation</span><br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_keywords': '<span class="hint-green">Please</span> chose <span class="hint-green">Keywords</span><br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_level': '<span class="hint-green">Please</span> chose your<span class="hint-green"> Education level</span><br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    selector: '#save',
                    event: 'click',
                    description : '<span class="hint-green">Please</span> click <span class="hint-green">SAVE to continion</span>.<br/>' +
                    'Click <span class="hint-green">Save</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                }
            ],
        };
        hint_set.push(profile_complete);
    }
});
