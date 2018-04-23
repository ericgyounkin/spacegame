import libtcodpy as libtcod
from game_messages import Message


class CombatShip:
    def __init__(self, hull, shields, defense, power):
        self.max_hull = hull
        self.hull = hull
        self.max_shields = shields
        self.shields = shields
        self.defense = defense
        self.power = power
        self.targeted = False

    def take_damage(self, amount):
        results = []
        overflow_damage = 0
        if self.shields:
            self.shields -= amount
            if self.shields <= 0:
                overflow_damage = abs(self.shields)
                self.shields = 0
            if overflow_damage:
                self.hull -= overflow_damage + 1
        elif self.hull:
            self.hull -= amount
        if self.hull <= 0:
            results.append({'dead': self.owner})
        return results

    def heal(self, amount):
        self.hull += amount
        if self.hull > self.max_hull:
            self.hull = self.max_hull

    def regen_shields(self):
        if self.shields < self.max_shields:
            self.shields += 1

    def attack(self, target):
        results = []
        damage = self.power - target.combatship.defense
        if damage > 0:
            results.append({'message': Message(
                    '{0} attacks {1} for {2} hit points.'.format(self.owner.name.capitalize(), target.name,
                                                                 str(damage)), 'white')})
            results.extend(target.combatship.take_damage(damage))
        else:
            results.append({'message': Message(
                    '{0} attacks {1} but does no damage.'.format(self.owner.name.capitalize(), target.name),
                                                                 'white')})
        return results