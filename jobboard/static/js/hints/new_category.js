$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        $('form').on('keydown', function (e) {
            if (e.which === 13) {
                return false;
            }
        });
        let new_category = {
            title: 'new_category',
            steps: [
                {
                    'key form>div:nth-child(2)': "Enter the <span class='hint-green'>category name</span> in this field<br/>" +
                    "Click <span class='hint-green'>TAB</span> button to continue.",
                    showSkip: false,
                    onBeforeStart: function () {
                        $('form>div:nth-child(2)>div>input').focus();
                    },
                    keyCode: 9,
                },
                {
                    'next form>div:nth-child(3)': 'Here you can choose <span class="hint-green">parent category</span> to make a hierarchy of categories.<br/>' +
                    '<span class="light-green-text text-accent-3">For example: <br/>' +
                    '&emsp;programming<br/>' +
                    '&emsp;&emsp;python<br/>' +
                    '&emsp;&emsp;&emsp;django<br/>' +
                    '&emsp;&emsp;&emsp;flask<br/>' +
                    '&emsp;management<br/>' +
                    '&emsp;&emsp;...' +
                    '</span><br/>' +
                    'But for now you have no more categories to choose.<br/>' +
                    "Click the <span class=\'light-green-text text-accent-3\'>next</span> button and move on.",
                    showSkip: false
                },
                {
                    'custom [type=submit]': 'And click <span class="light-green-text text-accent-3">Save</span> button to save the category.',
                    skipButton: {text: 'Done'},
                    shape: 'circle',
                    radius: 50
                }
            ],
            additional: {'disabled': 'id_parent_category'}
        };
        hint_set.push(new_category);
    }
});
