// Image Upload using Ajax
$('input[type="file"]').on('change', function () {
    let photo = document.getElementById("image-input").files[0];
    image_file_name = photo.name
	let formData = new FormData();
	formData.append("photo", photo);
	sessionStorage.setItem("image_file_name", image_file_name);
	$.ajax({
	    url : "/upload_image",
	    type: "POST",
	    data : formData,
	    processData: false,
	    contentType: false,
    success:function(data, textStatus, jqXHR){
	    if (data == 'Incorrect FileFormat'){
	    	$.ajax({
	    	url : "/upload_image",
	    	type: "GET",
	    });
	    }
    },
    error: function(jqXHR, textStatus, errorThrown){
        //if fails    
        // console.log(errorThrown)
    }
		});
		// console.log('Calling Ajx')
});

// Tool-tip
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});



// on click image upload link
$('.image_upload').click(function (e) {
    	
 	  	// Show last image box
        showUserImageMessage();
        console.log('Showing User Image')
        sayToBot('Image Provided');
        showTextBox();
        hideImageUploadOption();
});

// New Image Message Instance
var MessageImage;
MessageImage = function (arg) {
    this.text = arg.text, this.message_side = arg.message_side;
    this.draw = function (_this) {
        return function () {
            var $message;
            $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side)
            
            $('.messages').append($message);
            return setTimeout(function () {
                return $message.addClass('appeared');
            }, 0);
        };
    }(this);
    return this;
};

// Display User Image After Upload
function showUserImageMessage(){
        // $messages = $('.messages');
        image_message = new MessageImage({
            // text: msg,
            message_side: 'right'
        });
        disableBotAvatar();
        image_message.draw();
        $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);

        // Assign user image
        var img_tags = document.getElementsByTagName('img')
        user_image_file_name = sessionStorage.getItem("image_file_name"); 
        console.log(user_image_file_name)
        // assigning user image to last img_tag
        console.log(img_tags)
        img_tags[img_tags.length-3].src = "/media/"+ user_image_file_name;

        // Enable user message chat
        var text_box = document.getElementsByClassName("text_wrapper");
		text_box[text_box.length-2].style.display = "none";
		// Disable user image message
		var image_message = document.getElementsByClassName("image_wrapper");
		image_message[image_message.length-2].style.display = null;

}

// Hide Textbox input
function hideTextBox(){
        var text_box = document.getElementsByClassName("bottom_wrapper clearfix");
        text_box[text_box.length-1].style.display = "none";
}


// Enable Textbox input 
function showTextBox(){
        var text_box = document.getElementsByClassName("bottom_wrapper clearfix");
        text_box[text_box.length-1].style.display = null;
}


// Disable Image Upload
function hideImageUploadOption(){
        var text_box = document.getElementsByClassName("bottom_wrapper image_upload");
        text_box[text_box.length-1].style.display = "none";
}

// Enable Image Upload
function showImageUploadOption(){
        var text_box = document.getElementsByClassName("bottom_wrapper image_upload");
        text_box[text_box.length-1].style.display = null;
}


