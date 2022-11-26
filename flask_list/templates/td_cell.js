
$('tbody').on('click', 'td[data-href]', function () {
    window.location.href = $(this).data('href');
});
