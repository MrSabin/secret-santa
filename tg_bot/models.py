from django.db import models
import uuid


class Bonus(models.Model):
    BONUS_CHOICES = (
        (1000, 'от 1000р до 2000р'),
        (500, 'от 500р до 1000р'),
        (100, 'от 100р до 500р'),
        (0, 'Бюджет не ограничен'),
    )
    game_bonus = models.PositiveSmallIntegerField(verbose_name='Премиальное участие в игре Тайный Санта', choices=BONUS_CHOICES)

    def __str__(self):
        return f"{self.game_bonus}"


class Game(models.Model):
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, related_name="user_bonus")
    info = models.TextField(verbose_name='Описание игры', null=True, blank=True)
    end_game = models.DateField(help_text="Дата окончания игры", verbose_name='Дата окончания игры')
    promo_key = models.CharField(max_length=6, db_index=True, verbose_name='ПРОМО', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.promo_key = str(str(uuid.uuid4())[-6:]).upper()
        print(self.promo_key)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.info} до {self.end_game}"

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"



class UserSantaGame(models.Model):
    telegram_id = models.PositiveBigIntegerField(verbose_name='Telegram ID')
    first_name = models.CharField(max_length=40, verbose_name='Имя', null=True)
    email = models.EmailField(blank=True)
    is_game_start = models.BooleanField(default=False, null=True, blank=True, verbose_name='Создатель игры')
    partner = models.ForeignKey('self', on_delete=models.CASCADE, related_name='santa_game_partner', null=True, blank=True, verbose_name='Ваш партнер')
    my_wish = models.TextField(verbose_name='Пожелание', blank=True, null=True)
    my_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game', null=True, blank=True, verbose_name='Моя игра')

    def __str__(self):
        return f"{self.first_name} - {self.telegram_id}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Assistant(UserSantaGame):
    info = models.TextField(verbose_name='Дополнительная информация', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name}"
