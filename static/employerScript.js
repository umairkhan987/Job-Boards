$(document).ready(function () {

    // check if project type is hourly then hide the required days col.
    $('input[name=project_type]').change(function () {
        let type = $('input[name=project_type]:checked').val();
        if (type === "hourly") {
            $('#reqDaysDiv').hide();
        } else {
            $('#reqDaysDiv').show();
        }
    });


    $('a.cancel-popup').click(function (event) {
        $.magnificPopup.close();
    });

    let URL = null;
    let delete_btn_ref = null;
    $('a.show-popup').click(function (event) {
        delete_btn_ref = $(this);
        const title = $(this).attr('data-content');
        URL = $(this).attr('data-url');
        $('#task_name').html(title);
    });


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
                    if(data.html != null)
                        $(".js-task-list ul").html(data.html);
                    else
                        delete_btn_ref.closest("li").remove();
                    } else {
                    snackbar_error_msg(data.errors);
                }
            }
        })
    });

    let proposal_url = null;
    $('a.accept-offer').click(function () {
        const proposal = $(this).attr('data-content').split(",");
        proposal_url = $(this).attr('data-url');
        $('#first_name').html(proposal[0]);
        $('#accept_offer_rate').html(`$${proposal[1]} - in ${proposal[2]} Days `);
    });

    // Submit accept proposal
    $('#terms').submit(function (event) {
        event.preventDefault();
        const data = $(this).serialize();

        if (proposal_url === null) {
            console.log("Proposal url is null");
            return;
        }

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: proposal_url,
            data: data,
            success: function (data) {
                $.magnificPopup.close();
                // console.log(data);
                if (data.success) {
                    snackbar_msg(data.msg);
                    setTimeout(() => {
                        window.location = data.url;
                    }, 1000)
                } else {
                    snackbar_error_msg(data.errors);
                }
            }
        })
    });

    let review_url=null;
    $('a.reviews-popup').click(function () {
        const data = $(this).attr('data-content').split(',');
        review_url = $(this).attr('data-url');
        $('#username_anchor').html(data[0]+" "+data[1]);
        $('#project_title_anchor').html(data[2]);
    });

    //  Leave Review submit
    $('#leave-review-form').submit(function (event) {
        event.preventDefault();
        const data= $(this).serialize();
        if(review_url == null){
            console.log("Leave Review url is null");
            return;
        }

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: review_url,
            data: data,
            success: function (data) {
                $.magnificPopup.close();
                console.log(data);
                if(data.success){
                    snackbar_msg(data.msg);
                    setTimeout(()=>{
                        window.location.reload();
                    }, 1000)
                }
                else{
                    snackbar_error_msg(data.errors);
                }
            }
        });
    });

    // bookmark freelancer profile
    $('#bookmark_Btn').click(function () {
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

        })
    });

    $('a.delete-bookmark-Btn').click(function () {
        let delete_btn_ref = $(this);
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
                    if(data.html != null)
                        $(".js-employer-bookmark-list ul").html(data.html);
                    else
                        delete_btn_ref.closest('li').hide();
                }
                else{
                    console.log(data.errors);
                }
            }

        });
    });

    // Submit Offer
    $('#offer_form').submit(function (event) {
        event.preventDefault();
        const url = $(this).attr('action');
        const id = parseInt(window.location.pathname.replace(/[^\d.]/g,""));
        const formData = new FormData($('#offer_form')[0]);
        formData.append("profile_id", id.toString());

        // for(let value of formData.entries())
        //         console.log(value[0]+'  '+value[1]);

        $.ajax({
            type:"ajax",
            method: "POST",
            url: url,
            data:formData,
            processData: false,
            contentType: false,
            cache: false,
            success:function (data) {
                // console.log(data);
                if(data.success){
                    $.magnificPopup.close();
                    snackbar_msg(data.msg);
                }
                else{
                    if(data.errors['full_name']){
                        $('#offer-full_name-error').show().html(data.errors['full_name']);
                    }
                    else{
                        $('#offer-full_name-error').hide().html("");
                    }
                    if(data.errors['email']){
                        $('#offer-email-error').show().html(data.errors['email']);
                    }else{
                        $('#offer-email-error').hide().html("");
                    }
                    if(data.errors['offer_message']){
                        $('#offer-message-error').show().html(data.errors['offer_message']);
                    }else{
                        $('#offer-message-error').hide().html("");
                    }
                }
            }

        });

    });


    // csrf_token
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