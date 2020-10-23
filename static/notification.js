$(document).ready(function () {
    $(".js-user-notification").on("click", function () {
        const thisRef = $(this);
        const url = $(this).data("url");

        $.ajax({
            type: "ajax",
            method: "GET",
            url: url,
            success: function (data) {
                // console.log(data);
                if(data.success){
                    thisRef.find('span').attr("hidden", true);
                    $(".js-header-user-notifications ul").html(data.html);
                }
            }
        });
    });

     // views Message notification
    $(".js-message-notification").on("click", function () {
        const thisRef = $(this);
        const url = $(this).data("url");

        $.ajax({
            type: "ajax",
            method: "GET",
            url: url,
            success: function (data) {
                // console.log(data);
                if(data.success){
                    thisRef.find('span').attr("hidden", true);
                    $(".js-header-message-notification ul").html(data.html);
                }
            }
        });
    });


    let ws_schema = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_schema + '://' + window.location.host + "/notifications/";
    let ws = new WebSocket(ws_path);

    ws.onopen = function (event) {
        // console.log("opened ", event);
    };

    ws.onclose = function (event) {
        // console.log("closed ", event)
    };

    ws.onmessage = function (event) {
        // console.log("message ", event);
        let data = JSON.parse(event.data);

        // console.log("data ", data);
        if (data['type'] === "user") {
            // console.log("type is user");
            let unread_notification_count = parseInt(data.unread_notification_count);
            if (unread_notification_count > 0) {
                // console.log("unread_notification_count ", unread_notification_count);
                $('.js-user-notification span').removeAttr("hidden").html(unread_notification_count);
            }
        }

        if (data['type'] === "message") {
            // console.log("type is message");
            let unread_msg_notification_count = parseInt(data.unread_msg_notification_count);
            if (unread_msg_notification_count > 0) {
                // console.log("unread_notification_count ", unread_msg_notification_count);
                $('.js-message-notification span').removeAttr("hidden").html(unread_msg_notification_count);
            }
        }

    };

    ws.onerror = function (event) {
        console.log("error ", event)
    };

});