$(window).on("beforeunload", function () {
    window.sessionStorage.setItem(
        "scrollY@" + window.location.pathname,
        window.scrollY
    );
});

$(function () {
    var scrollY = window.sessionStorage.getItem("scrollY@" + window.location.pathname);
    if (scrollY !== null) {
        window.scrollTo(0, scrollY);
    }
});
