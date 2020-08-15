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
            success:function (data) {
                // console.log(data);
                    if(data.success){
                         $.magnificPopup.close();
                         window.location = '/';
                    }
                    else{
                        fromRef.find('input[type=password]').val("");

                        if(data.errors['email']) {
                            $("#emailError").html(data.errors['email'][0]);
                        }else{
                            $('#emailError').html("");
                        }
                        if(data.errors['password2']){
                            let passwordError = `<ul>`;
                            for(let error of data.errors['password2']){
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
        });
    })

    //Login Form
    const loginForm = $("#login-form");
    $(loginForm).submit(function (event) {
        event.preventDefault();
        const formData = loginForm.serialize();
        console.log("Login form data" + formData);
        const url = loginForm.attr('action');
        $.ajax({
            type:"ajax",
            url:url,
            method:"POST",
            data:formData,
            success:function (data) {
                    if(data.success){
                         $.magnificPopup.close();
                         window.location = '/';
                    }
                    else {
                        loginForm.find('input[type=password]').val("");
                        if(data.errors){
                            $("#loginError").html(data.errors['__all__'])
                        }
                        else{
                            $('#loginError').html("");
                        }
                    }
            }
        });
    })

        // change Password
    const chgPsdFormRef = $('#changePasswordForm');
    $(chgPsdFormRef).submit(function (e) {
        e.preventDefault();
        const formData = chgPsdFormRef.serialize();
        const url = chgPsdFormRef.attr('action');

        $.ajax({
            type:"ajax",
            url:url,
            method:"POST",
            data:formData,
            success:function (data) {
                if(data.success){
                    snackbar_msg(data.msg);
                    chgPsdFormRef.trigger('reset');
                }
                else{
                    chgPsdFormRef.trigger('reset');
                    if(data.errors['old_password']){
                        $('#old_password-error').show().html(data.errors['old_password']);
                    }
                    else{
                        $('#old_password-error').hide().html("");
                    }

                    if(data.errors['new_password2']){
                        $('#new_password-error').show().html(data.errors['new_password2']);
                    }
                    else{
                        $('#new_password-error').hide().html("");
                    }
                }
            }
        })

    });

    // Account Form
    const accountFormRef = $('#accountForm');
    accountFormRef.submit(function (e) {
        e.preventDefault();

        const url = accountFormRef.attr('action');
        const formData = new FormData($('#accountForm')[0]);
        // for(let value of formData.entries())
        //         console.log(value[0]+'  '+value[1]);

        $.ajax({
            type:"ajax",
            url: url,
            method: "POST",
            processData: false,
            contentType: false,
            cache: false,
            data: formData,
            success:function (data) {
                if(data.success){
                    snackbar_msg(data.msg)
                }
                else{
                    snackbar_msg(data.errors)
                }
            }
        });
    });

    // Offer form Submit.
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
                console.log(data);
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
});