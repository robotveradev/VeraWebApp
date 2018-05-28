from unittest import mock

from django.test import TestCase
from django.test.utils import override_settings

from google_address.signals import address_post_save
from google_address.models import Address

class PostSaveSignalTestCase(TestCase):
  def setUp(self):
    self.instance = Address(raw="Chicago")
    self.instance.save()

  @mock.patch('google_address.update.update_address', return_value=True)
  @override_settings(GOOGLE_ADDRESS={'API_LANGUAGE': 'en_US', 'ASYNC_CALLS': True})
  def test_async_settings(self, mocked_update_address):
    """Assert configuring ASYNC_CALLS setting makes the post_save signal spawn a thread"""
    thread = address_post_save(Address, self.instance)
    thread.join()
