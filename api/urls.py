from . import views
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()
router.register("golf-courses", views.GolfCourseViewSet, basename="golf-course")
router.register("games", views.GameViewSet, basename="game")
router.register("players", views.PlayerViewSet, basename="players")
router.register("tee-times", views.TeeTimeViewSet, basename="tee-times")
router.register("tees", views.TeeViewSet, basename="tee")

urlpatterns = router.urls
