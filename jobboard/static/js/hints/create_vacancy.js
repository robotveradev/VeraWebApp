$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let create_vacancy = {
            title: 'create_vacancy',
            steps: [
                {
                    'next a.uk-logo': '<span class="hint-green">Welcome</span> to the <span class="hint-green">first work site</span> built on <span class="hint-green">blockchain</span> technology.<br/>' +
                    'This guide will show you everything that you need to work with the site, will acquaint ' +
                    'you with all the features of the system.<br/>' +
                    'Click <span class="hint-green">NEXT</span> button, located in the lower right corner to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                },
                {
                    'next #help': 'Disable all tips, or start learning otherwise, you can in the <span class="hint-green">HELP</span> section.<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    'margin': 2,
                    showSkip: false
                },
                {
                    'next #login': 'By using the <span class="hint-green">LOGIN</span> button you can log in in the future.<br/>' +
                    'Click <span class="hint-green">NEXT</span> button to continue.',
                    'margin': 2,
                    showSkip: false
                },
                {
                    'click #register': 'But for now go at <span class="hint-green">register page</span> for register.<br/>' +
                    'Click <span class="hint-green">register</span> button to continue.',
                    'margin': 2,
                    showSkip: false
                },
            ],
        };
        hint_set.push(create_vacancy);
    }
});
