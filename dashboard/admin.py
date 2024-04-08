from django.db.models import JSONField
from django.contrib import admin
from django.forms import widgets
from django_json_widget.widgets import JSONEditorWidget
from .models import *

# Customise the Admin title and header.
admin.site.site_title = "Rise and Shine Golf"
admin.site.site_header = "Rise and Shine Golf Admin"

# Register your models here.
admin.site.register(GolfCourse)
admin.site.register(Hole)
admin.site.register(Tee)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(PlayerMembership)
admin.site.register(HoleScore)
admin.site.register(TeeTime)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget}
    }
