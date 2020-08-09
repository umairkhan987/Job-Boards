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
                // console.log(data);
                if (data.success) {
                    snackbar_msg(data.msg);
                    setTimeout(() => {
                        window.location = data.url;
                    }, 1000);
                } else {
                    snackbar_error_msg(data.errors);
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
        URL = $(this).attr('data-url');
        $('#popup-tabs').html("Cancel Task");
        $('#delete-proposal-p').html("Are you sure you want to cancel this job.");
        $('#delete-confirm-popup').html("Yes");
    });

    // delete proposals
    $('#delete-confirm-popup').click(function () {
        const data = $('#csrf_token-form').serialize();

        if (URL === null) {
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
                    snackbar_error_msg(data.errors);
                }
            }
        })
    });

    // complete job button click
    $('#complete_job_Btn').click(function (event) {
        const url = $(this).attr('data-url');
        const token = getCookie('csrftoken');
        console.log("Ajax submitted");

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: {csrfmiddlewaretoken: token},
            success: function (data) {
                console.log(data);
                if(data.success){
                    snackbar_msg(data.msg);
                    setTimeout(()=>{
                        window.location.reload();
                    }, 1000);
                }
                else{
                    snackbar_error_msg(data.errors);
                }
            }
        });

    });

    // get bookmark btn
    $('#bookmark_btn').click(function () {
        const id = parseInt(window.location.pathname.replace(/[^\d.]/g,""));
        const url = $(this).attr('data-url');
        const data = {
            "id": id,
             "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success:function (data) {
                // console.log(data);
                if(data.success){
                    snackbar_msg(data.msg);
                }
                else{
                    console.log(data.errors);
                }
            }
        });
    });

    // delete bookmark click on Bookmark page button
    $('a.delete-freelancer-bookmark').click(function () {
        const id = $(this).attr('data-id');
        const url = $(this).attr('data-url');
        const data = {
            "id": id,
             "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

         $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success:function (data) {
                // console.log(data);
                if(data.success){
                    snackbar_msg(data.msg);
                    setTimeout(()=>{
                        window.location.reload();
                    }, 1000);
                }
                else{
                    console.log(data.errors);
                }
            }

        });
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