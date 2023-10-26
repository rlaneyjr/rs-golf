from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

HOLE_CHOICES = (
    ("9", "9 Holes"),
    ("18", "18 Holes"),
)

PAR_CHOICES = (
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
)

User = get_user_model()


class GolfCourse(models.Model):
    name = models.CharField(max_length=128)
    initials = models.CharField(verbose_name="Course Initials", max_length=5, default="GC")
    hole_count = models.CharField(
        max_length=64, choices=HOLE_CHOICES, default=HOLE_CHOICES[1]
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


class Hole(models.Model):
    class Par(models.IntegerChoices):
        PAR_3 = 3
        PAR_4 = 4
        PAR_5 = 5

    class HoleOrder(models.IntegerChoices):
        HOLE_1 = 1
        HOLE_2 = 2
        HOLE_3 = 3
        HOLE_4 = 4
        HOLE_5 = 5
        HOLE_6 = 6
        HOLE_7 = 7
        HOLE_8 = 8
        HOLE_9 = 9
        HOLE_10 = 10
        HOLE_11 = 11
        HOLE_12 = 12
        HOLE_13 = 13
        HOLE_14 = 14
        HOLE_15 = 15
        HOLE_16 = 16
        HOLE_17 = 17
        HOLE_18 = 18

    name = models.CharField(max_length=64, blank=True)
    nickname = models.CharField(max_length=128, blank=True)
    par = models.PositiveSmallIntegerField(choices=Par.choices, default=Par.PAR_3)
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(choices=HoleOrder.choices, default=HoleOrder.HOLE_1)
    handicap = models.PositiveSmallIntegerField(choices=HoleOrder.choices, default=HoleOrder.HOLE_1)

    def __str__(self):
        return f"{self.course.initials}, Hole {self.order}, Par {self.par}"

    class Meta:
        unique_together = ["course", "order", "handicap"]


class Tee(models.Model):
    class TeeColor(models.TextChoices):
        BLACK = "BLACK", _("Black")
        BLUE = "BLUE", _("Blue")
        GOLD = "GOLD", _("Gold")
        WHITE = "WHITE", _("White")
        RED = "RED", _("Red")

    color = models.CharField(
        verbose_name="Tee Color",
        max_length=5,
        choices=TeeColor.choices,
        default=TeeColor.BLUE,
    )
    distance = models.CharField(verbose_name="Tee to Hole Distance", max_length=3)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["color", "hole"]


class Game(models.Model):
    STATUS_CHOICES = (
        ("setup", "Setup"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("not_finished", "Not Finished"),
    )

    date_played = models.DateTimeField(blank=True, null=True)
    course = models.ForeignKey(GolfCourse, on_delete=models.PROTECT)
    holes_played = models.CharField(
        max_length=2, choices=HOLE_CHOICES, default=HOLE_CHOICES[1]
    )
    status = models.CharField(
        max_length=64, choices=STATUS_CHOICES, default=STATUS_CHOICES[0]
    )
    players = models.ManyToManyField(
        "Player", through="PlayerGameLink", through_fields=("game", "player")
    )

    def start(self):
        self.status = "active"
        self.date_played = timezone.now()
        self.save()


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

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["name", "handicap", "added_by"]


class PlayerGameLink(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class HoleScore(models.Model):
    SCORE_CHOICES = (
        (-3, "Albatross"),
        (-2, "Eagle"),
        (-1, "Birdie"),
        (0, "Par"),
        (1, "Bogey"),
        (2, "Double Bogey"),
        (3, "Triple Bogey"),
    )

    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    score = models.IntegerField(choices=SCORE_CHOICES, default=SCORE_CHOICES[3])
    game = models.ForeignKey(PlayerGameLink, on_delete=models.CASCADE)


class TeeTime(models.Model):
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    tee_time = models.DateTimeField()
    players = models.ManyToManyField("Player")
    holes_to_play = models.CharField(
        max_length=2, choices=HOLE_CHOICES, default=HOLE_CHOICES[1]
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.name} - {self.holes_to_play} - {self.tee_time}"
