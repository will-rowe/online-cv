jQuery(document).ready(function($) {
    $('.level-bar-inner').css('width', '0')

    $(window).on('load', function() {
        $('.level-bar-inner').each(function() {
            var itemWidth = $(this).data('level')

            $(this).animate({
                    width: itemWidth
                },
                800
            )
        })
    })
})

/*Scroll to top when arrow up clicked BEGIN
from - https://html-online.com/articles/dynamic-scroll-back-top-page-button-javascript/
*/
$(window).scroll(function() {
    var height = $(window).scrollTop()
    if (height > 100) {
        $('#back2Top').fadeIn()
    } else {
        $('#back2Top').fadeOut()
    }
})
$(document).ready(function() {
        $('#back2Top').click(function(event) {
            event.preventDefault()
            $('html, body').animate({ scrollTop: 0 }, 'slow')
            return false
        })
    })
    /*Scroll to top when arrow up clicked END*/