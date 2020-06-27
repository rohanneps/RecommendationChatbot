from django.contrib import admin
from .models import Process

# Register your models here.
class ProcessAdmin(admin.ModelAdmin):
	save_as = True
	list_per_page = 20
	list_filter = ['user','start_date','initiated','completed']
	list_display = ['id','user','start_date','search_query','search_image','initiated','completed']
	search_fields = ['id','user','start_date','search_query','search_image','initiated','completed']
	readonly_fields = ['start_date','initiated','completed']

	fieldsets=[
				('Basic Info',{'fields':['user','start_date','search_query','search_image']}),

				('Active Status', {'fields': ('initiated','completed')})
				]	
admin.site.register(Process, ProcessAdmin)
