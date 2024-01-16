from rest_framework import serializers
from rest_framework.reverse import reverse
from dashboard import models
from users.api import serializers as core_serializers
from djmoney.contrib.django_rest_framework import MoneyField


class PlayerSerializer(serializers.ModelSerializer):
    added_by = core_serializers.UserSerializer(many=False, read_only=True)
    user_account = core_serializers.UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Player
        fields = "__all__"

    def create(self, validated_data):
        return models.Player.objects.create(**validated_data)


class GolfCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GolfCourse
        fields = "__all__"


class HoleScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HoleScore
        fields = "__all__"


class TeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tee
        fields = "__all__"


class TeeTimeSerializer(serializers.ModelSerializer):
    course = GolfCourseSerializer(many=False)
    players = PlayerSerializer(many=True)

    class Meta:
        model = models.TeeTime
        fields = "__all__"


class SimplePlayerMembershipSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False, read_only=True)

    class Meta:
        model = models.PlayerMembership
        fields = ["id", "player"]


class PlayerMembershipSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False, read_only=True)
    scores = serializers.SerializerMethodField()

    class Meta:
        model = models.PlayerMembership
        fields = [
            "id",
            "player",
            "game",
            "team",
            "scores"
        ]

    def get_scores(self, obj):
        if type(obj) == "Team":
            players = models.PlayerMembership.objects.filter(team=obj)
        elif type(obj) == "Player":
            players = models.PlayerMembership.objects.filter(player=obj)
        else:
            players = models.PlayerMembership.objects.filter(game=obj)
        queryset = models.HoleScore.objects.filter(player__in=[players])
        return [HoleScoreSerializer(m).data for m in queryset]


class GameSerializer(serializers.ModelSerializer):
    course = GolfCourseSerializer(many=False, read_only=True)
    players = PlayerMembershipSerializer(many=True)
    buy_in = MoneyField(max_digits=3, decimal_places=0)
    skin_cost = MoneyField(max_digits=2, decimal_places=0)
    player_list = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()
    score = serializers.JSONField(read_only=True, source="score", allow_null=True)

    class Meta:
        model = models.Game
        fields = [
            "id",
            "game_type",
            "date_played",
            "course",
            "players",
            "holes_played",
            "which_holes",
            "status",
            "buy_in",
            "skin_cost",
            "score",
            "player_list",
            "detail_url",
        ]
        depth = 1

    def create(self, validated_data):
        return models.Game.objects.create(**validated_data)

    def get_player_list(self, obj):
        queryset = models.PlayerMembership.objects.filter(game=obj)
        return [SimplePlayerMembershipSerializer(m).data for m in queryset]

    def get_detail_url(self, obj):
        if "request" in self.context:
            return reverse(
                "dashboard:game-detail",
                request=self.context["request"],
                args={obj.id}
            )
        return ""


class TeamSerializer(serializers.ModelSerializer):
    game = GameSerializer(many=False, read_only=True)
    players = PlayerMembershipSerializer(many=True)
    scores = serializers.SerializerMethodField()

    class Meta:
        model = models.PlayerMembership
        fields = [
            "id",
            "name",
            "game",
            "players",
            "handicap",
            "scores"
        ]

    def get_scores(self, obj):
        team_players = models.PlayerMembership.objects.filter(team=obj)
        queryset = models.HoleScore.objects.filter(player__in=[team_players])
        return [HoleScoreSerializer(m).data for m in queryset]
