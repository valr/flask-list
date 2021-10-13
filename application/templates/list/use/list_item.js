
var csrf_token = "{{ csrf_token() }}";

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrf_token);
        }
    }
});

$(document).on('click', '.btn', function () {
    element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.item_switch_selection") }}',
        data: JSON.stringify({
            list_id: '{{ list.list_id }}',
            item_id: $(element).attr('data-item-id'),
            version_id: $(element).attr('data-version-id')
        }),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json'
    })
        .done(function (data, textStatus, xhr) {
            if (data.status === 'ok') {
                if (data.selection === false) {
                    $(element)
                        .removeClass('btn-success text-white')
                        .addClass('bg-transparent text-dark')
                        .attr('data-version-id', data.version)
                        .html(`{{ render_icon("square") }}`);
                } else if (data.selection === true) {
                    $(element)
                        .removeClass('bg-transparent text-dark')
                        .addClass('btn-success text-white')
                        .attr('data-version-id', data.version)
                        .html(`{{ render_icon("check-square") }}`);
                }
            } else if (data.status === 'cancel') {
                window.location.href = data.cancel_url;
            }
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                'POST failed on list.item_switch_selection.' +
                ' list_id:' + '{{ list.list_id }}' +
                ' item_id:' + $(element).attr('data-item-id') +
                ' version_id:' + $(element).attr('data-version-id') +
                ' responseText:' + xhr.responseText);
        });
});

    return false;

$(document).on('click input', '.form-control', function (event) {
    element = $(this);

    if (event.type === 'click') {
        if ($(element).hasClass('text-danger')) {
            $(element).removeClass('text-danger');
        } else {
            return true;
        }
    } else {
        $(element)
            .addClass('font-weight-bold')
            .removeClass('text-danger');
    }

    debounce(
        $(element).attr('data-item-id'),
        function (element) {
            $.ajax({
                type: 'POST',
                url: '{{ url_for("list.item_set_text") }}',
                data: JSON.stringify({
                    list_id: '{{ list.list_id }}',
                    item_id: $(element).attr('data-item-id'),
                    version_id: $(element).attr('data-version-id'),
                    text: $(element).val()
                }),
                contentType: 'application/json; charset=UTF-8',
                dataType: 'json'
            })
                .done(function (data, textStatus, xhr) {
                    if (data.status === 'ok') {
                        $(element)
                            .removeClass('font-weight-bold')
                            .attr('data-version-id', data.version);
                    } else if (data.status === 'cancel') {
                        window.location.href = data.cancel_url;
                    }
                })
                .fail(function (xhr, textStatus, errorThrown) {
                    $(element).addClass('text-danger');
                    console.log(
                        'POST failed on list.item_set_text.' +
                        ' list_id:' + '{{ list.list_id }}' +
                        ' item_id:' + $(element).attr('data-item-id') +
                        ' version_id:' + $(element).attr('data-version-id') +
                        ' text:' + $(element).val() +
                        ' responseText:' + xhr.responseText);
                });
        }, 1000, element);
});
