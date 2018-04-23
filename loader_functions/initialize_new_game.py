import entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from spaceships import playerships
from render_functions import RenderOrder


def get_constants():
    # top level stuff
    window_title = 'Spacegame'
    fontsize = '16'

    # console parameters
    screen_width = 140
    screen_height = 50
    map_width = 110
    map_height = 40

    # ui health bar stuff
    bar_width = 40
    panel_height = int(screen_height - map_height)
    panel_y = int(screen_height - panel_height)
    message_x = int(bar_width + 4)
    message_width = int(screen_width - bar_width - 2)
    message_height = int(panel_height - 1)

    # equipment panel
    equip_width = int(screen_width - map_width)
    equip_height = int(map_height / 2)
    equip_x = int(screen_width - equip_width)

    # tactical panel
    tactical_width = equip_width
    tactical_height = equip_height
    tactical_x = equip_x
    tactical_y = equip_height + 1

    # parameters for map generation
    max_asteroid_radius = 3
    max_asteroids = 3
    max_stars_per_screen = 60

    # FOV parameters
    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 70

    # entity parameters
    max_enemies_per_screen = 5
    max_items_per_screen = 0

    # animation parameters
    line_shot_delay = 0.03
    explosion_delay = 0.3

    # colors
    colors = {
        'dark_wall': 'lighter grey',
        'dark_ground': 'black',
        'light_wall': 'dark yellow',
        'light_ground': 'grey'
    }

    constants = {
        'bar_width': bar_width,
        'colors': colors,
        'equip_width': equip_width,
        'equip_height': equip_height,
        'equip_x': equip_x,
        'explosion_delay': explosion_delay,
        'fontsize': fontsize,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'line_shot_delay': line_shot_delay,
        'map_width': map_width,
        'map_height': map_height,
        'max_asteroid_radius': max_asteroid_radius,
        'max_asteroids': max_asteroids,
        'max_enemies_per_screen': max_enemies_per_screen,
        'max_items_per_screen': max_items_per_screen,
        'max_stars_per_screen': max_stars_per_screen,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'tactical_width': tactical_width,
        'tactical_height': tactical_height,
        'tactical_x': tactical_x,
        'tactical_y': tactical_y,
        'window_title': window_title
    }

    return constants


def get_game_variables(constants):
    player = playerships.player_cruiser()
    targeting_cursor = entity.Entity(0, 0, '#', 'yellow', 'TargetingCursor', blocks=False,
                                     render_order=RenderOrder.INACTIVE_TARGETING)
    entities = [player, targeting_cursor]

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_asteroids'], constants['max_asteroid_radius'],
                      entities, constants['max_enemies_per_screen'], constants['max_items_per_screen'],
                      constants['max_stars_per_screen'])

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state