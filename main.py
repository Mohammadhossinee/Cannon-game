import datetime
import math
import os
import random

from kivy.clock import Clock
from kivy.graphics import Ellipse, PushMatrix, Rotate, Color, Rectangle, PopMatrix
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from Data.data import obstacle_width, obstacle_height
from constants import *
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable


class MainMenu(Screen):

    def new_game(self):
        game.game()

    def help_screen(self):
        game.help()

    def hall_of_fame_screen(self):
        game.records()

    def load_game(self):
        game.load_game()


class GameScreen(Screen):
    angle = StringProperty("45")
    velocity = StringProperty("7")
    round = StringProperty("1")
    shots_left = StringProperty("Unlimited")
    active_projectile = StringProperty("Bomb")

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        # Properties
        self.total_shots = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.current_shot = None
        self.running_shot_interval = None
        self.target = None
        self.cannon = None
        self.wormhole_cords = {}
        self.obstacles = []
        self.wormhole_entry_counts = 0
        # Functions
        self.spawn_cannon(int(self.angle))
        self.spawn_target()
        self.won_game = None
        self.lost_game = None
        self.size = (SCREEN_WIDTH, SCREEN_HEIGHT)

        if game.game_name != '':
            self.load_game(game.game_name)

    def on_size(self, *args):
        random_height = random.randint(self.height - 500, self.height - 100)
        self.target.pos = (self.width - 90, random_height)

    def attack(self):
        if self.current_shot is None:
            self.wormhole_entry_counts = 0
            if self.shots_left.lower() != 'unlimited':
                self.shots_left = str(int(self.shots_left) - 1)
                if int(self.shots_left) <= 0:
                    self.lose_game()
            velocity: int = 5
            try:
                entered_velocity = int(self.velocity_str)
                if 0 < entered_velocity <= 15:
                    velocity = entered_velocity
                elif entered_velocity <= 0:
                    velocity = 1
                else:
                    velocity = 15
            except:
                pass

            self.total_shots += 1
            self.spawn_projectile()
            angle_in_radian = math.radians(int(self.angle))
            if self.active_projectile.lower() == 'laser':
                self.velocity_x = float(LASER_VEL) * math.cos(angle_in_radian)
                self.velocity_y = float(LASER_VEL) * math.sin(angle_in_radian)

            else:
                self.velocity_x = float(self.velocity) * math.cos(angle_in_radian)
                self.velocity_y = float(self.velocity) * math.sin(angle_in_radian)

            self.running_shot_interval = Clock.schedule_interval(self.current_shot_movement, 1 / FPS)

    def current_shot_movement(self, dt):
        x, y = self.current_shot.pos

        # Movement
        x += dp(self.velocity_x)
        y += dp(self.velocity_y)
        if self.active_projectile.lower() != 'laser':
            self.velocity_y -= dt * 5
        self.current_shot.pos = (x, y)

        # Hitting The Target
        target_x = self.target.pos[0]
        target_y = self.target.pos[1]
        target_size_x = self.target.size[0]
        target_size_y = self.target.size[1]

        if self.current_shot is not None:
            if self.shot_collision_detector(target_x, target_y, target_size_x, target_size_y):
                # TODO: Round Winner
                self.win_round()
                self.delete_current_ongoing_shot()

        # Hitting Obstacles
        if self.current_shot is not None:
            rock_to_remove = None
            for obstacle in self.obstacles:
                if self.shot_collision_detector(obstacle['x'], obstacle['y'], obstacle['width'], obstacle['height']):
                    if obstacle['name'] == 'rock':
                        # Rock
                        rock_to_remove = obstacle
                        self.canvas.remove(obstacle['object'])
                        self.delete_current_ongoing_shot()
                        break

                    elif obstacle['name'] == 'mirror':
                        # Mirror
                        if self.active_projectile.lower() == 'laser':
                            self.velocity_x *= -1
                    else:
                        # Wormhole
                        new_x = int(obstacle['x'])
                        new_y = int(obstacle['y'])

                        self.current_shot.pos = (
                            self.wormhole_cords[new_x] + obstacle['width'] + 5, self.wormhole_cords[new_y])
                        self.wormhole_entry_counts += 1
                        if self.wormhole_entry_counts > 5:
                            self.delete_current_ongoing_shot()

            if rock_to_remove is not None:
                self.obstacles.remove(rock_to_remove)
        # Out of Screen Check
        if self.current_shot is not None:
            if x < 0 or x > self.size[0] + 10 or y < 0 or y > self.size[1] + 50:
                self.delete_current_ongoing_shot()

    def delete_current_ongoing_shot(self):
        self.canvas.remove(self.current_shot)
        self.current_shot = None
        self.running_shot_interval.cancel()
        self.running_shot_interval = None

    def shot_collision_detector(self, object_x, object_y, object_width, object_height):
        shot_x, shot_y = self.current_shot.pos
        shot_width, shot_height = self.current_shot.size
        return ((
                        object_x <= shot_x <= object_x + object_width or object_x <= shot_x + shot_width <= object_x + object_width) and (
                        object_y <= shot_y <= object_y + object_height or object_y <= shot_y + shot_height <= object_y + object_height))

    def spawn_projectile(self):
        with self.canvas:
            zero_angle_projectile = (440, 130)
            rotation_point_pos = (165, 165)
            new_x, new_y = self.rotate_point_around_another_point(zero_angle_projectile[0], zero_angle_projectile[1],
                                                                  rotation_point_pos[0], rotation_point_pos[1],
                                                                  int(self.angle))

            if self.active_projectile.lower() == 'bomb':
                Color(1, 1, 1)
                self.current_shot = Rectangle(pos=(new_x, new_y),
                                              size=(BOMB_RADIUS, BOMB_RADIUS),
                                              source=os.path.join('Images', 'bomb.png'))
            elif self.active_projectile.lower() == 'bullet':
                Color(rgb=(0, 0, 0))
                self.current_shot = Ellipse(pos=(new_x, new_y),
                                            size=(BULLET_RADIUS, BULLET_RADIUS))
            else:
                Color(rgb=(255, 0, 0))
                self.current_shot = Rectangle(pos=(new_x, new_y),
                                              size=(LASER_IMPULSE, LASER_IMPULSE))

    def spawn_cannon(self, angle: int):

        if self.cannon is not None:
            self.canvas.remove(self.cannon)
            self.cannon = None

        with self.canvas:
            Color(1, 1, 1)
            PushMatrix()
            Rotate(origin=(dp(125), dp(125)), angle=angle)

            self.cannon = Rectangle(pos=(dp(110), dp(0)), size=(300, 300),
                                    source=os.path.join('Images', 'cannon.png'))
            PopMatrix()

    def spawn_target(self, ):
        if self.target is not None:
            self.canvas.remove(self.target)
            self.target = None
        random_height = random.randint(self.height - 700, self.height - 100)
        with self.canvas:
            Color(1, 1, 1)
            self.target = Rectangle(pos=(self.width - 105, random_height),
                                    size=(102, 166), source=os.path.join('Images', 'target.png'))

    def adjust_angle(self, widget):
        try:
            change_angle_to: int = int(widget.text)
        except:
            pass
        else:
            if 90 >= change_angle_to >= 0:
                self.spawn_cannon(change_angle_to)
                self.angle = str(change_angle_to)
            elif change_angle_to < 0:
                self.spawn_cannon(0)
                self.angle = str(0)
            else:
                self.spawn_cannon(90)
                self.angle = str(90)

    def increase_velocity(self):
        if int(self.velocity) < 10:
            self.velocity = str(int(self.velocity) + 1)

    def decrease_velocity(self):
        if int(self.velocity) > 0:
            self.velocity = str(int(self.velocity) - 1)

    def win_round(self):
        if int(self.round) < 15:
            self.round = str(int(self.round) + 1)
            self.remove_obstacles()
            self.spawn_target()

            if int(self.round) <= 5:
                # Phase 1
                self.spawn_obstacle(1)

            elif int(self.round) <= 10:
                # Phase 2
                self.shots_left = str(20 - int(self.round))
                self.spawn_obstacle(2)
            else:
                # Phase 3
                self.shots_left = str(20 - int(self.round))
                self.spawn_obstacle(3)

        else:
            # Win Scenario
            self.win_game()

    def win_game(self):
        with open(os.path.join('Data', 'records.txt'), "a") as file:
            name = datetime.datetime.now().strftime('%A-%S-%f')
            file.write(f'{name}/{self.total_shots}')
            file.write('\n')
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos=(self.width / 2 - 300, self.height / 2 - 100), size=(600, 600),
                                      source=os.path.join('Images', 'Victory.png'))
            Clock.schedule_once(self.back_to_main_menu, 5)

    def lose_game(self):
        with self.canvas:
            Color(1, 1, 1)
            self.lose_banner = Rectangle(pos=(self.width / 2 - 300, self.height / 2 - 100), size=(600, 600),
                                         source=os.path.join('Images', 'defeat.png'))
            Clock.schedule_once(self.remove_banners, 5)

    def reset_game(self):
        self.remove_obstacles()
        self.round = '1'
        self.shots_left = 'Unlimited'
        self.spawn_cannon(45)

    def spawn_obstacle(self, obstacle_count: int):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(obstacle_count):
                random_x = random.randint(300, self.width - 100)
                random_y = random.randint(300, self.height - 200)
                obstacle_name = random.choice(['rock', 'mirror', 'wormhole'])
                if obstacle_name == 'wormhole':
                    object1 = Rectangle(pos=(random_x, random_y),
                                        size=(dp(obstacle_width[obstacle_name]), dp(obstacle_height[obstacle_name])),
                                        source=os.path.join('Images', obstacle_name + '.png'))
                    # Adding an extra wormhole(we need two wormholes)
                    random_x2 = random.randint(400, self.width - 100)
                    random_y2 = random.randint(400, self.height - 100)
                    object2 = Rectangle(pos=(random_x2, random_y2),
                                        size=(dp(obstacle_width[obstacle_name]), dp(obstacle_height[obstacle_name])),
                                        source=os.path.join('Images', obstacle_name + '.png'))
                    self.obstacles.append({'name': obstacle_name, 'x': random_x2, 'y': random_y2,
                                           'width': obstacle_width[obstacle_name],
                                           'height': obstacle_height[obstacle_name],
                                           'object': object2})
                    self.wormhole_cords[int(object1.pos[0])] = int(object2.pos[0])
                    self.wormhole_cords[int(object2.pos[0])] = int(object1.pos[0])
                    self.wormhole_cords[int(object1.pos[1])] = int(object2.pos[1])
                    self.wormhole_cords[int(object2.pos[1])] = int(object1.pos[1])

                else:
                    object1 = Rectangle(pos=(random_x, random_y),
                                        size=(dp(obstacle_width[obstacle_name]), dp(obstacle_height[obstacle_name])),
                                        source=os.path.join('Images', obstacle_name + '.png'))

                self.obstacles.append({'name': obstacle_name, 'x': random_x, 'y': random_y,
                                       'width': obstacle_width[obstacle_name],
                                       'height': obstacle_height[obstacle_name],
                                       'object': object1})

    def remove_obstacles(self):
        for obstacle in self.obstacles:
            self.canvas.remove(obstacle['object'])
        self.obstacles.clear()
        self.wormhole_cords.clear()

    def change_gun(self):
        if self.active_projectile == 'Bomb':
            self.active_projectile = 'Laser'
        elif self.active_projectile == 'Laser':
            self.active_projectile = 'Bullet'
        else:
            self.active_projectile = 'Bomb'

    def rotate_point_around_another_point(self, x_a, y_a, x_b, y_b, angle):
        # Convert angle to radians
        theta = math.radians(angle)

        # Step 1: Translate point A to the origin with respect to point B
        x_prime = x_a - x_b
        y_prime = y_a - y_b

        # Step 2: Apply the rotation matrix
        x_double_prime = x_prime * math.cos(theta) - y_prime * math.sin(theta)
        y_double_prime = x_prime * math.sin(theta) + y_prime * math.cos(theta)

        # Step 3: Translate the point back to the original position
        x_new = x_double_prime + x_b
        y_new = y_double_prime + y_b

        return x_new, y_new

    def back_to_main_menu(self, *args):
        game.main_menu()

    def save_game(self):
        with open(os.path.join('Data', 'Saves.txt'), 'a') as file:
            name = datetime.datetime.now().strftime('%A-%S-%f')
            file.write(f'{name}/{self.shots_left}/{self.round}')
            file.write('\n')

    def load_game(self, game_name):
        with open(os.path.join('Data', 'Saves.txt'), 'r') as file:
            all_lines = file.readlines()
            for line in all_lines:
                loaded_data = line.split('/')
                if game_name == loaded_data[0]:
                    self.round = str(int(loaded_data[2]) - 1)
                    self.win_round()
                    self.shots_left = loaded_data[1]


