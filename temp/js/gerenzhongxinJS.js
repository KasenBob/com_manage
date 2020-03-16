$(document).ready(function() {
    $('.fun-btn .glyphicon-ok').click(function() {
        var v = $(this).parent().parent();
        $(this).siblings().first().remove();
        $(this).remove();
        v.slideUp(function() {
            v.prependTo($('#confirmed .panel-body')).slideDown();
        })
    });
})

$(document).ready(function() {
    $('.fun-btn .glyphicon-remove').click(function() {
        var v = $(this).parent().parent();
        $(this).parent().remove();
        v.fadeOut('', function() {
            v.empty();
        })
    });
})
$(document).ready(function() {
    $("#avatar_file").change(function() {
        var file = $(this)[0].files[0];
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            $("#avatar_img").attr("src", this.result);
        }
    });
})