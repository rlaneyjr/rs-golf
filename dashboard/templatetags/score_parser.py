from django import template
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
def get_all_holes(game):
    return game.score.get("all_holes")

@register.simple_tag
def get_hole_list(game):
    return game.score.get("hole_list")
