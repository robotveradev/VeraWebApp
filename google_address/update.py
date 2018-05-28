import threading

from google_address.api import GoogleAddressApi
from google_address.models import Address, AddressComponent


def update_address(instance):
    if instance.raw:
        response = GoogleAddressApi().query(instance.raw)
    elif instance.lat and instance.lng:
        response = GoogleAddressApi().query([str(instance.lat), str(instance.lng)])

    if response and len(response["results"]) > 0:
        result = response["results"][0]
    else:
        return False

    instance.address_components.clear()
    for api_component in result["address_components"]:
        component = AddressComponent.get_or_create_component(api_component)
        instance.address_components.add(component)

    try:
        if result["geometry"]:
            Address.objects.filter(pk=instance.pk).update(lat=result["geometry"]["location"]["lat"],
                                                          lng=result["geometry"]["location"]["lng"])
    except:  # pragma: no cover
        pass

    # Using update to avoid post_save signal
    instance.address_line = instance.get_address()
    Address.objects.filter(pk=instance.pk).update(address_line=instance.address_line,
                                                  city_state=instance.get_city_state())


class UpdateThread(threading.Thread):
    def __init__(self, instance):
        self.instance = instance
        threading.Thread.__init__(self)

    def run(self):
        return update_address(self.instance)
