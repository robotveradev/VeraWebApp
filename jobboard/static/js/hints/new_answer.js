$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        $('form').on('keydown', function (e) {
            if (e.which === 13) {
                return false;
            }
        });
        let new_answer = {
            title: 'new_answer',
            steps: [
                {
                    'next [data-hint=question]': '<span class="hint-green">Great!</span><br/>' +
                    'Your first question added. Let\'s add first <span class="hint-green">answer</span>!<br/>' +
                    'Click <span class="hint-green">NEXT</span> and go on.',
                    showSkip: false,

                },
                {
                    'custom div.uk-container.uk-align-center>form>div:nth-child(2)': "Enter the text of the answer in this field.<br/>" +
                    "<span class='hint-green'>Use the editor to create a style.</span><br/>" +
                    "Click <span class='hint-green'>NEXT</span> to continue.",
                    showNext: true,
                    showSkip: false,
                    onBeforeStart: function () {
                        $('.jHtmlArea>div:eq(1)>iframe')[0].contentWindow.document.body.focus();
                    }
                },
                {
                    'custom div.uk-container.uk-align-center>form>div:nth-child(3)': 'Specify the weight (significance) of the answer.<br/>' +
                    '<span class="hint-green">It will be used to calculate the sum of the applicant\'s points. ' +
                    'The more weight of the question, the more significant ' +
                    'it is for the whole test.</span><br/>' +
                    "Click <span class='hint-green'>NEXT</span> to continue.",
                    showNext: true,
                    showSkip: false,
                    onBeforeStart: function () {
                        $('#id_weight').focus();
                    }
                },
                {
                    'next [name=_addanother]': 'Use this button if you want <span class="hint-green">save</span> and <span class="hint-green">add another</span> one answer.',
                    showSkip: false
                },
                {
                    'click #save': 'And another one button just for <span class="hint-green">save</span> answer and go at previous page.<br/>' +
                    'Click <span class="hint-green">SAVE</span> to continue.',
                    showSkip: false
                }
            ],
        };
        hint_set.push(new_answer);
    }
});
