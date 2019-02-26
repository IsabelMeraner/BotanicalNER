var language = 'en';
(function () {
    var deButton = document.getElementById('deClick');
    var enButton = document.getElementById('enClick');

    deButton.addEventListener('click', function () {
        language = 'de';
        checkLanguageButtonActive();

    }, false);

    enButton.addEventListener('click', function () {
        language = 'en';
        checkLanguageButtonActive();

    }, false);
    checkLanguageButtonActive();

})();

// check language button active
function checkLanguageButtonActive() {
        if (language === 'de') {
        $( "#enClick" ).removeClass( "langBtnActive" );
        $( "#deClick" ).addClass( "langBtnActive" );
    } else {
        $( "#deClick" ).removeClass( "langBtnActive" );
        $( "#enClick" ).addClass( "langBtnActive" );
    }
}

// Attach a submit handler to the form
$("#askForm").submit(function (event) {
    // Stop form from submitting normally
    event.preventDefault();

    //  Reset result
    $("#result").empty();
    $("#DownloadJson").css({ display: "none" });
    $('.modal2').addClass('active2');

    // Get some values from elements on the page:
    var $form = $(this),
        term = $form.find("textarea[name='data']").val(),
        url = $form.attr("action");
    if (term === '') {
        return;
    }

    // Send the data using post
    var posting = $.post(url, {
        data: term,
        lang: language
    });

    // On Success
    posting.done(function (data) {
        $("#result").append("<pre class='chatTextRow'><code class='botChatText'>" + data + "</code></pre>");
        $("#DownloadJson").css({ display: "block" });
        $('.modal2').removeClass('active2');
    });
});