$(document).ready(function(){
    $('.text_container').addClass("hidden");

    $('.text_container').click(function() {
        var $this = $(this);

        if ($this.hasClass("hidden")) {
            $(this).removeClass("hidden").addClass("visible");

        } else {
            $(this).removeClass("visible").addClass("hidden");
        }
    });
});