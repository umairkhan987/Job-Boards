$(document).ready(function () {
    // Submit proposal
    $('#submit-proposal').submit(function (event) {
        event.preventDefault();
        const url = $(this).attr('action');
        const data = $(this).serialize();


        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success: function (data) {
                console.log(data);
                if (data.success) {
                    const completeURL = window.location.href.replace(window.location.pathname, data.url);
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
    $('a.delete-popup').click(function (event) {
        const title = $(this).attr('data-content');
        URL = $(this).attr('data-url');
        $('#popup-tabs').html("Delete Proposal");
        $('#delete-proposal-p').html(`Are you sure you want to delete this job. <strong>${title}</strong>`);
        $('#delete-confirm-popup').html("Delete");
    });

    $('a.cancel-task-popup').click(function (event) {
       URL =  $(this).attr('data-url');
       $('#popup-tabs').html("Cancel Task");
       $('#delete-proposal-p').html("Are you sure you want to cancel this job.");
       $('#delete-confirm-popup').html("Yes");
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