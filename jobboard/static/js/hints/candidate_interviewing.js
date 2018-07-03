$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let $scheduled = $('[data-hint=scheduled]');
        if ($scheduled.length === 0) {
            let interviewing = {
                title: 'interviewing',
                steps: [
                    {
                        'next [data-hint=scheduling-main]': 'Now you at <span class="hint-green">interview configure</span> page.<br/>' +
                        'Click <span class="hint-green">NEXT</span> button to continue.',
                        showSkip: false,
                    },
                    {
                        'next [data-hint=meeting-available]': 'Here you can see ' +
                        '<span class="hint-green">next available meeting</span>' +
                        ' date and time<br/>' +
                        'Click <span class="hint-green">NEXT</span> button to continue.',
                        showSkip: false,
                    },
                    {
                        'click [data-hint=confirm]': 'Click <span class="hint-green">CONFIRM</span> button for now to schedule meeting',
                        showSkip: false,
                    }
                ],
            };

            hint_set.push(interviewing);
        } else {
            let interview_scheduled = {
                title: 'interview_scheduled',
                steps: [
                    {
                        'next [data-hint=scheduled]': '<span class="hint-green">All right!</span><br/>' +
                        'You successfully schedule meeting with employer.<br/>' +
                        'A few minutes before the ' +
                        '<span class="hint-green">interview</span>' +
                        ', you will receive an ' +
                        '<span class="hint-green">email containing a link</span>' +
                        ' to the video interview.',
                        showSkip: false,
                    }
                ]
            };

            if ($('[data-hint=link-available]').length > 0) {
                interview_scheduled.steps.push({
                    'click [data-hint=link-available]': 'But before the ' +
                    '<span class="hint-green">beginning</span>' +
                    ' of your ' +
                    '<span class="hint-green">interview</span>' +
                    ' is not so much ' +
                    'time, and ' +
                    '<span class="hint-green">you can start it</span>' +
                    ' right now!<br/>' +
                    'After interview, open vacancy page to continue.' +
                    'Click <span class="hint-green">link</span> to start interview.<br/>',
                    showSkip: false,

                })
            }

            hint_set.push(interview_scheduled);
        }

    }
});
