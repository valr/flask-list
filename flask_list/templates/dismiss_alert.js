$(function () {
    debounce(
        "dismiss alert",
        function () {
            $(".alert-dismissible.alert-primary").alert("close");
        },
        3000,
        null
    );
});
