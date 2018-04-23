import libtcodpy as libtcod
from game_messages import Message
from entity import get_blocking_entities_at_location
from components import ai
from engine import debug_mode

DEBUG = debug_mode()


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.combatship.hp == entity.combatship.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', 'yellow')})
    else:
        entity.combatship.heal(amount)
        results.append({'consumed': True, 'message': Message('Your ship starts mending itself!', 'green')})
    return results


def invisible_nearest_shot(*args, **kwargs):
    source = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')
    name = kwargs.get('name')
    hit = kwargs.get('hit')
    blocked = kwargs.get('blocked')

    results = []
    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.combatship and entity != source and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = source.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'autofire': True, 'consumed': True, 'target': target,
                        'message': Message('{} is hit by the {} for {} damage'.format(target.name, name, damage))})
        results.extend(target.combatship.take_damage(damage))
    else:
        pass
        # results.append(
        #     {'consumed': False, 'target': None, 'message': Message('No enemy close enough to target!', 'red')})
    return results


def target_area_attack(*args, **kwargs):
    source = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    maximum_range = kwargs.get('maximum_range')
    name = kwargs.get('name')
    hit = kwargs.get('hit')
    blocked = kwargs.get('blocked')

    results = []

    distance = source.distance(target_x, target_y)
    # if you arent processing a long miss arc (hit) and the user selected some point outside the FOV or wpn range...
    if hit == 'yes' and (not libtcod.map_is_in_fov(fov_map, target_x, target_y) or distance > maximum_range):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your maximum range.', 'yellow')})
        return results
    if hit == 'no':
        results.append({'message': Message('Error in computing firing solution for {}!'.format(name), 'yellow')})
    results.append({'consumed': True})

    # struck a wall
    if blocked:
        results.append({'message': Message(
            'The {} strikes the wall and detonates, in a blinding flash!'.format(name), 'orange')})
    else:
        results.append({'message': Message(
            'The {} detonates, in a blinding flash!'.format(name), 'orange')})

    results.append({'explosion': [radius, (target_x, target_y)]})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.combatship:
            dmg_result = libtcod.random_get_int(0, int(damage / 3), damage)
            results.append(
                {'message': Message('The {} gets hit for {} damage'.format(entity.name, dmg_result), 'orange')})
            results.extend(entity.combatship.take_damage(dmg_result))

    return results


def target_shot(*args, **kwargs):
    source = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    mode = kwargs.get('mode')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')
    name = kwargs.get('name')
    hit = kwargs.get('hit')
    blocked = kwargs.get('blocked')
    color = kwargs.get('color')

    results = []
    distance = source.distance(target_x, target_y)
    if DEBUG:
        print('DEBUG {} distance {} range {}'.format(source.name, distance, maximum_range))

    # if you arent processing a long miss arc (hit=yes) and the user selected some point outside the FOV or wpn range...
    if hit == 'yes' and (not libtcod.map_is_in_fov(fov_map, target_x, target_y) or distance > maximum_range):
        target_message = Message('You cannot target a tile outside of your field of view.', 'yellow')
        results.append({'consumed': False, 'message': target_message})
        return results

    if mode == 'confusion':
        for entity in entities:
            if entity.x == target_x and entity.y == target_y and entity.ai:
                virus_ai = ai.VirusAI(entity.ai, 10)
                virus_ai.owner = entity
                entity.ai = virus_ai
                results.append({'consumed': True, 'lineshot': [target_x, target_y],
                                'message': Message("The {}'s AI loses control.".format(entity.name), 'light_green')})
                break
        if not results:
            results.append(
                {'consumed': False, 'message': Message('There is no targetable enemy at that location.', 'yellow')})

    elif mode == 'damage':
        for entity in entities:
            if entity.x == target_x and entity.y == target_y and entity.combatship:
                # roll damage
                dmg_result = libtcod.random_get_int(0, int(damage/3), damage)
                if color:
                    clr = color
                else:
                    clr = 'yellow'
                results.append({'consumed': True, 'lineshot': {'pts': [target_x, target_y], 'clr': clr},
                                'message': Message(
                                    '{}:{} deals {} damage to {}'.format(source.name, name, dmg_result, entity.name),
                                    'orange')})
                dmg = entity.combatship.take_damage(dmg_result)
                if dmg:
                    results.append(dmg[0])
        if not results and hit == 'no':
                if color:
                    clr = color
                else:
                    clr = 'yellow'
                results.append({'consumed': True, 'lineshot': {'pts': [target_x, target_y], 'clr': clr},
                                'message': Message('{}:{} misses {}'.format(source.name, name, entity.name),
                                                   'yellow')})
        if not results:
            results.append(
                {'consumed': False, 'message': Message('There is no targetable enemy at that location.', 'yellow')})
    return results


