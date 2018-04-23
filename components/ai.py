import libtcodpy as libtcod
from game_messages import Message
import item_functions
from engine import debug_mode

DEBUG = debug_mode()


class BasicAI:
    def handle_turret(self, turret, target, fov_map, game_map, entities, constants):

        results = turret.ai.take_enemy_turn(self.owner, target, fov_map, game_map, entities, constants)
        if DEBUG:
            print('DEBUG {} handle turret {}, target health {}, results {}'.format(self.owner.name,
                                                                                   turret,
                                                                                   target.combatship.hull, results))
        return results

    def take_turn(self, target, fov_map, game_map, entities, constants):
        results = []
        enemy = self.owner
        if libtcod.map_is_in_fov(fov_map, enemy.x, enemy.y):
            if enemy.distance_to(target) >= 5:
                enemy.move_astar(target, entities, game_map)
            elif  enemy.distance_to(target) >= 0:
                enemy.move_randomly()
            elif target.combatship.hull > 0:
                attack_results = enemy.combatship.attack(target)
                results.extend(attack_results)
            enemy.combatship.regen_shields()
        return results


class VirusAI:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        if self.number_of_turns > 0:
            random_x = self.owner.x + libtcod.random_get_int(0, 0, 2) - 1
            random_y = self.owner.x + libtcod.random_get_int(0, 0, 2) - 1
            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)
            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {} regains control!'.format(self.owner.name), 'red')})
        return results


class TurretAI:
    def take_turn(self, player, target, fov_map, game_map, entities):
        results = []
        item_entity = self.owner
        if libtcod.map_is_in_fov(fov_map, target.x, target.y) and player.distance_to(
                                 target) <= item_entity.item.function_kwargs.get('maximum_range') and target.ai:
            if item_entity.item.targeting:
                hit, blocked, target_x, target_y = item_functions.target_with_accuracy(player, target.x, target.y,
                                                                        item_entity.item.function_kwargs.get('accuracy'),
                                                                        game_map, entities)
                results = player.inventory.use(item_entity, entities=entities, fov_map=fov_map,
                                               target_x=target_x, target_y=target_y, blocked=blocked, hit=hit)
            else:
                results = player.inventory.use(item_entity, entities=entities, fov_map=fov_map)
        else:
            results = []
        return results

    def take_enemy_turn(self, enemy, target, fov_map, game_map, entities, constants):
        results = []
        item_entity = self.owner
        if DEBUG:
            print('DEBUG {} check if {} in fov, source {}, target {}'.format(enemy.name, target.name, [enemy.x, enemy.y],
                                                                             [target.x, target.y]))
            print('DEBUG {} distance, max range to {} is  {}, {}'.format(enemy.name, target.name, enemy.distance_to(
                    target), item_entity.item.function_kwargs.get('maximum_range')))
        if libtcod.map_is_in_fov(fov_map, target.x, target.y) and enemy.distance_to(
                target) <= item_entity.item.function_kwargs.get('maximum_range'):
            hit, blocked, target_x, target_y = item_functions.target_with_accuracy(enemy, target.x, target.y,
                                                                                   item_entity.item.function_kwargs.get(
                                                                                       'accuracy'),
                                                                                   game_map, entities)
            if DEBUG:
                print('DEBUG {} new enemy target {}'.format(enemy.name, [target_x, target_y]))
            results = enemy.inventory.use(item_entity, entities=entities, fov_map=fov_map, target_x=target_x,
                                          target_y=target_y, blocked=blocked, hit=hit)
            if DEBUG:
                for result in results:
                    lineshot = result.get('lineshot')
                    if lineshot:
                        print('DEBUG {} lineshot {}'.format(enemy.name, lineshot))
        return results