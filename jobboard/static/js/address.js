$(function () {
    setTimeout(function () {
        $('input.address').each(function () {
            let self = $(this);
            let cmps = $('#' + self.attr('name') + '_components');
            let fmtd = $('input[name="' + self.attr('name') + '_formatted"]');
            self.geocomplete({
                details: cmps,
                detailsAttribute: 'data-geo'
            }).change(function () {
                if (self.val() != fmtd.val()) {
                    let cmp_names = [
                        'country',
                    ];

                    for (let ii = 0; ii < cmp_names.length; ++ii) {
                        $('input[name="' + self.attr('name') + '_' + cmp_names[ii] + '"]').val('');
                    }
                }
            });
        });
    }, 0);
    initMap();
});

function initMap() {
    if ($('#map').length > 0) {
        let uluru = {lat: -25.363, lng: 131.044};
        let markers = [];
        let map = new google.maps.Map(document.getElementById('map'), {
            zoom: 12,
            center: uluru
        });
        let infoWindow = new google.maps.InfoWindow({map: map});
        let geocoder = new google.maps.Geocoder();
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                let pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                infoWindow.setPosition(pos);
                infoWindow.setContent('Location found.');
                map.setCenter(pos);
            }, function () {
                handleLocationError(true, infoWindow, map.getCenter());
            });
        } else {
            // Browser doesn't support Geolocation
            handleLocationError(false, infoWindow, map.getCenter());
        }

        map.addListener('click', function (event) {
            addMarker(event.latLng);
        });

        function addMarker(location) {
            clearMarkers();
            let marker = new google.maps.Marker({
                position: location,
                map: map,
            });
            markers.push(marker);
            geocodeLatLng(geocoder, map, infoWindow, location, marker);
        }

        function setMapOnAll(map) {
            for (let i = 0; i < markers.length; i++) {
                markers[i].setMap(map);
            }
        }

        function clearMarkers() {
            setMapOnAll(null);
        }

        function geocodeLatLng(geocoder, map, infowindow, location, marker) {
            geocoder.geocode({'location': location}, function (results, status) {
                if (status === 'OK') {
                    if (results[1]) {
                        infowindow.setContent(results[0].formatted_address);
                        $('#id_address').val(results[0].formatted_address);
                        infowindow.open(map, marker);
                    } else {
                        window.alert('No results found');
                    }
                } else {
                    window.alert('Geocoder failed due to: ' + status);
                }
            });
        }
    }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
}
