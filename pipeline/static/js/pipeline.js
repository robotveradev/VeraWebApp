$(document).ready(function () {
    !function () {
        $(document).on('click', '#apply', pipAdd);
        var piplineElements = [];
        var viewState = [];
        createLines(piplineElements);
        UIkit.util.on($('.pipline'), 'moved', function (e, sortable, el) {
            console.log(e, sortable, el);
            $('.line').hide();
            var currentId = parseInt($(el).attr('data-id'));
            UIkit.modal.confirm('<p>Are you shore you want to change position of element ' + (currentId + 1) + ' to position ' + ($(el).index() + 1) + '</p><p>All other elements will be shifted</p>').then(function () {
                var removedEl = viewState.splice(currentId, 1);
                viewState.splice($(el).index(), 0, removedEl[0]);
                sendChanges('#', {
                    lastId: $(el).attr('data-id'),
                    newId: $(el).index(),
                    csrfmiddlewaretoken: $.cookie("csrftoken")
                }, newElementhendler, errorHandler);
                render(viewState);
                $('.pipLineContainer').addClass('uk-disabled')
            }, function () {
                render(piplineElements)
            });
        });

        function createLines(elements) {
            if (elements.length < 2) {
                return
            }
            for (var i = 0; i < $('.pipElement').length - 1; i++) {
                $('.pipElement:eq(' + i + ')').append('<canvas width="100px" height="100px" class="line uk-animation-scale-up uk-transform-origin-top-center"></canvas>');
                var line = $('.line')[i].getContext('2d');
                line.beginPath();
                line.setLineDash([5, 10]);
                line.moveTo(0, 50);
                line.lineTo(100, 50);
                line.stroke();
            }
        }

        function PiplineElement(type, fee, approveable, id) {
            this.id = id;
            this.type = type;
            this.fee = fee;
            this.approveable = approveable;
            this.toHtml = function () {
                return '<li class="pipElement" data-id="' + this.id + '">' +
                    '<div class="circle sort">' +
                    '<span class="uk-text-meta uk-text-small">' + this.type + '</span>' +
                    '</div>' +
                    '</li>';
            }
        }

        $('#add_pip').on('submit', function (event) {
            event.preventDefault()
        });

        function sendChanges(url, data, callback, handler) {
            $.post(url, {
                ...data,
                csrfmiddlewaretoken: getCookie('csrftoken')
            }).then(
                function (data, response) {
                    return callback(data, response);
                },
                function (error) {
                    return handler(error);
                }
            );
        }

        function errorHandler(error) {
            UIkit.modal.alert('<p><span style="color:red">Error: </span>' + error.status + '</p><p>' + error.statusText + '</p>').then(function () {
                $('.pipLineContainer').removeClass('uk-disabled');
                render(piplineElements);
            });
        }

        function newElementhendler(response) {
            var timer = setInterval(function () {
                function applyChanges(response) {
                    if (response) {
                        clearInterval(timer);
                        piplineElements = viewState;
                        for (var i = 0; i < piplineElements.length; i++) {
                            piplineElements[i].id = i;
                            $('.pipElement:eq(' + i + ')').attr('data-id', i)
                        }
                        render(piplineElements);
                        $('.pipLineContainer').removeClass('uk-disabled uk-grid-stack');
                    }
                }

                sendChanges('#', response, applyChanges, errorHandler)
            }, 10000);
        }

        function render(array) {
            var pipline = $('.pipline');
            $('.pipElement').remove();
            for (var i = 0; i < array.length; i++) {
                $(pipline).append(array[i].toHtml());
            }
            createLines(array);
        }

        function pipAdd() {
            console.log(getCookie('csrftoken'));
            var pip = new PiplineElement($('#pipType').val(), $('#fee').val(), $('#approveable')[0].checked, piplineElements.length);
            UIkit.modal('#modal_add_pip').hide();
            sendChanges($('#add_pip')[0].action, {
                actionType: pip.type,
                fee: pip.fee < 0 || !pip.fee ? 0 : pip.fee,
                approveable: pip.approveable
            }, newElementhendler, errorHandler);
            viewState.push(pip);
            render(viewState);
            $('.pipLineContainer').addClass('uk-disabled')
        }

    }()
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
