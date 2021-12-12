
$(function () {
    $('.collapse').not('.navbar-collapse').each(function () {
        var element = $(this);

        if (window.sessionStorage.getItem(
            $(element).attr('id') + '@' + window.location.pathname) !== null) {
            $(element).collapse();
            $(element)
                .closest('table').parent()
                .nextAll(':has(table):first').children('table:first')
                .removeClass('mt-3').addClass('mt-0');
        }
    });
});

$('.collapse').not('.navbar-collapse').on('hidden.bs.collapse', function () {
    var element = $(this);

    window.sessionStorage.setItem(
        $(element).attr('id') + '@' + window.location.pathname, 'hidden');

    $(element)
        .closest('table').parent()
        .nextAll(':has(table):first').children('table:first')
        .removeClass('mt-3').addClass('mt-0');
});

$('.collapse').not('.navbar-collapse').on('shown.bs.collapse', function () {
    var element = $(this);

    window.sessionStorage.removeItem(
        $(element).attr('id') + '@' + window.location.pathname);

    $(element)
        .closest('table').parent()
        .nextAll(':has(table):first').children('table:first')
        .removeClass('mt-0').addClass('mt-3');
});
