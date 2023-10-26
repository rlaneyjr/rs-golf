from django.shortcuts import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from home import models as home_models
from dashboard import utils
import json


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_manage_players_for_game(request):
    data = json.loads(request.body)
    if not all([data["playerId"], data["game"], data["action"]]):
        return HttpResponseBadRequest("Missing Data")
    game_data = home_models.Game.objects.filter(pk=data["game"]).first()
    player_data = home_models.Player.objects.filter(pk=data["playerId"]).first()
    if not all([game_data, player_data]):
        return HttpResponseBadRequest("Unable to find either game or player")

    if data["action"] == "add-player":
        if player_data in game_data.players.all():
            return HttpResponseBadRequest("Player already part of game")
        game_data.players.add(player_data)
    elif data["action"] == "remove-player":
        game_data.players.remove(player_data)
    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_manage_game(request):
    data = json.loads(request.body)
    game_id = data["gameId"]
    game_data = home_models.Game.objects.filter(pk=game_id).first()
    if game_data is None:
        return HttpResponseBadRequest("Cannot find game with that id")
    if data["action"] == "delete-game":
        game_data.delete()
        messages.add_message(request, messages.INFO, "Game Deleted.")
        return JsonResponse({"status": "success"})
    elif data["action"] == "start-game":
        game_data.status = "active"
        game_data.save()

        hole_list = home_models.Hole.objects.filter(course=game_data.course)
        for hole in hole_list:
            for player in game_data.players.all():
                game_link = home_models.PlayerGameLink.objects.filter(
                    player=player, game=game_data
                ).first()
                hole_score = home_models.HoleScore(hole=hole, game=game_link)
                hole_score.save()
        messages.add_message(request, messages.INFO, "Game Started.")
        return JsonResponse({"status": "success"})
    return HttpResponseBadRequest("Unknown Action")


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_record_score_for_hole(request):
    data = json.loads(request.body)

    hole_score_id = data["hole_score_id"]
    hole_score_val = data["hole_score"]

    hole_score = home_models.HoleScore.objects.filter(pk=hole_score_id).first()

    hole_score.score = hole_score_val
    hole_score.save()

    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def save_par_to_hole(request):
    data = json.loads(request.body)
    hole_par = data["hole_par"]
    hole_id = data["hole_id"]
    hole_data = home_models.Hole.objects.filter(pk=hole_id).first()

    # be sure we have a hole to deal with
    if hole_data is None:
        return JsonResponse(
            {"status": "failed", "message": f"Unable to find hole with ID: {hole_id}"}
        )

    # be sure our par is a number
    try:
        hole_par = int(hole_par)
    except ValueError:
        return JsonResponse(
            {"status": "failed", "message": "Par value does not appear to be a number"}
        )

    hole_data.par = hole_par
    hole_data.save()

    messages.add_message(request, messages.INFO, "Tee Created.")

    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_manage_tee_time(request):
    data = json.loads(request.body)
    action = data["action"]

    if action == "add-player":
        tee_time_id = data["tee_time_id"]
        player_id = data["player_id"]
        tee_time = home_models.TeeTime.objects.filter(pk=tee_time_id).first()
        player_data = home_models.Player.objects.filter(pk=player_id).first()
        if tee_time is None or player_data is None:
            return JsonResponse({"status": "failed"})
        tee_time.players.add(player_data)
        return JsonResponse({"status": "success"})
    elif action == "start-game":
        tee_time_id = data.get("tee_time_id", None)
        if tee_time_id is None:
            return JsonResponse({"status": "failed"})
        tee_time = home_models.TeeTime.objects.filter(pk=tee_time_id).first()
        if tee_time is None:
            return JsonResponse({"status": "failed"})

        new_game = home_models.Game.objects.create(
            date_played=tee_time.tee_time,
            course=tee_time.course,
            holes_played=tee_time.holes_to_play,
        )

        # add players from tee time to game
        for player in tee_time.players.all():
            new_game.players.add(player)

        tee_time.is_active = False
        tee_time.save()

        return JsonResponse({
            "status": "success",
            "game_url": settings.BASE_URL + reverse("dashboard:game-detail", args=[new_game.id])}
        )
    return JsonResponse({"status": "failed", "message": "Unknown Action"})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_delete_hole_score(request):
    data = json.loads(request.body)
    score_id = data["score_id"]

    score_data = home_models.HoleScore.objects.filter(pk=score_id).first()
    if score_data:
        score_data.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Unable to find hole score"})