class Help(Screen):
    def __init__(self, **kwargs):
        super(Help, self).__init__(**kwargs)

    def back_to_main_menu(self):
        game.main_menu()


class Records(MDScreen):

    def load_table(self):
        layout = AnchorLayout()
        data = self.load_data()
        self.data_tables = MDDataTable(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            size_hint=(0.9, 0.7),
            use_pagination=True,
            check=False,
            column_data=[
                ("No.", dp(30)),
                ("Name", dp(60)),
                ("Total Shots", dp(30)),
            ],
            row_data=[
                (f"{i + 1}", item[0], item[1])
                for i, item in enumerate(data)], )
        button = Button(text="Back To Main Menu", on_press=self.main_menu, size_hint=(1, 0.1))
        self.add_widget(button)
        self.add_widget(self.data_tables)

        return layout

    def on_enter(self):
        self.load_table()

    def load_data(self):
        all_data = []
        loaded_data = []
        with open(os.path.join('Data', 'records.txt'), 'r') as file:
            all_lines = file.readlines()

            if len(all_lines) != 0:
                for line in all_lines:
                    line_split = line.split('/')
                    all_data.append(line_split)

        all_data.sort(key=lambda x: x[1])

        for i, data in enumerate(all_data):
            loaded_data.append([data[0], data[1]])
        return loaded_data

    def main_menu(self, *args):
        game.main_menu()


