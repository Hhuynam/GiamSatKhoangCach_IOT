$(document).ready(function() {
    $("#save_time_button").click(function() {
        $.ajax({
            url: "/save_time",  // Gọi route lưu thời gian và ảnh
            type: "POST",
            success: function(response) {
                // Hiển thị thời gian vừa lưu và ảnh
                $("#saved_time").text("Time saved: " + response);
                let img_url = response.split('Image Path: ')[1];  // Cắt phần đường dẫn ảnh từ response
                $("#saved_image").attr("src", img_url).show();  // Hiển thị ảnh
            }
        });
    });
});
