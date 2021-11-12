from django.contrib import admin

# Register your models here.
from .models import Captain, Queue, Hunter, Key, Bot_Table, AdminId

class Hunter_Inline(admin.StackedInline):
    model = Hunter

class Queue_Inline(admin.StackedInline):
    model = Queue

class AdminId_Inline(admin.StackedInline):
    model = AdminId

class Captain_Admin(admin.ModelAdmin):
    inlines = [
        Hunter_Inline,
    ]

class Hunter_Admin(admin.ModelAdmin):
    inlines = [
        Queue_Inline,
    ]

class Bot_Table_Admin(admin.ModelAdmin):
    inlines = [
        AdminId_Inline
    ]

admin.site.register(Captain, Captain_Admin)
admin.site.register(Hunter, Hunter_Admin)
admin.site.register(Key)
admin.site.register(Bot_Table, Bot_Table_Admin)
admin.site.register(AdminId)
