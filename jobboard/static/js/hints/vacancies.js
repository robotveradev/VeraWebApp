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
            enjoyhint_script_steps.push(
                {
                    'next [data-hint=filtered]': 'Here you can see most relevant vacancies for you',
                    showSkip: false,
                },
                {
                    'click [data-hint=filtered]': 'Choose <span class="hint-green">@HINTS_TUTORIAL_VACANCY</span>',
                }
            )
        }

        enjoyhint_script_steps.push(
            {
                'next [data-hint=filters]': 'Using the filtering panel, you can find work on different parameters...',
                showSkip: false
            }, {
                'next [data-hint=industries]': 'Like <span class="hint-green">industries</span>',
                showSkip: false
            }, {
                'next [data-hint=keywords]': '<span class="hint-green">Keywords</span>',
                showSkip: false
            }, {
                'next [data-hint=salary]': '<span class="hint-green">Salary</span>',
                showSkip: false
            }, {
                'next [data-hint=busyness]': '<span class="hint-green">Busyness</span>',
                showSkip: false
            }, {
                'next [data-hint=schedule]': '<span class="hint-green">Or schedule</span>',
                showSkip: false
            }, {
                'next [data-hint=sort]': 'Also you can sort filtered vacancies',
                showSkip: false,
                shape: 'circle',
                radius: 80
            }, {
                'next [data-hint=reset]': 'Or reset all filters and sorts',
                showSkip: false,
            },
            {
                'click [data-hint=keywords]': 'Choose <span class="hint-green">programming</span> keyword',
                showSkip: false

            });

        enjoyhint_instance.set(enjoyhint_script_steps);
        enjoyhint_instance.run();
    }
});

