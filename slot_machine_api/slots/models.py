from django.db import models
from django.contrib.auth.models import User
import uuid


class Symbol(models.Model):
    name = models.CharField(max_length=50)
    image_path = models.CharField(max_length=200)
    payout_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name



class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    total_won = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_wager = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Player: {self.user.username}"


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='games')
    machine_balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.id}"


class Spin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='spins')
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    result = models.JSONField()  # Store the spin result as JSON
    win_data = models.JSONField(null=True, blank=True)  # Win information
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Spin {self.id} for Game {self.game.id}"