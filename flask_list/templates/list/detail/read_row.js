$("tbody").on("click", ".item-selection", function () {
    var element = $(this);

    $.ajax({
        type: "POST",
        url: '{{ url_for("item.switch_selection") }}',
        headers: { "X-CSRFToken": "{{ csrf_token() }}" },
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            item_id: $(element).attr("data-item-id"),
            version_id: $(element).attr("data-version-id"),
        }),
        dataType: "json",
    })
        .done(function (data, textStatus, xhr) {
            if (data.status === "ok") {
                if (data.selection === false) {
                    $(element)
                        .removeClass("btn-success text-white")
                        .addClass("bg-transparent text-dark")
                        .attr("data-version-id", data.version)
                        .html(`{{ render_icon("square") }}`);
                } else if (data.selection === true) {
                    $(element)
                        .removeClass("bg-transparent text-dark")
                        .addClass("btn-success text-white")
                        .attr("data-version-id", data.version)
                        .html(`{{ render_icon("check-square") }}`);
                }
            } else if (data.status === "cancel") {
                window.location.href = data.cancel_url;
            }
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                "POST failed on item.switch_selection." +
                    " item_id:" +
                    $(element).attr("data-item-id") +
                    " version_id:" +
                    $(element).attr("data-version-id") +
                    " responseText:" +
                    xhr.responseText
            );
        });
});

$("tbody").on("click input", ".item-number", function (event) {
    var element = $(this);

    if (event.type === "click") {
        if ($(element).hasClass("text-danger")) {
            $(element).removeClass("text-danger");
        } else {
            return true;
        }
    } else {
        $(element).addClass("font-weight-bold").removeClass("text-danger");
    }

    var regex = /^\s*((\+|-)?((\d+(\.\d+)?)|(\.\d+)))?\s*$/;
    var value = $(element).val();

    if (!regex.test(value)) {
        $(element).addClass("text-danger");
        return true;
    }

    var number = $(element).val().trim() ? $(element).val().trim() : "0";

    debounce(
        $(element).attr("data-item-id"),
        function (element) {
            $.ajax({
                type: "POST",
                url: '{{ url_for("item.set_number") }}',
                headers: { "X-CSRFToken": "{{ csrf_token() }}" },
                contentType: "application/json; charset=UTF-8",
                data: JSON.stringify({
                    item_id: $(element).attr("data-item-id"),
                    version_id: $(element).attr("data-version-id"),
                    number: number,
                }),
                dataType: "json",
            })
                .done(function (data, textStatus, xhr) {
                    if (data.status === "ok") {
                        $(element)
                            .removeClass("font-weight-bold")
                            .attr("data-version-id", data.version);
                    } else if (data.status === "cancel") {
                        window.location.href = data.cancel_url;
                    }
                })
                .fail(function (xhr, textStatus, errorThrown) {
                    $(element).addClass("text-danger");
                    console.log(
                        "POST failed on item.set_number." +
                            " item_id:" +
                            $(element).attr("data-item-id") +
                            " version_id:" +
                            $(element).attr("data-version-id") +
                            " number:" +
                            number +
                            " responseText:" +
                            xhr.responseText
                    );
                });
        },
        1000,
        element
    );
});

$("tbody").on("click", ".item-number-plus, .item-number-minus", function (event) {
    var element_button = $(this);
    var element = $(
        ".item-number[data-item-id=" + $(element_button).attr("data-item-id") + "]"
    );

    if ($(element).hasClass("font-weight-bold") || $(element).hasClass("text-danger")) {
        return true;
    }

    var number = $(element).val().trim() ? $(element).val().trim() : "0";
    var to_add = $(element_button).hasClass("item-number-plus") ? "1" : "-1";

    $.ajax({
        type: "POST",
        url: '{{ url_for("item.set_number") }}',
        headers: { "X-CSRFToken": "{{ csrf_token() }}" },
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            item_id: $(element).attr("data-item-id"),
            version_id: $(element).attr("data-version-id"),
            number: number,
            to_add: to_add,
        }),
        dataType: "json",
    })
        .done(function (data, textStatus, xhr) {
            if (data.status === "ok") {
                $(element)
                    .val(data.number !== "0" ? data.number : "")
                    .attr("data-version-id", data.version);
            } else if (data.status === "cancel") {
                window.location.href = data.cancel_url;
            }
        })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log(
                "POST failed on item.set_number." +
                    " item_id:" +
                    $(element).attr("data-item-id") +
                    " version_id:" +
                    $(element).attr("data-version-id") +
                    " number:" +
                    number +
                    " to_add:" +
                    to_add +
                    " responseText:" +
                    xhr.responseText
            );
        });
});

$("tbody").on("click input", ".item-text", function (event) {
    var element = $(this);

    if (event.type === "click") {
        if ($(element).hasClass("text-danger")) {
            $(element).removeClass("text-danger");
        } else {
            return true;
        }
    } else {
        $(element).addClass("font-weight-bold").removeClass("text-danger");
    }

    debounce(
        $(element).attr("data-item-id"),
        function (element) {
            $.ajax({
                type: "POST",
                url: '{{ url_for("item.set_text") }}',
                headers: { "X-CSRFToken": "{{ csrf_token() }}" },
                contentType: "application/json; charset=UTF-8",
                data: JSON.stringify({
                    item_id: $(element).attr("data-item-id"),
                    version_id: $(element).attr("data-version-id"),
                    text: $(element).val(),
                }),
                dataType: "json",
            })
                .done(function (data, textStatus, xhr) {
                    if (data.status === "ok") {
                        $(element)
                            .removeClass("font-weight-bold")
                            .attr("data-version-id", data.version);
                    } else if (data.status === "cancel") {
                        window.location.href = data.cancel_url;
                    }
                })
                .fail(function (xhr, textStatus, errorThrown) {
                    $(element).addClass("text-danger");
                    console.log(
                        "POST failed on item.set_text." +
                            " item_id:" +
                            $(element).attr("data-item-id") +
                            " version_id:" +
                            $(element).attr("data-version-id") +
                            " text:" +
                            $(element).val() +
                            " responseText:" +
                            xhr.responseText
                    );
                });
        },
        1000,
        element
    );
});
