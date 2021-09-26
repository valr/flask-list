
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
        url: '{{ url_for("list.item_switch_type") }}',
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
                if (data.type === 'none') {
                    $(element).removeClass('btn-secondary text-white');
                    $(element).addClass('bg-transparent text-dark');
                    $(element).attr('data-version-id', 'none');
                    $(element).html(`{{ render_icon("square") }}`);
                } else if (data.type === 'selection') {
                    $(element).removeClass('bg-transparent text-dark');
                    $(element).addClass('btn-success text-white');
                    $(element).attr('data-version-id', data.version);
                    $(element).html(`{{ render_icon("check-square") }}`);
                } else if (data.type === 'counter') {
                    $(element).removeClass('btn-success text-white');
                    $(element).addClass('btn-info text-white');
                    $(element).attr('data-version-id', data.version);
                    $(element).html(`{{ render_icon("calculator") }}`);
                } else if (data.type === 'text') {
                    $(element).removeClass('btn-info text-white');
                    $(element).addClass('btn-secondary text-white');
                    $(element).attr('data-version-id', data.version);
                    $(element).html(`{{ render_icon("card-text") }}`);
                }
            } else if (data.status === 'cancel') {
                window.location.href = data.url;
            }
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(xhr.responseText);
        });
});
