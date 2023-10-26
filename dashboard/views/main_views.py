from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from home import models as home_models
from home import utils as home_utils
from dashboard import forms
from dashboard import utils


def no_permission(request):
    return render(request, "dashboard/no-permission.html", {})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def index(request):
    return render(request, "dashboard/index.html", {})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def course_list(request):
    course_list = home_models.GolfCourse.objects.all()
    return render(request, "dashboard/courses.html", {"course_list": course_list})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def create_course(request):
    if request.method == "POST":
        form = forms.GolfCourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            utils.create_holes_for_course(course)
            messages.add_message(request, messages.INFO, "Course Created.")
            return redirect("dashboard:courses")
    else:
        form = forms.GolfCourseForm()
    return render(request, "dashboard/create-course.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def edit_course(request, pk):
    course_data = get_object_or_404(home_models.GolfCourse, pk=pk)
    if request.method == "POST":
        form = forms.EditGolfCourseForm(request.POST, instance=course_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Course updated.")
            return redirect("dashboard:course_detail", pk)
    else:
        form = forms.EditGolfCourseForm(instance=course_data)
    return render(
        request,
        "dashboard/edit-course.html",
        {"form": form, "course_data": course_data},
    )


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def course_detail(request, pk):
    course_data = get_object_or_404(home_models.GolfCourse, pk=pk)
    course_location = None
    hole_list = home_models.Hole.objects.filter(course=course_data).order_by("order")
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
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def hole_detail(request, pk):
    hole_data = get_object_or_404(home_models.Hole, pk=pk)
    tee_list = home_models.Tee.objects.filter(hole=hole_data)
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
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def create_tee(request, hole_pk):
    hole_data = get_object_or_404(home_models.Hole, pk=hole_pk)
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
        request, "dashboard/create-tee.html", {"form": form, "hole_data": hole_data}
    )


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def game_list(request):
    game_list = home_models.Game.objects.all()
    return render(request, "dashboard/game-list.html", {"game_list": game_list})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def game_detail(request, pk):
    game_data = get_object_or_404(home_models.Game, pk=pk)
    current_player_count = game_data.players.count()
    player_list = home_utils.get_players_for_game(request.user, game_data)
    hole_data = {}
    hole_list = []
    all_scores = []

    filter_scores = request.GET.get("filter_scores", "false")

    for player in game_data.players.all():
        hole_data[player.id] = {
            "player_name": player.name,
            "hole_list": [],
            "total_score": 0,
            "par": 0,
        }
        player_game_link = home_models.PlayerGameLink.objects.filter(
            game=game_data, player=player
        ).first()
        hole_score_list = home_models.HoleScore.objects.filter(game=player_game_link)

        if filter_scores == "true":
            filtered_scores = home_models.HoleScore.objects.filter(game=player_game_link, score__gt=0)
            all_scores.extend(filtered_scores)
        else:
            all_scores.extend(hole_score_list)

        for hole_item in hole_score_list:
            hole_data[player.id]["hole_list"].append(
                {
                    "hole_score_id": hole_item.id,
                    "hole_score": hole_item.score,
                    "hole_name": hole_item.hole.name,
                }
            )
            hole_data[player.id]["total_score"] += hole_item.score
            hole_data[player.id]["par"] += hole_item.hole.par

    hole_count = 9
    if game_data.holes_played == "18":
        hole_count = 18
    for hole_num in range(1, hole_count + 1):
        hole_list.append(f"{hole_num}")

    return render(
        request,
        "dashboard/game-detail.html",
        {
            "game_data": game_data,
            "player_list": player_list,
            "current_player_count": current_player_count,
            "hole_data": hole_data,
            "hole_list": hole_list,
            "all_scores": all_scores,
            "filter_scores": filter_scores,
        },
    )


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def player_list(request):
    player_list = home_models.Player.objects.all()
    return render(request, "dashboard/players.html", {"player_list": player_list})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def player_detail(request, pk):
    player_data = get_object_or_404(home_models.Player, pk=pk)
    return render(request, "dashboard/player-detail.html", {"player_data": player_data})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def create_player(request):
    if request.method == "POST":
        form = forms.PlayerForm(request.POST)
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
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def edit_player(request, pk):
    player_data = get_object_or_404(home_models.Player, pk=pk)
    if request.method == "POST":
        form = forms.PlayerForm(request.POST, instance=player_data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Player Saved.")
            return redirect("dashboard:player_detail", pk)
    else:
        form = forms.PlayerForm(instance=player_data)
    return render(request, "dashboard/create-player.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def create_game(request):
    if request.method == "POST":
        form = forms.GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.date_played = timezone.now()
            game.save()
            return redirect("dashboard:game_detail", game.id)
    else:
        form = forms.GameForm()
    return render(request, "dashboard/create-game.html", {"form": form})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def tee_time_list(request):
    tee_times = home_models.TeeTime.objects.all()
    return render(request, "dashboard/tee-time-list.html", {"tee_time_list": tee_times})


@login_required
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
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
@user_passes_test(
    utils.is_admin, login_url="/dashboard/no-permission/", redirect_field_name=None
)
def tee_time_detail(request, pk):
    teetime_data = get_object_or_404(home_models.TeeTime, pk=pk)
    potential_player_list = home_models.Player.objects.all().exclude(teetime__in=[teetime_data.id])
    return render(
        request,
        "dashboard/tee-time-detail.html",
        {"teetime_data": teetime_data, "potential_player_list": potential_player_list}
    )
