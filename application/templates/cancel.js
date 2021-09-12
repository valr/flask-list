
$('#cancel').click(function () {
    // bypass the client side validations that still happen when
    // the cancel button is clicked and a mandatory field is empty
    window.location.href = '{{ cancel }}';
});

$(document).keyup(function (e) {
    if (e.key === 'Escape') {
        window.location.href = '{{ cancel }}';
    }
});
