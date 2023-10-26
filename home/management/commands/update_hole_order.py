from django.core.management.base import BaseCommand
from home import models


class Command(BaseCommand):
    help = "Updates the order number on holes"

    def handle(self, *args, **options):
        holes_updated = 0
        for hole_obj in models.Hole.objects.all():
            hole_order_num = int(hole_obj.name.split(":")[-1])
            hole_obj.order = hole_order_num
            hole_obj.save()
            holes_updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {holes_updated} holes"))
