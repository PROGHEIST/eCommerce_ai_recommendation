var tl = gsap.timeline();

tl.from('.logocontainer', {
    y: -100,
    duration: 0.8,
    stagger: true
})

tl.from('#links', {
    y: -100,
    duration: 0.8,
    stagger: 1.0
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



