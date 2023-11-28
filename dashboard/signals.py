from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=get_user_model())
def send_email_to_admin(sender, instance, created, **kwargs):
    if created:
        admin_list = []
        if len(settings.ADMINS):
            for admin in settings.ADMINS:
                admin_list.append(admin[1])
            send_mail(
                "User: {} has registered".format(instance.email),
                "A new user has registered",
                settings.DEFAULT_FROM_EMAIL,
                admin_list
            )
