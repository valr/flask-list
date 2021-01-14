
$('.collapse').not('.navbar-collapse').on('hidden.bs.collapse', function(){
    window.sessionStorage.setItem(this.id+'@'+window.location.pathname, 'hidden');
})

$('.collapse').not('.navbar-collapse').on('shown.bs.collapse', function(){
    window.sessionStorage.removeItem(this.id+'@'+window.location.pathname);
})

$(function() {
    $('.collapse').not('.navbar-collapse').each(function(){
        if (window.sessionStorage.getItem(this.id+'@'+window.location.pathname) !== null) {
            $(this).collapse()
        }
    });
});
