$('.signup-image-link').click(function(e) {
    e.preventDefault()
        $('.signup').hide()
        $('.sign-in').show()
        $('.reset').hide()
    })
$('#signup-image-link').click(function(e) {
    e.preventDefault()
        $('.signup').show()
        $('.sign-in').hide()
        $('.reset-password').hide()
    })
$('.reset-image-link').click(function(e) {
    e.preventDefault()
        $('.reset').show()
        $('.sign-in').hide()
        $('.signup').hide()
    })