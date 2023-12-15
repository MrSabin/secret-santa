from django.contrib import admin
from .models import *


@admin.register(UserSantaGame)
class UserSantaGameAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "telegram_id",
        "my_wish",
        "is_game_start",
        "id",
    )
    readonly_fields = ['is_game_start']



@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = (
        "game_bonus",
    )


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "telegram_id",
    )


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['info', 'end_game', 'promo_key', 'id']
    readonly_fields = ['promo_key', 'id']

