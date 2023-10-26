from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("no-permission/", views.no_permission, name="no_permission"),
    path("courses/", views.course_list, name="courses"),
    path("courses/add/", views.create_course, name="create_course"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("courses/<int:pk>/edit/", views.edit_course, name="edit_course"),
    path("holes/<int:pk>/", views.hole_detail, name="hole_detail"),
    path("tees/<int:hole_pk>/", views.create_tee, name="create_tee"),
    path("games/", views.game_list, name="games"),
    path("games/<int:pk>/", views.game_detail, name="game_detail"),
    path("games/add/", views.create_game, name="create_game"),
    path("players/", views.player_list, name="players"),
    path("players/<int:pk>/", views.player_detail, name="player_detail"),
    path("players/add/", views.create_player, name="create_player"),
    path("players/<int:pk>/edit/", views.edit_player, name="edit_player"),
    path("tee-times/", views.tee_time_list, name="tee_times"),
    path("tee-times/add/", views.create_tee_time, name="create_tee_time"),
    path("tee-times/<int:pk>/", views.tee_time_detail, name="tee_time_detail"),
    # ajax
    path(
        "ajax/add-player-to-game/",
        views.ajax_manage_players_for_game,
        name="ajax_manage_players_for_game",
    ),
    path("ajax/manage-game/", views.ajax_manage_game, name="ajax_manage_game"),
    path(
        "ajax/record-score-for-hole/",
        views.ajax_record_score_for_hole,
        name="ajax_record_score_for_hole",
    ),
    path(
        "ajax/save-par-to-hole/", views.save_par_to_hole, name="ajax-save-par-to-hole"
    ),
    path("ajax/manage-tee-time/", views.ajax_manage_tee_time, name="ajax-manage-tee-time"),
    path("ajax/delete-hole-score/", views.ajax_delete_hole_score, name="ajax-delete-hole-score"),
]
