
$('thead').on('click', '.item-type', function () {
    var element = $(this);

    $(element)
        .closest('table')
        .children('tbody')
        .find('.item-type')
        .each(function () {
            $(this).trigger('click');
        });
});

$('tbody').on('click', '.item-type', function () {
    var element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.item_switch_type") }}',
        headers: { 'X-CSRFToken': '{{ csrf_token() }}' },
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify({
            list_id: '{{ list.list_id }}',
            item_id: $(element).attr('data-item-id'),
            version_id: $(element).attr('data-version-id')
        }),
        dataType: 'json'
    })
        .done(function (data, textStatus, xhr) {
            if (data.status === 'ok') {
                if (data.type === 'none') {
                    $(element)
                        .removeClass('btn-secondary text-white')
                        .addClass('bg-transparent text-dark')
                        .attr('data-version-id', data.version)
                        .html(`{{ render_icon("square") }}`);
                } else if (data.type === 'selection') {
                    $(element)
                        .removeClass('bg-transparent text-dark')
                        .addClass('btn-success text-white')
                        .attr('data-version-id', data.version)
                        .html(`{{ render_icon("check-square") }}`);
                } else if (data.type === 'number') {
                    $(element)
                        .removeClass('btn-success text-white')
                        .addClass('btn-info text-white')
                        .attr('data-version-id', data.version)
                        .html(`{{ render_icon("calculator") }}`);
                } else if (data.type === 'text') {
                    $(element)
                        .removeClass('btn-info text-white')
                        .addClass('btn-secondary text-white')
                        .attr('data-version-id', data.version)
                        .html(`{{ render_icon("card-text") }}`);
                }
            } else if (data.status === 'cancel') {
                window.location.href = data.cancel_url;
            }
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                'POST failed on list.item_switch_type.' +
                ' list_id:' + '{{ list.list_id }}' +
                ' item_id:' + $(element).attr('data-item-id') +
                ' version_id:' + $(element).attr('data-version-id') +
                ' responseText:' + xhr.responseText);
        });
});
