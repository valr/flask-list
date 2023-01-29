$(document).ready(function () {
    $('[data-bs-toggle="tooltip"]').tooltip({
        customClass: "tooltip-info",
        trigger: "click hover",
        title: function () {
            var element = this;

            /* text is ellipsized */
            if (element.scrollWidth > element.clientWidth) {
                return element.innerText;
            } else {
                return "";
            }
        },
    });
});
