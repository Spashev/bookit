from django.contrib import admin
from faq.models import Faq, HelpCenter

admin.site.register(Faq)


@admin.register(HelpCenter)
class HelpCenterAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone_number', 'text', 'is_approved')
    list_display_links = ('id', 'email', 'phone_number', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('id', 'email', 'phone_number')
