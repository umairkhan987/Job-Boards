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
    let delete_btn_ref=null;
    $('a.delete-popup').click(function (event) {
        delete_btn_ref = $(this);
        const title = $(this).attr('data-content');
        URL = $(this).attr('data-url');
        $('#popup-tabs').html("Delete Proposal");
        $('#delete-proposal-p').html(`Are you sure you want to delete this proposal. <strong>${title}</strong>`);
        $('#delete-confirm-popup').html("Delete");
    });

    $('a.cancel-task-popup').click(function (event) {
        URL = $(this).attr('data-url');
        $('#popup-tabs').html("Cancel Task");
        $('#delete-proposal-p').html("Are you sure you want to cancel this job.");
        $('#delete-confirm-popup').html("Yes");
    });

    // delete proposals
    // TODO: when the all bid is deleted then displayed the message or create partial views to display all bids via ajax
    $('#delete-confirm-popup').click(function () {
        const data = {
            "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

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
                // console.log(data);
                if (data.success) {
                    snackbar_msg(data.msg);
                    if(data.delete){
                        delete_btn_ref.closest('li').hide();
                    }
                    else {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    snackbar_error_msg(data.errors);
                }
            }
        })
    });

    // TODO: change location.reload to ajax functionality
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
                // console.log(data);
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
        let btn_ref = $(this);
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
                    btn_ref.closest("li").hide();
                }
                else{
                    console.log(data.errors);
                }
            }

        });
    });


    // delete offer
    let offer_url = null;
    let offer_btn_ref=null;
    $('a[href=#small-dialog]').click(function () {
         offer_btn_ref = $(this);
        offer_url = $(this).attr("data-url");
    });

    $('#delete-offer-popup').click(function () {

        if(offer_url === null){
            console.log("offer url is null");
            return;
        }
        const data = {
             "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: offer_url,
            data: data,
            success:function (data) {
                $.magnificPopup.close();
                // console.log(data);
                if(data.success){
                    snackbar_msg(data.msg);
                    offer_btn_ref.closest('li').hide();
                }
                else{
                    snackbar_error_msg(data.errors);
                }
            }
        });
    });


    // when user click on page tow view proposal against each task
    // js- include and its working....
    // TODO: find the way to call through ajax way...
    $('#proposals-list-div').on('click', 'a', function (event) {
        event.preventDefault();
        const parameter = $(this).attr('href');

        if (parameter === "javascript:" || parameter === null) return;
        let url = window.location.pathname + parameter;

        $.ajax({
            type: 'ajax',
            method:'get',
            url: url,
            success:function (data) {
                if(data.success){
                    $('#js-proposals-list-div').html(data.html_proposal_list);
                }else{
                    snackbar_error_msg(data.errors);
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