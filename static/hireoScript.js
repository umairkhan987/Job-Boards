$(document).ready(function () {
    // cancel popup
    $('a.cancel-popup').click(function (event) {
        $.magnificPopup.close();
    });

    // deactivate user account.
    $('#deactivate-confirm-popup').click(function () {
        const url = $(this).attr('data-url');
        const data= {
            "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success:function (data) {
                $.magnificPopup.close();
                if(data.success){
                    snackbar_msg(data.msg);
                    setTimeout(()=>{
                        window.location = data.url;
                    }, 1000);
                }
            }
        })
    });

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

    // Message Popup open
    let message_url = null;
    $('a[href=#small-dialog-2]').click(function () {
        const firstName = $(this).attr('data-firstName');
        const user_id = $(this).attr('data-id');
        message_url = $(this).attr('data-url');
        $('textarea[name=message_content]').val("");
        $('#receiver_name_h3').html("Direct Message to "+ firstName);
        $('input[name=receiver_id]').val(user_id);
    });

    // send message
    $('#send-pm').submit(function (event) {
        event.preventDefault();

        if(message_url === null){
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
                if(data.success){
                    snackbar_msg(data.msg);
                }
                else{
                    snackbar_error_msg(data.errors['message_content']);
                }
            }
        });
    });

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