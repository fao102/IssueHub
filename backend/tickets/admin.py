from django.contrib import admin

from .models import Category, Ticket, TicketActivity


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


class TicketActivityInline(admin.TabularInline):
    model = TicketActivity
    extra = 0
    readonly_fields = ["actor", "action", "detail", "created_at"]
    can_delete = False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "priority", "category", "created_by", "assigned_to", "created_at"]
    list_filter = ["status", "priority", "category"]
    search_fields = ["title", "description"]
    inlines = [TicketActivityInline]
