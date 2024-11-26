import json, math, random
from dashboard import models
from djmoney.money import Money


points_map = {
    -4: 6,
    -3: 5,
    -2: 4,
    -1: 3,
    0: 2,
    1: 1,
    2: 0,
}


def round_up(x):
  frac = x - math.floor(x)
  if frac < 0.5:
    return math.floor(x)
  return math.ceil(x)


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()


def is_player_in_skins(player, game):
    player_mem = models.PlayerMembership.objects.filter(game=game, player=player).first()
    return player_mem.skins


def num_players_in_skins(game):
    return len([p for p in game.players.all() if is_player_in_skins(p, game)])


def get_first_course_id():
    return models.GolfCourse.objects.first().id


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
    elif game_type == "stableford":
        game.game_type = models.GameTypeChoices.STABLEFORD
    elif game_type == "stroke":
        game.game_type = models.GameTypeChoices.STROKE


def get_players_not_in_game(game):
    return models.Player.objects.all().exclude(game__in=[game.id])


def get_current_players_for_game(game):
    current_players = []
    for player in game.players.all():
        player_mem = models.PlayerMembership.objects.filter(game=game, player=player).first()
        current_players.append({
            "id": player.id,
            "name": player.name,
            "hcp": player.handicap,
            "points_needed": player_mem.points_needed,
            "skins": player_mem.skins,
        })
    return current_players


def get_avg_hcp(hcps):
    avg_hcp = sum(hcps)/len(hcps)
    return round(avg_hcp, 1)


def get_team_hcp(team, game):
    team_members = models.PlayerMembership.objects.filter(game=game, team=team)
    all_hcps = [_t.player.handicap for _t in team_members]
    return get_avg_hcp(all_hcps)


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


def get_par_for_course(course):
    holes = models.Hole.objects.filter(course=course).order_by("order")
    return sum([h.par for h in holes])


def get_holes_for_game(game):
    holes = models.Hole.objects.filter(course=game.course).order_by("order")
    if game.which_holes == "front":
        holes = holes.filter(order__gte=1, order__lt=10)
    elif game.which_holes == "back":
        holes = holes.filter(order__gte=10)
    return holes


def get_par_for_game(game):
    holes = get_holes_for_game(game)
    return sum([h.par for h in holes])


def clean_game(game):
    if game.use_teams:
        for team in get_teams_for_game(game):
            team.delete()
    players = models.PlayerMembership.objects.filter(game=game)
    for player_mem in players:
        player_mem.delete()
    if game.league_game:
        for p in game.players.all():
            p.revert_hcp()


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


def create_hole_scores_for_game(game):
    for hole in get_holes_for_game(game):
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
    players = game.players.all()
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
        team.handicap = get_team_hcp(team, game)
        team.save()


