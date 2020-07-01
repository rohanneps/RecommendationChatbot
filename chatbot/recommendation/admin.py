from django.contrib import admin
from .models import Process

# Register your models here.
class ProcessAdmin(admin.ModelAdmin):
	save_as = True
	list_per_page = 20
	list_filter = ['user','start_date','status']
	list_display = ['id','user','start_date','search_query','search_image','status']
	search_fields = ['id','user','start_date','search_query','search_image','status']
	readonly_fields = ['start_date']

	fieldsets=[
				('Basic Info',{'fields':['user','start_date','search_query','search_image']}),
				('Process Details', {'fields': ('output_file','failed_log')}),
				('Active Status', {'fields': ('status',)})
				]	
admin.site.register(Process, ProcessAdmin)
