$('.dropdown-list').on('click', '.dropdown-item', function () {
    var dropdown_item = $(this);

    $(dropdown_item)
        .closest('table')
        .children('tbody')
        .find('.item-type')
        .each(function () {
            var element = $(this);

            $.ajax({
                type: 'POST',
                url: '{{ url_for("list.item_set_type") }}',
                headers: { 'X-CSRFToken': '{{ csrf_token() }}' },
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({
                    list_id: '{{ list.list_id }}',
                    item_id: $(element).attr('data-item-id'),
                    version_id: $(element).attr('data-version-id'),
                    type: $(dropdown_item).attr('dropdown-item-id')
                }),
                dataType: 'json'
            })
                .done(function (data, textStatus, xhr) {
                    if (data.status === 'ok') {
                        element_refresh(element, data);
                    } else if (data.status === 'cancel') {
                        window.location.href = data.cancel_url;
                    }
                })
                .fail(function (xhr, textStatus, errorThrown) {
                    console.log(
                        'POST failed on list.item_set_type.' +
                        ' list_id:' + '{{ list.list_id }}' +
                        ' item_id:' + $(element).attr('data-item-id') +
                        ' version_id:' + $(element).attr('data-version-id') +
                        ' type:' + $(dropdown_item).attr('dropdown-item-id') +
                        ' responseText:' + xhr.responseText);
                });
        });
});

$('tbody').on('click', '.item-type', function () {
    var element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.item_set_type") }}',
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
                element_refresh(element, data);
            } else if (data.status === 'cancel') {
                window.location.href = data.cancel_url;
            }
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                'POST failed on list.item_set_type.' +
                ' list_id:' + '{{ list.list_id }}' +
                ' item_id:' + $(element).attr('data-item-id') +
                ' version_id:' + $(element).attr('data-version-id') +
                ' responseText:' + xhr.responseText);
        });
});

function element_refresh(element, data) {
    $(element)
        .attr('data-version-id', data.version)
        .removeClass('bg-transparent btn-success btn-info btn-secondary')
        .removeClass('text-dark text-white');

    if (data.type === 'none') {
        $(element)
            .addClass('bg-transparent text-dark')
            .html(`{{ render_icon("square") }}`);
    } else if (data.type === 'selection') {
        $(element)
            .addClass('btn-success text-white')
            .html(`{{ render_icon("check-square") }}`);
    } else if (data.type === 'number') {
        $(element)
            .addClass('btn-info text-white')
            .html(`{{ render_icon("calculator") }}`);
    } else if (data.type === 'text') {
        $(element)
            .addClass('btn-secondary text-white')
            .html(`{{ render_icon("card-text") }}`);
    }
}

$('.table-responsive').on('show.bs.dropdown', function () {
    var element = $(this);

    /* no scrollbar if the height of the dropdown menu is bigger than */
    /* the height of the table. However, display the dropdown menu entirely */
    $(element).css('overflow', 'inherit');

    /* scroll to the right so the dropdown menu remains visible */
    $('body, html').scrollLeft($(document).outerWidth() - $(window).width());
});

$('.table-responsive').on('hide.bs.dropdown', function () {
    var element = $(this);

    $(element).css('overflow', 'auto');
})