def get_team_score(team):
    team_score = {
        "team_id": team.id,
        "team_name": team.name,
        "handicap": str(team.handicap),
        "players": [],
        "hole_list": [],
        "team_score": 0,
        "winner": False,
        "money": 0,
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
                "hole_score": hole_score.strokes,
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
                if current_hole["hole_score"] > hole_score.strokes:
                    hole_index = team_score["hole_list"].index(current_hole)
                    old_hole = team_score["hole_list"].pop(hole_index)
                    team_score["hole_list"].insert(hole_index, hole_data)
                elif current_hole["hole_score"] == hole_score.strokes:
                    hole_index = team_score["hole_list"].index(current_hole)
                    old_hole = team_score["hole_list"].pop(hole_index)
                    hole_data.update(player_name="Multiple")
                    team_score["hole_list"].insert(hole_index, hole_data)
            else:
                team_score["hole_list"].append(hole_data)
    team_score["team_score"] = sum([_h["hole_score"] for _h in team_score["hole_list"]])
    return team_score


def update_team_data_low_score(team_data, score_list, pot, percent_money=100):
    low_score = min(score_list)
    low_filter = filter(lambda t: t["team_score"] == low_score, team_data)
    team_winners = list(low_filter)
    pot_pct = percent_money/100
    money = (pot * pot_pct)/len(team_winners)
    for tw in team_winners:
        ti = team_data.index(tw)
        team = team_data.pop(ti)
        team.update({"winner": True})
        team.update({"money": str(money)})
        team_data.insert(ti, team)
        score_list.remove(tw["team_score"])
    return team_data, score_list


def score_teams(game):
    team_data = [get_team_score(t) for t in get_teams_for_game(game)]
    score_list = [td["team_score"] for td in team_data]
    if not game.payout_positions or game.payout_positions == 1:
        team_data, _ = update_team_data_low_score(team_data, score_list, game.pot)
    elif game.payout_positions == 2:
        team_data, sl = update_team_data_low_score(team_data, score_list, game.pot, 80)
        team_data, _ = update_team_data_low_score(team_data, sl, game.pot, 20)
    elif game.payout_positions == 3:
        team_data, sl = update_team_data_low_score(team_data, score_list, game.pot, 70)
        team_data, sl = update_team_data_low_score(team_data, sl, game.pot, 20)
        team_data, _ = update_team_data_low_score(team_data, sl, game.pot, 10)
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


def get_hole_data_for_game(game, final_scores=False):
    hole_data = []
    # Always keep track of each players score
    for player in game.players.all():
        player_data = {
            "course_name": game.course.name,
            "player_id": player.id,
            "player_name": player.name,
            "hcp": float(player.handicap),
            "skins": None,
            "points_needed": None,
            "team_id": None,
            "team_name": None,
            "team_hcp": None,
            "game_hcp": None,
            "game_points": None,
            "hole_list": [],
            "player_score": 0,
            "player_points": 0,
            "par": 0,
            "winner": False,
            "money": 0,
        }
        player_mem = models.PlayerMembership.objects.filter(
            game=game, player=player
        ).first()
        player_data["skins"] = player_mem.skins
        player_data["points_needed"] = player_mem.points_needed
        if game.use_teams and player_mem.team != None:
            player_data["team_id"] = player_mem.team.id
            player_data["team_name"] = player_mem.team.name
            player_data["team_hcp"] = str(player_mem.team.handicap)
        hole_score_list = models.HoleScore.objects.filter(player=player_mem)
        for hole_score in hole_score_list:
            player_data["hole_list"].append(
                {
                    "hole_score_id": hole_score.id,
                    "hole_order": hole_score.hole.order,
                    "hole_name": hole_score.hole.name,
                    "hole_strokes": hole_score.strokes,
                    "hole_points": hole_score.points,
                    "hole_par": hole_score.hole.par,
                    "hole_handicap": str(hole_score.hole.handicap),
                    "hole_score": hole_score.score,
                }
            )
            player_data["player_score"] += hole_score.strokes
            player_data["player_points"] += hole_score.points
            player_data["par"] += hole_score.hole.par
        player_data["game_hcp"] = player_data["player_score"] - player_data["par"]
        player_data["game_points"] = player_data["player_points"] - player_data["points_needed"]
        if final_scores:
            player_mem.game_handicap = player_data["game_hcp"]
            player_mem.game_score = player_data["player_score"]
            player_mem.game_points = player_data["game_points"]
            player_mem.save()
        hole_data.append(player_data)
    return hole_data


def get_all_scores_for_game(game):
    all_scores = []
    for hole in get_holes_for_game(game):
        hole_data = {
            "order": hole.order,
            "name": hole.name,
            "scores": [],
            "par": hole.par,
            "handicap": int(hole.handicap),
        }
        for player in game.players.all():
            player_mem = models.PlayerMembership.objects.filter(
                game=game, player=player
            ).first()
            hole_score = models.HoleScore.objects.filter(
                player=player_mem, hole=hole
            ).first()
            hole_score = {
                "player": player.name,
                "strokes": hole_score.strokes,
                "points": hole_score.points,
                "score": hole_score.score,
                "skins": player_mem.skins,
            }
            hole_data["scores"].append(hole_score)
        hole_data["scores"].sort(key=lambda s: s["strokes"])
        all_scores.append(hole_data)
    all_scores.sort(key=lambda h: h["order"])
    return all_scores


def all_holes_from_hole_data(hole_data):
    all_holes = []
    for p in hole_data:
        for h in p["hole_list"]:
            h.update({"player_name": p["player_name"]})
            all_holes.append(h)
    return all_holes


def filter_skins_from_all_scores(all_scores):
    skin_holes = []
    for hole in all_scores:
        skin_filter = filter(lambda s: s["skins"] == True, hole["scores"])
        hole.update({"scores": list(skin_filter)})
        skin_holes.append(hole)
    return skin_holes


def filter_skins_from_hole_data(hole_data):
    skin_holes = []
    for player in hole_data:
        if player["skins"]:
            for hole in player["hole_list"]:
                hole.update({"player_name": player["player_name"]})
                skin_holes.append(hole)
    return skin_holes


def get_skins_all_scores(all_scores, skin_cost):
    skins = []
    carry_money = None
    skin_holes = filter_skins_from_all_scores(all_scores)
    for hole in skin_holes:
        hole_money = skin_cost * len(hole["scores"])
        low_score = min([h["strokes"] for h in hole["scores"]])
        low_filter = filter(lambda h: h["strokes"] == low_score, hole["scores"])
        low_scores = list(low_filter)
        if low_scores and len(low_scores) == 1:
            player = low_scores[0]["player"]
            if carry_money == None:
                money = hole_money
            else:
                money = hole_money + carry_money
                carry_money = None
        else:
            player = "carry"
            money = "---"
            if carry_money == None:
                carry_money = hole_money
            else:
                carry_money += hole_money
        skins.append({"hole": hole["name"], "player": player, "money": str(money)})
    return skins


def skin_holes_from_game(game):
    skin_holes = []
    for hole in get_holes_for_game(game):
        hole_data = {
            "order": hole.order,
            "name": hole.name,
            "scores": [],
            "par": hole.par,
            "handicap": str(hole.handicap),
        }
        for player in game.players.all():
            player_mem = models.PlayerMembership.objects.filter(
                game=game, player=player
            ).first()
            if player_mem.skins:
                hole_score = models.HoleScore.objects.filter(
                    player=player_mem, hole=hole
                ).first()
                hole_data["scores"].append(
                    {
                        "player": player.name,
                        "strokes": hole_score.strokes
                    }
                )
        skin_holes.append(hole_data)
    skin_holes.sort(key=lambda s: s["order"])
    return skin_holes


def get_skins(game):
    skins = []
    carry_money = None
    skin_holes = skin_holes_from_game(game)
    for hole in skin_holes:
        if len(hole["scores"]):
            hole_money = game.skin_cost * len(hole["scores"])
            low_score = min([h["strokes"] for h in hole["scores"]])
            low_filter = filter(lambda h: h["strokes"] == low_score, hole["scores"])
            low_scores = list(low_filter)
            if low_scores and len(low_scores) == 1:
                player = low_scores[0]["player"]
                if carry_money == None:
                    money = hole_money
                else:
                    money = hole_money + carry_money
                    carry_money = None
            else:
                player = "carry"
                money = Money(0, "USD")
                if carry_money == None:
                    carry_money = hole_money
                else:
                    carry_money = hole_money + carry_money
            skins.append({"hole": hole["name"], "player": player, "money": str(money)})
    return skins


def update_hole_data_high_points(hole_data, points_list, pot, percent_money=100):
    high_score = max(points_list)
    high_filter = filter(lambda t: t["game_points"] == high_score, hole_data)
    winners = list(high_filter)
    pot_pct = percent_money/100
    money = (pot * pot_pct)/len(winners)
    for w in winners:
        i = hole_data.index(w)
        player = hole_data.pop(i)
        player.update({"winner": True})
        player.update({"money": str(money)})
        hole_data.insert(i, player)
        points_list.remove(w["game_points"])
    return hole_data, points_list


def update_hole_data_low_score(hole_data, score_list, pot, percent_money=100):
    low_score = min(score_list)
    low_filter = filter(lambda t: t["player_score"] == low_score, hole_data)
    winners = list(low_filter)
    pot_pct = percent_money/100
    money = (pot * pot_pct)/len(winners)
    for w in winners:
        i = hole_data.index(w)
        player = hole_data.pop(i)
        player.update({"winner": True})
        player.update({"money": str(money)})
        hole_data.insert(i, player)
        score_list.remove(w["player_score"])
    return hole_data, score_list


def score_hole_data(hole_data, pot, payout_positions, use_points=False):
    if use_points:
        points_list = [h["game_points"] for h in hole_data]
        if payout_positions == 1:
            hole_data, _ = update_hole_data_high_points(hole_data, points_list, pot)
        elif payout_positions == 2:
            hole_data, pl = update_hole_data_high_points(hole_data, points_list, pot, 80)
            hole_data, _ = update_hole_data_high_points(hole_data, pl, pot, 20)
        elif payout_positions == 3:
            hole_data, pl = update_hole_data_high_points(hole_data, points_list, pot, 70)
            hole_data, pl = update_hole_data_high_points(hole_data, pl, pot, 20)
            hole_data, _ = update_hole_data_high_points(hole_data, pl, pot, 10)
    else:
        score_list = [h["player_score"] for h in hole_data]
        if payout_positions == 1:
            hole_data, _ = update_hole_data_low_score(hole_data, score_list, pot)
        elif payout_positions == 2:
            hole_data, sl = update_hole_data_low_score(hole_data, score_list, pot, 80)
            hole_data, _ = update_hole_data_low_score(hole_data, sl, pot, 20)
        elif payout_positions == 3:
            hole_data, sl = update_hole_data_low_score(hole_data, score_list, pot, 70)
            hole_data, sl = update_hole_data_low_score(hole_data, sl, pot, 20)
            hole_data, _ = update_hole_data_low_score(hole_data, sl, pot, 10)
    return hole_data


def update_player_hcp(hole_data):
    for pd in hole_data:
        player = models.Player.objects.filter(pk=pd["player_id"]).first()
        player.update_hcp(pd["game_hcp"])


def score_game(game):
    hole_list = get_hole_list_for_game(game)
    all_scores = get_all_scores_for_game(game)
    hole_data = get_hole_data_for_game(game, final_scores=True)
    if game.game_type == "stableford":
        scores = score_hole_data(hole_data, game.pot, game.payout_positions, use_points=True)
    else:
        scores = score_hole_data(hole_data, game.pot, game.payout_positions)
    game_score = {
        "all_scores": all_scores,
        "hole_list": hole_list,
        "scores": scores,
    }
    if game.use_skins:
        skins = get_skins_all_scores(all_scores, game.skin_cost)
        game_score.update({"skins": skins})
    if game.use_teams:
        team_scores = score_teams(game)
        game_score.update({"team_scores": team_scores})
    if game.league_game:
        update_player_hcp(hole_data)
    return game_score


def get_player_scores_for_course(player, course):
    scores = []
    for game in models.Game.objects.filter(course=course, league_game=True):
        if player in game.players.all():
            player_mem = models.PlayerMembership.objects.filter(
                game=game, player=player
            ).first()
            scores.append(player_mem.game_score)
    return scores


def get_player_league_standings(player, course):
    scores = get_player_scores_for_course(player, course)
    if not len(scores):
        avg = f"HCP:{player.handicap}"
        points = course.points - round_up(player.handicap)
    elif len(scores) > 1:
        avg = round_up(sum(scores)/len(scores))
        points = course.points - (avg - course.par)
    return avg, points


def get_league_standings():
    league_standings = []
    for player in models.Player.objects.all():
        points = 36 - round_up(player.handicap)
        player_standing = {
            "id": player.id,
            "name": player.name,
            "hcp": player.handicap,
            "points": points
        }
        league_standings.append(player_standing)
    league_standings.sort(key=lambda p: p["hcp"])
    return league_standings
