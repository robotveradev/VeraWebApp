$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let index_choose_role = {
            title: 'index_choose_role',
            steps: [
                {
                    'next #logout': '<span class="hint-green">Congratulation!</span> You successfully log in!<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    showSkip: false
                },
                {
                    'click [data-hint=profile_drop]': 'Now click here...',
                    'timeout': 3,
                    showSkip: false
                },
                {
                    'click [data-hint=profile]': '...and go at profile page!',
                    showSkip: false
                }
            ],
        };
        hint_set.push(index_choose_role);
    }
});
