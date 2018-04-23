import libtcodpy as libtcod
from bearlibterminal import terminal

import death_functions
import entity
import fov_functions
from game_messages import Message
from game_states import GameStates
import input_handlers
import item_functions
from loader_functions import data_loaders, initialize_new_game
from map_objects.diamond import Diamond
from menus import menu, message_box
import render_functions

DEBUG = False


def debug_mode():
    return DEBUG


def play_game(player, entities, game_map, message_log, game_state, constants):
    explosion_radius = 0
    explosion_target = []
    explosion_shape = []
    targeting_item = None
    lineshot_pts = []
    lineshot_clr = ''
    equip_index = 0
    move = ''

    # get the targeting cursor
    targeting_cursor = entity.find_entity_by_name(entities, 'TargetingCursor')

    # build the game map, setting up the fov for the map
    fov_recompute = True
    fov_map = fov_functions.initialize_fov(game_map)

    turn_cnt = 0
    game_state = GameStates.PLAYER_TURRET_TURN
    previous_game_state = game_state
    turret_find = True
    active_turrets = []
    disabled_turrets = []
    entity_turn_order = []
    active_enemy_turrets = []
    enemy_turret_results = []
    death_game_state = ''
    left_click = []

    while True:
        if DEBUG:
            turn_cnt += 1
            print('*******************************')
            print('TURN {} {}'.format(turn_cnt, game_state))
        player_turn_results = []
        found_turrets = False
        if fov_recompute:
            fov_functions.recompute_fov(fov_map, player.x, player.y, constants['fov_radius'],
                                        constants['fov_light_walls'], constants['fov_algorithm'])

        # initialize set target mode
        mindist = 1000
        foundtarget = None
        for ent in entities:
            if ent.ai and ent.combatship and ent not in [player,
                                                         targeting_cursor] and libtcod.map_is_in_fov(fov_map, ent.x, ent.y):
                if ent.combatship.targeted:
                    foundtarget = None
                    break
                else:
                    dist = player.distance_to(ent)
                    if dist < mindist:
                        mindist = dist
                        foundtarget = ent
        if foundtarget is not None:
            foundtarget.combatship.targeted = True

        # player turrets take a turn
        # for targeting turrets (animated), cycle through the whole animation cycle, come back through for next turret
        if game_state == GameStates.PLAYER_TURRET_TURN:
            results = []

            # first get all the active turrets if turret_find flag is set
            if turret_find:
                for item_entity in player.inventory.items:
                    if item_entity.ai is not None and item_entity not in active_turrets and \
                            item_entity.item.max_charge_time is not None:
                        # handle charge time here as well.  Subtract one if charging, fire if charged
                        if not item_entity.item.charge_time:
                            active_turrets.append(item_entity)
                        else:
                            item_entity.item.charge_time -= 1
                found_turrets = True
                turret_find = False
            else:
                for item_entity in player.inventory.items:
                    if item_entity.ai is not None and item_entity not in active_turrets and not item_entity.item.charge_time:
                        active_turrets.append(item_entity)

            if DEBUG:
                print('DEBUG {} total items is {}, active turrets pre check is {}'.format(player.name,
                                                                                          len(player.inventory.items),
                                                                                          len(active_turrets)))
            # remove all the disabled turrets and recharging turrets second time through
            active_turrets = [turret for turret in active_turrets if turret not in disabled_turrets]
            if DEBUG:
                print('DEBUG {} has {} remaining turrets'.format(player.name, len(active_turrets)))
            # now look for a good target, get results if you used the turret and remove it from active turrets
            if active_turrets and not found_turrets:
                for ent in entities:
                    if ent.combatship:
                        if ent.combatship.targeted:
                            results = active_turrets[0].ai.take_turn(player, ent, fov_map, game_map, entities)
                            if results:
                                player_turn_results.extend(results)
                                active_turrets.remove(active_turrets[0])
                                break
                    else:
                        results = []

            # with no shots or no active turrets, switch to players turn
            if not results:
                # do a pass through to rdy up turrets in case you only fired some of your complement
                if active_turrets:
                    for item_entity in player.inventory.items:
                        if item_entity.ai is not None and item_entity not in active_turrets and \
                                item_entity.item.max_charge_time is not None:
                            if item_entity.item.charge_time:
                                item_entity.item.charge_time -= 1
                game_state = GameStates.PLAYERS_TURN
            if not active_turrets:
                turret_find = True

        # print to screen for render_functions.render_all to display/refresh
        render_functions.render_all(entities, player, targeting_cursor, game_map, fov_map, fov_recompute, message_log,
                                    constants, game_state, equip_index, left_click, active_turrets, lineshot_pts,
                                    lineshot_clr, explosion_shape)

        # clear all explosion points and one line point each time (with delay)

        render_functions.clear_all(entities, fov_map)

        # blocking read input (unless an animation is going on)
        key = None
        if game_state not in [GameStates.EXPLOSION, GameStates.LINESHOT, GameStates.PLAYER_TURRET_TURN,
                              GameStates.ENEMY_TURN, GameStates.ENEMY_TURRET_TURN]:
            key = terminal.read()

        action = input_handlers.handle_keys(key, game_state)

        move = action.get('move')
        pickup = action.get('pickup')
        enter = action.get('enter')
        goto_equip = action.get('goto_equip')
        drop_equip = action.get('drop_equip')
        equip_inc = action.get('menupos')
        equip_select = action.get('select')
        set_target = action.get('set_target')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        left_click = action.get('left_click')
        right_click = action.get('right_click')

        # move the player and attack if an entity is in the way
        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = entity.get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    attack_results = player.combatship.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    targeting_cursor.move(dx, dy)
                    fov_recompute = True
                player.combatship.regen_shields()
                game_state = GameStates.ENEMY_TURRET_TURN

        # if you hit g and there is an item under you, add to inventory
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for ent in entities:
                if ent.item and ent.x == player.x and ent.y == player.y:
                    pickup_results = player.inventory.add_item(ent)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', 'yellow'))

        # change modes to show (i) / drop (d) if you hit those keys
        if goto_equip:
            previous_game_state = game_state
            game_state = GameStates.GOTO_EQUIP
        if drop_equip:
            previous_game_state = game_state
            game_state = GameStates.DROP_EQUIP
        if set_target:
            message_log.add_message(Message('Use the arrow keys and press enter to set an enemy target', 'light cyan'))
            previous_game_state = game_state
            game_state = GameStates.SET_TARGET

        # handle moving around within the inventory
        if equip_inc is not None and previous_game_state != GameStates.PLAYER_DEAD:
            equip_index += equip_inc
            if equip_index < 0:
                equip_index = 0
            elif equip_index >= len(player.inventory.items) - 1:
                equip_index = len(player.inventory.items) - 1

        # hit enter in inventory, use item / drop item and append to player_turn_results
        if equip_select:
            item = player.inventory.items[equip_index]
            if game_state == GameStates.GOTO_EQUIP:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map,
                                                                inventory_enter_key=True))
            elif game_state == GameStates.DROP_EQUIP:
                player_turn_results.extend(player.inventory.drop_item(item))

        # once you finish animating the line, check if there is a turret left to fire
        # if not, going through the turret turn will rebuild active turrets list for next turn
        if not lineshot_pts and game_state == GameStates.LINESHOT:
            game_state = previous_game_state

        # first time through, build the shape of the explosion
        # second time through (it's been animated and cleared)
        if game_state == GameStates.EXPLOSION:
            if explosion_shape:
                explosion_shape = []
                game_state = previous_game_state
            else:
                explosion_shape = Diamond((explosion_target[0], explosion_target[1]), explosion_radius)
                explosion_shape.build_diamond()

        # set target mode:
        if game_state == GameStates.SET_TARGET:
            if left_click:
                target_x, target_y = left_click
                for ent in entities:
                    if ent.ai and ent.combatship and ent not in [player, targeting_cursor]:
                        if ent.x == target_x and ent.y == target_y:
                            ent.combatship.targeted = True
                        else:
                            ent.combatship.targeted = False
                player_turn_results.append({'set_target': True})
            elif right_click:
                player_turn_results.append({'set_target_cancelled': True})
            elif move:
                dx, dy = move
                if dx + dy >= 0:
                    move = 1
                else:
                    move = -1
                for ent in entities:
                    if ent.ai and ent.combatship and ent not in [player, targeting_cursor]:
                        if ent.combatship.targeted:
                            ships = [ent for ent in entities if ent.ai and ent.combatship
                                     and ent not in [player, targeting_cursor]
                                     and libtcod.map_is_in_fov(fov_map, ent.x, ent.y)]
                            ent.combatship.targeted = False

                            ind = ships.index(ent)
                            newind = ind + move
                            if newind >= 0 and newind < len(ships):
                                entities[entities.index(ships[newind])].combatship.targeted = True
                            else:
                                if move == 1:
                                    entities[entities.index(ships[0])].combatship.targeted = True
                                else:
                                    entities[entities.index(ships[-1])].combatship.targeted = True
                            break
                player_turn_results.append({'move_target': True})
            elif enter:
                player_turn_results.append({'set_target': True})
        # targeting mode:
        # left click from mouse_handler targets entity (without using targeting cursor
        # right click cancels target mode
        # move will move around the targeting cursor
        # enter fires and resets cursor
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click
                hit, blocked, target_x, target_y = \
                    item_functions.target_with_accuracy(player, target_x, target_y,
                                                        targeting_item.item.function_kwargs.get('accuracy'), game_map,
                                                        entities)
                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y, blocked=blocked, hit=hit)
                player_turn_results.extend(item_use_results)
                player.combatship.regen_shields()
            elif right_click:
                targeting_cursor.render_order = render_functions.RenderOrder.INACTIVE_TARGETING
                targeting_cursor.x = player.x
                targeting_cursor.y = player.y
                player_turn_results.append({'targeting_cancelled': True})
            elif move:
                targeting_cursor.render_order = render_functions.RenderOrder.ACTIVE_TARGETING
                dx, dy = move
                targeting_cursor.move(dx, dy)

            elif enter:
                render_functions.clear_targeting_line(player, targeting_cursor, fov_map)
                hit, blocked, target_x, target_y = \
                    item_functions.target_with_accuracy(player, targeting_cursor.x, targeting_cursor.y,
                                                        targeting_item.item.function_kwargs.get('accuracy'), game_map,
                                                        entities)
                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y, blocked=blocked, hit=hit)
                player_turn_results.extend(item_use_results)
                targeting_cursor.render_order = render_functions.RenderOrder.INACTIVE_TARGETING
                targeting_cursor.x = player.x
                targeting_cursor.y = player.y
                player.combatship.regen_shields()

        # hit escape at any point
        # if in inventory mode, clears the inventory screen and goes back to player state
        if exit:
            if game_state in [GameStates.GOTO_EQUIP, GameStates.DROP_EQUIP, GameStates.SET_TARGET]:
                terminal.clear()
                fov_recompute = True
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                targeting_cursor.render_order = render_functions.RenderOrder.INACTIVE_TARGETING
                targeting_cursor.x = player.x
                targeting_cursor.y = player.y
                player_turn_results.append({'targeting_cancelled': True})
            else:
                data_loaders.save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            autofire = player_turn_result.get('autofire')
            explosion = player_turn_result.get('explosion')
            lineshot = player_turn_result.get('lineshot')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            toggle_turret = player_turn_result.get('toggle_turret')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            set_target_result = player_turn_result.get('set_target')
            set_target_cancelled = player_turn_result.get('set_target_cancelled')
            move_target = player_turn_result.get('move_target')

            if message:
                message_log.add_message(message)
            if autofire:
                pass
            if explosion:
                explosion_radius = explosion[0]
                explosion_target = explosion[1]
                game_state = GameStates.EXPLOSION
                previous_game_state = GameStates.ENEMY_TURRET_TURN
            if lineshot:
                lineshot_pts = [step for step in libtcod.line_iter(player.x, player.y, lineshot.get('pts')[0],
                                                                   lineshot.get('pts')[1])]
                lineshot_clr = lineshot.get('clr')
                game_state = GameStates.LINESHOT
                previous_game_state = GameStates.PLAYER_TURRET_TURN
            if dead_entity:
                if dead_entity == player:
                    message, game_state = death_functions.kill_player(dead_entity)
                else:
                    entity_turn_order.remove(dead_entity)
                    message = death_functions.kill_enemy(dead_entity)

                message_log.add_message(message)
            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURRET_TURN
            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURRET_TURN
            if targeting:
                terminal.clear()
                fov_recompute = True
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)
            if toggle_turret:
                if toggle_turret in disabled_turrets:
                    toggle_turret.item.targeting = 'auto_on'
                    disabled_turrets.remove(toggle_turret)
                else:
                    toggle_turret.item.targeting = 'auto_off'
                    disabled_turrets.append(toggle_turret)
                game_state = GameStates.PLAYERS_TURN
            if targeting_cancelled:
                fov_recompute = True
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled.'))
            if set_target_result:
                game_state = GameStates.PLAYERS_TURN
                fov_recompute = True
            if set_target_cancelled:
                game_state = previous_game_state
            if move_target:
                fov_recompute = True

        if game_state == GameStates.ENEMY_TURN:
            active_enemy_turrets = []
            if entity_turn_order:
                ent = entity_turn_order[0]
                entity_turn_order.remove(ent)
                enemy_turn_results = ent.ai.take_turn(player, fov_map, game_map, entities, constants)
                for enemy_turn_result in enemy_turn_results:
                    message = enemy_turn_result.get('message')
                    dead_entity = enemy_turn_result.get('dead')
                    if message:
                        message_log.add_message(message)
                    if dead_entity:
                        if dead_entity == player:
                            message, game_state = death_functions.kill_player(dead_entity)
                        else:
                            entity_turn_order.remove(dead_entity)
                            message = death_functions.kill_enemy(dead_entity)

                        message_log.add_message(message)

                        if game_state == GameStates.PLAYER_DEAD:
                            break

                if game_state == GameStates.PLAYER_DEAD:
                    break
                elif not entity_turn_order:
                    game_state = GameStates.PLAYER_TURRET_TURN
                else:
                    game_state = GameStates.ENEMY_TURRET_TURN
            else:
                game_state = GameStates.PLAYER_TURRET_TURN

        if game_state == GameStates.ENEMY_TURRET_TURN:
            enemy_turret_results = []
            dead_entity = ''
            if entity_turn_order:
                ent = entity_turn_order[0]
                if not active_enemy_turrets:
                    for item_entity in ent.inventory.items:
                        if item_entity.ai is not None and item_entity not in active_turrets and \
                                item_entity.item.max_charge_time is not None:
                            # handle charge time here as well.  Subtract one if charging, fire if charged
                            if not item_entity.item.charge_time:
                                active_enemy_turrets.append(item_entity)
                            else:
                                item_entity.item.charge_time -= 1
                if DEBUG:
                    print('DEBUG {} {} items, {} with ai'.format(ent.name, len(ent.inventory.items),
                                                                 len([i for i in ent.inventory.items if i.ai is not None])))
                    print('DEBUG {} position {}'.format(ent.name, [ent.x, ent.y]))
                    print('DEBUG {} has {} remaining turrets'.format(ent.name, len(active_enemy_turrets)))
                if active_enemy_turrets:
                    enemy_turret_results = ent.ai.handle_turret(active_enemy_turrets[0], player, fov_map, game_map,
                                                                entities, constants)
                    active_enemy_turrets.remove(active_enemy_turrets[0])
                    for result in enemy_turret_results:
                        if DEBUG and result:
                            print('DEBUG {} turret result {}'.format(ent.name, result))
                        dead_entity = result.get('dead')
                        lineshot = result.get('lineshot')
                        message = result.get('message')

                        if dead_entity == player and not death_game_state:
                            message, death_game_state = death_functions.kill_player(dead_entity)
                        if lineshot:
                            lineshot_pts = [step for step in libtcod.line_iter(ent.x, ent.y, lineshot.get('pts')[0],
                                                                               lineshot.get('pts')[1])]
                            lineshot_clr = lineshot.get('clr')

                            if DEBUG:
                                print('DEBUG {} enemy target lineshot {}'.format(ent.name, lineshot_pts))
                            game_state = GameStates.LINESHOT
                            if not active_enemy_turrets:
                                previous_game_state = GameStates.ENEMY_TURN
                            else:
                                previous_game_state = GameStates.ENEMY_TURRET_TURN
                        if message:
                            message_log.add_message(message)
                    if death_game_state:
                        previous_game_state = death_game_state

                # with no shots or no active turrets, switch to players turn
                if not enemy_turret_results and not dead_entity:
                    # do a pass through to rdy up turrets in case you only fired some of your complement
                    if active_enemy_turrets:
                        for item_entity in ent.inventory.items:
                            if item_entity.ai is not None and item_entity not in active_turrets and \
                                    item_entity.item.max_charge_time is not None:
                                if item_entity.item.charge_time:
                                    item_entity.item.charge_time -= 1
                    game_state = GameStates.ENEMY_TURN
            else:
                game_state = GameStates.ENEMY_TURN

        # build list of enemies
        if not entity_turn_order:
            entity_turn_order = [ent for ent in entities if ent.ai is not None and
                                 libtcod.map_is_in_fov(fov_map, ent.x, ent.y)]


