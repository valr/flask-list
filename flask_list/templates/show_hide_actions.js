$(function () {
    ShowHideActions();
});

$("#ShowHideActions").click(function () {
    var key = "ShowHideActions@" + window.location.pathname;
    if (window.sessionStorage.getItem(key)) {
        window.sessionStorage.removeItem(key);
    } else {
        window.sessionStorage.setItem(key, "hidden");
    }

    ShowHideActions();
});

function ShowHideActions() {
    var key = "ShowHideActions@" + window.location.pathname;
    if (window.sessionStorage.getItem(key)) {
        $("table th:last-child, table td:last-child").each(function () {
            $(this).addClass("d-none");
        });
    } else {
        $("table th:last-child, table td:last-child").each(function () {
            $(this).removeClass("d-none");
        });
    }
}