def target_with_accuracy(owner, target_x, target_y, accuracy, game_map, entities):
    blocked = False
    acc_roll = libtcod.random_get_int(0, 0, 100)
    if DEBUG:
        print('DEBUG {} actual target: {}, {}'.format(owner.name, target_x, target_y))
        print('DEBUG {} roll: {}, accuracy: {}'.format(owner.name, acc_roll, accuracy))
    if acc_roll < accuracy:  # hit! return target
        newtarget_x = target_x
        newtarget_y = target_y
        hit = 'yes'
    else:   # miss! continue the line a bit longer to allow the projectile to keep moving
        xoff = libtcod.random_get_int(0, 1, 1)
        yoff = libtcod.random_get_int(0, 1, 1)
        pos_or_neg = libtcod.random_get_int(0, 0, 1)
        if pos_or_neg:
            target_x = target_x + xoff
        else:
            target_x = target_x - xoff
        pos_or_neg = libtcod.random_get_int(0, 0, 1)
        if pos_or_neg:
            target_y = target_y + yoff
        else:
            target_y = target_y - yoff

        # build new line extending out much further
        newtarget_x = 2 * target_x - 1 * owner.x
        newtarget_y = 2 * target_y - 1 * owner.y

        # make sure its in the game map
        if newtarget_x <= 0:
            newtarget_y = newtarget_y - newtarget_x
            newtarget_x = 0
            if DEBUG:
                print('DEBUG {} out_of_map, using {}, {}'.format(owner.name, newtarget_x, newtarget_y))
        elif newtarget_x >= game_map.width - 1:
            newtarget_y = newtarget_y - (newtarget_x - game_map.width - 1)
            newtarget_x = game_map.width - 1
            if DEBUG:
                print('DEBUG {} out_of_map, using {}, {}'.format(owner.name, newtarget_x, newtarget_y))
        if newtarget_y <= 0:
            newtarget_x = newtarget_x - newtarget_y
            newtarget_y = 0
            if DEBUG:
                print('DEBUG {} out_of_map, using {}, {}'.format(owner.name, newtarget_x, newtarget_y))
        elif newtarget_y >= game_map.height - 1:
            newtarget_x = newtarget_x - (newtarget_y - game_map.height - 1)
            newtarget_y = game_map.height - 1
            if DEBUG:
                print('DEBUG {} out_of_map, using {}, {}'.format(owner.name, newtarget_x, newtarget_y))

        for pts in libtcod.line_iter(owner.x, owner.y, newtarget_x, newtarget_y):
            if game_map.is_blocked(pts[0], pts[1]) or get_blocking_entities_at_location(entities, pts[0], pts[1]):
                if (pts[0], pts[1]) != (owner.x, owner.y):
                    if DEBUG:
                        print('DEBUG {} blocked'.format(owner.name))
                    newtarget_x = pts[0]
                    newtarget_y = pts[1]
                    break
        hit = 'no'
        if DEBUG:
            print('DEBUG {} failed roll, new target: {}, {}, player: {}, {}'.format(owner.name, newtarget_x, newtarget_y, owner.x, owner.y))
    if game_map.is_blocked(newtarget_x, newtarget_y):
        blocked = True

    return hit, blocked, newtarget_x, newtarget_y


