$(document).ready(function () {
    if (typeof hint_set !== "undefined") {

        if ($('[data-hint=passed]').length == 0) {
            let examining = {
                title: 'examining',
                steps: [
                    {
                        'next [data-hint=examining-head]': 'Now you at <span class="hint-green">examining</span> page.<br/>' +
                        'Click <span class="hint-green">NEXT</span> button to continue.',
                        showSkip: false,
                    },
                    {
                        'custom [data-hint=questions]': 'Answer the ' +
                        '<span class="hint-green">exam questions</span>' +
                        ' and click ' +
                        '<span class="hint-green">Continue</span>',
                        showNext: false,
                        skipButton: {text: 'Done'}
                    }
                ],
            };
            hint_set.push(examining);
        } else {
            let exam_passed = {
                title: 'exam_passed',
                steps: [
                    {
                        'next [data-hint=passed]': '<span class="hint-green">Great!</span><br/>' +
                        'You answered <span class="hint-green">all questions</span> of the <span class="hint-green">exam</span><br/>' +
                        'If you scored the minimum <span class="hint-green">passing grade</span> and <br/>' +
                        'and action <span class="hint-green">not approvable</span> - you will be automatically level up<br/>' +
                        'on next <span class="hint-green">pipeline action.</span><br/>' +
                        'Otherwise you have to wait for <span class="hint-green">employer\'s approving.</span><br/>' +
                        'Click <span class="hint-green">NEXT</span> button to continue.',
                        showSkip: false,
                    },
                    {
                        'click [data-hint=to-vacancy]': 'Now go back on <span class="hint-green">vacancy page</span>.<br/>' +
                        'Click button to continue.',
                        showSkip: false,
                    }
                ],
            };
            hint_set.push(exam_passed);
        }


    }
});
