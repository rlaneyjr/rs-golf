from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from djmoney.money import Money
from dashboard import utils

User = get_user_model()


def get_ttcc_course():
    return GolfCourse.objects.get(initials="TTCC").id


class GameTypeChoices(models.TextChoices):
    BEST_BALL = "best-ball", _("Best Ball")
    STROKE = "stroke", _("Stroke")
    STABLEFORD = "stableford", _("Stableford")


class HolesToPlayChoices(models.IntegerChoices):
    HOLES_9 = 9, _("9 Holes")
    HOLES_18 = 18, _("18 Holes")


class WhichHolesChoices(models.TextChoices):
    ALL = "all", _("All")
    FRONT = "front", _("Front 9")
    BACK = "back", _("Back 9")


class ParChoices(models.IntegerChoices):
    PAR_3 = 3, _("Par 3")
    PAR_4 = 4, _("Par 4")
    PAR_5 = 5, _("Par 5")


class PayoutChoices(models.IntegerChoices):
    _1 = 1
    _2 = 2
    _3 = 3


class OrderChoices(models.IntegerChoices):
    _1 = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9
    _10 = 10
    _11 = 11
    _12 = 12
    _13 = 13
    _14 = 14
    _15 = 15
    _16 = 16
    _17 = 17
    _18 = 18


class StrokeChoices(models.IntegerChoices):
    _0 = 0
    _1 = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9


class ScoreChoices(models.IntegerChoices):
    ALBATROSS = -3, _("Albatross")
    EAGLE = -2, _("Eagle")
    BIRDIE = -1, _("Birdie")
    PAR = 0, _("Par")
    BOGEY = 1, _("Bogey")
    DOUBLE_BOGEY = 2, _("Double Bogey")
    TRIPLE_BOGEY = 3, _("Triple Bogey")


class HoleNameChoices(models.TextChoices):
    HOLE_1 = "Hole1", _("Hole 1")
    HOLE_2 = "Hole2", _("Hole 2")
    HOLE_3 = "Hole3", _("Hole 3")
    HOLE_4 = "Hole4", _("Hole 4")
    HOLE_5 = "Hole5", _("Hole 5")
    HOLE_6 = "Hole6", _("Hole 6")
    HOLE_7 = "Hole7", _("Hole 7")
    HOLE_8 = "Hole8", _("Hole 8")
    HOLE_9 = "Hole9", _("Hole 9")
    HOLE_10 = "Hole10", _("Hole 10")
    HOLE_11 = "Hole11", _("Hole 11")
    HOLE_12 = "Hole12", _("Hole 12")
    HOLE_13 = "Hole13", _("Hole 13")
    HOLE_14 = "Hole14", _("Hole 14")
    HOLE_15 = "Hole15", _("Hole 15")
    HOLE_16 = "Hole16", _("Hole 16")
    HOLE_17 = "Hole17", _("Hole 17")
    HOLE_18 = "Hole18", _("Hole 18")


class GameStatusChoices(models.TextChoices):
    SETUP = "setup", _("Setup")
    ACTIVE = "active", _("Active"),
    COMPLETED = "completed", _("Completed"),


