from django.contrib import admin
from .models import *


@admin.register(UserSantaGame)
class UserSantaGameAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "telegram_id",
        "is_game_start",
    )


@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = (
        "game_bonus",
    )


@admin.register(SuperUser)
class SuperUserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "telegram_id",
    )


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['info', 'end_game', 'promo_key']
    readonly_fields = ['promo_key']

