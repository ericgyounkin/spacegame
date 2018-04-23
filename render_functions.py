import libtcodpy as libtcod
from bearlibterminal import terminal

import time
from enum import Enum
from game_states import GameStates


class RenderOrder(Enum):
    INACTIVE_TARGETING = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4
    ACTIVE_TARGETING = 5


def initialize_with_bkcolor(old_color, new_color, width, height, startx, starty):
    terminal.bkcolor(new_color)
    terminal.color('white')
    for i in range(width):
        for j in range(height):
            terminal.print_(startx + i, starty + j, ' ')
    terminal.bkcolor(old_color)


def draw_panel_box(color, width, height, startx, starty):
    for i in range(width):
        terminal.print_(startx + i, starty, '[color=' + color + '][U+2550]')
        terminal.print_(startx + i, starty + height - 1, '[color=' + color + '][U+2550]')
    for i in range(height):
        terminal.print_(startx, starty + i, '[color=' + color + '][U+2551]')
        terminal.print_(startx + width - 2, starty + i, '[color=' + color + '][U+2551]')
    terminal.print_(startx + width - 2, starty, '[color=' + color + '][U+2557]')
    terminal.print_(startx + width - 2, starty + height - 1, '[color=' + color + '][U+255D]')
    terminal.print_(startx, starty, '[color=' + color + '][U+2554]')
    terminal.print_(startx, starty + height - 1, '[color=' + color + '][U+255A]')


def get_names_under_mouse(entities, fov_map):
    (x, y) = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
    # create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [entity.name for entity in entities if
            entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y) and
             entity.name != 'TargetingCursor']
    names = ', '.join(names)
    return names.capitalize(), x, y


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    terminal.layer(0)

    bar_width = int(float(value) / maximum * total_width)

    # Render background first
    terminal.bkcolor(back_color)
    for i in range(total_width):
        terminal.print_(x + i, y, ' ')

    # Render bar on top
    terminal.bkcolor(bar_color)
    for i in range(bar_width):
        terminal.print_(x + i, y, ' ')

    terminal.layer(1)
    txt = name + ': ' + str(value) + '/' + str(maximum)
    terminal.print_(int(total_width / 2 - len(txt) / 2), int(y), '[align=center][color=white]' + txt)

    # clean up
    terminal.bkcolor('black')


def render_equip_panel(x, y, total_width, total_height, items, active_turrets, game_state, equip_index=None):
    terminal.layer(0)
    initialize_with_bkcolor('black', 'darkest azure', total_width, total_height, x, y)
    draw_panel_box('white', total_width, total_height, x, y)

    x = x + 1
    terminal.print_(int(x + total_width / 2 - len('LOADOUT PANEL (i)') / 2), y, 'LOADOUT PANEL (i)')
    terminal.print_(x, y + 2, 'MANUAL')
    terminal.print_(x, y + 5, 'AUTO')
    terminal.layer(1)
    terminal.print_(x, y + 2, '________________')
    terminal.print_(x, y + 5, '________________')
    terminal.layer(0)

    run = 0
    man_height = 3
    auto_height = 6
    for item_entity in items:
        if item_entity in active_turrets:
            bground = 'green'
            status = 'RDY'
        elif item_entity.item.charge_time == item_entity.item.max_charge_time:
            bground = 'red'
            status = 'FIRING'
        else:
            bground = 'yellow'
            status = 'LOAD' + str(item_entity.item.charge_time + 1)

        if item_entity.item.targeting == 'manual':
            action = 'Fire'
            bground = 'green'
            status = 'RDY'
            h = man_height
            man_height += 1
        elif item_entity.item.targeting == 'auto_on':
            action = 'Disable'
            h = auto_height
            auto_height += 1
        elif item_entity.item.targeting == 'auto_off':
            action = 'Enable'
            bground = 'yellow'
            status = 'DSABLD'
            h = auto_height
            auto_height += 1
        else:
            break

        item_name = ': ' + item_entity.name + '{' + str(item_entity.item.quantity) + ')'
        if equip_index is not None and run == equip_index:
            if game_state == GameStates.DROP_EQUIP:
                terminal.print_(x, y + h, '[color=black][bkcolor=yellow]DROP')
            else:
                terminal.print_(x, y + h, '[color=black][bkcolor=yellow]' + action)
            terminal.print_(x + len(action), y + h, '[color=white]' + item_name)
        else:
            terminal.print_(x, h + y, '[color=' + bground + ']' + status)
            terminal.print_(x + len(status), h + y, '[color=white]' + item_name)

        h += 2
        run += 1
    terminal.bkcolor('black')