class GolfCourse(models.Model):
    name = models.CharField(max_length=128)
    initials = models.CharField(verbose_name="Course Initials", max_length=5, default="GC")
    hole_count = models.PositiveSmallIntegerField(
        choices=HolesToPlayChoices.choices, default=HolesToPlayChoices.HOLES_18
    )
    tee_time_link = models.URLField(blank=True)
    website_link = models.URLField(blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=64, blank=True)
    zip_code = models.CharField(max_length=128, blank=True)
    card = models.ImageField(upload_to="images", default=None, blank=True, null=True)
    overview = models.ImageField(upload_to="images", default=None, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def par(self):
        return utils.get_par_for_course(self)

    @property
    def points(self):
        return round(self.par/2)


class Hole(models.Model):
    name = models.CharField(max_length=7, choices=HoleNameChoices.choices, default=HoleNameChoices.HOLE_1)
    nickname = models.CharField(max_length=64, blank=True)
    par = models.PositiveSmallIntegerField(choices=ParChoices.choices, default=ParChoices.PAR_4)
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(choices=OrderChoices.choices, default=OrderChoices._1)
    handicap = models.PositiveSmallIntegerField(choices=OrderChoices.choices, default=OrderChoices._1)

    class Meta:
        unique_together = ["name", "course", "order", "handicap"]

    def __str__(self):
        return f"{self.course.initials} - {self.name}"


class Tee(models.Model):
    TEE_COLORS = (
        ("black", _("Black")),
        ("blue", _("Blue")),
        ("gold", _("Gold")),
        ("white", _("White")),
        ("red", _("Red")),
    )

    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    color = models.CharField(
        verbose_name="Tee Color",
        max_length=5,
        choices=TEE_COLORS,
        default=TEE_COLORS[1],
    )
    distance = models.CharField(verbose_name="Tee distance in yards", max_length=3)

    class Meta:
        unique_together = ["color", "hole"]

    def __str__(self):
        return f"{self.hole} - {self.color}"


class Game(models.Model):
    course = models.ForeignKey(
        GolfCourse,
        on_delete=models.PROTECT,
        default=get_ttcc_course,
    )
    game_type = models.CharField(
        max_length=32,
        choices=GameTypeChoices.choices,
        default=GameTypeChoices.STABLEFORD,
    )
    date_played = models.DateTimeField(blank=True, null=True)
    holes_played = models.PositiveSmallIntegerField(
        choices=HolesToPlayChoices.choices, default=HolesToPlayChoices.HOLES_18
    )
    which_holes = models.CharField(
        max_length=5,
        choices=WhichHolesChoices.choices,
        default=WhichHolesChoices.ALL,
    )
    status = models.CharField(
        max_length=64,
        choices=GameStatusChoices.choices,
        default=GameStatusChoices.SETUP,
    )
    players = models.ManyToManyField(
        "Player", through="PlayerMembership", through_fields=("game", "player")
    )
    buy_in = MoneyField(
        name="buy_in",
        verbose_name="Per-player buy-in",
        max_digits=3,
        decimal_places=0,
        default=10,
        default_currency="USD",
        validators=[
            MinMoneyValidator({"USD": 10}),
            MaxMoneyValidator({"USD": 100}),
        ],
    )
    skin_cost = MoneyField(
        name="skin_cost",
        verbose_name="Per-hole skin cost",
        max_digits=2,
        decimal_places=0,
        default=1,
        default_currency="USD",
        validators=[
            MinMoneyValidator({"USD": 0}),
            MaxMoneyValidator({"USD": 10}),
        ],
    )
    score = models.JSONField(blank=True, null=True)
    use_teams = models.BooleanField(default=False)
    use_skins = models.BooleanField(default=True)
    league_game = models.BooleanField(default=True)
    payout_positions = models.PositiveSmallIntegerField(
        choices=PayoutChoices.choices,
        default=PayoutChoices._1,
    )

    @property
    def par(self):
        return utils.get_par_for_game(self)

    @property
    def pot(self):
        return self.buy_in * self.players.count()

    @property
    def points(self):
        return self.course.points

    @property
    def skin_pot(self):
        return self.skin_cost * utils.num_players_in_skins(self) * self.holes_played

    def start(
            self,
            holes_to_play=None,
            game_type=None,
            buy_in=None,
            skin_cost=None,
            use_teams=None,
            league_game=None,
            payout_positions=None,
        ):
        # if not any([game_type, self.game_type]):
        #     raise ValidationError("You must provide a game type")
        if holes_to_play is not None:
            self.holes_to_play = holes_to_play
        if game_type is not None:
            self.game_type = game_type
        if buy_in is not None:
            self.buy_in = buy_in
        if skin_cost is not None:
            self.skin_cost = skin_cost
        if use_teams is not None:
            self.use_teams = use_teams
        if league_game is not None:
            self.league_game = league_game
        if not self.date_played:
            self.date_played = timezone.now()
        if payout_positions is not None:
            self.payout_positions = payout_positions
        utils.create_hole_scores_for_game(self)
        if self.use_teams:
            utils.create_teams_for_game(self)
        self.status = GameStatusChoices.ACTIVE
        self.save()

    def stop(self):
        if self.status != GameStatusChoices.COMPLETED:
            self.score = utils.score_game(self)
            self.status = GameStatusChoices.COMPLETED
            self.save()

    def reset(self):
        utils.clean_game(self)
        self.score = None
        self.status = GameStatusChoices.SETUP
        self.save()

    def clean(self):
        if self.course.hole_count - self.holes_played == 9:
            if self.which_holes == 'all':
                raise ValidationError("Please choose front or back")

    def __str__(self):
        return f"{self.course.initials} - {self.date_played.date()} - {self.status}"

    class Meta:
        ordering = ["date_played", "status"]
        verbose_name_plural = "games"


class Player(models.Model):
    first_name = models.CharField(max_length=32, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=32, default=None, blank=True, null=True)
    email = models.EmailField(max_length=254, default=None, blank=True, null=True)
    phone = models.CharField(max_length=12, default=None, blank=True, null=True)
    handicap = models.DecimalField(
        max_digits=3, decimal_places=1, default=20.0
    )
    photo = models.ImageField(
        upload_to="images", default=None, blank=True, null=True
    )
    user_account = models.OneToOneField(
        User, on_delete=models.CASCADE, default=None, blank=True, null=True
    )
    added_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="added_by"
    )
    previous_handicap = models.DecimalField(
        max_digits=3, decimal_places=1, default=None, blank=True, null=True
    )

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name

    def update_hcp(self, game_hcp):
        self.previous_handicap = self.handicap
        self.handicap = round(sum([self.handicap, float(game_hcp)])/2, 1)
        self.save()

    def revert_hcp(self):
        if self.previous_handicap:
            self.handicap = self.previous_handicap
            self.save()

    class Meta:
        ordering = ["first_name", "last_name"]
        unique_together = ["first_name", "last_name"]


