from vdi.models import Instance
from opus.lib import log
log = log.get_logger('vdi')

from django.conf import settings
from django.db.models.query import QuerySet

from opus.lib.prov import DRIVERS
Driver = DRIVERS[settings.PROV_DRIVER]
driver = Driver(settings.PROV_USERNAME,
                settings.PROV_PASSWORD,
                settings.PROV_URI)

def create_instance(image_id):
    """Creates a given the instance.

    image_id should be a string identifier of the image to be instantiated.
    Returns the instance id of the newly created instance.

    """
    image = driver.instance_create(image_id)
    return image.id

def terminate_instances(instances):
    """Turns off the list of instances given.

    instances should be an iterable of vdi.models.Instance objects, for
    example, a django queryset.  The number of instances that were successfully
    terminated is returned.

    """
    num = 0
    for instance in instances:
        prov_instance = driver.instance(instance.instanceId)
        if prov_instance.stop():
            dbitem = Instance.objects.filter(instanceId=instance.instanceId)[0]
            log.debug('The node has been deleted.  I will now move %s into a deleted state' % dbitem.instanceId)
            dbitem.state = 5
            dbitem.save()
            num += 1
        else:
            log.warning('Could not shut down instance "%s"' % instance.instanceId)
    return num

def get_instances(instances):
    """Return instance objects baised on database model.

    instances should be an iterable of vdi.models.Instance objects, for
    example, a django queryset.

    """
    id_list = []
    for instance in instances:
        id_list.append(instance.instanceId)
    all_instances = driver.instances()
    return filter(lambda x: x.id in id_list, all_instances)
