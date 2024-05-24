""" from django.contrib import admin
from .models import UserProfile, chatMessages
from .models import Room

admin.site.register(UserProfile)
admin.site.register(chatMessages)

admin.site.register(Room)
 """


from django.contrib import admin
from .models import Room
from .models import UserProfile, chatMessages

admin.site.register(UserProfile)
admin.site.register(chatMessages)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

