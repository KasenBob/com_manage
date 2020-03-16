/* 筛选栏的js */
$(document).ready(function() {
    $("#select1 dd").click(function() {
        $(this).addClass("selected").siblings().removeClass("selected");
        if ($(this).hasClass("select-all")) {
            $("#selectA").remove();
        } else {
            var copyThisA = $(this).clone();
            if ($("#selectA").length > 0) {
                $("#selectA a").html($(this).text());
            } else {
                $(".clean").before(copyThisA.attr("id", "selectA"));
            }
        }
    });

    $("#select2 dd").click(function() {
        $(this).addClass("selected").siblings().removeClass("selected");
        if ($(this).hasClass("select-all")) {
            $("#selectB").remove();
        } else {
            var copyThisB = $(this).clone();
            if ($("#selectB").length > 0) {
                $("#selectB a").html($(this).text());
            } else {
                $(".clean").before(copyThisB.attr("id", "selectB"));
            }
        }
    });

    $("#select3 dd").click(function() {
        $(this).addClass("selected").siblings().removeClass("selected");
        if ($(this).hasClass("select-all")) {
            $("#selectB").remove();
        } else {
            var copyThisC = $(this).clone();
            if ($("#selectC").length > 0) {
                $("#selectC a").html($(this).text());
            } else {
                $(".clean").before(copyThisC.attr("id", "selectC"));
            }
        }
    });

    $("#selectA").on("click", function() {
        $(this).remove();
        $("#select1 .select-all").addClass("selected").siblings().removeClass("selected");
    });

    $("#selectB").on("click", function() {
        $(this).remove();
        $("#select2 .select-all").addClass("selected").siblings().removeClass("selected");
    });

    $("#selectC").on("click", function() {
        $(this).remove();
        $("#select3 .select-all").addClass("selected").siblings().removeClass("selected");
    });

    $(".select dd").on("click", function() {
        if ($(".select-result>dl>dd").length > 1) {
            $(".select-no").hide();
            $(".clean").show();
        } else {
            $(".clean").hide();
            $(".select-no").show();
        }
    });

    $(".clean").on("click", function() {
        $(this).prevAll('dd').remove();
        $(".select-all").click();
    })

    $(".shaixuan-open").on("click", function() {
        $(".shaixuanlan-body").slideToggle("slow");
        $(this).siblings().show();
        $(this).hide();
    })

    $(".shaixuan-close").on("click", function() {
        $(".shaixuanlan-body").slideToggle("slow");
        $(this).siblings().show();
        $(this).hide();
    })
});