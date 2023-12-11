import random
from dashboard import models


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()


def create_holes_for_course(course):
    for hole_num in range(1, int(course.hole_count) + 1):
        hole_obj = models.Hole(
            name=f"Hole{hole_num}",
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


def get_team_hcp(team):
    all_hcps = [_p.handicap for _p in team.players.all()]
    avg_hcp = sum(all_hcps)/len(all_hcps)
    return round(avg_hcp, 1)


def get_teams_for_game(game):
    return models.Team.objects.filter(game__in=[game.id])


def calculate_teams(player_count):
    if player_count == 4:
        return 2, 2
    if player_count < 4:
        return 1, player_count
    if player_count % 4 == 0:
        return round(player_count/4), 4
    if player_count % 3 == 0:
        return round(player_count/3), 3
    if player_count % 2 == 0:
        return round(player_count/2), 2
    num_teams, num_players = calculate_teams(player_count - 1)
    if num_teams == 1:
        return 1, player_count
    return num_teams, num_players, 1


def get_holes_for_game(game):
    hole_list = models.Hole.objects.filter(course=game.course).order_by("order")
    if game.which_holes == "front":
        hole_list = hole_list.filter(order__gte=1, order__lt=10)
    elif game.which_holes == "back":
        hole_list = hole_list.filter(order__gte=10)
    return hole_list


def delete_teams_for_game(game):
    for team in get_teams_for_game(game):
        team.delete()


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
    all_teams = []
    num_teams = None
    num_players = None
    remainder = None
    players = game.players.all().order_by("handicap")
    calculated_teams = calculate_teams(players.count())
    if len(calculated_teams) == 3:
        num_teams, num_players, remainder = calculated_teams
    else:
        num_teams, num_players = calculated_teams
    for team_num in range(1, num_teams + 1):
        new_team = models.Team(name=f"Team{team_num}", game=game)
        new_team.save()
        for _ in range(1, num_players + 1):
            if players.count() > 0:
                _player = random.choice(players)
                player_mem = models.PlayerMembership.objects.filter(
                    game=game, player=_player, team=None
                ).first()
                player_mem.team = new_team
                player_mem.save()
                players = players.exclude(id=_player.id)
        new_team.save()
        all_teams.append(new_team)
    if remainder and players.count() == 1:
        rem_player = players[0]
        rem_mem = models.PlayerMembership.objects.filter(
            game=game, player=rem_player, team=None
        ).first()
        random_team = random.choice(all_teams)
        rem_mem.team = random_team
        rem_mem.save()
    for team in all_teams:
        team.handicap = get_team_hcp(team)
        team.save()


def create_hole_scores_for_game(game):
    hole_list = get_holes_for_game(game)
    for hole in hole_list:
        for player in game.players.all():
            player_mem = models.PlayerMembership.objects.filter(
                player=player, game=game
            ).first()
            existing_hole_score = models.HoleScore.objects.filter(
                player=player_mem, hole=hole
            )
            if existing_hole_score:
                continue
            hole_score = models.HoleScore(player=player_mem, hole=hole)
            hole_score.save()


def get_team_score(team):
    team_score = {
        "name": team.name,
        "handicap": team.handicap,
        "hole_list": [],
        "team_score": 0,
    }
    for player in team.players.all():
        player_mem = models.PlayerMembership.objects.filter(
            game=team.game, player=player, team=team
        ).first()
        player_score_list = models.HoleScore.objects.filter(
            player=player_mem,
            score__gt=0,
        )
        for hole_score in player_score_list:
            hole_data = {
                "hole_score_id": hole_score.id,
                "player_name": player.name,
                "hole_id": hole_score.hole.id,
                "hole_name": hole_score.hole.name,
                "hole_score": hole_score.score,
                "hole_par": hole_score.hole.par,
                "hole_handicap": hole_score.hole.handicap,
                "skin": True,
            }
            current_hole_filter = filter(
                lambda h: h["hole_id"] == hole_score.hole.id,
                team_score["hole_list"],
            )
            current_holes = list(current_hole_filter)
            if current_holes and len(current_holes) == 1:
                current_hole = current_holes[0]
                if current_hole["hole_score"] > hole_score.score:
                    team_score["hole_list"].remove(current_hole)
                    team_score["hole_list"].append(hole_data)
                elif current_hole["hole_score"] == hole_score.score:
                    hole_data.update(player_name="Multiple")
                    hole_data.update(skin=False)
                    team_score["hole_list"].remove(current_hole)
                    team_score["hole_list"].append(hole_data)
            else:
                team_score["hole_list"].append(hole_data)
    team_score["team_score"] = sum([_h["hole_score"] for _h in team_score["hole_list"]])
    return team_score


def get_skins(team_data):
    all_holes = [_h["hole_list"] for _, _h in team_data.items()]
    skin_holes = [h for h in all_holes if h["skin"] == True]
    for hole in skin_holes:
        cur_skin = filter(lambda h: h["hole_id"] == hole["hole_id"], skin_holes)


def get_team_data_for_game(game):
    team_list = get_teams_for_game(game=game)
    team_data = False
    if team_list:
        team_data = {}
        for team in team_list:
            team_data[team.id] = get_team_score(team)
    return team_data
