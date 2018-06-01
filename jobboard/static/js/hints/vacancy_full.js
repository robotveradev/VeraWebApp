$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let vacancy_full = {
            title: 'vacancy_full',
            steps: [
                {
                    'next body>div:nth-child(4)>div.uk-container.uk-align-center.uk-offcanvas-content>section:nth-child(2)': '<span class="hint-green">The are</span><br/>' +
                    'employer <span class="hint-green">contract info</span>',
                    showSkip: false,
                    showNext: true
                },
                {
                    'next body>div:nth-child(4)>div.uk-container.uk-align-center.uk-offcanvas-content>section:nth-child(4)': '<span class="hint-green">Here is</span><br/>' +
                    '<span class="hint-green">general vacancy info</span> like a <span class="hint-green">office location</span> and <span class="hint-green">required experience</span>',
                    showSkip: false,
                    showNext: true
                },
                {
                    'next body>div:nth-child(4)>div.uk-container.uk-align-center.uk-offcanvas-content>section:nth-child(6)': '<span class="hint-green">Here is</span><br/>' +
                    '<span class="hint-green">working conditions</span> like a <span class="hint-green">schedule</span>, <span class="hint-green">busyness</span> and <span class="hint-green">salary</span> level',
                    showSkip: false,
                    showNext: true
                },
                {
                    'next body>div:nth-child(4)>div.uk-container.uk-align-center.uk-offcanvas-content>section:nth-child(8)': '<span class="hint-green">Here is</span><br/>' +
                    '<span class="hint-green">Vacancy description</span> and <span class="hint-green">Vacancy requirement</span>',
                    showSkip: false,
                    showNext: true
                },
                {
                    'next body>div:nth-child(4)>div.uk-container.uk-align-center.uk-offcanvas-content>div>div': 'These are  <span class="hint-green">steps</span>that you need to go through as a post-graduate.<br/>' +
                    '<span class="hint-green">After </span> the approval of your candidacy by the employer, you need to pass all <span class="hint-green">examinations </span> and <span class="hint-green"> interviews</span>. <br> <span class="hint-green"> Done </span> means that you have gone through all the necessary steps.',
                    showSkip: false,
                    showNext: true
                },
                {
                    'click a:contains("Subscribe")': '<span class="hint-green">Here is</span><br/>' +
                    '<span class="hint-green">Now, </span> click <span class="hint-green">subscribe</span> to subscribe to the vacancy',
                    showSkip: false,
                },
            ],
        };
        let transaction_start = {
            title: 'transaction_start',
            steps: [
                {
                    'next [data-hint=profile_drop]': 'Lets see on a <span class="hint-green">Transactions</span> menu<br/>' +
                    'Please click on <span class="hint-green">PROFILE button</span> then select <span class="hint-green">Transactions</span>',
                    showSkip: false,
                    showNext: true
                }
            ],
        };
        hint_set.push(vacancy_full, transaction_start);
    }
});