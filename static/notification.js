  let ws_schema = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_schema + '://' + window.location.host + "/notifications/";
    let ws = new WebSocket(ws_path);

    ws.onopen = function (event) {
        console.log("opened ", event);
    };

    ws.onclose = function (event) {
        console.log("closed ", event)
    };

    ws.onmessage = function (event) {
        console.log("message ", event);
        let data = JSON.parse(event.data);
        let unread_notification_count = parseInt(data.unread_notification_count);
        if(unread_notification_count > 0) {
            console.log("unread_notification_count ", unread_notification_count);
            $('.js-user-notification span').removeAttr("hidden").html(unread_notification_count);
        }
    };

    ws.onerror = function (event) {
        console.log("error ", event)
    };
