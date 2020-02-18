$(function () {
    

    
    $("#myMsg .msg-piece").click(function () {
        $("#myMsg").css("display","none");
        $("#myMsg-show").css("display","block");
        makeFooter();
    });
    
    $("#msg-back").click(function () {
        $("#myMsg").css("display","block");
        $("#myMsg-show").css("display","none");
        makeFooter();
    });

    $("#myCtx .msg-piece").click(function () {
        $("#myCtx").css("display","none");
        $("#myCtx-show").css("display","block");
        makeFooter();
    });

    $("#ctx-back").click(function () {
        $("#myCtx").css("display","block");
        $("#myCtx-show").css("display","none");
        makeFooter();
    });

    function makeFooter() {
        $("#footer").remove();
        var contentHeight = document.body.scrollHeight,
            winHeight = window.innerHeight;
        if (winHeight > contentHeight) {
            $("body").append("<footer id=\"footer\" class='navbar-fixed-bottom'>地址：广东惠州市演达大道46号 邮编：516007<br>总机：0752-2529000 E-mail:webmaster@hzu.edu.cn<br>版权所有©惠州学院 粤ICP备********号</footer>\n")
        }else{
            $("body").append("<footer id=\"footer\">地址：广东惠州市演达大道46号 邮编：516007<br>总机：0752-2529000 E-mail:webmaster@hzu.edu.cn<br>版权所有©惠州学院 粤ICP备********号</footer>\n")
        }
    }
    makeFooter();
    
});

window.onresize=function () {
    $("#footer").remove();
    var contentHeight = document.body.scrollHeight,
        winHeight = window.innerHeight;
    if (winHeight > contentHeight) {
        $("body").append("<footer id=\"footer\" class='navbar-fixed-bottom'>地址：广东惠州市演达大道46号 邮编：516007<br>总机：0752-2529000 E-mail:webmaster@hzu.edu.cn<br>版权所有©惠州学院 粤ICP备********号</footer>\n")
    }else{
        $("body").append("<footer id=\"footer\">地址：广东惠州市演达大道46号 邮编：516007<br>总机：0752-2529000 E-mail:webmaster@hzu.edu.cn<br>版权所有©惠州学院 粤ICP备********号</footer>\n")
    }
};