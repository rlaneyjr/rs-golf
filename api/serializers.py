from rest_framework import serializers
from rest_framework.reverse import reverse
from home import models
from users.api import serializers as core_serializers


class PlayerSerializer(serializers.ModelSerializer):
    added_by = core_serializers.UserSerializer(many=False, read_only=True)
    user_account = core_serializers.UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Player
        fields = ["id", "name", "handicap", "photo", "added_by", "user_account"]

    def create(self, validated_data):
        return models.Player.objects.create(**validated_data)


class GolfCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GolfCourse
        fields = [
            "id",
            "name",
            "initials",
            "hole_count",
            "tee_time_link",
            "website_link",
            "city",
            "state",
            "zip_code",
            "card",
            "overview",
        ]


class HoleScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HoleScore
        fields = ["id", "hole", "score", "game"]

    # def validate_game(self, value):
    #     print("VALIDATE", value)
    #     if value == "":
    #         raise serializers.ValidationError()
    #     return value


class SimplePlayerGameLinkSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False, read_only=True)

    class Meta:
        model = models.PlayerGameLink
        fields = [
            "id",
            "player",
        ]


class PlayerGameLinkSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False, read_only=True)
    scores = serializers.SerializerMethodField()

    class Meta:
        model = models.PlayerGameLink
        fields = [
            "id",
            "player",
            "scores"
            # "game_set",
            # "holescore_set"
        ]

    def get_scores(self, obj):
        queryset = models.HoleScore.objects.filter(game=obj)
        return [HoleScoreSerializer(m).data for m in queryset]


class GameSerializer(serializers.ModelSerializer):
    # course = GolfCourseSerializer(many=False, read_only=True)
    # players = PlayerGameLinkSerializer(many=True)
    player_list = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Game
        fields = [
            "id",
            "date_played",
            "course",
            "holes_played",
            "status",
            "player_list",
            "detail_url",
        ]
        # extra_kwargs = {"course": ""}
        # fields = "__all__"
        # depth = 1

    def create(self, validated_data):
        course_data = validated_data.pop("course")
        game = models.Game.objects.create(course=course_data, **validated_data)
        return game

    def get_player_list(self, obj):
        queryset = models.PlayerGameLink.objects.filter(game=obj)
        return [SimplePlayerGameLinkSerializer(m).data for m in queryset]

    def get_detail_url(self, obj):
        if "request" in self.context:
            return reverse(
                "home:game-detail", request=self.context["request"], args={obj.id}
            )
        return ""


class TeeTimeSerializer(serializers.ModelSerializer):
    course = GolfCourseSerializer(many=False)
    players = PlayerSerializer(many=True)

    class Meta:
        model = models.TeeTime
        fields = ["id", "course", "tee_time", "holes_to_play", "is_active", "players"]


class TeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tee
        fields = ["id", "color", "distance", "hole"]
