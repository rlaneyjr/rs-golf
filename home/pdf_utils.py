from home import models
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


LEFT_MARGIN = inch * 0.25
TOP_MARGIN = inch * 0.15
MARGIN = LEFT_MARGIN

PAGESIZE = (inch * 8, inch * 3)


def generate_header_for_scorecard(game):
    data = []
    first_row = ["Hole"]
    for i in range(int(game.holes_played)):
        first_row.append(str(i + 1))

    # if we played 18 we need to add in a separator
    if game.holes_played == "18":
        first_row.insert(10, "Front")
        first_row.append("Back")

    first_row.append("Total")
    data.append(first_row)

    second_row = ["Par"]
    hole_list = models.Hole.objects.filter(course=game.course).order_by("order")
    par_total = 0

    if game.holes_played == "9":
        for hole in hole_list:
            second_row.append(str(hole.par))
            par_total += hole.par
    else:
        front_par = 0
        back_par = 0
        for index, hole in enumerate(hole_list):
            second_row.append(str(hole.par))
            par_total += hole.par
            if index < 9:
                front_par += hole.par
            else:
                back_par += hole.par

        second_row.insert(10, front_par)
        second_row.append(back_par)

    second_row.append(par_total)

    data.append(second_row)

    return data


def generate_score_data(game):
    data = []

    headers = generate_header_for_scorecard(game)

    for header in headers:
        data.append(header)

    player_link_list = models.PlayerGameLink.objects.filter(game=game)

    for player_link in player_link_list:
        player_row = []
        player_row.append(player_link.player.name)

        score_list = models.HoleScore.objects.filter(game=player_link).order_by("hole__order")
        player_total_score = 0

        if game.holes_played == "9":
            for score_item in score_list:
                player_row.append(str(score_item.score))
                player_total_score += score_item.score

            player_row.append(str(player_total_score))
        else:
            front_nine_score = 0
            back_nine_score = 0
            for index, score_item in enumerate(score_list):
                player_row.append(str(score_item.score))
                player_total_score += score_item.score
                if index < 9:
                    front_nine_score += score_item.score
                else:
                    back_nine_score += score_item.score
            player_row.insert(10, str(front_nine_score))
            player_row.append(str(back_nine_score))
            player_row.append(str(player_total_score))

        data.append(player_row)
    return data


def generate_data_for_scorecard(game):
    data = {
        "course_name": game.course.name,
        "date_played": game.date_played.strftime("%m-%d-%Y"),
        "scores": generate_score_data(game)
    }

    return data


def generate_scorecard(game):
    buffer = BytesIO()
    story = []
    doc = SimpleDocTemplate(
        buffer,
        leftMargin=LEFT_MARGIN,
        rightMargin=LEFT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=TOP_MARGIN,
        pagesize=PAGESIZE
    )

    game_data = generate_data_for_scorecard(game)

    base_styles = getSampleStyleSheet()
    course_name_paragraph = Paragraph(game_data["course_name"], style=base_styles["Normal"])
    date_played_paragraph = Paragraph(game_data["date_played"], style=base_styles["Normal"])

    story.append(course_name_paragraph)
    story.append(date_played_paragraph)
    story.append(Spacer(width=0, height=MARGIN))

    styles = [
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.gray, colors.white]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (10, 0), (10, -1), colors.red)
    ]

    if game.holes_played == "18":
        styles.append(("BACKGROUND", (20, 0), (20, -1), colors.red))
        styles.append(("BACKGROUND", (21, 0), (21, -1), colors.red))

    table_style = TableStyle(styles)

    table = Table(game_data["scores"], hAlign="LEFT")
    table.setStyle(table_style)

    story.append(table)
    doc.build(story)

    return buffer
