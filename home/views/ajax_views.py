import json
from django.shortcuts import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from home import models
from home import utils


@login_required
def ajax_manage_game(request):
    data = json.loads(request.body)
    game_id = data["game_id"]
    action = data["action"]

    game_data = models.Game.objects.filter(pk=game_id).first()
    if game_data is None:
        return JsonResponse(
            {"status": "failed", "message": f"Unable to find game with ID: {game_id}"}
        )
    elif action == "complete-game":
        game_data.status = "completed"
        game_data.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "message": "Unknown Error"})


@login_required
def ajax_manage_tee_time(request):
    data = json.loads(request.body)
    action = data["action"]

    if action == "add-player":
        tee_time_id = data["tee_time_id"]
        player_id = data["player_id"]
        tee_time = models.TeeTime.objects.filter(pk=tee_time_id).first()
        player_data = models.Player.objects.filter(pk=player_id).first()
        if tee_time is None or player_data is None:
            return JsonResponse(
                {"status": "failed", "message": "Unable to find tee time or player"}
            )
        tee_time.players.add(player_data)
        return JsonResponse({"status": "success"})
    elif action == "start-game":
        tee_time_id = data.get("tee_time_id", None)
        if tee_time_id is None:
            return JsonResponse(
                {"status": "failed", "message": "Unable to find tee time id"}
            )
        tee_time = models.TeeTime.objects.filter(pk=tee_time_id).first()
        if tee_time is None:
            return JsonResponse(
                {"status": "failed", "message": "Unable to find tee time"}
            )

        new_game = models.Game.objects.create(
            date_played=tee_time.tee_time,
            course=tee_time.course,
            holes_played=tee_time.holes_to_play,
        )

        # add players from tee time to game
        for player in tee_time.players.all():
            new_game.players.add(player)

        tee_time.is_active = False
        tee_time.save()

        return JsonResponse(
            {
                "status": "success",
                "game_url": settings.BASE_URL
                + reverse("home:game-detail", args=[new_game.id]),
            }
        )
    return JsonResponse({"status": "failed", "message": "Unknown Action"})
