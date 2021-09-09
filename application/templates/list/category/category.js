
var csrf_token = "{{ csrf_token() }}";

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrf_token);
        }
    }
});

$(document).on('click', '.category-checked', function() {
    element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.category_switch_selection") }}',
        data: JSON.stringify({
            list_id: '{{ list.list_id }}',
            category_id: $(element).attr('id').replace('category', '')
        }),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json'
    })
        .always(function() {
            $(element).removeClass('category-checked btn-success text-white');
        })
        .done(function(data, textStatus, xhr) {
            $(element).addClass('category-unchecked bg-transparent text-dark');
            $(element).html(`{{ render_icon("square") }}`);
        })
        .fail(function(xhr, textStatus, errorThrown) {
            $(element).addClass('category-error btn-danger text-white');
            $(element).html(`{{ render_icon("arrow-repeat") }}`);
            console.log(xhr.responseText);
        });

    return false;
});

$(document).on('click', '.category-unchecked', function() {
    element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.category_check") }}',
        data: JSON.stringify({
            list_id: '{{ list.list_id }}',
            category_id: $(element).attr('id').replace('category', '')
        }),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json'
    })
        .always(function() {
            $(element).removeClass('category-unchecked bg-transparent text-dark');
        })
        .done(function(data, textStatus, xhr) {
            $(element).addClass('category-checked btn-success text-white');
            $(element).html(`{{ render_icon("check-square") }}`);
        })
        .fail(function(xhr, textStatus, errorThrown) {
            $(element).addClass('category-error btn-danger text-white');
            $(element).html(`{{ render_icon("arrow-repeat") }}`);
            console.log(xhr.responseText);
        });

    return false;
});

$(document).on('click', '.category-error', function() {
    element = $(this);

    $.getJSON('{{ url_for("list.category_get") }}', {
        list_id: '{{ list.list_id }}',
        category_id: $(element).attr('id').replace('category', '')
    })
        .done(function(data, textStatus, xhr) {
            if (data.status === 'checked') {
                $(element).removeClass('category-error btn-danger text-white');
                $(element).addClass('category-checked btn-success text-white');
                $(element).html(`{{ render_icon("check-square") }}`);
            } else if (data.status === 'unchecked') {
                $(element).removeClass('category-error btn-danger text-white');
                $(element).addClass('category-unchecked bg-transparent text-dark');
                $(element).html(`{{ render_icon("square") }}`);
            } else {
                console.log(data.status);
            }
        })
        .fail(function(xhr, textStatus, errorThrown) {
            console.log(xhr.responseText);
        });

    return false;
});
