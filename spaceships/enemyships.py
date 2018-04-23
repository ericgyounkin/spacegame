from components import combatship, inventory, item, ai
import entity
import item_functions
from render_functions import RenderOrder


def cruiser(x, y):
    combatship_component = combatship.CombatShip(hull=80, shields=20, defense=0, power=3)
    ai_component = ai.BasicAI()
    inventory_component = inventory.Inventory(5)
    item_component1 = item.Item(use_function=item_functions.target_shot, targeting='auto_on',
                                targeting_message='', quantity=50, max_charge_time=2, damage=10,
                                maximum_range=10, accuracy=70, mode='damage', name='Laser Turret', color='light blue')
    turret1 = entity.Entity(None, None, '#', 'yellow', 'Laser Turret', render_order=RenderOrder.ITEM,
                            ai=ai.TurretAI(), item=item_component1)
    inventory_component.items.append(turret1)

    item_component2 = item.Item(use_function=item_functions.target_shot, targeting='auto_on',
                                targeting_message='', quantity=50, max_charge_time=2, damage=10,
                                maximum_range=10, accuracy=70, mode='damage', name='Laser Turret', color='light blue')
    turret2 = entity.Entity(None, None, '#', 'yellow', 'Laser Turret', render_order=RenderOrder.ITEM,
                            ai=ai.TurretAI(), item=item_component2)
    inventory_component.items.append(turret2)
    enemy = entity.Entity(x, y, 'c', 'green', 'Cruiser', blocks=True, render_order=RenderOrder.ACTOR,
                          combatship=combatship_component, ai=ai_component, inventory=inventory_component)
    return enemy


def battleship(x, y):
    combatship_component = combatship.CombatShip(hull=100, shields=20, defense=0, power=3)
    ai_component = ai.BasicAI()
    inventory_component = inventory.Inventory(5)
    item_component = item.Item(use_function=item_functions.target_shot, targeting='auto_on',
                               targeting_message='', quantity=50, max_charge_time=2, damage=10,
                               maximum_range=10, accuracy=70, mode='damage', name='Laser Turret', color='light blue')
    turret1 = entity.Entity(None, None, '#', 'yellow', 'Laser Turret', render_order=RenderOrder.ITEM,
                            ai=ai.TurretAI(), item=item_component)
    inventory_component.items.append(turret1)
    enemy = entity.Entity(x, y, 'b', 'darker green', 'Battleship', blocks=True, render_order=RenderOrder.ACTOR,
                          combatship=combatship_component, ai=ai_component, inventory=inventory_component)
    return enemy