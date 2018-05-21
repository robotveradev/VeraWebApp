$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        $('form').on('keydown', function (e) {
            if (e.which === 13) {
                return false;
            }
        });
        let new_question = {
            title: 'new_question',
            steps: [
                {
                    'custom div.uk-container.uk-align-center>form>div:nth-child(2)': "Enter the text of the question in this field.<br/>" +
                    "<span class='hint-green'>Use the editor to create a style.</span><br/>" +
                    "Click <span class='hint-green'>NEXT</span> to continue.",
                    showNext: true,
                    showSkip: false,
                    onBeforeStart: function () {
                        $('.jHtmlArea>div:eq(1)>iframe')[0].contentWindow.document.body.focus();
                    }
                },
                {
                    'custom div.uk-container.uk-align-center>form>div:nth-child(3)': 'Specify the weight (significance) of the question.<br/>' +
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
                    'next [name=_addanother]': 'Use this button if you want <span class="hint-green">save</span> and <span class="hint-green">add another</span> one question at this category.',
                    showSkip: false
                },
                {
                    'next [name=_addanswers]': 'This button for <span class="hint-green">save</span> and <span class="hint-green">add answers</span> for current question.',
                    showSkip: false
                },
                {
                    'next #save': 'And another one button just for <span class="hint-green">save</span> question and go at previous page.',
                    showSkip: false
                },
                {
                    'click [name=_addanswers]': 'Now let\'s add <span class="hint-green">some answers</span> for this question!<br/>' +
                    'Click <span class="hint-green">SAVE AND ADD ANSWERS</span> button to continue.'
                }
            ],
        };
        hint_set.push(new_question);
    }
});