def draw_targeting_box(x, y):
    terminal.layer(2)
    terminal.color('lightest red')
    terminal.print_(x + 1, y - 1, '[color=dark red][U+2511]')
    terminal.print_(x - 1, y + 1, '[color=dark red][U+2515]')
    terminal.print_(x + 1, y + 1, '[color=dark red][U+2519]')
    terminal.print_(x - 1, y - 1, '[color=dark red][U+250D]')
    terminal.color('black')
    terminal.layer(0)


def render_tactical_panel(x, y, total_width, total_height, entities, player):
    terminal.layer(0)
    target = ''
    for ent in entities:
        if ent.combatship:
            if ent.combatship.targeted:
                target = ent
                break
    initialize_with_bkcolor('black', 'darkest azure', total_width, total_height, x, y)
    draw_panel_box('white', total_width, total_height, x, y)
    terminal.print_(int(x + total_width / 2 - len('TACTICAL PANEL (t)') / 2), y, 'TACTICAL PANEL (t)')
    if target:
        target_name = target.name
        target_hull = target.combatship.hull
        target_shields = target.combatship.shields
        target_armament = target.inventory.items
    else:
        target_name = 'None'
        target_hull = r'N/A'
        target_shields = r'N/A'
        target_armament = []
    terminal.print_(x + 1, y + 2, 'Target: {}'.format(target_name))
    terminal.print_(x + 1, y + 3, 'Hull: {}'.format(target_hull))
    terminal.print_(x + 1, y + 4, 'Shields: {}'.format(target_shields))
    terminal.print_(x + 1, y + 6, 'Armament:')
    for cnt, wpn in enumerate(target_armament):
        terminal.print_(x + 1, y + 7 + cnt, '  ' + wpn.name)
    terminal.bkcolor('black')


def render_all(entities, player, targeting_cursor, game_map, fov_map, fov_recompute, message_log, constants, game_state,
               equip_index, left_click, active_turrets, lineshot_pts, lineshot_clr, explosion_shape):
    render = True
    while render:
        terminal.layer(0)
        if fov_recompute:
            terminal.clear()
            # draw bounding boxes for the message and health bars
            for x in range(constants['screen_width']):
                terminal.print_(x, game_map.height, '[color=white][U+2550]')
            terminal.print_(constants['bar_width'] + 2, game_map.height, '[color=white][U+2566]')
            for y in range(game_map.height + 1, constants['screen_height']):
                terminal.print_(constants['bar_width'] + 2, y, '[color=white][U+2551]')
            # Draw all the tiles in the game map
            for y in range(game_map.height):
                for x in range(game_map.width):
                    visible = libtcod.map_is_in_fov(fov_map, x, y)
                    wall = game_map.tiles[x][y].block_sight

                    if visible:
                        if wall:
                            terminal.color(constants['colors'].get('light_wall'))
                            terminal.print_(x, y, '#')
                        else:
                            terminal.bkcolor('darkest grey')
                            terminal.print_(x, y, ' ')
                            terminal.bkcolor('black')
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            terminal.print_(x, y, '[color=' + constants['colors'].get('dark_wall') + ']#')
                        else:
                            terminal.print_(x, y, ' ')

        # Draw stars
        for star in game_map.stars_pts:
            draw_star(star, fov_map)

        if game_state == GameStates.TARGETING:
            draw_targeting_line(player, targeting_cursor, fov_map, game_map)

        # Draw all entities in the list
        entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            draw_entity(entity, fov_map)
            if entity.combatship:
                if entity.combatship.targeted:
                    draw_targeting_box(entity.x, entity.y)

        terminal.layer(1)
        terminal.clear_area(0, 0, constants['screen_width'], constants['screen_height'])

        # print the game messages one line at a time
        y = 1
        for message in message_log.messages:
            terminal.color(message.color)
            terminal.print_(message_log.x, y + constants['panel_y'], message.text)
            y += 1

        render_bar(1, 1 + constants['panel_y'], constants['bar_width'], 'Hull', player.combatship.hull,
                   player.combatship.max_hull, 'light red', 'darker red')
        render_bar(1, 3 + constants['panel_y'], constants['bar_width'], 'Shields', player.combatship.shields,
                   player.combatship.max_shields, 'light azure', 'darker azure')

        # if you are in inventory mode, highlight the item selected (equip index)
        if game_state in [GameStates.GOTO_EQUIP, GameStates.DROP_EQUIP]:
            render_equip_panel(1 + constants['equip_x'], 1, constants['equip_width'], constants['equip_height'],
                               player.inventory.items, active_turrets, game_state, equip_index=equip_index)
        else:
            render_equip_panel(1 + constants['equip_x'], 1, constants['equip_width'], constants['equip_height'],
                               player.inventory.items, active_turrets, game_state)

        render_tactical_panel(1 + constants['tactical_x'], constants['tactical_y'], constants['tactical_width'],
                              constants['tactical_height'], entities, player)

        # display names of objects under the mouse
        # name, x, y = get_names_under_mouse(entities, fov_map)
        # txt = '{}, [{},{}]'.format(name, x, y)
        # terminal.print_(1, int(constants['panel_y']), '[color=white]' + txt)
        animate_line_draw(game_state, lineshot_pts, lineshot_clr)
        animate_explosion(game_state, explosion_shape)
        terminal.refresh()
        fov_recompute = clear_explosion(game_state, explosion_shape, constants)
        fov_recompute, lineshot_pts = clear_line_draw(game_state, lineshot_pts, fov_recompute, constants)
        if lineshot_pts:
            render = True
        else:
            render = False
    # just in case return to 'root'
    terminal.layer(0)


