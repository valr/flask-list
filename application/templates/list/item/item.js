
var csrf_token = "{{ csrf_token() }}";

$.ajaxSetup({
    beforeSend: function(xhr, settings){
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain){
            xhr.setRequestHeader('X-CSRFToken', csrf_token);
        }
    }
});

$(document).on('click', '.item-checked', function(){
    element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.item_uncheck") }}',
        data: JSON.stringify({
            list_id: '{{ list.list_id }}',
            item_id: $(element).attr('id').replace('item', '')
        }),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json'
    })
    .always(function(){
        $(element).removeClass('item-checked btn-success text-white')
    })
    .done(function(data, textStatus, xhr){
        $(element).addClass('item-unchecked bg-transparent text-dark');
        $(element).html(`{{ render_icon("square") }}`);
    })
    .fail(function(xhr, textStatus, errorThrown){
        $(element).addClass('item-error btn-danger text-white');
        $(element).html(`{{ render_icon("arrow-repeat") }}`);
        console.log(xhr.responseText)
    });

    return false;
});

$(document).on('click', '.item-unchecked', function(){
    element = $(this);

    $.ajax({
        type: 'POST',
        url: '{{ url_for("list.item_check") }}',
        data: JSON.stringify({
            list_id: '{{ list.list_id }}',
            item_id: $(element).attr('id').replace('item', '')
        }),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json'
    })
    .always(function(){
        $(element).removeClass('item-unchecked bg-transparent text-dark')
    })
    .done(function(data, textStatus, xhr){
        $(element).addClass('item-checked btn-success text-white');
        $(element).html(`{{ render_icon("check-square") }}`);
    })
    .fail(function(xhr, textStatus, errorThrown){
        $(element).addClass('item-error btn-danger text-white');
        $(element).html(`{{ render_icon("arrow-repeat") }}`);
        console.log(xhr.responseText)
    });

    return false;
});

$(document).on('click', '.item-error', function(){
    element = $(this);

    $.getJSON('{{ url_for("list.item_get") }}',{
        list_id: '{{ list.list_id }}',
        item_id: $(element).attr('id').replace('item', '')
    })
    .done(function(data, textStatus, xhr){
        if (data.status === 'checked') {
            $(element).removeClass('item-error btn-danger text-white')
            $(element).addClass('item-checked btn-success text-white');
            $(element).html(`{{ render_icon("check-square") }}`);
        } else if (data.status === 'unchecked') {
            $(element).removeClass('item-error btn-danger text-white')
            $(element).addClass('item-unchecked bg-transparent text-dark');
            $(element).html(`{{ render_icon("square") }}`);
        } else {
            console.log(data.status)                    
        }
    })
    .fail(function(xhr, textStatus, errorThrown){
        console.log(xhr.responseText)
    });

    return false;
});
