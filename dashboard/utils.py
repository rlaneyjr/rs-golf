import random
from dashboard import models


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()


def create_holes_for_course(course):
    for hole_num in range(1, int(course.hole_count) + 1):
        hole_obj = models.Hole(
            name=f"Hole {hole_num}",
            course=course,
            order=hole_num,
            handicap=hole_num,
        )
        hole_obj.save()
    return True


def get_players_not_in_game(game):
    return models.Player.objects.all().exclude(game__in=[game.id])


def get_players_avg_hcp(players):
    all_hcps = [_p.handicap for _p in players]
    avg_hcp = sum(all_hcps)/len(all_hcps)
    return round(avg_hcp, 1)


def get_teams_for_game(game):
    return models.Team.objects.filter(game__in=[game.id])


def get_team_score(team):
    team_score = {
        "name": team.name,
        "handicap": team.handicap,
        "hole_list": [],
        "team_score": 0,
    }
    for player in team.players.all():
        player_game_link = models.PlayerGameLink.objects.filter(
            game=team.game, player=player
        ).first()
        player_score_list = models.HoleScore.objects.filter(
            game=player_game_link,
            score__gt=0,
        )
        for hole in player_score_list:
            hole_data = {
                "hole_id": hole.id,
                "player_name": player.name,
                "hole_name": hole.name,
                "hole_score": hole.score,
                "hole_par": hole.par,
                "hole_handicap": hole.handicap,
                "skin": True,
            }
            current_hole_filter = filter(
                lambda h: h["hole_name"] == hole.name,
                team_score["hole_list"],
            )
            current_holes = list(current_hole_filter)
            if current_holes and len(current_holes) == 1:
                current_hole = current_holes[0]
                if current_hole.score > hole.score:
                    team_score["hole_list"].remove(current_hole)
                    team_score["hole_list"].append(hole_data)
                elif current_hole.score == hole.score:
                    hole_data.update(player_name="Multiple")
                    hole_data.update(skin=False)
                    team_score["hole_list"].remove(current_hole)
                    team_score["hole_list"].append(hole_data)
            else:
                team_score["hole_list"].append(hole_data)
    team_score["team_score"] = sum([_h["hole_score"] for _h in team_score["hole_list"]])
    return team_score


def get_team_data_for_game(game):
    team_list = get_teams_for_game(game=game)
    team_data = False
    if team_list:
        team_data = {}
        for team in team_list:
            team_data[team.id] = get_team_score(team)
    return team_data


def get_holes_for_game(game):
    hole_list = models.Hole.objects.filter(course=game.course).order_by("order")
    if game.which_holes == "all" or game.course.hole_count == 9:
        return hole_list
    if game.which_holes == "front":
        return hole_list.filter(order__gte=1, order__lt=10)
    if game.which_holes == "back":
        return hole_list.filter(order__gte=10)
    return None


def create_teams_for_game(game):
    '''
    Not doing below. All random at the moment.
    How a Balanced Draw is calculated
    The calculation is based on the Handicap Index of those players already added to the game.
    1. The first column in the grid is filled with players with the lowest handicaps.
    2. The last column is filled with players with the highest handicaps.
    3. Any middle columns are filled with players with handicaps in the best range(s) possible.
    4. Players in each column are then randomly shuffled (column by column), to create a more random
    spread across the games.
    Pairs Competitions
    Where the Start Sheet is for a pairs competition (such as Foursomes, Four-ball, etc), HandicapMaster
    will balance the players in each team pairing (rather than across all four players in each Tee Time).
    Effectively, one player from the 50% of players with lower handicaps will be paired with one player from
    the 50% with higher handicaps.
    '''
    players = game.players.all().order_by("handicap")
    num_teams = None
    num_players = None
    while num_teams == None:
        # Try 4 man teams
        for team_num in range(2, 11):
            if players.count()/4 % team_num == 0:
                num_teams = team_num
                num_players = 4
        # Try 3 man teams
        for team_num in range(2, 11):
            if players.count()/3 % team_num == 0:
                num_teams = team_num
                num_players = 3
        # Try 2 man teams
        for team_num in range(2, 11):
            if players.count()/2 % team_num == 0:
                num_teams = team_num
                num_players = 2
        else:
            num_teams = 1
            num_players = players.count()
    for _team in range(1, num_teams + 1):
        new_team = models.Team(name=f"Team {_team}", game=game)
        new_team.save()
        for _player in range(1, num_players + 1):
            _man = random.choice(players)
            team_mem = models.TeamMembership(new_team, _man)
            team_mem.save()
            players = players.exclude(id=_man.id)
        new_team.handicap = get_players_avg_hcp(new_team.players)
        new_team.save()


def create_hole_scores_for_game(game):
    """
        Unused at the moment
    """
    hole_list = get_holes_for_game(game)
    for hole in hole_list:
        for player in game.players.all():
            game_link = models.PlayerGameLink.objects.filter(
                player=player, game=game
            ).first()
            existing_hole_score = models.HoleScore.objects.filter(
                hole=hole, game=game_link
            )
            if existing_hole_score:
                continue

            hole_score = models.HoleScore(hole=hole, game=game_link)
            hole_score.save()
