$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let index_candidate = {
            title: 'index_candidate',
            steps: [
                {
                    'next #vacancies': 'Here you can <span class="hint-green">find a job</span><br>' +
                    'Click <span class="hint-green">NEXT</span>',
                    showSkip: false
                },
                {
                    'next [data-hint=feedback]': 'and here you will see all jobs offered to you',
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
        hint_set.push(index_candidate);
    }
});
