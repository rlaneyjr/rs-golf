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
def ajax_record_score_for_hole(request):
    data = json.loads(request.body)
    hole_id = data["hole_score_id"]
    hole_val = int(data["hole_score"])
    if hole_val == 0:
        return HttpResponseBadRequest("Missing score for hole")
    hole_score = models.HoleScore.objects.filter(pk=hole_id).first()
    hole_score.score_hole(hole_val)
    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/no-permission/",
    redirect_field_name=None
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
        player_mem = models.PlayerMembership.objects.create(game=game_data, player=player_data)
        player_mem.skins = data.get("skins", False)
        player_mem.save()
    elif data["action"] == "remove-player":
        game_data.players.remove(player_data)
    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/no-permission/",
    redirect_field_name=None
)
def ajax_manage_game(request):
    data = json.loads(request.body)
    game_id = data["game_id"]
    game_data = models.Game.objects.filter(pk=game_id).first()
    if game_data is None:
        return HttpResponseBadRequest(f"Cannot find game with id: {game_id}")
    if data["action"] == "start-game":
        game_data.start(
            holes_to_play=data.get("holes_to_play"),
            game_type=data.get("game_type"),
            buy_in=data.get("buy_in"),
            skin_cost=data.get("skin_cost"),
            use_teams=data.get("use_teams"),
            payout_positions=data.get("payout_positions"),
        )
        messages.add_message(request, messages.INFO, "Game Started.")
        return JsonResponse({"status": "success"})
    elif data["action"] == "reset-game":
        game_data.reset()
        messages.add_message(request, messages.INFO, "Game Reset.")
        return JsonResponse({"status": "success"})
    elif data["action"] == "delete-game":
        utils.clean_game(game_data)
        game_data.delete()
        messages.add_message(request, messages.INFO, "Game Deleted.")
        return JsonResponse({"status": "success"})
    return HttpResponseBadRequest("Unknown Action")


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/no-permission/",
    redirect_field_name=None
)
def ajax_edit_hole_score(request):
    data = json.loads(request.body)
    if not all([data["score_id"], data["score"]]):
        return HttpResponseBadRequest("Missing Data")
    score_id = data["score_id"]
    score = data["score"]
    score_data = models.HoleScore.objects.filter(pk=score_id).first()
    if not score_data:
        return JsonResponse({"status": "failed", "message": f"Unable to find hole id: {score_id}"})
    score_data.score = score
    score_data.save()
    return JsonResponse({"status": "success"})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/no-permission/",
    redirect_field_name=None
)
def ajax_manage_tee_time(request):
    data = json.loads(request.body)
    action = data["action"]
    if action == "add-player":
        tee_time_id = data["tee_time_id"]
        player_id = data["player_id"]
        skins = data.get("skins", None)
        tee_time = models.TeeTime.objects.filter(pk=tee_time_id).first()
        player_data = models.Player.objects.filter(pk=player_id).first()
        if tee_time is None or player_data is None:
            return JsonResponse({"status": "failed"})
        if skins != None:
            player_mem = models.PlayerMembership.objects.filter(game=game_data, player=player_data).first()
            player_mem.skins = skins
            player_mem.save()
        tee_time.players.add(player_data)
        return JsonResponse({"status": "success"})
    elif action == "start-game":
        tee_time_id = data.get("tee_time_id")
        if not tee_time_id:
            return JsonResponse({"status": "failed"})
        tee_time = models.TeeTime.objects.filter(pk=tee_time_id).first()
        if not tee_time:
            return JsonResponse({"status": "failed"})
        new_game = models.Game.objects.create(
            game_type=data.get("game_type"),
            date_played=tee_time.tee_time,
            course=tee_time.course,
            holes_played=tee_time.holes_to_play,
            which_holes=tee_time.which_holes,
            buy_in=data.get("buy_in"),
            skin_cost=data.get("skin_cost"),
            use_teams=data.get("use_teams"),
            payout_positions=data.get("payout_positions"),
        )
        # add players from tee time to game
        for player in tee_time.players.all():
            new_game.players.add(player)
        new_game.save()
        tee_time.is_active = False
        tee_time.save()
        new_game.start()
        messages.add_message(request, messages.INFO, "Game Started.")
        return JsonResponse({
            "status": "success",
            "game_url": settings.BASE_URL + reverse("dashboard:game_detail", args=[new_game.id])}
        )
    return JsonResponse({"status": "failed", "message": "Unknown Action"})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/no-permission/",
    redirect_field_name=None
)
def ajax_delete_hole_score(request):
    data = json.loads(request.body)
    score_id = data["score_id"]
    score_data = models.HoleScore.objects.filter(pk=score_id).first()
    if score_data:
        score_data.reset_score()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Unable to find hole score"})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/no-permission/",
    redirect_field_name=None
)
def ajax_delete_tee(request):
    data = json.loads(request.body)
    tee_id = data["tee_id"]
    tee_data = models.Tee.objects.filter(pk=tee_id).first()
    if tee_data:
        tee_data.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Unable to find tee"})
