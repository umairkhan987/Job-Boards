$(document).ready(function () {
    // cancel popup
    $('a.cancel-popup').click(function (event) {
        $.magnificPopup.close();
    });

    // deactivate user account.
    $('#deactivate-confirm-popup').click(function () {
        const url = $(this).attr('data-url');
        const data = {
            "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success: function (data) {
                $.magnificPopup.close();
                if (data.success) {
                    snackbar_msg(data.msg);
                    setTimeout(() => {
                        window.location = data.url;
                    }, 1000);
                }
            }
        })
    });

    // Message Popup open
    let message_url = null;
    $('a[href=#small-dialog-2]').click(function () {
        const firstName = $(this).attr('data-firstName');
        const user_id = $(this).attr('data-id');
        message_url = $(this).attr('data-url');
        $('textarea[name=message_content]').val("");
        $('#receiver_name_h3').html("Direct Message to " + firstName);
        $('input[name=receiver_id]').val(user_id);
    });

    // Click on message popup to send message inside profile page or manage proposal page.
    $('#send-pm').submit(function (event) {
        event.preventDefault();
        if (message_url === null) {
            console.log("message url is null");
            return;
        }
        const data = $(this).serialize();
         $.ajax({
            type: "ajax",
            method: "POST",
            url: message_url,
            data: data,
            success: function (data) {
                $.magnificPopup.close();
                // console.log(data);
                if (data.success) {
                    snackbar_msg(data.msg);
                } else {
                    snackbar_error_msg(data.errors['message_content']);
                }
            }
        });
    });

    // delete Messages
    $('#delete-conversation-popup').click(function () {
        const url = $(this).attr("data-url");
        const data = {
            "receiver_id": parseInt(window.location.pathname.replace(/[^\d.]/g,"")),
            "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success: function (data) {
                $.magnificPopup.close();
                console.log(data);

                if (data.success) {
                    snackbar_msg(data.msg);
                    setTimeout(() => {
                        window.location.pathname = data.url;
                    }, 1000);
                }else{
                    snackbar_error_msg(data.errors);
                }
            }
        });

    });

    // Replay message
    $('#send-message-form').submit(function (event) {
        event.preventDefault();
        const message_textarea_ref = $('#send-message-form textarea');
        // check if user enter some message content or not
        if(message_textarea_ref.val().length === 0){
            console.log("Textarea is empty");
            return;
        }

        const url = $(this).attr('action');
        const receiver_id = parseInt(window.location.pathname.replace(/[^\d.]/g,""));
        let data = $(this).serialize() + "&receiver_id="+receiver_id;
        console.log(data);
        $.ajax({
            type: "ajax",
            method: "POST",
            url: url,
            data: data,
            success: function (data) {
                if(data.success){
                    $('#message_content_div').append(data.current_message)
                    message_textarea_ref.val("");
                }
                else{
                    snackbar_error_msg(data.errors);
                }
            }
        });
    });

    // TODO: add message detail using ajax
    // $('a.js-detail-message-chat').click(function (event) {
    //     event.preventDefault();
    //
    //     const url = $(this).attr('href');
    //     console.log("Message click ", url);
    // });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // snackbar for display msg
    function snackbar_msg(msg) {
        Snackbar.show({
            text: msg,
            pos: 'bottom-center',
            showAction: false,
            actionText: "Dismiss",
            duration: 3000,
            textColor: '#fff',
            backgroundColor: '#2a41e8'
        });
    }

    // snackbar for display error msg
    function snackbar_error_msg(msg) {
        Snackbar.show({
            text: msg,
            pos: 'bottom-center',
            showAction: true,
            actionText: "X",
            actionTextColor: '#fff',
            duration: 5000,
            textColor: '#fff',
            backgroundColor: '#DC3139'
        });
    }
});