from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.utils import timezone
from dashboard import forms
from dashboard import models
from dashboard import pdf_utils
from dashboard import utils


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
        "dashboard/index.html",
        {"game_list": game_list, "tee_time_list": tee_time_list},
    )


def no_permission(request):
    return render(request, "dashboard/no-permission.html", {})


@login_required
def view_my_games(request):
    game_list = models.Game.objects.filter(players__in=[request.user.player])
    return render(request, "dashboard/view-my-games.html", {"game_list": game_list})


@login_required
def my_profile(request):
    player_data = models.Player.objects.filter(user_account=request.user).first()
    game_count = models.Game.objects.filter(players__in=[request.user.player]).count()
    return render(
        request,
        "dashboard/profile.html",
        {
            "player_data": player_data,
            "game_count": game_count,
        },
    )


@login_required
def download_scorecard(request, game_pk):
    game_data = get_object_or_404(models.Game, pk=game_pk)
    pdf_data = pdf_utils.generate_scorecard(game_data)
    response = HttpResponse(pdf_data.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=scorecard.pdf'
    return response


@login_required
def location_test(request):
    return render(request, "dashboard/location-test.html", {})


@login_required
def course_list(request):
    course_list = models.GolfCourse.objects.all()
    return render(request, "dashboard/courses.html", {"course_list": course_list})


@login_required
def game_list(request):
    game_list = models.Game.objects.all()
    return render(request, "dashboard/game-list.html", {"game_list": game_list})


@login_required
def player_list(request):
    player_list = models.Player.objects.all()
    return render(request, "dashboard/players.html", {"player_list": player_list})


@login_required
def course_detail(request, pk):
    course_data = get_object_or_404(models.GolfCourse, pk=pk)
    course_location = None
    hole_list = models.Hole.objects.filter(course=course_data).order_by("order")
    if all([course_data.city, course_data.state, course_data.zip_code]):
        course_location = (
            f"{course_data.city}, {course_data.state}, {course_data.zip_code}"
        )
    return render(
        request,
        "dashboard/course-detail.html",
        {
            "course_data": course_data,
            "course_location": course_location,
            "hole_list": hole_list,
        },
    )


@login_required
def hole_detail(request, pk):
    hole_data = get_object_or_404(models.Hole, pk=pk)
    tee_list = models.Tee.objects.filter(hole=hole_data)
    course_data = hole_data.course
    form = forms.HoleForm(instance=hole_data)
    return render(
        request,
        "dashboard/hole-detail.html",
        {
            "hole_data": hole_data,
            "course_data": course_data,
            "tee_list": tee_list,
            "form": form,
        },
    )


@login_required
def game_detail(request, pk):
    team_list = False
    game_data = get_object_or_404(models.Game, pk=pk)
    current_player_count = game_data.players.count()
    current_players = utils.get_current_players_for_game(game_data)
    player_list = utils.get_players_not_in_game(game_data)
    hole_list = utils.get_hole_list_for_game(game_data)
    hole_data = utils.get_hole_data_for_game(game_data)
    if game_data.use_teams:
        team_list = utils.get_team_list_for_game(game_data)
    return render(
        request,
        "dashboard/game-detail.html",
        {
            "user_is_admin": utils.is_admin(request.user),
            "game_data": game_data,
            "team_list": team_list,
            "player_list": player_list,
            "current_player_count": current_player_count,
            "current_players": current_players,
            "hole_data": hole_data,
            "hole_list": hole_list,
        },
    )


@login_required
def game_score(request, pk):
    game_data = get_object_or_404(models.Game, pk=pk)
    game_data.stop()
    return render(
        request,
        "dashboard/game-score.html",
        {
            "game_data": game_data,
        },
    )


@login_required
def game_score_detail(request, pk):
    game_data = get_object_or_404(models.Game, pk=pk)
    if game_data.status != "completed":
        current_scores = []
        filter_scores = request.GET.get("filter_scores", "false")
        for player in game_data.players.all():
            player_game_link = models.PlayerMembership.objects.filter(
                game=game_data, player=player
            ).first()
            if filter_scores == "true":
                hole_score_list = models.HoleScore.objects.filter(player=player_game_link, strokes__gt=0)
            else:
                hole_score_list = models.HoleScore.objects.filter(player=player_game_link)
            current_scores.extend(hole_score_list)
        return render(
            request,
            "dashboard/game-score-detail.html",
            {
                "game_data": game_data,
                "current_scores": current_scores,
                "filter_scores": filter_scores,
            },
        )
    else:
        return render(
            request,
            "dashboard/game-score-detail.html",
            {
                "game_data": game_data,
                "current_scores": False,
            },
        )


@login_required
def player_detail(request, pk):
    player_data = get_object_or_404(models.Player, pk=pk)
    return render(request, "dashboard/player-detail.html", {"player_data": player_data})


@login_required
def tee_time_list(request):
    tee_times = models.TeeTime.objects.all()
    return render(request, "dashboard/tee-time-list.html", {"tee_time_list": tee_times})


@login_required
def create_tee_time(request):
    if request.method == "POST":
        form = forms.TeeTimeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard:tee_times")
    else:
        form = forms.TeeTimeForm()
    return render(request, "dashboard/create-tee-time.html", {"form": form})


@login_required
def tee_time_detail(request, pk):
    teetime_data = get_object_or_404(models.TeeTime, pk=pk)
    potential_player_list = models.Player.objects.all().exclude(teetime__in=[teetime_data.id])
    return render(
        request,
        "dashboard/tee-time-detail.html",
        {"teetime_data": teetime_data, "potential_player_list": potential_player_list}
    )


@login_required
def hole_score_detail(request, pk):
    hole_score_data = get_object_or_404(models.HoleScore, pk=pk)
    return render(
        request,
        "dashboard/hole-score-detail.html",
        {"hole_score_data": hole_score_data},
    )


##############################
# Admin permissions required #
##############################
@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def create_course(request):
    if request.method == "POST":
        form = forms.GolfCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            utils.create_holes_for_course(course)
            messages.add_message(request, messages.INFO, "Course Created.")
            return redirect("dashboard:courses")
    form = forms.GolfCourseForm()
    return render(request, "dashboard/create-course.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def edit_course(request, pk):
    course_data = get_object_or_404(models.GolfCourse, pk=pk)
    if request.method == "POST":
        form = forms.EditGolfCourseForm(request.POST, request.FILES, instance=course_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Course updated.")
            return redirect("dashboard:course_detail", pk)
    form = forms.EditGolfCourseForm(instance=course_data)
    return render(request, "dashboard/edit-course.html",
                  {"form": form, "course_data": course_data})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def edit_hole(request, pk):
    hole_data = get_object_or_404(models.Hole, pk=pk)
    if request.method == "POST":
        form = forms.EditHoleForm(request.POST, instance=hole_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Hole updated.")
            return redirect("dashboard:hole_detail", pk)
    form = forms.EditHoleForm(instance=hole_data)
    return render(request, "dashboard/edit-hole.html",
                  {"form": form, "hole_data": hole_data})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def create_tee(request, hole_pk):
    hole_data = get_object_or_404(models.Hole, pk=hole_pk)
    if request.method == "POST":
        form = forms.TeeForm(request.POST)
        if form.is_valid():
            tee = form.save(commit=False)
            tee.hole = hole_data
            tee.save()
            messages.add_message(request, messages.INFO, "Tee Created.")
            return redirect("dashboard:hole_detail", hole_pk)
    form = forms.TeeForm()
    return render(
        request,
        "dashboard/create-tee.html",
        {"form": form, "hole_data": hole_data},
    )


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def create_game(request):
    if request.method == "POST":
        form = forms.GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.date_played = timezone.now()
            game.save()
            return redirect("dashboard:game_detail", game.id)
    form = forms.GameForm()
    return render(request, "dashboard/create-game.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def edit_game(request, pk):
    game_data = get_object_or_404(models.Game, pk=pk)
    if request.method == "POST":
        form = forms.EditGameForm(request.POST, instance=game_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Game Saved.")
            return redirect("dashboard:game_detail", pk)
    else:
        form = forms.EditGameForm(instance=game_data)
    return render(request, "dashboard/edit-game.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def create_player(request):
    if request.method == "POST":
        form = forms.PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.added_by = request.user
            item.save()
            messages.add_message(request, messages.INFO, "Player Created.")
            return redirect("dashboard:players")
    else:
        form = forms.PlayerForm()
    return render(request, "dashboard/create-player.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def edit_player(request, pk):
    player_data = get_object_or_404(models.Player, pk=pk)
    if request.method == "POST":
        form = forms.EditPlayerForm(request.POST, request.FILES, instance=player_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Player Saved.")
            return redirect("dashboard:player_detail", pk)
    else:
        form = forms.EditPlayerForm(instance=player_data)
    return render(request, "dashboard/edit-player.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def create_hole(request, pk):
    course_data = get_object_or_404(models.GolfCourse, pk=pk)
    if request.method == "POST":
        form = forms.HoleForm(request.POST)
        if form.is_valid():
            hole = form.save(commit=False)
            hole.course = course_data
            hole.save()
            messages.add_message(request, messages.INFO, "Hole Created.")
            return redirect("dashboard:course_detail", pk)
    else:
        form = forms.HoleForm()
    return render(
        request,
        "dashboard/create-hole.html",
        {"form": form, "course_data": course_data},
    )


@login_required
@user_passes_test(
    utils.is_admin,
    login_url="/dashboard/no-permission/",
    redirect_field_name=None
)
def edit_hole_score(request, pk):
    hole_score_data = get_object_or_404(models.HoleScore, pk=pk)
    if request.method == "POST":
        form = forms.EditHoleScoreForm(request.POST, instance=hole_score_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Hole score updated.")
            return redirect("dashboard:hole_score_detail", pk)
    form = forms.EditHoleScoreForm(instance=hole_score_data)
    return render(request, "dashboard/edit-hole-score.html",
                  {"form": form, "hole_score_data": hole_score_data})
