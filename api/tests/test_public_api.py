import pytest
from django.shortcuts import reverse
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
def test_public_create_player_requires_login():
    client = APIClient()
    player_endpoint = reverse("api:players-list")
    data = {
        "name": "Test Player"
    }

    res = client.post(player_endpoint, data)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_public_get_game_list_requires_login():
    client = APIClient()
    game_endpoint = reverse("api:game-list")

    res = client.get(game_endpoint)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_public_create_game_requires_login(golf_course):
    client = APIClient()
    game_endpoint = reverse("api:game-list")
    data = {
        "course": golf_course.id,
        "holes_played": golf_course.hole_count
    }

    res = client.post(game_endpoint, data)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_public_get_tee_times_requires_login():
    client = APIClient()
    tee_time_endpoint = reverse("api:tee-times-list")
    res = client.get(tee_time_endpoint)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_public_get_tees_requires_login():
    client = APIClient()
    tee_time_endpoint = reverse("api:tee-list")
    res = client.get(tee_time_endpoint)
    assert res.status_code == status.HTTP_403_FORBIDDEN
