$(document).ready(function() {
	$("#ce").toggle();
	$("#cece").toggle();
	$("#cebian").animate({
		"width": "63px",
		"word-spacing": "1px"
	}, 0);

	var contentHeight = document.body.scrollHeight,
		winHeight = window.innerHeight;
	if (winHeight > contentHeight) {
		$("#dibu").addClass("navbar-fixed-bottom");
	}


	$("#cebiankaiguan").on("click", function() {
		if ($("#cebiankaiguan").hasClass("glyphicon-menu-right") == true) {
			$("#cebiankaiguan").removeClass("glyphicon-menu-right");
			$("#cebiankaiguan").addClass("glyphicon-menu-left");
			$("#cebian").animate({
				"width": "200px",
			}, 0);
			$("#cebiankaiguan").animate({
				"left": "170px"
			}, 0);
			$("#cebianneirong").css("display", "block");
		} else {
			$("#cebiankaiguan").removeClass("glyphicon-menu-left");
			$("#cebiankaiguan").addClass("glyphicon-menu-right");
			$("#cebian").animate({
				"width": "63px",
			}, 100);
			$("#cebiankaiguan").animate({
				"left": "30px"
			}, 100);
			$("#cebianneirong").css("display", "none");

		}
	});

	$("#qiebiao,#qhlb").on("click", function() {
		$("#biao").css("display", "block");
		$("#tiao").css("display", "none");
		$("#qiebiao").css("color", "#6CB670");
		$("#qiezhou").css("color", "white");
	});

	$("#qiezhou,#qhsjz").on("click", function() {
		$("#biao").css("display", "none");
		$("#tiao").css("display", "block");
		$("#qiezhou").css("color", "#6CB670");
		$("#qiebiao").css("color", "white");
	});



	$("#zhu1").click(function() {
		$("#zhu1").addClass("tcolor");
		$("#zhu2").removeClass("tcolor");
		$("#zhu3").removeClass("tcolor");
		$("#zhuping2").css("display", "none");
		$("#zhuping3").css("display", "none");
		$("#zhuping1").fadeIn(500);
	});

	$("#zhu2").click(function() {
		$("#zhu2").addClass("tcolor");
		$("#zhu3").removeClass("tcolor");
		$("#zhu1").removeClass("tcolor");
		$("#zhuping1").css("display", "none");
		$("#zhuping3").css("display", "none");
		$("#zhuping2").fadeIn(500);
	});

	$("#zhu3").click(function() {
		$("#zhu3").addClass("tcolor");
		$("#zhu2").removeClass("tcolor");
		$("#zhu1").removeClass("tcolor");
		$("#zhuping2").css("display", "none");
		$("#zhuping1").css("display", "none");
		$("#zhuping3").fadeIn(500);
	});

	




	/* 筛选栏的js */


});