class LoadGame(Screen):
    game_to_load_name = StringProperty("")

    def __init__(self, **kwargs):
        super(LoadGame, self).__init__(**kwargs)
        self.all_games_data = []
        self.current_index = 0
        self.current_game = None
        with open(os.path.join('Data', 'Saves.txt'), "r") as file:
            all_lines = file.readlines()

            for line in all_lines:
                line_split = line.split('/')
                self.all_games_data.append(line_split)

        if len(self.all_games_data) != 0:
            self.game_to_load_name = self.all_games_data[0][0]
            self.current_game = self.all_games_data[0]

    def left_button(self):
        if self.current_index > 0:
            self.game_to_load_name = self.all_games_data[self.current_index - 1][0]
            self.current_game = self.all_games_data[self.current_index - 1]
            self.current_index -= 1

    def right_button(self):
        if self.current_index < len(self.all_games_data) - 1:
            self.game_to_load_name = self.all_games_data[self.current_index + 1][0]
            self.current_game = self.all_games_data[self.current_index + 1]
            self.current_index += 1

    def load_game(self):
        game.game_name = self.game_to_load_name
        game.game()

    def back_to_main_menu(self):
        game.main_menu()


class Cannon(MDApp):
    def __init__(self):
        super().__init__()
        self.screen_manager = None
        self.game_name = ''

    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(MainMenu())
        self.screen_manager.add_widget(GameScreen())
        self.screen_manager.add_widget(Help())
        self.screen_manager.add_widget(Records())
        self.screen_manager.add_widget(LoadGame())

        return self.screen_manager

    def main_menu(self):
        self.screen_manager.switch_to(MainMenu())

    def game(self):
        self.screen_manager.switch_to(GameScreen())

    def help(self):
        self.screen_manager.switch_to(Help())

    def load_game(self):
        self.screen_manager.switch_to(LoadGame())

    def records(self):
        self.screen_manager.switch_to(Records())


if __name__ == "__main__":
    game = Cannon()
    game.run()