def main():
    constants = initialize_new_game.get_constants()
    position = 0

    terminal.open()
    terminal.set(
        "window: size=" + str(constants['screen_width']) + "x" + str(constants['screen_height']) + ', title=Space Game')
    terminal.set("font: fonts\courbd.ttf, size=" + constants.get('fontsize'))
    # terminal.set("input.filter={keyboard, mouse}")

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    while True:
        # show the background image, at twice the regular console resolution
        # clear scene especially after quitting game
        terminal.layer(0)
        terminal.clear()
        # show the game's title, and some credits!
        title = 'SPACE GAME'
        titlex = int(constants['screen_width'] / 2 - len(title) / 2)
        titley = int(constants['screen_height'] / 2)

        subtitle = 'Game by Eric Younkin'
        subtitlex = int(constants['screen_width'] / 2 - len(subtitle) / 2)
        subtitley = int(constants['screen_height'] / 2 + 2)

        terminal.color('yellow')
        terminal.print_(titlex, titley, '[align=center]' + title)
        terminal.print_(subtitlex, subtitley, '[align=center][font=0xE000]' + subtitle)

        # show options and wait for the player's choice
        options = ['Play a new game', 'Continue last game', 'Quit']
        menu('', options, 30, constants['screen_width'],
             constants['screen_height'], position=position, type='main')

        key = terminal.read()
        action = input_handlers.handle_menu_keys(key)

        menupos = action.get('menupos')
        select = action.get('select')
        ex = action.get('exit')
        resize = action.get('resize')

        if ex:
            break
        elif menupos:
            position += menupos
            if position < 0:
                position = 0
            if position >= len(options) - 1:
                position = len(options) - 1
        elif select:
            if position == 0:
                player, entities, game_map, message_log, game_state = initialize_new_game.get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN
                play_game(player, entities, game_map, message_log, game_state, constants)
            elif position == 1:  # load last game
                try:
                    player, entities, game_map, message_log, game_state = data_loaders.load_game()
                    play_game(player, entities, game_map, message_log, game_state, constants)
                except FileNotFoundError:
                    message_box('No save game to load', 50, constants['screen_width'], constants['screen_height'])
                    play_game(player, entities, game_map, message_log, game_state, constants)
            elif position == 2:  # quit
                break
        elif resize:
            print(size)
            if size == '8':
                size = '12'
            elif size == '12:':
                size = '16'
            elif size == '16':
                size = '8'
                terminal.set("font: fonts\courbd.ttf, size=" + size)


if __name__ == '__main__':
    main()
