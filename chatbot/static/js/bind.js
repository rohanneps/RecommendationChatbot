
function addBr(text){
    return text.replace(/\n/g, "<br />");

}
var Message;
Message = function (arg) {
    this.text = arg.text, this.message_side = arg.message_side;
    this.draw = function (_this) {
        return function () {
            var $message;
            $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side).find('.text').html(addBr(_this.text));
            $('.messages').append($message);
            return setTimeout(function () {
                return $message.addClass('appeared');
            }, 0);
        };
    }(this);
    return this;
};


function showBotMessage(msg){
        message = new Message({
             text: msg,
             message_side: 'left'
        });
        var img_avatar_tag = document.getElementsByTagName("img");
        // -2 as last image is upload image
        var lastSelect = img_avatar_tag[img_avatar_tag.length-2];
        lastSelect.className = "img_enabled";
        message.draw();
        $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
}


function disableBotAvatar(){
    var img_avatar_tag = document.getElementsByTagName("img");
    var lastSelect = img_avatar_tag[img_avatar_tag.length-2];
    lastSelect.className = "img_disabled";
}

function showUserMessage(msg){
        $messages = $('.messages');
        message = new Message({
            text: msg,
            message_side: 'right'
        });
        disableBotAvatar();
        // var img_avatar_tag = document.getElementsByTagName("img");
        // var lastSelect = img_avatar_tag[img_avatar_tag.length-2];
        // lastSelect.className = "img_disabled";

        message.draw();
        $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
        $('#msg_input').val('');
}


function sayToBot(text){
    document.getElementById("msg_input").placeholder = "Type your messages here..."
    $.post("/chat",
            {
                //csrfmiddlewaretoken:csrf,
                text:text,
            },
            function(jsondata, status){
                // console.log(jsondata)
                if(jsondata["status"]=="success"){
                    response=jsondata["response"];

                    if(response){
                        showBotMessage(response);
                        // console.log(response)
                        if(response.search('now please provide an image')!= -1){
                            // handle for image upload
                            // console.log(response);
                            // console.log('cat');
                            hideTextBox()
                            showImageUploadOption()
                        }
                    }
                }
            });

}

getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };

$("#say").keypress(function(e) {
    if(e.which == 13) {
        $("#saybtn").click();
    }
});

$('.send_message').click(function (e) {
        msg = getMessageText();
        if(msg){
        showUserMessage(msg);
        sayToBot(msg);
    $('.message_input').val('');}
});

$('.message_input').keyup(function (e) {
    if (e.which === 13) {
        msg = getMessageText();
        if(msg){
        showUserMessage(msg);
        sayToBot(msg);
    $('.message_input').val('') ;}
    }
});



