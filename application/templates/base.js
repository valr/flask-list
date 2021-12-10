
$('.dropdown-filter').on('show.bs.dropdown', function () {
    var element = $(this);

    $.ajax({
        url: '{{ url_for("category.get_filters") }}',
        headers: { 'X-CSRFToken': '{{ csrf_token() }}' },
        dataType: 'html'
    })
        .done(function (data, textStatus, xhr) {
            $(element).children('.dropdown-menu').html(data);
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                'POST failed on category.get_filters.' +
                ' responseText:' + xhr.responseText);
        });
});

$('.dropdown-filter').on('click', '.dropdown-item', function () {
    var element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("category.set_filter") }}',
        headers: { 'X-CSRFToken': '{{ csrf_token() }}' },
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify({
            item_id: $(element).attr('data-item-id'),
            version_id: $(element).attr('data-version-id')
        }),
        dataType: 'json'
    })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                'POST failed on category.set_filter.' +
                ' item_id:' + $(element).attr('data-item-id') +
                ' version_id:' + $(element).attr('data-version-id') +
                ' responseText:' + xhr.responseText);
        })
        .always(function () {
            location.reload();
        });
});
