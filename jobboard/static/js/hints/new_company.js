$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        $('form').on('keydown', (e) => {
            if (e.which === '13') {
                return false;
            }
        });
        let new_company = {
            title: 'new_company',
            steps: [
                {
                    'next h3': 'Complete the <span class="hint-green">form</span> bellow for create new company.<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    showSkip: false,
                },
                {
                    'next button': 'Click <span class="hint-green">SAVE</span> button when you\'re ready.',
                    showSkip: false,
                }
            ],
        };
        hint_set.push(new_company);
    }
});
