import json

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path

from .models import *
from .tasks import start_game_task


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
    change_list_template = 'game_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start_game/', self.draw_of_lots, name='draw_of_lots'),
        ]
        return custom_urls + urls

    def draw_of_lots(self, request):
        promos = [game.promo_key for game in
                  Game.objects.all()]
        promos_serialized = json.dumps(promos)
        print(promos_serialized)
        start_game_task.delay(promos_serialized)
        self.model.objects.all().update(end_game=None)
        self.message_user(request, 'Жребьевка успешно проведена')
        return HttpResponseRedirect('../')
