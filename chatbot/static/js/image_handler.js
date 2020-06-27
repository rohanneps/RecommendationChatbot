// Image Upload using Ajax
$('input[type="file"]').on('change', function () {
    let photo = document.getElementById("image-input").files[0];
    // console.log(photo)

    // File Name run time modification
    new_photo_name = getCurrentDateTime()+'_'+photo.name
    var blob = photo.slice(0, photo.size); 
    new_photo = new File([blob], new_photo_name);
    image_file_name = new_photo.name

    // Form data for post request
	let formData = new FormData();
	formData.append("photo", new_photo);

    // File extension check

    if(new_photo != null && isImageFile(image_file_name)) {
        // console.log('Session variable saved')
    	sessionStorage.setItem("image_file_name", image_file_name);
    	$.ajax({
    	    url : "/upload_image",
    	    type: "POST",
    	    data : formData,
    	    processData: false,
    	    contentType: false,
        success:function(data, textStatus, jqXHR){
            // console.log(data)
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
    }else{
        sessionStorage.setItem("image_file_name", null);
    }
});

// Tool-tip
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});

// Check Image File Extension 
function isImageFile(file_name){
        var image_file_extensions = ['jpg','png','jpeg'];
        var file_extension = file_name.split('.');
        file_extension = file_extension[file_extension.length-1];
        return image_file_extensions.includes(file_extension.toLowerCase());
}

function getCurrentDateTime(){
    var d = new Date()
    return d.getUTCFullYear()+d.getUTCMonth()+d.getDate()+'-'+d.getHours()+d.getMinutes()+d.getSeconds()
}
// on click image upload link
$('#image_upload').click(function (e) {
    	
 	  	// Show last image box
        user_image_file_name = sessionStorage.getItem("image_file_name"); 
        if (user_image_file_name != null && isImageFile(image_file_name)){
            // when user image is provided
            showUserImageMessage();
            console.log('Showing User Image')
            sayToBot('Image Provided');
            showTextBox();
            hideImageUploadOption();
    }else{
        sayToBot('Image not provided');
    }
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
        // console.log(user_image_file_name)
        // assigning user image to last img_tag
        // console.log(img_tags)
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


