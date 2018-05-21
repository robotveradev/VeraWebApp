$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let profile = {
            title: 'profile',
            steps: [
                {
                    'next [data-hint=profile_head]': '<span class="hint-green">Congratulations!</span><br/>' +
                    'You have <span class="hint-green">successfully</span> created a profile in the <span class="hint-green">Vera Oracle system</span>, ' +
                    'and soon all the features of the portal will be available to you.',
                    showSkip: false,
                },
                {
                    'next [data-hint=status_change]': 'Later in this place you will see the current <span class="hint-green">status</span> of ' +
                    'your <span class="hint-green">contract</span> in the system,<br/>' +
                    'also you can independently <span class="hint-green">change the status</span> of your contract.',
                    showSkip: false,
                }
            ],
        };
        hint_set.push(profile);
    }
});
