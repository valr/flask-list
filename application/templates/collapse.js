
$(function () {
    $('.collapse').not('.navbar-collapse').each(function () {
        if (window.sessionStorage.getItem(this.id + '@' + window.location.pathname) !== null) {
            $(this).collapse();
            $(this).closest('table').addClass('mb-0');
        }
    });
});

$('.collapse').not('.navbar-collapse').on('hidden.bs.collapse', function () {
    $(this).closest('table').addClass('mb-0');
    window.sessionStorage.setItem(this.id + '@' + window.location.pathname, 'hidden');
});

$('.collapse').not('.navbar-collapse').on('shown.bs.collapse', function () {
    $(this).closest('table').removeClass('mb-0');
    window.sessionStorage.removeItem(this.id + '@' + window.location.pathname);
});
