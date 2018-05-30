$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        if ($('.company').length < 1) {
            localStorage.setItem('companies_main', '1');
            let companies_main = {
                title: 'companies_main',
                steps: [
                    {
                        'next [data-hint=companies-main]': '<span class="hint-green">Welcome</span> at <span class="hint-green">companies</span> page.<br/>' +
                        'Here you can add new companies, offices and company vacancies.<br/>' +
                        'Click <span class="hint-green">NEXT</span> button, located in the lower right corner to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                        showSkip: false,
                    },
                    {
                        'click [data-hint=new-company]': 'Now cllick <span class="hint-green">new company</span> button and go on.',
                        showSkip: false
                    },
                ],
            };
            hint_set.push(companies_main);
        } else {
            let $el = $('.company:eq(0)');
            let company_created = {
                title: 'company_created',
                steps: [
                    {
                        event: 'next',
                        selector: $el,
                        description: '<span class="hint-green">Congratulations! </span> Now you have one company added!<br/>' +
                        'Click <span class="hint-green">NEXT</span> to continue!',
                        showSkip: false,
                        showNext: true
                    },
                    {
                        event: 'next',
                        selector: $el,
                        description: 'Here you can see your company name and main info.<br/>' +
                        'Click <span class="hint-green">NEXT</span> to continue!',
                        showSkip: false,
                        showNext: true
                    },
                    {
                        event: 'click',
                        selector: $el.find('a:eq(0)'),
                        description: 'Now go at company page.<br/>' +
                        'Click at <span class="hint-green">company name</span> to continue!',
                        showSkip: false,
                    }
                ]
            };

            hint_set.push(company_created);
        }
    }
});
