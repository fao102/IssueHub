from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AssignableUsersView, CategoryViewSet, TicketDashboardView, TicketViewSet

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    # These two must stay ahead of the router include below - the router's
    # detail route pattern (tickets/<pk>/) would otherwise swallow
    # "dashboard"/"assignable-users" as an invalid pk.
    path("tickets/dashboard/", TicketDashboardView.as_view(), name="ticket-dashboard"),
    path("tickets/assignable-users/", AssignableUsersView.as_view(), name="ticket-assignable-users"),
    path("", include(router.urls)),
]
