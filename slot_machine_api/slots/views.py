from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import Player, Game, Spin, Symbol
from .serializers import (
    PlayerSerializer, GameSerializer, SpinSerializer,
    SymbolSerializer, SpinRequestSerializer, RegistrationSerializer
)
from .services import SlotMachineService


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        description="Register a new user and create a player profile",
        responses={201: PlayerSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return the player data for the newly created user
        player = Player.objects.get(user=user)
        return Response(
            PlayerSerializer(player).data,
            status=status.HTTP_201_CREATED
        )


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Player.objects.filter(user=self.request.user)

    @extend_schema(
        description="Get current player information",
        responses={200: PlayerSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        player = Player.objects.get(user=request.user)
        serializer = self.get_serializer(player)
        return Response(serializer.data)


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Game.objects.filter(player__user=self.request.user)


class SpinViewSet(viewsets.GenericViewSet):
    serializer_class = SpinSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Spin the slot machine",
        request=SpinRequestSerializer,
        responses={200: SpinSerializer}
    )
    @action(detail=False, methods=['post'])
    def spin(self, request):
        serializer = SpinRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bet_size = serializer.validated_data['bet_size']
        player = Player.objects.get(user=request.user)

        slot_machine = SlotMachineService()
        result = slot_machine.play_spin(player, bet_size)

        if not result['success']:
            return Response(
                {'detail': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return the spin result
        return Response(result)

    @extend_schema(
        description="Get player's spin history",
        responses={200: SpinSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        player = Player.objects.get(user=request.user)
        games = Game.objects.filter(player=player)
        spins = Spin.objects.filter(game__in=games).order_by('-timestamp')

        # Optional pagination could be added here
        serializer = self.get_serializer(spins, many=True)
        return Response(serializer.data)


class SymbolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Symbol.objects.all()
    serializer_class = SymbolSerializer
    permission_classes = [IsAuthenticated]