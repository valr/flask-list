
$(window).on('beforeunload', function () {
    window.sessionStorage.setItem('scrollY@' + window.location.pathname, window.scrollY);
});

$(function () {
    var scrolly = window.sessionStorage.getItem('scrollY@' + window.location.pathname);
    if (scrolly !== null) {
        window.scrollTo(0, scrolly);
    }
});
