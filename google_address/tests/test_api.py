from django.test import TestCase
from django.test.utils import override_settings

from google_address.api import GoogleAddressApi

class GoogleAddressApiTestCase(TestCase):
  def test_can_request_without_key(self):
    """ Assert it's possible to make requests without setting a key """
    url = GoogleAddressApi()._get_url()
    self.assertTrue("key=" not in url)

  @override_settings(GOOGLE_ADDRESS={'API_KEY': 'test'})
  def test_can_request_with_key(self):
    """ Assert it's possible to make requests setting a key """
    url = GoogleAddressApi()._get_url()
    self.assertTrue("key=test" in url)

