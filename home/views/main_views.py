from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from home import models
from home import pdf_utils
from home import utils
from dashboard import forms as dashboard_forms


def index(request):
    game_list = None
    tee_time_list = None
    if request.user.is_authenticated:
        game_list = models.Game.objects.filter(
            status="active", players__in=[request.user.player]
        )
        tee_time_list = models.TeeTime.objects.filter(
            players__in=[request.user.player], is_active=True
        )

    return render(
        request,
        "home/index.html",
        {"game_list": game_list, "tee_time_list": tee_time_list},
    )


def course_list(request):
    course_list = models.GolfCourse.objects.all().order_by("name")
    return render(request, "home/course-list.html", {"course_list": course_list})


def course_detail(request, pk):
    course_data = get_object_or_404(models.GolfCourse, pk=pk)
    return render(request, "home/course-detail.html", {"course_data": course_data})


@login_required
def game_detail(request, pk):
    hole_num = int(request.GET.get("hole", 1))
    game_data = get_object_or_404(models.Game, pk=pk)
    hole_data = None
    next_hole = None
    prev_hole = None
    hole_scores = []
    available_players = []
    player_scores = {}

    if game_data.status == "setup":
        available_players = utils.get_players_for_game(request.user, game_data)

        game_links = models.PlayerGameLink.objects.filter(
            player__in=game_data.players.all(), game=game_data
        )
        for game_link in game_links:
            if game_link.player.name not in player_scores.keys():
                player_scores[game_link.player.name] = {
                    "id": game_link.player.id,
                    "score": 0,
                }

    if game_data.status in ["active", "completed"]:
        hole_data = models.Hole.objects.filter(
            course=game_data.course, order=hole_num
        ).first()
        game_links = models.PlayerGameLink.objects.filter(
            player__in=game_data.players.all(), game=game_data
        )
        next_hole = models.Hole.objects.filter(
            course=game_data.course, order=hole_num + 1
        ).first()
        prev_hole = models.Hole.objects.filter(
            course=game_data.course, order=hole_num - 1
        ).first()

        for game_link in game_links:
            hole_score = models.HoleScore.objects.filter(
                hole=hole_data, game=game_link
            ).first()
            hole_scores.append(
                {
                    "player": game_link.player.name,
                    "hole_score_id": hole_score.id,
                    "score": hole_score.score,
                }
            )
            hole_score_list = models.HoleScore.objects.filter(game=game_link)
            for hole_score_item in hole_score_list:
                if game_link.player.name not in player_scores.keys():
                    player_scores[game_link.player.name] = {
                        "id": game_link.player.id,
                        "score": 0,
                    }
                player_scores[game_link.player.name]["score"] += hole_score_item.score

    return render(
        request,
        "home/game-detail.html",
        {
            "game_data": game_data,
            "hole_scores": hole_scores,
            "current_hole": hole_data,
            "next_hole": next_hole,
            "prev_hole": prev_hole,
            "available_players": available_players,
            "player_scores": player_scores,
            "hole_list": models.Hole.objects.filter(course=game_data.course),
        },
    )


@login_required
def tee_time_detail(request, pk):
    tee_time_data = get_object_or_404(models.TeeTime, pk=pk)
    potential_player_list = models.Player.objects.all().exclude(
        teetime__in=[tee_time_data.id]
    )
    return render(
        request,
        "home/tee-time-detail.html",
        {
            "tee_time_data": tee_time_data,
            "potential_player_list": potential_player_list,
        },
    )


@login_required
def create_tee_time(request):
    if request.method == "POST":
        form = dashboard_forms.TeeTimeForm(request.POST)
        if form.is_valid():
            item = form.save()
            item.players.add(request.user.player)
            return redirect("home:tee-time-detail", item.id)
    else:
        form = dashboard_forms.TeeTimeForm()
    return render(request, "home/create-tee-time.html", {"form": form})


@login_required
def view_my_games(request):
    game_list = models.Game.objects.filter(players__in=[request.user.player])
    return render(request, "home/view-my-games.html", {"game_list": game_list})


@login_required
def my_profile(request):
    game_count = models.Game.objects.filter(players__in=[request.user.player]).count()
    return render(request, "home/profile.html", {"game_count": game_count})


@login_required
def download_scorecard(request, game_pk):
    game_data = get_object_or_404(models.Game, pk=game_pk)
    pdf_data = pdf_utils.generate_scorecard(game_data)
    response = HttpResponse(pdf_data.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=scorecard.pdf'
    return response


@login_required
def player_list(request):
    player_list = models.Player.objects.all()
    return render(request, "home/player-list.html", {"player_list": player_list})


@login_required
def location_test(request):
    return render(request, "home/location-test.html", {})
