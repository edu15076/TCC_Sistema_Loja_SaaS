const $sidebar = $('.sidebar-collapse');

$sidebar.on('shown.bs.collapse', function () {
        localStorage.setItem('togglerState', 'show');
});

$sidebar.on('hidden.bs.collapse', function () {
        localStorage.setItem('togglerState', 'collapse');
});

document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('togglerState') === 'show')
        $sidebar.addClass('show');
    else
        $sidebar.removeClass('show');
});