def clear_all(entities, fov_map):
    for entity in entities:
        clear_entity(entity, fov_map)


def draw_entity(entity, fov_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        terminal.bkcolor('darkest grey')
        terminal.color(entity.color)
        terminal.print_(entity.x, entity.y, entity.char)
        terminal.bkcolor('black')


def draw_star(star, fov_map):
    visible = libtcod.map_is_in_fov(fov_map, star[0], star[1])
    if visible:
        terminal.bkcolor('darkest grey')
    terminal.color(star[2])
    terminal.print_(star[0], star[1], '.')
    terminal.color('black')
    terminal.bkcolor('black')


def clear_entity(entity, fov_map):
    # erase the character that represents this object
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        terminal.color(entity.color)
        terminal.print_(entity.x, entity.y, ' ')


def animate_line_draw(game_state, lineshot_pts, lineshot_clr):
    if lineshot_pts and game_state == GameStates.LINESHOT:
        terminal.layer(2)
        terminal.color(lineshot_clr)
        if abs(lineshot_pts[-1][1] - lineshot_pts[0][1]) > abs(lineshot_pts[-1][0] - lineshot_pts[0][0]):
            symbol = '|'
        else:
            symbol = '-'
        for pts in lineshot_pts:
            terminal.print_(pts[0], pts[1], symbol)
        terminal.layer(0)


def animate_explosion(game_state, explosion_shape):
    if explosion_shape and game_state == GameStates.EXPLOSION:
        shades = ['lighter', 'light', '', 'dark', 'darker']
        terminal.layer(2)
        for pts in explosion_shape.points:
            shade = shades[libtcod.random_get_int(0, 0, len(shades) - 1)]
            if shade:
                terminal.color(shade + ' violet')
            else:
                terminal.color('violet')
            terminal.print_(pts[0], pts[1], '*')
        terminal.layer(0)


def clear_explosion(game_state, explosion_shape, constants):
    if explosion_shape and game_state == GameStates.EXPLOSION:
        time.sleep(constants['explosion_delay'])
        fov_recompute = True
    else:
        fov_recompute = False
    return fov_recompute, explosion_shape


def clear_line_draw(game_state, lineshot_pts, fov_recompute, constants):
    if lineshot_pts and game_state == GameStates.LINESHOT:
        time.sleep(constants['line_shot_delay'])
        for pts in lineshot_pts:
            clear_layer_points(2, 0, pts[0], pts[1])
            lineshot_pts.remove((pts[0], pts[1]))
        if not lineshot_pts:
            fov_recompute = True
    return fov_recompute, lineshot_pts


def clear_targeting_line(player, targeting_cursor, fov_map):
    for pts in libtcod.line_iter(player.x, player.y, targeting_cursor.x, targeting_cursor.y):
        if libtcod.map_is_in_fov(fov_map, pts[0], pts[1]):
            clear_layer_points(2, 0, pts[0], pts[1])


def draw_targeting_line(player, targeting_cursor, fov_map, game_map):
    for pts in libtcod.line_iter(player.x, player.y, targeting_cursor.x, targeting_cursor.y):
        if libtcod.map_is_in_fov(fov_map, pts[0], pts[1]) and (pts[0], pts[1]) not in [(targeting_cursor.x,
                                                                                        targeting_cursor.y)]:
            if game_map.tiles[pts[0]][pts[1]].block_sight:
                draw_layer_points(2, 0, pts[0], pts[1], 'lightest red', '*')
                targeting_cursor.color = 'red'
            else:
                draw_layer_points(2, 0, pts[0], pts[1], 'lightest yellow', '*')
                targeting_cursor.color = 'yellow'


def clear_layer_points(layer, returnlayer, x, y):
    terminal.layer(layer)
    terminal.clear_area(x, y, 1, 1)
    terminal.layer(returnlayer)


def draw_layer_points(layer, returnlayer, x, y, color, symbol):
    terminal.layer(layer)
    terminal.color(color)
    terminal.print_(x, y, '*')
    terminal.layer(returnlayer)