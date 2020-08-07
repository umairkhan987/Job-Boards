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

    // Post Task button clicked
    // $('#post_task_Btn').click(function () {
    //     $('#post_task_form').submit();
    //
    //     return;
    //
    //     const postFormRef = $('#post_task_form');
    //     const url = postFormRef.attr("action");
    //     const formData = new FormData(postFormRef[0]);
    //
    //     // convert list of skills into string
    //     const skills = formData.getAll('skills');
    //     formData.delete('skills');
    //     formData.append('skills', skills.toString());
    //
    //     // for(let value of formData.entries())
    //     //         console.log(value[0]+'  '+value[1]);
    //
    //     $.ajax({
    //         type: "ajax",
    //         url: url,
    //         method: "POST",
    //         processData: false,
    //         contentType: false,
    //         cache: false,
    //         data: formData,
    //         success: function (data) {
    //             if (data.success) {
    //                 snackbar_msg(data.msg);
    //                 setTimeout(() => {
    //                     console.log("Time out call");
    //                     window.location = "/employer/tasks/";
    //                 }, 2000);
    //             } else {
    //                 console.log(data);
    //                 if (data.errors['title'])
    //                     $("#title-error").show().html(data.errors['title']);
    //                 else
    //                     $("#title-error").hide().html("");
    //
    //                 if (data.errors['skills'])
    //                     $("#skills-error").show().html(data.errors['skills']);
    //                 else
    //                     $("#skills-error").hide().html("");
    //
    //                 if (data.errors['exp_level'])
    //                     $("#experience-error").show().html(data.errors['exp_level']);
    //                 else
    //                     $("#experience-error").hide().html("");
    //             }
    //         }
    //     })
    //
    // });

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
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
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

    // Leave Review submit
    $('#leave-review-form').submit(function (event) {
        event.preventDefault();
        const data= $(this).serialize();
        // console.log("Leave form submit ", data);

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