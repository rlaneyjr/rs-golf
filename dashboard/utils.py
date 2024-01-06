import random
from dashboard import models


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()


def set_holes_for_game(game, holes_to_play):
    if game.course.hole_count == 18:
        if holes_to_play == "front":
            game.which_holes = models.WhichHolesChoices.FRONT
            game.holes_played = models.HolesToPlayChoices.HOLES_9
        elif holes_to_play == "back":
            game.which_holes = models.WhichHolesChoices.BACK
            game.holes_played = models.HolesToPlayChoices.HOLES_9
        else:
            game.which_holes = models.WhichHolesChoices.ALL
            game.holes_played = models.HolesToPlayChoices.HOLES_18
    else:
        game.which_holes = models.WhichHolesChoices.ALL
        game.holes_played = models.HolesToPlayChoices.HOLES_9


def set_game_type(game, game_type):
    if game_type == "best-ball":
        game.game_type = models.GameTypeChoices.BEST_BALL
    elif game_type == "stroke":
        game.game_type = models.GameTypeChoices.STROKE
    elif game_type == "skins":
        game.game_type = models.GameTypeChoices.SKINS
    elif game_type == "stroke-skins":
        game.game_type = models.GameTypeChoices.STROKE_SKINS
    elif game_type == "best-ball-skins":
        game.game_type = models.GameTypeChoices.BEST_BALL_SKINS


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


def get_team_list_for_game(game):
    team_list = []
    for team in get_teams_for_game(game):
        team_data = {
            "id": team.id,
            "name": team.name,
            "players": [],
            "handicap": str(team.handicap),
        }
        for player in team.players.all():
            team_data["players"].append(player.name)
        team_list.append(team_data)
    return team_list


def game_has_teams(game):
    teams = get_teams_for_game(game)
    if teams and len(teams) > 1:
        return True
    return False


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


def calculate_teams(player_count):
    if player_count == 4:
        return 2, 2
    if player_count < 4:
        return 0, player_count
    if player_count % 4 == 0:
        return round(player_count/4), 4
    if player_count % 3 == 0:
        return round(player_count/3), 3
    if player_count % 2 == 0:
        return round(player_count/2), 2
    num_teams, num_players = calculate_teams(player_count - 1)
    if num_teams == 0:
        return 0, player_count
    return num_teams, num_players, 1


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
    num_teams = None
    num_players = None
    remainder = None
    new_teams = []
    players = game.players.all().order_by("handicap")
    calculated_teams = calculate_teams(players.count())
    if len(calculated_teams) == 3:
        num_teams, num_players, remainder = calculated_teams
    else:
        num_teams, num_players = calculated_teams
    for team_num in range(1, num_teams + 1):
        new_team = models.Team(name=f"Team{team_num}", game=game)
        new_team.save()
        new_teams.append(new_team)
        for _ in range(1, num_players + 1):
            if players.count() > 0:
                _player = random.choice(players)
                player_mem = models.PlayerMembership.objects.filter(
                    game=game, player=_player
                ).first()
                player_mem.team = new_team
                player_mem.save()
                players = players.exclude(id=_player.id)
    if remainder and players.count() == 1:
        rem_player = players[0]
        rem_mem = models.PlayerMembership.objects.filter(
            game=game, player=rem_player
        ).first()
        random_team = random.choice(new_teams)
        rem_mem.team = random_team
        rem_mem.save()
    for team in new_teams:
        team.handicap = get_team_hcp(team)
        team.save()


def create_hole_scores_for_game(game):
    game_holes = get_holes_for_game(game)
    for hole in game_holes:
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
        "team_id": team.id,
        "team_name": team.name,
        "players": [],
        "handicap": str(team.handicap),
        "hole_list": [],
        "team_score": 0,
        "winner": False,
    }
    for player in team.players.all():
        team_score["players"].append(player.name)
        player_mem = models.PlayerMembership.objects.filter(
            game=team.game, player=player, team=team
        ).first()
        player_score_list = models.HoleScore.objects.filter(
            player=player_mem,
            score__gt=0,
        )
        for hole_score in player_score_list:
            hole_data = {
                "player_name": player.name,
                "hole_order": hole_score.hole.order,
                "hole_name": hole_score.hole.name,
                "hole_score": hole_score.score,
                "hole_par": hole_score.hole.par,
                "hole_handicap": str(hole_score.hole.handicap),
            }
            current_hole_filter = filter(
                lambda h: h["hole_order"] == hole_score.hole.order,
                team_score["hole_list"],
            )
            current_holes = list(current_hole_filter)
            if current_holes and len(current_holes) == 1:
                current_hole = current_holes[0]
                if current_hole["hole_score"] > hole_score.score:
                    hole_index = team_score["hole_list"].index(current_hole)
                    old_hole = team_score["hole_list"].pop(hole_index)
                    team_score["hole_list"].insert(hole_index, hole_data)
                elif current_hole["hole_score"] == hole_score.score:
                    hole_index = team_score["hole_list"].index(current_hole)
                    old_hole = team_score["hole_list"].pop(hole_index)
                    hole_data.update(player_name="Multiple")
                    team_score["hole_list"].insert(hole_index, hole_data)
            else:
                team_score["hole_list"].append(hole_data)
    team_score["team_score"] = sum([_h["hole_score"] for _h in team_score["hole_list"]])
    return team_score


