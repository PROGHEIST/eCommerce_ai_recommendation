var tl = gsap.timeline();

tl.from('.logocontainer', {
    y: -100,
    duration: 0.8,
    stagger: true
})

tl.from('.navlinks-animation', {
    y: -100,
    duration: 0.8,
    stagger: true
})

tl.from('.signupContainer ul', {
    y: -100,
    duration: 0.8,
    stagger: true
});


tl.from('.slogan', {
    y: 100,
    opacity:0,
    duration: 0.8,
    stagger: true
})
tl.from('.heroContainer a', {
    y: 100,
    opacity:0,
    duration: 0.8,
    stagger: true
})

tl.from('.heroContainer img', {
    y: 100,
    opacity:0,
    duration: 0.8,
    stagger: true
})


tl.from('.heroContainer i', {
    y: 100,
    opacity:0,
    duration: 0.8,
    stagger: true
})


$(document).ready(function(){
    $('#prev').click(function(){
        gsap.to('.cardContainer', {
            x:-100,
            duration:1,
            ease: 'power1.out'
        })
    })
    $('#next').click(function(){
        gsap.to('.cardContainer', {
            x:100,
            duration:1,
            ease: 'power1.out'
        })
    })
    $('#prev2').click(function(){
        gsap.to('.cardContainer1', {
            x:-100,
            duration:1,
            ease: 'power1.out'
        })
    })
    $('#next2').click(function(){
        gsap.to('.cardContainer1', {
            x:100,
            duration:1,
            ease: 'power1.out'
        })
    })
})

$(document).ready(function(){
    $('#user').click(function(){
      $('#panel').hide('slow');
    })
})