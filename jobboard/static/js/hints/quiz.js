$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        if ($('[data-hint=categories]').length < 1) {
            localStorage.setItem('quiz', '1');
            let quiz = {
                title: 'quiz',
                steps: function () {
                    let steps = [{
                        'next [data-hint=quiz_main]': "<span class='light-green-text text-accent-3'>Welcome at quiz application page!<br>" +
                        "Here you can:</span>" +
                        "<ol>" +
                        "<li>Add categories to questions of any nesting</li>" +
                        "<li>Add general questions and questions to categories</li>" +
                        "</ol>" +
                        "Click the <span class='light-green-text text-accent-3'>next</span> button and move on.",
                        showSkip: false,
                    },
                        {
                            'click [data-hint=new_cat]': '<span class=\'light-green-text text-accent-3\'>This button allow you to create new question category</span><br/>' +
                            'Click it right now',
                            showSkip: false
                        }];
                    return steps
                },
            };
            hint_set.push(quiz);
        } else {
            let category_created = {
                title: 'category_created_successfully',
                steps: [{
                    'next [data-hint=categories]': '<span class="hint-green">Congratulations!</span><br/>' +
                    '<span class="hint-green">You</span> successfully <span class="hint-green">create</span> new quiz category!<br/>' +
                    'Let\'s create your first quiz question!',
                    showSkip: false,
                },
                    {
                        'click div.uk-container.uk-align-center>div:nth-child(2)>div>a': 'Now go at <span class="hint-green">your</span> first ' +
                        '<span class="hint-green">quiz category</span> and create your first <span class="hint-green">question</span>!<br/>' +
                        'Click at <span class="hint-green">category name</span> to continue.',
                        showSkip: false
                    }]
            };
            hint_set.push(category_created);
        }
    }
});
