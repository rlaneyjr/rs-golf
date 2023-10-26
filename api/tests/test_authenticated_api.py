import pytest
from django.shortcuts import reverse
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from home import models


@pytest.mark.django_db
def test_can_add_player(normal_user):
    player_endpoint = reverse("api:players-list")
    client = APIClient()
    client.force_authenticate(user=normal_user)

    data = {"name": "Test Player"}

    res = client.post(player_endpoint, data)
    assert res.status_code == status.HTTP_200_OK
    assert res.data["name"] == data["name"]


@pytest.mark.django_db
def test_cant_see_other_users_players(normal_user, second_user):
    player_endpoint = reverse("api:players-list")
    client = APIClient()
    client.force_authenticate(user=normal_user)

    player_name = "First Player User"

    models.Player.objects.create(name="Second User Player", added_by=second_user)

    models.Player.objects.create(name=player_name, added_by=normal_user)

    player_list = client.get(player_endpoint)
    assert len(player_list.data) == 1
    assert player_list.data[0]["name"] == player_name


@pytest.mark.django_db
def test_create_game_works(normal_user, player, golf_course):
    game_endpoint = reverse("api:game-list")
    client = APIClient()
    client.force_authenticate(user=normal_user)

    data = {"course": golf_course.id, "holes_played": golf_course.hole_count}

    res = client.post(game_endpoint, data)
    assert res.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_game_without_course_returns_error(normal_user):
    game_endpoint = reverse("api:game-list")
    client = APIClient()
    client.force_authenticate(user=normal_user)

    data = {"course": "", "holes_played": "9"}

    res = client.post(game_endpoint, data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_add_player_to_game_works(normal_user, golf_game, player):
    add_player_endpoint = reverse("api:game-add_player", args=[golf_game.id])

    client = APIClient()
    client.force_authenticate(user=normal_user)

    data = {"player": player.id}

    res = client.post(add_player_endpoint, data)
    assert res.status_code == status.HTTP_200_OK

    golf_game.refresh_from_db()
    assert player in golf_game.players.all()


@pytest.mark.django_db
def test_remove_player_from_game_works(normal_user, golf_game_with_player):
    player = golf_game_with_player.players.all().first()
    remove_player_endpoint = reverse(
        "api:game-remove_player", args=[golf_game_with_player.id]
    )
    data = {"player": player.id}
    client = APIClient()
    client.force_authenticate(user=normal_user)

    res = client.post(remove_player_endpoint, data)
    assert res.status_code == status.HTTP_200_OK

    golf_game_with_player.refresh_from_db()

    assert golf_game_with_player.players.count() == 0
    assert player not in golf_game_with_player.players.all()


@pytest.mark.django_db
def test_add_player_to_game_with_no_player_returns_error(
    normal_user, golf_game, player
):
    add_player_endpoint = reverse("api:game-add_player", args=[golf_game.id])

    client = APIClient()
    client.force_authenticate(user=normal_user)

    data = {}

    res = client.post(add_player_endpoint, data)
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_set_hole_score_for_game(normal_user, golf_game_with_player, player):
    add_score_endpoint = reverse("api:game-set_score", args=[golf_game_with_player.id])
    player_link = models.PlayerGameLink.objects.get(
        game=golf_game_with_player, player=player
    )
    hole_score = models.HoleScore.objects.get(game=player_link, hole=1)
    data = {"hole_number": 1, "score_list": [{"id": hole_score.id, "score": 3}]}

    client = APIClient()
    client.force_authenticate(user=normal_user)

    res = client.post(add_score_endpoint, data, format="json")
    assert res.status_code == status.HTTP_200_OK

    hole_score.refresh_from_db()
    assert hole_score.score == 3


@pytest.mark.django_db
def test_start_game_with_user_that_has_no_player_returns_error(
    normal_user, golf_course
):
    start_game_endpoint = reverse("api:game-list")

    data = {
        "course": golf_course.id,
        "holes_played": golf_course.hole_count,
    }

    client = APIClient()
    client.force_authenticate(user=normal_user)

    res = client.post(start_game_endpoint, data)
    assert settings.CONSTANTS["PLAYER_NOT_SETUP"] == res.data["message"]
    assert res.status_code == status.HTTP_400_BAD_REQUEST


# @pytest.mark.django_db
# def test_set_hole_score_with_missing_data_returns_error(
#     normal_user, golf_game_with_player, player
# ):
#     add_score_endpoint = reverse("api:game-set_score", args=[golf_game_with_player.id])
#     data = {"hole_number": 1, "score_list": [{"id": "", "score": 3}]}

#     client = APIClient()
#     client.force_authenticate(user=normal_user)

#     res = client.post(add_score_endpoint, data, format="json")
#     assert res.status_code == status.HTTP_400_BAD_REQUEST
