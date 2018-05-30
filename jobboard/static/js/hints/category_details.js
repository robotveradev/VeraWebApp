$(document).ready(function () {
    if ($('[data-hint="question"]').length < 1) {
        let category_details = {
            title: 'category_details',
            steps: [
                {
                    'next [data-hint=main]': "<span class='hint-green'>All right!</span> This is category page.<br/>" +
                    "<span class='light-green-text text-accent-3'>Here you can add questions to category.</span>",
                    showSkip: false,
                },
                {
                    'click [data-hint=add_link]': 'Click this link for create one right now',
                    showSkip: false,
                    shape: 'circle',
                    radius: 80
                }
            ]
        };
        hint_set.push(category_details);
    } else {
        let $el = $('[data-hint=question]:eq(0)');
        let quiz_question_types = {
            title: 'quiz_question_types',
            steps: [
                {
                    selector: $el,
                    event: 'next',
                    description: '<span class="hint-green">Excellent!</span><br/>' +
                    'Now you have: <br>' +
                    '&emsp;one <span class="hint-green">quiz category</span><br/>' +
                    '&emsp;one <span class="hint-green">question</span><br/>' +
                    '&emsp;and one <span class="hint-green">answer</span> for this question!',
                    showSkip: false,
                    showNext: true,
                }, {
                    selector: $el,
                    event: 'next',
                    description: 'let\'s <span class="hint-green">now</span> consider ' +
                    'this page <span class="hint-green">more</span>.<br/>' +
                    'Click <span class="hint-green">NEXT</span> to continue.',
                    showSkip: false,
                    showNext: true
                }, {
                    selector: $el.children('span'),
                    event: 'next',
                    description: 'This is a <span class="hint-green">question</span> here.<br/>' +
                    'Click <span class="hint-green">NEXT</span> to continue.',
                    showSkip: false,
                    showNext: true
                }, {
                    selector: $el.find('ul:eq(1)>li:eq(0)'),
                    event: 'next',
                    description: 'This is a <span class="hint-green">answer</span> and <span class="hint-green">it\'s weight</span>.<br/>' +
                    'Click <span class="hint-green">NEXT</span> to continue.',
                    showSkip: false,
                    showNext: true
                }, {
                    selector: $el.children('div:eq(0)'),
                    event: 'next',
                    description: 'Here you can see <span class="hint-green">max points</span> ' +
                    'and <span class="hint-green">question type</span> for this one question.<br/>' +
                    'Click <span class="hint-green">NEXT</span> to continue.',
                    showSkip: false,
                    showNext: true
                }, {
                    selector: $el.children('div:eq(0)').children('span:eq(0)'),
                    event: 'next',
                    description: 'The maximum <span class="hint-green">number of points</span> is calculated differently' +
                    ' for different <span class="hint-green">types of questions</span>.<br/>' +
                    'Click <span class="hint-green">NEXT</span> to continue.',
                    showSkip: false,
                    showNext: true
                },{
                    selector: $el.children('div:eq(0)').children('span:eq(1)'),
                    event: 'next',
                    description: 'The <span class="hint-green">question type</span> is determined <span class="hint-green">automatically</span> ' +
                    'by the system,<br/>but <span class="hint-green">you can change</span> the type yourself if you think it\'s necessary.<br/>' +
                    'Click <span class="hint-green">NEXT</span> to continue.',
                    showSkip: false,
                    showNext: true
                },{
                    'click [data-hint=profile_drop]': 'Now click here...',
                    'timeout': 3,
                    showSkip: false
                },{
                    'click [data-hint=companies]': 'Time to create your first company! <br/>' +
                    'Click <span class="hint-green">companies</span> to continue.',
                    showSkip: false,
                },
            ]
        };
        hint_set.push(quiz_question_types);
    }

});