def score_teams(game):
    team_data = []
    team_list = get_teams_for_game(game)
    for t in team_list:
        team_data.append(get_team_score(t))
    # team_data.sort(key=lambda t: t["team_score"])
    low_score = min([t["team_score"] for t in team_data])
    low_filter = filter(lambda t: t["team_score"] == low_score, team_data)
    team_winners = list(low_filter)
    for tw in team_winners:
        ti = team_data.index(tw)
        team = team_data.pop(ti)
        team.update({"winner": True})
        team_data.insert(ti, team)
    return team_data


def get_hole_list_for_game(game):
    hole_list = []
    if game.which_holes == "front":
        for hole_num in range(1, 10):
            hole_list.append(f"{hole_num}")
    elif game.which_holes == "back":
        for hole_num in range(10, 19):
            hole_list.append(f"{hole_num}")
    else:
        for hole_num in range(1, game.holes_played + 1):
            hole_list.append(f"{hole_num}")
    return hole_list


def get_hole_data_for_game(game):
    hole_data = {}
    # Always keep track of each players score
    for player in game.players.all():
        hole_data[player.id] = {
            "user_account": player.user_account,
            "player_name": player.name,
            "hcp": str(player.handicap),
            "hole_list": [],
            "total_score": 0,
            "par": 0,
            "winner": False,
        }
        player_game_link = models.PlayerMembership.objects.filter(
            game=game, player=player
        ).first()
        hole_score_list = models.HoleScore.objects.filter(player=player_game_link)
        for hole_item in hole_score_list:
            hole_data[player.id]["hole_list"].append(
                {
                    "hole_order": hole_item.hole.order,
                    "hole_name": hole_item.hole.name,
                    "hole_score": hole_item.score,
                    "hole_par": hole_item.hole.par,
                    "hole_handicap": str(hole_item.hole.handicap),
                }
            )
            hole_data[player.id]["total_score"] += hole_item.score
            hole_data[player.id]["par"] += hole_item.hole.par
    # hole_data.sort(key=lambda h: h[player.id]["total_score"])
    return hole_data


def all_holes_from_hole_data(hole_data):
    all_holes = []
    for _, d in hole_data.items():
        for h in d["hole_list"]:
            h.update({"player_name": d["player_name"]})
            all_holes.append(h)
    return all_holes


def get_skins_all_holes(all_holes):
    skins = []
    for hole in all_holes:
        hole_filter = filter(lambda h: h["hole_order"] == hole["hole_order"], all_holes)
        same_holes = list(hole_filter)
        low_score = min([h["hole_score"] for h in same_holes])
        low_filter = filter(lambda h: h["hole_score"] == low_score, same_holes)
        low_holes = list(low_filter)
        if low_holes and len(low_holes) == 1:
            player = low_holes[0]["player_name"]
        else:
            player = "carry"
        skin_hole = {"hole": hole["hole_name"], "player": player}
        if skin_hole not in skins:
            skins.append(skin_hole)
    return skins


def score_hole_data(hole_data):
    scores = []
    for _, player_data in hole_data.items():
        scores.append(player_data)
    # scores.sort(key=lambda s: s["total_score"])
    low_score = min([h["total_score"] for h in scores])
    low_filter = filter(lambda h: h["total_score"] == low_score, scores)
    low_scores = list(low_filter)
    for ls in low_scores:
        si = scores.index(ls)
        score = scores.pop(si)
        score.update({"winner": True})
        scores.insert(si, score)
    return scores


def score_game(game):
    hole_list = get_hole_list_for_game(game)
    hole_data = get_hole_data_for_game(game)
    all_holes = all_holes_from_hole_data(hole_data)
    skins = get_skins_all_holes(all_holes)
    game_score = {"all_holes": all_holes, "hole_list": hole_list, "skins": skins}
    if game_has_teams(game):
        scores = score_teams(game)
        game_score.update({"team_scores": scores})
    else:
        scores = score_hole_data(hole_data)
        game_score.update({"scores": scores})
    return game_score
