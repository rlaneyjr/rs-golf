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


class GameStatusChoices(models.TextChoices):
    SETUP = "setup", _("Setup")
    ACTIVE = "active", _("Active")
    COMPLETED = "completed", _("Completed")


class PayoutChoices(models.IntegerChoices):
    _1 = 1
    _2 = 2
    _3 = 3


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


class ParChoices(models.IntegerChoices):
    PAR_3 = 3, _("Par 3")
    PAR_4 = 4, _("Par 4")
    PAR_5 = 5, _("Par 5")


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


class TeeColorChoices(models.TextChoices):
    BLACK = "black", _("Black")
    BLUE = "blue", _("Blue")
    GOLD = "gold", _("Gold")
    WHITE = "white", _("White")
    GREEN = "green", _("Green")
    RED = "red", _("Red")
    ORANGE = "orange", _("Orange")


class HolesToPlayChoices(models.IntegerChoices):
    HOLES_9 = 9, _("9 Holes")
    HOLES_18 = 18, _("18 Holes")


class WhichHolesChoices(models.TextChoices):
    ALL = "all", _("All")
    FRONT = "front", _("Front 9")
    BACK = "back", _("Back 9")


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


class GolfCourse(models.Model):
    name = models.CharField(max_length=128)
    initials = models.CharField(
        verbose_name="Course Initials",
        max_length=5,
        default="GC"
    )
    hole_count = models.PositiveSmallIntegerField(
        choices=HolesToPlayChoices.choices,
        default=HolesToPlayChoices.HOLES_18
    )
    tee_time_link = models.URLField(blank=True)
    website_link = models.URLField(blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=64, blank=True)
    zip_code = models.CharField(max_length=128, blank=True)
    card = models.ImageField(
        upload_to="images",
        default=None,
        blank=True,
        null=True
    )
    overview = models.ImageField(
        upload_to="images",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ["name", "city", "state"]
        ordering = ["state", "city"]

    def __str__(self):
        return self.name

    @property
    def par(self):
        return utils.get_par_for_course(self)

    @property
    def points(self):
        return utils.round_up(self.par/2)


class Hole(models.Model):
    name = models.CharField(
        max_length=7,
        choices=HoleNameChoices.choices,
        default=HoleNameChoices.HOLE_1
    )
    nickname = models.CharField(max_length=64, blank=True)
    par = models.PositiveSmallIntegerField(
        choices=ParChoices.choices,
        default=ParChoices.PAR_4
    )
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(
        choices=OrderChoices.choices,
        default=OrderChoices._1
    )
    handicap = models.PositiveSmallIntegerField(
        choices=OrderChoices.choices,
        default=OrderChoices._1
    )

    def __str__(self):
        return f"{self.course.initials} - {self.name}"

    class Meta:
        unique_together = ["name", "course", "order", "handicap"]
        ordering = ["course", "order"]


class Tee(models.Model):
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    color = models.CharField(
        verbose_name="Tee Color",
        max_length=6,
        choices=TeeColorChoices.choices,
        default=TeeColorChoices.BLACK,
    )
    distance = models.CharField(
        verbose_name="Tee distance in yards",
        max_length=3
    )

    def __str__(self):
        return f"{self.hole} - {self.color}"

    class Meta:
        unique_together = ["hole", "color"]
        ordering = ["hole", "-distance"]


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
    date_played = models.DateTimeField(default=timezone.now)
    holes_to_play = models.PositiveSmallIntegerField(
        choices=HolesToPlayChoices.choices,
        default=HolesToPlayChoices.HOLES_18
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
        "Player",
        through="PlayerMembership",
        through_fields=("game", "player")
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
        num_players = utils.num_players_in_skins(self)
        return self.skin_cost * num_players * self.holes_to_play

    def __str__(self):
        if self.status == GameStatusChoices.COMPLETED:
            return f"{self.course.initials} - {self.date_played.date()}"
        else:
            return f"{self.course.initials} - {self.status}"

    def start(self, **kwargs):
        for key, value in kwargs.items():
            if key == "which_holes":
                utils.set_holes_for_game(self, value)
            if key == "game_type":
                self.game_type = value
            if key == "buy_in":
                self.buy_in = value
            if key == "skin_cost":
                self.skeyin_cost = value
            if key == "use_teams":
                self.use_teams = value
            if key == "league_game":
                self.league_game = value
            if key == "payout_positions":
                self.payout_positions = value
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
        num_holes = self.course.hole_count - self.holes_to_play
        if num_holes == 9 and self.which_holes == WhichHolesChoices.ALL:
            raise ValidationError("Please choose front or back")

    def delete(self, **kwargs):
        utils.clean_game(self)
        super().delete(**kwargs)

    class Meta:
        ordering = ["date_played", "status"]
        verbose_name_plural = "games"
        get_latest_by = "date_played"


class Player(models.Model):
    first_name = models.CharField(
        max_length=32,
        default=None,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=32,
        default=None,
        blank=True,
        null=True
    )
    email = models.EmailField(
        max_length=254,
        default=None,
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=12,
        default=None,
        blank=True,
        null=True
    )
    handicap = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=20.0
    )
    photo = models.ImageField(
        upload_to="images",
        default=None,
        blank=True,
        null=True
    )
    user_account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )
    added_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="added_by"
    )

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["first_name", "last_name"]
        ordering = ["last_name", "first_name"]
        verbose_name_plural = "players"


