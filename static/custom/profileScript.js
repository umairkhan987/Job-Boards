$(document).ready(function () {
    // Display freelancers profile for editing...
   function getProfileData() {
       console.log("get profile data");

        $.ajax({
            type:'GET',
            url: '/account/getProfile/',
            success: function (data) {
                console.log(data);
                if(data.success){
                     $('select[name=country]').val(data.profile.country).change();
                     // const skills = data.profile.skills.split(",");
                     // $('select[name=skills]').val(skills).change();

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
   //  getProfileData();

    // change value of rate when slider slide
    $('.js-profile-setting-div').on('change', '.js-bidding-slider', function (e) {
        e.preventDefault();
        let value = $(this).val();
        $("#biddingVal").html(value);
    });

    // when click Upload File Button for upload User CV
    let userCvFile = null;
    let fileChange = false;

    $('.js-profile-setting-div').on("change", "#upload", function () {
        let file = $(this)[0].files[0];
        fileChange = true;
        userCvFile = file;
        if (file) {
            let extension = file.name.split('.').pop().toUpperCase();
            let fileMarkup = `<span>${file.name}</span> <i>${extension}</i><button type="button" id="removeFile" class="remove-attachment" title="Remove" data-tippy-placement="top"></button>`;
            $('#attachmentBox').show().html(fileMarkup);
        }
    });

    // Delete File Click delegate
    $('.js-profile-setting-div').on('click','#removeFile', function () {
        userCvFile = null;
        fileChange = true;

        $('#upload').val(null);
        $('#attachmentBox').hide().html("");
        $('#uploadFileName').html('Maximum file size: 10 MB');
    });


    // Save Profile Button Click

    $('.js-profile-setting-div').on("submit", "form",function (e) {
        e.preventDefault();
        const url = $(this).attr('action');
        const formData = new FormData($(this)[0]);
        if(userCvFile === null && fileChange === true)
            formData.set('userCV', null);
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
                 // console.log(data);
                $('.js-profile-change-loading-spinner').attr('hidden', true);
                $('.js-profile-setting-div').html(data.html);
                $('.selectpicker').selectpicker('render');
                $('.bidding-slider').slider();

                 if(data.success){
                    snackbar_msg(data.msg);
                }
                // else{
                //     snackbar_error_msg("Upload Profile Error");
                // }
             }
         })
    });

    // change Password
    $('.js-password-change-div').on('submit','form', function (e) {
        e.preventDefault();

        const formData = $(this).serialize();
        const url = $(this).attr('action');

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
              $('.js-password-change-div').html(data.html);

                if(data.success){
                    snackbar_msg(data.msg);
                }
                // else{
                //     chgPsdFormRef.trigger('reset');
                //     if(data.errors['old_password']){
                //         $('#old_password-error').show().html(data.errors['old_password']);
                //     }
                //     else{
                //         $('#old_password-error').hide().html("");
                //     }
                //
                //     if(data.errors['new_password2']){
                //         $('#new_password-error').show().html(data.errors['new_password2']);
                //     }
                //     else{
                //         $('#new_password-error').hide().html("");
                //     }}
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