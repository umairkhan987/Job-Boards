$(document).ready(function () {

    // Register Form
    const fromRef = $('#register-account-form');
    $(fromRef).submit(function (event) {
        event.preventDefault();
        const formData = fromRef.serialize();
        const url = fromRef.attr('action');
        $.ajax({
            type:"ajax",
            url:url,
            method:"POST",
            data:formData,
            beforeSend:function(){
                $('#register-loading-spinner').removeAttr("hidden");
            },
            success:function (data) {
                  $('#register-loading-spinner').attr("hidden", true);
                    if(data.success){
                         $.magnificPopup.close();
                         window.location = '/';
                    }
            },
            error:function (xhr, status, error) {
                $('#register-loading-spinner').attr("hidden", true);
                if(xhr.status == 400){
                    let response = xhr.responseJSON;
                    if(response.success === false){
                        fromRef.find('input[type=password]').val("");
                        if(response.errors['email']) {
                            $("#emailError").html(response.errors['email'][0]);
                        }else{
                            $('#emailError').html("");
                        }
                        if(response.errors['password2']){
                            let passwordError = `<ul>`;
                            for(let error of response.errors['password2']){
                                passwordError += `<li>${error}</li>`
                            }
                            passwordError += "</ul>";
                            $('#password2Error').html(passwordError);
                        }
                        else{
                            $('#password2Error').html("");
                        }
                    }
                }
            }
        });
    });

    //Login Form
    const loginForm = $("#login-form");
    $(loginForm).submit(function (event) {
        event.preventDefault();
        $('#loginError').html("");

        const formData = loginForm.serialize();
        const url = loginForm.attr('action');
        let path = window.location.pathname;
        $.ajax({
            type:"ajax",
            url:url,
            method:"POST",
            data:formData,
            beforeSend:function(){
                $('#loading-spinner').removeAttr("hidden");
                $('#loginError').html("");
            },
            success:function (data) {
                $('#loading-spinner').attr("hidden", true);
                    if(data.success){
                         $.magnificPopup.close();
                         window.location = path;
                    }
            },
            error: function (xhr, status, error) {
                $('#loading-spinner').attr("hidden", true);
                if(xhr.status == 404){
                    let response = xhr.responseJSON;
                    if(response.success === false){
                        loginForm.find('input[type=password]').val("");
                        if(response.errors){
                            $("#loginError").html(response.errors['__all__'])
                        }
                        else{
                            $('#loginError').html("");
                        }
                    }
                }

            }
        });
    });

    // when user click on page to view proposal against each task
    $('.js-proposals-list-div').on('click', '.js-pagination a', function (event) {
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
                    $('.js-proposals-list-div').html(data.html);
                    starRating('.star-rating');
                }else{
                    snackbar_error_msg(data.errors);
                }
            }
        });
    });

    // work history pagination
    // add js- for working
    // TODO: debug star-rating
    $('.partial-work-history-div').on('click', '.js-pagination a', function (e) {
        e.preventDefault();
        const parameter = $(this).attr('href');

        if (parameter === "javascript:" || parameter === null) return;
        let url = window.location.pathname + parameter;

        $.ajax({
            type: 'ajax',
            method:'get',
            url: url,
            success:function (data) {
                if(data.success){
                    $('.js-partial-work-history-div').html(data.html);
                    starRating('.star-rating');
                }else{
                    snackbar_error_msg(data.errors);
                }
            }
        });
    });

    // after ajax call we need a function to load star-rating
    function starRating(ratingElem) {
            $(ratingElem).each(function () {
                var dataRating = $(this).attr("data-rating");
                function starsOutput(firstStar, secondStar, thirdStar, fourthStar, fifthStar) {
                    return (
                        "" +
                        '<span class="' +
                        firstStar +
                        '"></span>' +
                        '<span class="' +
                        secondStar +
                        '"></span>' +
                        '<span class="' +
                        thirdStar +
                        '"></span>' +
                        '<span class="' +
                        fourthStar +
                        '"></span>' +
                        '<span class="' +
                        fifthStar +
                        '"></span>'
                    );
                }
                var fiveStars = starsOutput("star", "star", "star", "star", "star");
                var fourHalfStars = starsOutput("star", "star", "star", "star", "star half");
                var fourStars = starsOutput("star", "star", "star", "star", "star empty");
                var threeHalfStars = starsOutput("star", "star", "star", "star half", "star empty");
                var threeStars = starsOutput("star", "star", "star", "star empty", "star empty");
                var twoHalfStars = starsOutput("star", "star", "star half", "star empty", "star empty");
                var twoStars = starsOutput("star", "star", "star empty", "star empty", "star empty");
                var oneHalfStar = starsOutput("star", "star half", "star empty", "star empty", "star empty");
                var oneStar = starsOutput("star", "star empty", "star empty", "star empty", "star empty");
                if (dataRating >= 4.75) {
                    $(this).append(fiveStars);
                } else if (dataRating >= 4.25) {
                    $(this).append(fourHalfStars);
                } else if (dataRating >= 3.75) {
                    $(this).append(fourStars);
                } else if (dataRating >= 3.25) {
                    $(this).append(threeHalfStars);
                } else if (dataRating >= 2.75) {
                    $(this).append(threeStars);
                } else if (dataRating >= 2.25) {
                    $(this).append(twoHalfStars);
                } else if (dataRating >= 1.75) {
                    $(this).append(twoStars);
                } else if (dataRating >= 1.25) {
                    $(this).append(oneHalfStar);
                } else if (dataRating < 1.25) {
                    $(this).append(oneStar);
                }
            });
    }

    // snackbar for display msg
    function snackbar_msg(msg)
        {
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