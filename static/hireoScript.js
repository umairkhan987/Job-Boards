$(document).ready(function () {
    // cancel popup
    $('a.cancel-popup').click(function (event) {
        $.magnificPopup.close();
    });

    // deactivate user account.
    $('#deactivate-confirm-popup').click(function () {
        const url = $(this).attr('data-url');
        const data= {
            "csrfmiddlewaretoken": getCookie('csrftoken'),
        };

        $.ajax({
            type: 'ajax',
            method: 'POST',
            url: url,
            data: data,
            success:function (data) {
                $.magnificPopup.close();
                if(data.success){
                    snackbar_msg(data.msg);
                    setTimeout(()=>{
                        window.location = data.url;
                    }, 1000);
                }
            }
        })
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
});