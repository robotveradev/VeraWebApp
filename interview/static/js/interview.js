$(document).ready(function () {
    var websocket = null;
    var monitor = null;

    function getOpponnentUsername() {
        return oppenent_uuid;
    }

    function getInterviewId() {
        return $('#interview_id').val();
    }

    function addNewMessage(packet) {
        var msg_class = "";
        var last_mess_user = $('.username:last').text();
        if (packet['sender_name'] === $("#owner_username").val()) {
            msg_class = "uk-text-left";
        } else {
            msg_class = "uk-text-right";
        }
        var msgElem = "";

        console.log(packet);

        if (last_mess_user !== packet['sender_name']) {
            msgElem = '<hr class="uk-divider-icon"/>' +
                '<div class="uk-text-center">' +
                '<span class="uk-text-muted">' + packet['created'] + '</span>' +
                '</div>';
        }
        msgElem +=
            '<div class="' + msg_class + '" data-id="' + packet.message_id + '">';
        if (last_mess_user !== packet['sender_name']) {
            msgElem += '<div class="username uk-text-capitalize">' + packet['sender_name'] + '</div>';
        }
        msgElem +=
            '<div class="uk-padding-small uk-padding-remove-top uk-padding-remove-bottom">' +
            packet['message'] +
            // ' <span class="uk-text-muted">&ndash; <span data-livestamp="' + packet['created'] + '"> ' + packet['created'] + '</span></span> ' +
            '</div>';
        $('#messages').append(msgElem);
        scrollToLastMessage();
    }

    function scrollToLastMessage() {
        var $msgs = $('#messages');
        $msgs.animate({"scrollTop": $msgs.prop('scrollHeight')})
    }

    function setUserOnlineOffline(username, online) {
        var elem = $("#user-" + username);
        if (online) {
            elem.attr("class", "btn btn-success");
        } else {
            elem.attr("class", "btn btn-danger");
        }
    }

    function gone_online() {
        $("#offline-status").hide();
        $("#online-status").show();
    }

    function gone_offline() {
        $("#online-status").hide();
        $("#offline-status").show();
    }

    function flash_user_button(username) {
        var btn = $("#user-" + username);
        btn.fadeTo(700, 0.1, function () {
            $(this).fadeTo(800, 1.0);
        });
    }

    function setupChatWebSocket() {
        var opponent_username = getOpponnentUsername();
        websocket = new WebSocket(base_ws_server_path + '/' + session_key + '/' + getInterviewId());

        websocket.onopen = function (event) {

            var onOnlineCheckPacket = JSON.stringify({
                    type: "check-online",
                    session_key: session_key,
                    interview: getInterviewId()
                })
            ;
            var onConnectPacket = JSON.stringify({
                type: "online",
                session_key: session_key

            });

            // console.log('connected, sending:', onConnectPacket);
            websocket.send(onConnectPacket);
            // console.log('checking online opponents with:', onOnlineCheckPacket);
            websocket.send(onOnlineCheckPacket);
            // monitor = initScrollMonitor();
        };


        window.onbeforeunload = function () {

            var onClosePacket = JSON.stringify({
                    type: "offline",
                    session_key: session_key,
                    interview: getInterviewId(),
                })
            ;
            // console.log('unloading, sending:', onClosePacket);
            websocket.send(onClosePacket);
            websocket.close();
        };


        websocket.onmessage = function (event) {
            var packet;

            try {
                packet = JSON.parse(event.data);
                // console.log(packet)
            } catch (e) {
                // console.log(e);
            }

            console.log(packet);

            switch (packet.type) {
                case "user-not-found":
                    // TODO: dispay some kind of an error that the user is not found
                    break;
                case "gone-online":
                    if (packet.usernames.indexOf(opponent_username) != -1) {
                        gone_online();
                    } else {
                        gone_offline();
                    }
                    for (var i = 0; i < packet.usernames.length; ++i) {
                        setUserOnlineOffline(packet.usernames[i], true);
                    }
                    break;
                case "gone-offline":
                    if (packet.username == opponent_username) {
                        gone_offline();
                    }
                    setUserOnlineOffline(packet.username, false);
                    break;
                case "new-message":
                    // if (packet['sender_name'] == getOpponnentUsername() || packet['sender_name'] == $("#owner_username").val()) {
                        addNewMessage(packet);
                    // } else {
                    //     flash_user_button(packet['sender_name']);
                    // }
                    break;
                case "opponent-typing":
                    var typing_elem = $('#typing-text');
                    if (!typing_elem.is(":visible")) {
                        typing_elem.fadeIn(500);
                    } else {
                        typing_elem.stop(true);
                        typing_elem.fadeIn(0);
                    }
                    typing_elem.fadeOut(3000);
                    break;
                case "opponent-read-message":
                    if (packet['username'] == getOpponnentUsername()) {
                        $("div[data-id='" + packet['message_id'] + "']").removeClass('msg-unread').addClass('msg-read');
                    }
                    break;

                default:
                    console.log('error: ', event)
            }
        }
    }

    function sendMessage(message) {
        var newMessagePacket = JSON.stringify({
            type: 'new-message',
            session_key: session_key,
            interview: getInterviewId(),
            message: message
        });
        websocket.send(newMessagePacket)
    }

    $('#chat-message').keypress(function (e) {
        if (e.which == 13 && this.value) {
            sendMessage(this.value);
            this.value = "";
            return false
        } else {
            var packet = JSON.stringify({
                type: 'is-typing',
                session_key: session_key,
                interview: getInterviewId(),
                typing: true
            });
            websocket.send(packet);
        }
    });

    $('#btn-send-message').click(function (e) {
        var $chatInput = $('#chat-message');
        var msg = $chatInput.val();
        if (!msg) return;
        sendMessage($chatInput.val());
        $chatInput.val('')
    });

    setupChatWebSocket();
    scrollToLastMessage();
});