class Team(models.Model):
    name = models.CharField(max_length=32)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    players = models.ManyToManyField(
        "Player", through="PlayerMembership", through_fields=("team", "player")
    )
    handicap = models.DecimalField(
        max_digits=3, decimal_places=1, default=20.0
    )

    class Meta:
        ordering = ["game", "name", "handicap"]
        verbose_name_plural = "teams"

    def __str__(self):
        return f"{self.game} - {self.name}"


class PlayerMembership(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_DEFAULT,
        default=None,
        blank=True,
        null=True
    )
    skins = models.BooleanField(default=False)
    game_handicap = models.SmallIntegerField(default=None, blank=True, null=True)
    game_score = models.SmallIntegerField(default=None, blank=True, null=True)
    game_points = models.SmallIntegerField(default=None, blank=True, null=True)

    @property
    def points_needed(self):
        return self.game.points - utils.round_up(self.player.handicap)

    def __str__(self):
        string = f"{self.player.name} - {self.game}"
        if self.team:
            string = f"{string} - {self.team.name}"
        return string


class HoleScore(models.Model):
    player = models.ForeignKey(PlayerMembership, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    strokes = models.PositiveSmallIntegerField(choices=StrokeChoices.choices, default=StrokeChoices._0)
    points = models.PositiveSmallIntegerField(choices=StrokeChoices.choices, default=StrokeChoices._0)
    score = models.SmallIntegerField(choices=ScoreChoices.choices, default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.player} - {self.hole}"

    def score_hole(self, strokes: int):
        self.strokes = strokes
        self.score = strokes - self.hole.par
        self.points = utils.stableford_map.get(strokes - self.hole.par)
        self.save()

    class Meta:
        ordering = ["player", "hole"]
        verbose_name_plural = "scores"


class TeeTime(models.Model):
    WHICH_CHOICES = (
        ("all", _("All")),
        ("front", _("Front")),
        ("back", _("Back")),
    )
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    tee_time = models.DateTimeField()
    players = models.ManyToManyField("Player")
    holes_to_play = models.PositiveSmallIntegerField(
        choices=HolesToPlayChoices.choices, default=HolesToPlayChoices.HOLES_18
    )
    which_holes = models.CharField(
        max_length=5,
        choices=WHICH_CHOICES,
        default=WHICH_CHOICES[0],
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.initials} - {self.tee_time.date()}"

    def clean(self):
        if self.course.hole_count - self.holes_to_play == 9:
            if self.which_holes == 'all':
                raise ValidationError("Please choose front or back")
