$(document).ready(function () {
      // try{
      //      window.onload = $('.conversation').scrollTop($('.conversation')[0].scrollHeight);
      // }catch (e) {
      //     console.log("height error");
      // }


    // TODO: add message detail using ajax
    // $('a.js-detail-message-chat').click(function (event) {
    //     event.preventDefault();
    //
    //     const url = $(this).attr('href');
    //     console.log("Message click ", url);
    // });
    // message notifications mark-all-as-read
    $('#js-mark-all-as-read').click(function () {
        const url = $(this).data("url");
        $.ajax({
            type: "ajax",
            method: "POST",
            url: url,
            success: function (data) {
                console.log(data);
                if(data.success){
                    $(".js-header-message-notification ul").html(data.html);
                }
            }
        });

    });

    // Send direct Message
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
        let formData = $(this).serialize() + "&receiver_id="+receiver_id;

        $.ajax({
            type: "ajax",
            method: "POST",
            url: url,
            data: formData,
            success: function (data) {
                if(data.success){
                    $('#message_content_div').append(data.current_message);
                    $("#send-message-form input[name=last_message_date]").val(data.date);
                    $('.conversation').scrollTop($('.conversation')[0].scrollHeight);
                    message_textarea_ref.val("");
                    message_textarea_ref.focus();
                }
                else{
                    snackbar_error_msg(data.errors);
                }
            }
        });
    });



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