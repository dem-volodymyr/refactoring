from rest_framework import serializers
from .models import Player, Game, Spin, Symbol
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'user', 'balance', 'total_won', 'total_wager']
        read_only_fields = ['id', 'total_won', 'total_wager']


class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = ['id', 'name', 'image_path']


class SpinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spin
        fields = ['id', 'game', 'bet_amount', 'payout', 'result', 'win_data', 'timestamp']
        read_only_fields = ['id', 'game', 'payout', 'result', 'win_data', 'timestamp']


class GameSerializer(serializers.ModelSerializer):
    spins = SpinSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'player', 'machine_balance', 'created_at', 'updated_at', 'spins']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SpinRequestSerializer(serializers.Serializer):
    bet_size = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        # Create a player profile for the user
        Player.objects.create(user=user)

        return user