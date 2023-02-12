$(function () {
    debounce(
        "dismiss alert",
        function () {
            $(".alert").alert("close");
        },
        3000,
        null
    );
});
