from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class HoleChoices(models.IntegerChoices):
    HOLES_9 = 9, _("9 Holes")
    HOLES_18 = 18, _("18 Holes")


class GolfCourse(models.Model):
    name = models.CharField(max_length=128)
    initials = models.CharField(verbose_name="Course Initials", max_length=5, default="GC")
    hole_count = models.PositiveSmallIntegerField(
        choices=HoleChoices.choices, default=HoleChoices.HOLES_18
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
    PAR_CHOICES = (
        (3, "3"),
        (4, "4"),
        (5, "5"),
    )

    HOLE_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
        (11, "11"),
        (12, "12"),
        (13, "13"),
        (14, "14"),
        (15, "15"),
        (16, "16"),
        (17, "17"),
        (18, "18"),
    )

    nickname = models.CharField(max_length=128, blank=True)
    par = models.PositiveSmallIntegerField(choices=PAR_CHOICES, default=PAR_CHOICES[0], blank=True)
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(choices=HOLE_CHOICES, default=HOLE_CHOICES[0])
    handicap = models.PositiveSmallIntegerField(choices=HOLE_CHOICES, default=HOLE_CHOICES[0], blank=True)

    def __str__(self):
        return f"{self.course.initials} - Hole {self.order}"

    class Meta:
        unique_together = ["course", "order", "handicap"]


class Tee(models.Model):
    TEE_COLORS = (
        ("black", _("Black")),
        ("blue", _("Blue")),
        ("gold", _("Gold")),
        ("white", _("White")),
        ("green", _("Green")),
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

    def __str__(self):
        return f"{self.hole} - {self.color}"

    class Meta:
        unique_together = ["color", "hole"]


class Game(models.Model):
    STATUS_CHOICES = (
        ("setup", _("Setup")),
        ("active", _("Active")),
        ("completed", _("Completed")),
        ("not_finished", _("Not Finished")),
    )

    date_played = models.DateTimeField(blank=True, null=True)
    course = models.ForeignKey(GolfCourse, on_delete=models.PROTECT)
    holes_played = models.PositiveSmallIntegerField(
        choices=HoleChoices.choices, default=HoleChoices.HOLES_18
    )
    status = models.CharField(
        max_length=64, choices=STATUS_CHOICES, default=STATUS_CHOICES[0]
    )
    players = models.ManyToManyField(
        "Player", through="PlayerGameLink", through_fields=("game", "player")
    )

    def __str__(self):
        return f"{self.course.initials} - {self.date_played} - {self.status}"

    def get_status_display(self):
        return f"{self.status}"

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
        return f"{self.name} - {self.handicap}"

    class Meta:
        unique_together = ["name", "handicap", "added_by"]


class PlayerGameLink(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class HoleScore(models.Model):
    SCORE_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
    )

    game = models.ForeignKey(PlayerGameLink, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, default=SCORE_CHOICES[0])

    def __str__(self):
        return f"{self.hole} - {self.score - self.hole.par}"


class TeeTime(models.Model):
    WHICH_CHOICES = (
        ("all", _("All")),
        ("front", _("Front")),
        ("back", _("Back")),
    )
    course = models.ForeignKey(GolfCourse, on_delete=models.CASCADE)
    tee_time = models.DateTimeField(
        default=datetime.now().strftime("%m-%d-%Y %H:%M"),
    )
    players = models.ManyToManyField("Player")
    holes_to_play = models.PositiveSmallIntegerField(
        choices=HoleChoices.choices, default=HoleChoices.HOLES_18
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
