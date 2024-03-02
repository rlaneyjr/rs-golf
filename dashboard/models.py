from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from dashboard import utils


User = get_user_model()


class GameTypeChoices(models.TextChoices):
    BEST_BALL = "best-ball", _("Best Ball")
    STROKE = "stroke", _("Stroke")
    SKINS = "skins", _("Skins")
    STROKE_SKINS = "stroke-skins", _("Stroke w/Skins")
    BEST_BALL_SKINS = "best-ball-skins", _("Best Ball w/Skins")


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


class ScoreChoices(models.IntegerChoices):
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


class Hole(models.Model):
    name = models.CharField(max_length=7, choices=HoleNameChoices.choices, default=HoleNameChoices.HOLE_1)
    nickname = models.CharField(max_length=64, blank=True)
    par = models.PositiveSmallIntegerField(choices=ParChoices.choices, default=ParChoices.PAR_4, blank=True)
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(choices=OrderChoices.choices, default=OrderChoices._1, blank=True)
    handicap = models.PositiveSmallIntegerField(choices=OrderChoices.choices, default=OrderChoices._1, blank=True)

    class Meta:
        unique_together = ["name", "course", "order", "handicap"]

    def __str__(self):
        return f"{self.course.initials} {self.name}"


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
    game_type = models.CharField(
        max_length=32,
        choices=GameTypeChoices.choices,
        default=GameTypeChoices.BEST_BALL,
    )
    date_played = models.DateTimeField(blank=True, null=True)
    course = models.ForeignKey(GolfCourse, on_delete=models.PROTECT)
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
            MinMoneyValidator({"USD": 1}),
            MaxMoneyValidator({"USD": 10}),
        ],
    )
    score = models.JSONField(blank=True, null=True)

    @property
    def pot(self):
        return self.buy_in * self.players.count()

    @property
    def par(self):
        return utils.get_par_for_game(self)

    def start(
            self,
            holes_to_play=None,
            game_type=None,
            buy_in=None,
            skin_cost=None,
        ):
        # if not any([game_type, self.game_type]):
        #     raise ValidationError("You must provide a game type")
        if holes_to_play != None:
            self.holes_to_play = holes_to_play
        if game_type != None:
            self.game_type = game_type
        if buy_in != None:
            self.buy_in = buy_in
        if skin_cost != None:
            self.skin_cost = skin_cost
        if not self.date_played:
            self.date_played = timezone.now()
        utils.create_teams_for_game(self)
        utils.create_hole_scores_for_game(self)
        self.status = GameStatusChoices.ACTIVE
        self.save()

    def stop(self):
        if self.status != GameStatusChoices.COMPLETED:
            self.score = utils.score_game(self)
            self.status = GameStatusChoices.COMPLETED
            self.save()

    def reset(self):
        self.players.set(clear=True)
        self.score = None
        self.status = GameStatusChoices.SETUP
        self.save()

    def __str__(self):
        return f"{self.course.initials} - {self.date_played.date()} - {self.status}"

    class Meta:
        ordering = ["date_played", "status"]
        verbose_name_plural = "games"


class Player(models.Model):
    name = models.CharField(max_length=64)
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

    class Meta:
        unique_together = ["name", "handicap", "user_account"]

    @property
    def first_name(self):
        return self.name.split()[0]

    @property
    def last_name(self):
        return self.name.split()[1]

    def __str__(self):
        return f"{self.name}"

    def update_hcp(self, new_hcp):
        _hcp = sum([self.handicap, new_hcp])/len([self.handicap, new_hcp])
        self.handicap = round(_hcp, 1)
        self.save()


class Team(models.Model):
    name = models.CharField(max_length=64)
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

    def __str__(self):
        string = f"{self.player}"
        if self.team:
            string = f"{string} - {self.team}"
        if self.skins:
            string = f"{string} - Skins"
        return string


class HoleScore(models.Model):
    player = models.ForeignKey(PlayerMembership, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=ScoreChoices.choices, default=ScoreChoices._0)

    def __str__(self):
        return f"{self.player} - {self.hole} - {self.score}"


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
        return f"{self.course.initials} - {self.holes_to_play} - {self.tee_time}"

    def clean(self):
        if self.course.hole_count - self.holes_to_play == 9:
            if self.which_holes == 'all':
                raise ValidationError("Please choose front or back")
