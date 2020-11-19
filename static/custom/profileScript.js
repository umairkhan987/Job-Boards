$(document).ready(function () {

    // Display freelancers profile for editing...
   function getProfileData() {
        $.ajax({
            type:'GET',
            url: '/account/getProfile/',
            success: function (data) {
                // console.log(data);
                if(data.success){
                     $('select[name=country]').val(data.profile.country).change();
                     const skills = data.profile.skills.split(",");
                     $('select[name=skills]').val(skills).change();

                     if(data.file){
                     const filename = data.file.split("/").pop().replace('"', "");
                     let extension = filename.split('.').pop().toUpperCase();
                     let fileMarkup = `<span>${filename}</span> <i>${extension}</i><button type="button" id="removeFile" class="remove-attachment" title="Remove" data-tippy-placement="top"></button>`;
                     $('#attachmentBox').show().html(fileMarkup);
                     $('#uploadFileName').html(filename);
                     }
                }
            }
        })
   }
   // call function to set data
    getProfileData();


    // when click Upload File Button for upload User CV
    let userCvFile = null;
    $('#upload').change(function () {
        let file = $('#upload')[0].files[0];
        userCvFile = file;
        if (file) {
            let extension = file.name.split('.').pop().toUpperCase();
            let fileMarkup = `<span>${file.name}</span> <i>${extension}</i><button type="button" id="removeFile" class="remove-attachment" title="Remove" data-tippy-placement="top"></button>`;
            $('#attachmentBox').show().html(fileMarkup);
        }
    });

    // Delete File Click
    $('#attachmentBox').delegate('#removeFile','click', function () {
        userCvFile = null;
        $('#upload').val(null);
        $('#attachmentBox').hide().html("");
        $('#uploadFileName').html('Maximum file size: 10 MB');
    });


    // Save Profile Button Click
    const profileFormRef = $('#profileForm');
    profileFormRef.submit(function (e) {
        e.preventDefault();
        const url = profileFormRef.attr('action');
        const formData =new FormData(profileFormRef[0]);

        // convert list of skills into string
        const skills = formData.getAll('skills');
        formData.delete('skills');
        formData.append('skills', skills.toString());

         // for(let value of formData.entries())
         //        console.log(value[0]+'  '+value[1]);

         $.ajax({
             type:"ajax",
             url: url,
            method: "POST",
            processData: false,
            contentType: false,
            cache: false,
            data: formData,
             beforeSend:function(){
                 $('.js-profile-change-loading-spinner').removeAttr('hidden');
             },
             success: function (data) {
                $('.js-profile-change-loading-spinner').attr('hidden', true);

                 if(data.success){
                    snackbar_msg(data.msg);
                }
                else{
                    snackbar_error_msg("Upload Profile Error");
                }
             }
         })
    });

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
            beforeSend: function(){
              $('.js-password-change-loading-spinner').removeAttr('hidden');
            },
            success:function (data) {
              $('.js-password-change-loading-spinner').attr('hidden', true);

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
    $('.js-account-setting-div').on('submit', 'form', function (e) {
        e.preventDefault();

        const url = $(this).attr('action');
        const formData = new FormData($(this)[0]);
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
            beforeSend:function(){
                $('.js-account-loading-spinner').removeAttr('hidden');
            },
            success:function (data) {
                $('.js-account-loading-spinner').attr('hidden', true);
                $('.js-account-setting-div').html(data.html);
                if(data.success){
                    snackbar_msg(data.msg)
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