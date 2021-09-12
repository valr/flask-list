
$('td[data-href]').on('click', function () {
    window.location.href = $(this).data('href');
});
