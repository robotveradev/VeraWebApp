$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let vacancy = {
            title: 'vacancy',
            steps: [
                {
                    'next [data-hint=main-info]': 'Here you can see main vacancy info.<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    showSkip: false,
                },
                {
                    'next [data-hint=vacancy-info]': 'Here you find additional vacancy information<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    showSkip: false,
                }
            ],
        };

        if ($('[data-hint=apply-vacancy]').length > 0) {
            vacancy.steps.push(...[
                {
                    'next [data-hint=pipeline]': 'There is the <span class="hint-green">vacancy pipeline</span><br/>' +
                    'It usually consists of several <span class="hint-green">actions</span><br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    showSkip: false,
                },
                {
                    'next #pipeline>div>div.uk-width-2-3.uk-margin-small-top.uk-padding-remove-left>div>div:nth-child(1)': 'Here is the <span class="hint-green">action</span><br/>' +
                    'Action may be approvable or not, payable or unpayable.<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    shape: 'circle',
                    radius: 60,
                    showSkip: false,
                },
                {
                    'custom [data-hint=apply-vacancy]': 'Now <span class="hint-green">apply</span> this vacancy and go on.<br/>' +
                    'Click <span class="hint-green">APPLY</span> button to continue.',
                    showSkip: false,
                    showNext: false,

                }
            ])
        } else {
            vacancy.steps.push(...[
                {
                    'click [data-hint=profile-drop]': 'Looks like you don\'t set <span class="hint-green"> career objectives </span><br/>' +
                    'without them you can not<span class="hint-green"> apply vacancy</span><br/>' +
                    'Go at <span class="hint-green">profile</span> page and complete it.',
                    showSkip: false,
                },
            ])
        }

        if ($('.pulse').length > 0) {
            let $first_passed = $('.action.green.lighten-5');

            if ($first_passed.length > 0) {
                let action_passed = {
                    title: 'action_passed',
                    steps: [
                        {
                            'next .lighten-5': 'Here you can see that first action now ' +
                            '<span class="hint-green">passed</span> and now you can <span class="hint-green">pass next</span><br/>' +
                            'Click <span class="hint-green">NEXT</span> button to continue.',
                            shape: 'circle',
                            radius: 65,
                            showSkip: false,
                        },
                        {
                            'next .pulse': 'Now you at <span class="hint-green">interview </span>' +
                            'vacancy <span class="hint-green">pipeline</span> action.<br/>' +
                            'Click <span class="hint-green">NEXT</span> button to continue.',
                            showSkip: false,
                            shape: 'circle',
                            radius: 65,
                        },
                        {
                            'click [data-hint=passage-condition]>li:nth-child(1)': 'Here your interview action <span class="hint-green">condition of passage.</span><br/>' +
                            '<span class="hint-green">Click</span> it to continue.',
                            showSkip: false,
                        }
                    ]
                };

                hint_set.push(action_passed);
            }
            let vacancy_pipeline = {
                title: 'vacancy_pipeline',
                steps: [
                    {
                        'next .pulse': '<span class="hint-green">Congratulation!</span> Now you at <span class="hint-green">first </span>' +
                        'vacancy <span class="hint-green">pipeline</span> action.<br/>' +
                        'Click <span class="hint-green">NEXT</span> button to continue.',
                        showSkip: false,
                        shape: 'circle',
                        radius: 65,
                    },
                    {
                        'next [data-hint=step-info]': 'Here you can see action info, like <br/>' +
                        '<span class="hint-green">fee amount</span> and ' +
                        '<span class="hint-green">passage conditions</span>.<br/>' +
                        'Click <span class="hint-green">NEXT</span> button to continue.',
                        showSkip: false,
                    },
                    {
                        'click [data-hint=passage-condition]>li:nth-child(1)': 'Here your first action <span class="hint-green">condition of passage.</span><br/>' +
                        '<span class="hint-green">Click</span> it to continue.',
                        showSkip: false,
                    }
                ],
            };
            hint_set.push(vacancy_pipeline);
        }

        hint_set.push(vacancy);
    }
});
