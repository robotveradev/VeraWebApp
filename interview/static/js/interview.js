$(document).ready(function () {
    $('#calendar').fullCalendar({
        height: 450,
        dayClick: function () {
            alert('a day has been clicked!');
        }
    });
});
