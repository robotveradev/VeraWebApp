$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        $('form').on('keydown', function (e) {
            if (e.which === 13) {
                return false;
            }
        });
        let new_education = {
            title: 'new_education',
            steps: [
                {
                    'next legend': '<span class="hint-green">Please</span> fill in <span class="hint-green">ALL FIELDS</span>.<br/>' +
                    ' click Next to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                    showNext: true
                },
                {
                    'next button': '<span class="hint-green">Then</span> click <span class="hint-green">SAVE button </span><br>' +
                    'Click <span class="hint-green">Next</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                    showNext: true
                }
            ],
        };
        hint_set.push(new_education);
    }
});