class Team(models.Model):
    name = models.CharField(max_length=32)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    players = models.ManyToManyField(
        "Player",
        through="PlayerMembership",
        through_fields=("team", "player")
    )
    handicap = models.DecimalField(
        max_digits=3, decimal_places=1, default=20.0
    )

    def __str__(self):
        return f"{self.game} - {self.name}"

    class Meta:
        ordering = ["game", "name"]
        verbose_name_plural = "teams"


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
    game_handicap = models.SmallIntegerField(
        default=None,
        blank=True,
        null=True
    )
    game_score = models.SmallIntegerField(
        default=None,
        blank=True,
        null=True
    )
    game_points = models.SmallIntegerField(
        default=None,
        blank=True,
        null=True
    )

    @property
    def points_needed(self):
        return self.game.points - utils.round_up(self.player.handicap)

    def __str__(self):
        if self.team:
            return f"{self.player} - {self.team}"
        else:
            return f"{self.player} - {self.game}"

    class Meta:
        unique_together = ["game", "player"]
        order_with_respect_to = "game"


class HoleScore(models.Model):
    player = models.ForeignKey(PlayerMembership, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    strokes = models.PositiveSmallIntegerField(
        choices=StrokeChoices.choices,
        default=StrokeChoices._0
    )

    @property
    def is_scored(self):
        if self.strokes == StrokeChoices._0:
            return False
        return True

    @property
    def points(self):
        if self.is_scored:
            return utils.points_map.get(self.strokes - self.hole.par)
        return 0

    @property
    def score(self):
        if self.is_scored:
            return self.strokes - self.hole.par
        return 0

    @property
    def score_name(self):
        if not self.is_scored:
            return _("Hole not scored")
        if self.strokes == 1:
            return _("Hole in One")
        elif self.strokes == 2:
            if self.hole.par == 3:
                return _("Birdie")
            elif self.hole.par == 4:
                return _("Eagle")
            elif self.hole.par == 5:
                return _("Albatross")
        elif self.strokes == 3:
            if self.hole.par == 3:
                return _("Par")
            elif self.hole.par == 4:
                return _("Birdie")
            elif self.hole.par == 5:
                return _("Eagle")
        elif self.strokes == 4:
            if self.hole.par == 3:
                return _("Bogey")
            elif self.hole.par == 4:
                return _("Par")
            elif self.hole.par == 5:
                return _("Birdie")
        elif self.strokes == 5:
            if self.hole.par == 4:
                return _("Bogey")
            elif self.hole.par == 5:
                return _("Par")
        elif self.strokes == 6:
            if self.hole.par == 5:
                return _("Bogey")
        return _("Double Bogey Max")

    def __str__(self):
        return f"{self.player} - {self.hole}"

    def score_hole(self, strokes: int=None):
        if strokes is not None:
            self.strokes = strokes
            self.save()

    def reset_score(self):
        if self.is_scored:
            self.strokes = StrokeChoices._0
            self.save()

    class Meta:
        ordering = ["player", "hole", "-strokes"]
        verbose_name_plural = "scores"


class TeeTime(models.Model):
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    tee_time = models.DateTimeField()
    players = models.ManyToManyField("Player")
    holes_to_play = models.PositiveSmallIntegerField(
        choices=HolesToPlayChoices.choices,
        default=HolesToPlayChoices.HOLES_18
    )
    which_holes = models.CharField(
        max_length=5,
        choices=WhichHolesChoices.choices,
        default=WhichHolesChoices.ALL,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.initials} - {self.tee_time.date()}"

    def clean(self):
        num_holes = self.course.hole_count - self.holes_to_play
        if num_holes == 9 and self.which_holes == WhichHolesChoices.ALL:
            raise ValidationError("Please choose front or back")

    class Meta:
        ordering = ["tee_time"]
        verbose_name_plural = "tee_times"

