$(document).ready(function () {
    let pass = localStorage.getItem('find_job');
    if (pass !== '0') {
        let enjoyhint_instance = new EnjoyHint({
            onSkip: function () {
                localStorage.setItem('find_job', '0')
            }
        });
        let enjoyhint_script_steps = [];
        if ($('[data-hint=filtered]').length > 0) {
            enjoyhint_script_steps.push({
                'next [data-hint=filtered]': 'Here you can see most relevant vacancies for you',
                showSkip: false,
            },)
        }


        enjoyhint_script_steps.push(
            {
                'next [data-hint=filters]': 'Using the filtering panel, you can find work on different parameters...',
                showSkip: false
            }, {
                'next [data-hint=industries]': 'Like <span class="light-green-text text-accent-3">industries</span>',
                showSkip: false
            }, {
                'next [data-hint=keywords]': '<span class="light-green-text text-accent-3">Keywords</span>',
                showSkip: false
            }, {
                'next [data-hint=salary]': '<span class="light-green-text text-accent-3">Salary</span>',
                showSkip: false
            }, {
                'next [data-hint=busyness]': '<span class="light-green-text text-accent-3">Busyness</span>',
                showSkip: false
            }, {
                'next [data-hint=schedule]': '<span class="light-green-text text-accent-3">Or schedule</span>',
                showSkip: false
            }, {
                'next [data-hint=sort]': 'Also you can sort filtered vacancies',
                showSkip: false,
                shape: 'circle',
                radius: 80
            }, {
                'custom [data-hint=reset]': 'Or reset all filters and sorts',
                skipButton: {text: 'Done'},
                shape: 'circle',
                'radius': 20,

            });

        enjoyhint_instance.set(enjoyhint_script_steps);
        enjoyhint_instance.run();
    }
});

