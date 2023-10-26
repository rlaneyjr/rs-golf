from django.shortcuts import get_object_or_404
from django.conf import settings
from . import serializers
from home import models
from home import utils
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class GolfCourseViewSet(viewsets.ViewSet):
    """
    API endpoint that allows golf courses to be viewed
    """

    def list(self, request):
        queryset = models.GolfCourse.objects.all()
        serializer = serializers.GolfCourseSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.GolfCourse.objects.all()
        course = get_object_or_404(queryset, pk=pk)
        serializer = serializers.GolfCourseSerializer(course)
        return Response(serializer.data)


class GameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be viewed or edited
    """

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.GameSerializer

    def get_queryset(self):
        player = self.request.user.player
        queryset = models.Game.objects.filter(players__in=[player])
        return queryset

    def create(self, request):
        if not hasattr(request.user, "player"):
            return Response(
                {"message": settings.CONSTANTS["PLAYER_NOT_SETUP"]}, status=400
            )

        serializer = serializers.GameSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            model_obj = serializer.save()
            model_obj.players.add(request.user.player)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["post"], url_name="add_player")
    def add_player(self, request, pk=None):
        queryset = models.Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        player_id = request.data.get("player")
        player_data = get_object_or_404(models.Player, pk=player_id)
        game.players.add(player_data)
        serializer = serializers.GameSerializer(game, many=False)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_name="remove_player")
    def remove_player(self, request, pk=None):
        queryset = models.Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        player_id = request.data.get("player")
        player_data = get_object_or_404(models.Player, pk=player_id)
        game.players.remove(player_data)
        serializer = serializers.GameSerializer(game, many=False)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_name="set_score")
    def set_hole_score(self, request, pk=None):
        queryset = models.Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)

        score_list = request.data.get("score_list")
        for score_data in score_list:

            hole_score = models.HoleScore.objects.get(pk=score_data["id"])
            hole_score_serializer = serializers.HoleScoreSerializer(
                hole_score, data=score_data, partial=True
            )

            if hole_score_serializer.is_valid():
                hole_score_serializer.save()
            else:
                return Response(hole_score_serializer.errors, status=400)

        serializer = serializers.GameSerializer(game, many=False)

        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_name="start")
    def start_game(self, request, pk=None):
        queryset = models.Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        game.start()
        utils.create_hole_scores_for_game(game)

        serializer = serializers.GameSerializer(game, many=False)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PlayerSerializer

    def get_queryset(self):
        return models.Player.objects.filter(added_by=self.request.user)

    def create(self, request):
        serializer = serializers.PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(added_by=request.user)
        return Response(serializer.data)


class TeeTimeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        player = request.user.player
        queryset = models.TeeTime.objects.filter(players__in=[player])
        serializer = serializers.TeeTimeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        player = request.user.player
        queryset = models.TeeTime.objects.filter(players__in=[player])
        tee_time = get_object_or_404(queryset, pk=pk)
        serializer = serializers.TeeTimeSerializer(tee_time, many=False)
        return Response(serializer.data)


class TeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.Tee.objects.all()

    def retrieve(self, request, pk=None):
        tee = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.TeeSerializer(tee, many=False)
        return Response(serializer.data)

    def list(self, request):
        serializer = serializers.TeeSerializer(self.queryset, many=True)
        return Response(serializer.data)
