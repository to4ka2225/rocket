from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy import platform
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
import time
import random
from kivy.metrics import dp
from kivymd.uix.dialog import (MDDialog,MDDialogHeadlineText,MDDialogButtonContainer)
from kivymd.uix.button import MDButton,MDButtonText
from kivy.uix.widget import Widget


class Bullet(Image):
    def __init__(self, speed, **kwargs):
        super().__init__(**kwargs)
        self.source = "assets/images/bullet.png"
        self.size_hint = (None, None)
        self.size = (10, 30)
        self.speed = speed

class BaseShip(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None,None)

class PlayerShip(BaseShip):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.speed = dp(5)

    def move(self,keys,screen_width):
        if keys["left"] and self.x > 0:
            self.x -= self.speed
        if keys["right"] and self.right < screen_width:
            self.x += self.speed

    def fire(self):
        bullet = Bullet(speed=dp(10))
        bullet.center_x = self.center_x
        bullet.y = self.top
        return bullet

class EnemyShip(BaseShip):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.speed = dp(3)
        self.last_shot = time.time()
        self.fire_rate = random.uniform(1.5,3.0)

    def move(self):
        self.y -= self.speed

    def fire(self):
        bullet = Bullet(speed=dp(-8))
        bullet.center_x = self.center_x
        bullet.top = self.y
        return bullet


class MainScreen(MDScreen):
    ...


class GameScreen(MDScreen):
    fps = 60
    #ship_speed = 5
    #bullet_speed = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keys = {"left": False, "right": False, "fire": False}
        self.bullets = []
        self.enemies = []
        self.dialog_pause = None
        self.game_event = None
        self.spawn_timer = 0
        self.spawn_delay = 2.0

    def on_enter(self, *args):
        self.spawn_enemy()
        self.game_event = Clock.schedule_interval(self.update, 1 / self.fps)

    def on_leave(self, *args):
        if self.game_event:
            self.game_event.cancel()

    # [ЗМІНА] Метод створення ворожого корабля у випадковій позиції
    def spawn_enemy(self):
        enemy = EnemyShip()
        enemy.x = random.randint(0, int(Window.width - dp(80)))  # dp(80) - ширина ворога
        enemy.y = Window.height
        self.ids.front.add_widget(enemy)
        self.enemies.append(enemy)

    def update(self, dt):
        #ship = self.ids.ship
        #if self.keys["left"] and ship.x > 0:

        #     ship.x -= self.ship_speed
        # if self.keys["right"] and ship.right < Window.width:
        #     ship.x += self.ship_speed
        # [ЗМІНА] Метод створення ворожого корабля у випадковій позиції
        # [ЗМІНА] Оновлення стану головного корабля через його власний метод
        self.ids.ship.move(self.keys, Window.width)

        # [ЗМІНА] Таймер спавну ворогів
        self.spawn_timer += dt  # Додаємо час, що пройшов з минулого кадру
        if self.spawn_timer > self.spawn_delay:
            self.spawn_enemy()  # Створюємо ворога
            self.spawn_timer = 0  # Скидаємо таймер на нуль
            self.spawn_delay = random.uniform(1.0, 3.0)  # Робимо наступний спавн випадковим (від 1 до 3 сек)

        # [ЗМІНА] Оновлення ворогів
        for enemy in self.enemies[:]:
            enemy.move()

            # Викликаємо метод стрільби ворожого корабля
            if time.time() - enemy.last_shot > enemy.fire_rate:
                # Отримуємо кулю від ворога
                new_bullet = enemy.fire()
                self.ids.front.add_widget(new_bullet)
                self.bullets.append(new_bullet)

                enemy.last_shot = time.time()

            if enemy.top < 0:
                self.ids.front.remove_widget(enemy)
                self.enemies.remove(enemy)

        for bullet in self.bullets[:]:
            bullet.y += bullet.speed
            if bullet.y > Window.height:
                self.ids.front.remove_widget(bullet)
                self.bullets.remove(bullet)

    def fire(self):
        bullet = Bullet()

        bullet.center_x = self.ids.ship.center_x
        bullet.y = self.ids.ship.top

        self.ids.front.add_widget(bullet)
        self.bullets.append(bullet)


class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"

        self.sm = MDScreenManager()

        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(GameScreen(name="game"))

        return self.sm


if platform != "android":
    Window.size = (400, 900)
    Window.top = 100
    Window.left = 600

app = ShooterApp()
app.run()
