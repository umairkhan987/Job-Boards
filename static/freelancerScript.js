$(document).ready(function () {
    // Submit proposal
    $('#submit-proposal').submit(function (event) {
        event.preventDefault();
        const url = $(this).attr('action');
        const data = $(this).serialize();

        const completeURL = window.location.href.replace(window.location.pathname, "/freelancer/myProposals/");

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success: function (data) {
                console.log(data);
                if (data.success) {
                    snackbar_msg(data.msg);
                    setTimeout(() => {
                        window.location.replace(completeURL);
                    }, 1000);
                } else {
                    snackbar_msg(data.errors);
                }
            }
        })
    });

    $('a.cancel-popup').click(function (event) {
        $.magnificPopup.close();
    });

    let URL = null;
    $('a.show-popup').click(function (event) {
        const title = $(this).attr('data-content');
        URL = $(this).attr('data-url');
        $('#task_name').html(title);
    });

    $('#delete-confirm-popup').click(function () {
        const data = $('#csrf_token-form').serialize();

        if(URL === null) {
         console.log("url is null");
         return;
        }

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: URL,
            data: data,
            success: function (data) {
                $.magnificPopup.close();
                console.log(data);
                if (data.success) {
                    snackbar_msg(data.msg);
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    snackbar_msg(data.errors);
                }
            }
        })
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
});