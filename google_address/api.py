import requests

from google_address import helpers


class GoogleAddressApi:
    url = 'https://maps.googleapis.com/maps/api/geocode/json?{geo_type}={params}'
    geo_type = None
    key = None
    params = None

    def __init__(self):
        # Set key
        self.key = helpers.get_settings().get("API_KEY", None)

        # Set language
        self.language = helpers.get_settings().get("API_LANGUAGE", "en_US")

    def _get_url(self):
        url = self.url

        if self.key:
            url = "{}&key={}".format(url, self.key)

        if self.language:
            url = "{}&language={}".format(url, self.language)

        return url

    def query(self, params):
        if isinstance(params, list):
            self.geo_type = 'latlng'
            self.params = ','.join(params)
        else:
            self.geo_type = 'address'
            self.params = params
        url = self._get_url().format(geo_type=self.geo_type, params=self.params)

        r = requests.get(url)
        data = r.json()
        return data
