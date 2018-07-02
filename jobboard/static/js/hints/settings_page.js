$(document).ready(function () {
    let $ul = $('#hints_list');
    if (localStorage.length === 0) {
        $ul.append(
            '<li>No one tutorial passed yet.</li>'
        )
    }
    for (let i = 0; i < localStorage.length; i++) {
        let $li = $('<li></li>');
        let name = localStorage.key(i).replace(/_/g, ' ');
        name = name.substr(0, 1).toUpperCase() + name.substr(1) + ' hints';
        let $checkbox_div = $('<div class="uk-margin uk-grid-small uk-child-width-auto uk-grid">' +
            '<label><input name="' + localStorage.key(i) + '" class="uk-checkbox hint" type="checkbox"> ' + name + '</label>' +
            '</div>');
        $li.append($checkbox_div);
        $ul.append($li);
        $('input[name=' + localStorage.key(i) + ']')[0].checked = localStorage.getItem(localStorage.key(i)) === '1';
    }
    $('.hint').on('change', function () {
        localStorage.setItem($(this).attr('name'), Number($(this)[0].checked));
    })
});
