var debounce = (function () {
    var timer = {};
    return function (id, callback, delay, arg) {
        if (timer[id]) {
            clearTimeout(timer[id]);
        }
        timer[id] = setTimeout(callback, delay, arg);
    };
})();
