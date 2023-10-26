from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(GolfCourse)
admin.site.register(Hole)
admin.site.register(Tee)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(PlayerGameLink)
admin.site.register(HoleScore)
admin.site.register(TeeTime)
