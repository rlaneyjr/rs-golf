from django import template
from dashboard import utils

register = template.Library()

@register.simple_tag
def get_team_scores(game):
  return game.score.get("team_scores", False)

@register.simple_tag
def get_scores(game):
    return game.score.get("scores", False)

@register.simple_tag
def get_skins(game):
    return game.score.get("skins", False)

@register.simple_tag
def get_all_scores(game):
    return game.score.get("all_scores")

@register.simple_tag
def get_hole_list(game):
    return game.score.get("hole_list")

@register.simple_tag
def format_players(players):
    return str(players).lstrip('[').rstrip(']').replace("'", "")

@register.simple_tag
def player_in_skins(player, game):
    return utils.is_player_in_skins(player, game)
