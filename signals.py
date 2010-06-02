from django.db.models import signals
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from opus.lib import log
log = log.getLogger()

signals.pre_save.connect(create_application_permission, sender=Application)
signals.post_delete.connect(delete_application_permission, sender=Application)


def create_application_permission(sender, instance, **kwargs):
    try:
        app = sender.objects.get(pk=instance.id)
        perm = Permission.objects.get(codename='use_%s' % app.name)
        if not instance.name == app.name:
            log.debug("Application being saved - name: " + str(app.name))
            perm.name = 'Use %s' % instance.name
            perm.codename = 'use_%s' % instance.name
            perm.save()
    except ObjectDoesNotExist:
        log.debug("No permission")
        log.debug('Use %s' % instance.name)
        log.debug('vdi.use_%s' % instance.name)
        ct = ContentType.objects.get(model='application')
        perm = Permission.objects.create(name='Use %s' % instance.name, content_type = ct, codename='use_%s' % instance.name)

def delete_application_permission(sender, instance, **kwargs):
    perm = Permission.objects.get(codename='use_%s' % instance.name)
    perm.delete()

