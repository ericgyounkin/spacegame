from bearlibterminal import terminal
from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in [GameStates.TARGETING, GameStates.SET_TARGET]:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.GOTO_EQUIP, GameStates.DROP_EQUIP):
        return handle_menu_keys(key)
    return{}


def handle_mouse():
    (x, y) = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    if terminal.state(terminal.TK_MOUSE_LEFT):
        return {'left_click': {x, y}}
    elif terminal.state(terminal.TK_MOUSE_RIGHT):
        return {'right_click': {x, y}}
    return {}


def handle_targeting_keys(key):
    # Movement keys
    if key == terminal.TK_UP or key == terminal.TK_KP_8:
        return {'move': (0, -1)}
    elif key == terminal.TK_DOWN or key == terminal.TK_KP_2:
        return {'move': (0, 1)}
    elif key == terminal.TK_LEFT or key == terminal.TK_KP_4:
        return {'move': (-1, 0)}
    elif key == terminal.TK_RIGHT or key == terminal.TK_KP_6:
        return {'move': (1, 0)}
    elif key == terminal.TK_HOME or key == terminal.TK_KP_7:
        return {'move': (-1, -1)}
    elif key == terminal.TK_PAGEUP or key == terminal.TK_KP_9:
        return {'move': (1, -1)}
    elif key == terminal.TK_END or key == terminal.TK_KP_1:
        return {'move': (-1, 1)}
    elif key == terminal.TK_PAGEDOWN or key == terminal.TK_KP_3:
        return {'move': (1, 1)}
    elif key == terminal.TK_KP_5:
        pass  # do nothing ie wait for the monster to come to you

    if key == terminal.TK_ENTER:
        return {'enter': True}

    if key == terminal.TK_ESCAPE:
        return {'exit': True}
    return {}


def handle_player_turn_keys(key):
    # Movement keys
    if key == terminal.TK_UP or key == terminal.TK_KP_8:
        return {'move': (0, -1)}
    elif key == terminal.TK_DOWN or key == terminal.TK_KP_2:
        return {'move': (0, 1)}
    elif key == terminal.TK_LEFT or key == terminal.TK_KP_4:
        return {'move': (-1, 0)}
    elif key == terminal.TK_RIGHT or key == terminal.TK_KP_6:
        return {'move': (1, 0)}
    elif key == terminal.TK_HOME or key == terminal.TK_KP_7:
        return {'move': (-1, -1)}
    elif key == terminal.TK_PAGEUP or key == terminal.TK_KP_9:
        return {'move': (1, -1)}
    elif key == terminal.TK_END or key == terminal.TK_KP_1:
        return {'move': (-1, 1)}
    elif key == terminal.TK_PAGEDOWN or key == terminal.TK_KP_3:
        return {'move': (1, 1)}
    elif key == terminal.TK_KP_5:
        pass  # do nothing ie wait for the monster to come to you

    if key == terminal.TK_G:
        return {'pickup': True}
    elif key == terminal.TK_I:
        return {'goto_equip': True}
    elif key == terminal.TK_D:
        return {'drop_equip': True}
    elif key == terminal.TK_T:
        return {'set_target': True}

    if key == terminal.TK_ENTER and terminal.check(terminal.TK_ALT):
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key == terminal.TK_ESCAPE:
        # Exit the game
        return {'exit': True}

    if key == terminal.TK_MOUSE_LEFT:
        # Get the coordinates
        return {'left_click': [terminal.TK_MOUSE_X, terminal.TK_MOUSE_Y]}
    elif key == terminal.TK_MOUSE_RIGHT:
        # Get the coordinates
        return {'right_click': [terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y)]}

    # No key was pressed
    return {}


def handle_player_dead_keys(key):
    if key == terminal.TK_I:
        return {'show_inventory': True}

    if key == terminal.TK_ENTER and terminal.check(terminal.TK_ALT):
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key == terminal.TK_ESCAPE:
        # Exit the game
        return {'exit': True}
    return {}


def handle_menu_keys(key):
    # normalize to 'a', index = 0 for a, 1 for b, etc
    if key == terminal.TK_ESCAPE:
        return {'exit': True}

    elif key == terminal.TK_UP or key == terminal.TK_KP_8:
        return {'menupos': -1}

    elif key == terminal.TK_DOWN or key == terminal.TK_KP_2:
        return {'menupos': 1}

    elif key == terminal.TK_ENTER:
        return {'select': True}

    elif key == terminal.TK_R:
        return {'resize': True}

    return {}