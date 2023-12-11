from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import reverse
from django.utils import timezone
from dashboard import models
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
    game_data = models.Game.objects.filter(pk=data["game"]).first()
    player_data = models.Player.objects.filter(pk=data["playerId"]).first()
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
    game_id = data["game_id"]
    game_data = models.Game.objects.filter(pk=game_id).first()
    if game_data is None:
        return HttpResponseBadRequest("Cannot find game with that id")
    if data["action"] == "delete-game":
        utils.delete_teams_for_game(game_data)
        game_data.delete()
        messages.add_message(request, messages.INFO, "Game Deleted.")
        return JsonResponse({"status": "success"})
    elif data["action"] == "start-game":
        holes_to_play = data["holes_to_play"] or None
        game_type = data["game_type"] or None
        game_data.start(holes_to_play=holes_to_play, game_type=game_type)
        hole_list = utils.get_holes_for_game(game=game_data)
        for hole in hole_list:
            for player in game_data.players.all():
                game_link = models.PlayerMembership.objects.filter(
                    player=player, game=game_data
                ).first()
                hole_score = models.HoleScore(hole=hole, player=game_link)
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
    hole_score = models.HoleScore.objects.filter(pk=hole_score_id).first()
    hole_score.score = hole_score_val
    hole_score.save()
    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_edit_hole_score(request):
    data = json.loads(request.body)
    score_id = data["score_id"]
    score = data["score"]
    if not score:
        return JsonResponse({"status": "failed", "message": "Must provide score"})
    score_data = models.HoleScore.objects.filter(pk=score_id).first()
    if not score_data:
        return JsonResponse({"status": "failed", "message": f"Unable to find hole id: {score_id}"})
    score_data.score = score
    score_data.save()
    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def ajax_edit_hole(request):
    data = json.loads(request.body)
    hole_par = data["hole_par"]
    hole_id = data["hole_id"]
    hole_order = data["hole_order"]
    hole_handicap = data["hole_handicap"]
    hole_data = models.Hole.objects.filter(pk=hole_id).first()

    # be sure we have a hole to deal with
    if hole_data is None:
        return JsonResponse(
            {"status": "failed", "message": f"Unable to find hole with ID: {hole_id}"}
        )

    # be sure all is a number
    try:
        hole_par = int(hole_par)
        hole_order = int(hole_order)
        hole_handicap = int(hole_handicap)
    except ValueError:
        return JsonResponse(
            {"status": "failed", "message": "Some value does not appear to be a number"}
        )

    hole_data.par = hole_par
    hole_data.order = hole_order
    hole_data.handicap = hole_handicap
    hole_data.save()

    messages.add_message(request, messages.INFO, "Hole updated.")

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
        tee_time = models.TeeTime.objects.filter(pk=tee_time_id).first()
        player_data = models.Player.objects.filter(pk=player_id).first()
        if tee_time is None or player_data is None:
            return JsonResponse({"status": "failed"})
        tee_time.players.add(player_data)
        return JsonResponse({"status": "success"})
    elif action == "start-game":
        tee_time_id = data.get("tee_time_id", None)
        if tee_time_id is None:
            return JsonResponse({"status": "failed"})
        tee_time = models.TeeTime.objects.filter(pk=tee_time_id).first()
        if tee_time is None:
            return JsonResponse({"status": "failed"})

        new_game = models.Game.objects.create(
            date_played=tee_time.tee_time,
            course=tee_time.course,
            holes_played=tee_time.holes_to_play,
            which_holes=tee_time.which_holes,
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

    score_data = models.HoleScore.objects.filter(pk=score_id).first()
    if score_data:
        score_data.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Unable to find hole score"})
