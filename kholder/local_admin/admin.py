from django.contrib import admin
from django.contrib.auth.models import User, Group


admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.site_header = "KHolder Django Panel"
admin.site.site_title = "KHolder Django Panel"
admin.site.index_title = "KHolder Django Panel"
