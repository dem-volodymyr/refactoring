from django.contrib import admin
from .models import Player, Game, Spin, Symbol

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_won', 'total_wager')
    search_fields = ('user__username',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'machine_balance', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('player__user__username',)

@admin.register(Spin)
class SpinAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'bet_amount', 'payout', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('game__player__user__username',)

@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_path')
    search_fields = ('name',)