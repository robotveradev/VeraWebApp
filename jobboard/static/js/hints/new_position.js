$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        $('form').on('keydown', function (e) {
            if (e.which === 13) {
                return false;
            }
        });
        let new_position = {
            title: 'new_position',
            steps: [
                {
                    'key #id_title': '<span class="hint-green">Please</span> enter <span class="hint-green">position title</span>.<br/>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                    onBeforeStart: ()=>{
                        $('#id_title').focus();
                    }
                },
                {
                    'key #id_busyness': '<span class="hint-green">Please</span> chose <span class="hint-green">your business level </span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_schedule': '<span class="hint-green">Please</span> chose <span class="hint-green">your schedule level</span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'key #id_salary_from': '<span class="hint-green">Please</span> enter <span class="hint-green"> desired level of remuneration </span><br>' +
                    'Click <span class="hint-green">Tab</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    keyCode: 9,
                    showSkip: false,
                },
                {
                    'custom #id_carier_start': '<span class="hint-green">Chose</span> it your <span class="hint-green">carier start</span><br/>' +
                    'Click <span class="hint-green">Next</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                    showNext: true
                },
                {
                    'next form>fieldset>div:nth-child(8)>div': '<span class="hint-green">Please</span> enter <span class="hint-green">description </span><br>' +
                    'Click <span class="hint-green">Next</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                    onBeforeStart: ()=>{
                         $('.jHtmlArea>div:eq(1)>iframe')[0].contentWindow.document.body.focus();
                    }
                },
                {

                    selector: 'button',
                    event: 'click',
                    description : '<span class="hint-green">Please</span> click <span class="hint-green">Agree button to continue</span>.<br/>' +
                    'Click <span class="hint-green">Agree</span> button to continue or <span class="hint-green">CLOSE</span> for close tutorial for this page',
                    showSkip: false,
                    onBeforeStart: function () {
                                let form = $('[required]');
                                for(let i of form){
                                    if($(i).val()){
                                        this.selector = 'legend';
                                        this.event = 'next';
                                        this.description = '<span class="hint-green">Please</span> fill in <span class="hint-green">ALL FIELDS</span>.<br/>' +
                                            'Then click Agree to continion' +
                    ' or <span class="hint-green">CLOSE</span> for close tutorial for this page';
                                        this.showNext=true;
                                    }
                                }
                            }
                }
            ],
        };
        hint_set.push(new_position);
    }
});