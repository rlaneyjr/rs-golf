import pytest
import json
from django.shortcuts import reverse
from django.test import Client
from home import utils
from home import models


@pytest.mark.django_db
def test_get_available_players_works(
    normal_user, golf_game_with_player, player, player_two, second_player
):
    # get players that we can add to a game
    available_players = utils.get_players_for_game(normal_user, golf_game_with_player)

    # the game currently has one player added
    # so we should only have one other player that we can add
    assert len(available_players) == 1

    # the available player should be our second player
    assert available_players[0] == player_two

    # check to be sure that we are looking at all three players
    # one of these players were added by a different user
    # it should be there, but not available for us to add to a game
    all_player_count = models.Player.objects.all().count()
    assert all_player_count == 3


@pytest.mark.django_db
def test_get_all_holes_for_18_hole_course(eighteen_hole_golf_course):
    hole_list = utils.get_holes_for_game(eighteen_hole_golf_course, "18")
    assert hole_list.count() == 18


@pytest.mark.django_db
def test_get_holes_for_front_9_on_18_hole_course(eighteen_hole_golf_course):
    hole_list = utils.get_holes_for_game(eighteen_hole_golf_course, "front-9")
    assert hole_list.count() == 9
    assert hole_list[0].order == 1
    assert hole_list.last().order == 9


@pytest.mark.django_db
def test_get_holes_for_back_9_on_18_hole_course(eighteen_hole_golf_course):
    hole_list = utils.get_holes_for_game(eighteen_hole_golf_course, "back-9")
    assert hole_list.count() == 9
    assert hole_list[0].order == 10
    assert hole_list.last().order == 18


@pytest.mark.django_db
def test_adding_player_late_doesnt_create_duplicate_holes(
    normal_user, golf_game_with_player, player, player_two
):
    client = Client()
    client.force_login(user=normal_user)

    data = {"game_id": golf_game_with_player.id, "action": "start-game"}

    manage_game_url = reverse("home:ajax-manage-game")
    response = client.post(manage_game_url, data, content_type="application/json")
    assert response.status_code == 200

    golf_game_with_player.refresh_from_db()
    golf_game_with_player.players.add(player_two)

    data = {"game_id": golf_game_with_player.id, "action": "start-game"}

    manage_game_url = reverse("home:ajax-manage-game")
    response = client.post(manage_game_url, data, content_type="application/json")
    assert response.status_code == 200

    player_one_game_link = models.PlayerGameLink.objects.get(
        player=player, game=golf_game_with_player
    )
    player_one_holes = models.HoleScore.objects.filter(game=player_one_game_link)
    assert player_one_holes.count() == 9


@pytest.mark.django_db
def test_start_game_sets_correct_status(normal_user, golf_game):
    assert golf_game.status == "setup"
    golf_game.start()
    assert golf_game.status == "active"
