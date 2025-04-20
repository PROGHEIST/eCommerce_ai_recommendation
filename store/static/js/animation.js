var tl = gsap.timeline();

tl.from('.logocontainer', {
    y: -100,
    duration: 0.8
})

tl.from('.navlinks-animation', {
    y: -100,
    duration: 0.8,
    stagger: 1.0
})

tl.from('.fa-search', {
    y: -100,
    duration: 0.8,
    stagger: 1.0
})

tl.from('.signupContainer ul', {
    y: -100,
    duration: 0.8
});


tl.from('.slogan', {
    y: 100,
    opacity:0,
    duration: 0.8
})
tl.from('.heroContainer a', {
    y: 100,
    opacity:0,
    duration: 0.8
})

tl.from('.heroContainer img', {
    y: 100,
    opacity:0,
    duration: 0.8
})


tl.from('.heroContainer i', {
    y: 100,
    opacity:0,
    duration: 0.8
})


$(document).ready(function(){
    $('.fa-bars').click(function(){
        gsap.to('.sidebar', {
            x: 0,
            duration:.5,
            ease: "power1.in"
        })
        $('.fa-bars').fadeOut('fast')
        $('.fa-close').fadeIn('slow')
    })
    $('.fa-close').click(function(){
        gsap.to('.sidebar', {
            x: -400,
            duration:.5,
            ease: "power1.out"
        })
        $('.fa-bars').fadeIn('slow')
        $('.fa-close').fadeOut('fast')
    })
})


$(document).ready(function(){
    $('#review').click(function(){
        $('#review-form').fadeToggle('linear')
    })

    $('.fa-search').click(function(){
        $('.navlinks-animation').fadeToggle('fast')
        $('.search-box').fadeToggle('fast')

        if ($(window).width() < 600) {
            $('.logocontainer').fadeToggle('fast')
        }
    })
})