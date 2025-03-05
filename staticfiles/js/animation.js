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
})