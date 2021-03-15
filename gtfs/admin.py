from django.contrib import admin

from .models import Agency, Calendar, CalendarDate, Feed, Route, Stop, StopTime, Trip

admin.site.register(Agency)
admin.site.register(Calendar)
admin.site.register(CalendarDate)
admin.site.register(Feed)
admin.site.register(Route)
admin.site.register(Stop)
admin.site.register(StopTime)
admin.site.register(Trip)
