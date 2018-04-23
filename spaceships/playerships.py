from components import combatship, inventory, item, ai
from game_messages import Message
import entity
import item_functions
from render_functions import RenderOrder


def player_cruiser():
    combatship_component = combatship.CombatShip(hull=100, shields=100, defense=2, power=5)
    inventory_component = inventory.Inventory(5)

    targetmessage = Message('Use the arrow keys and hit enter to target the enemy!', 'light cyan')

    item_component = item.Item(use_function=item_functions.target_area_attack, targeting='manual',
                               targeting_message=targetmessage, quantity=5, max_charge_time=4, damage=12, radius=2,
                               maximum_range=80, accuracy=50, name='Antimatter Warhead')
    warhead = entity.Entity(None, None, '#', 'darker red', 'AM Warhead Launcher', render_order=RenderOrder.ITEM,
                            item=item_component)
    inventory_component.items.append(warhead)

    item_component1 = item.Item(use_function=item_functions.target_shot, targeting='auto_on',
                                targeting_message=targetmessage, quantity=50, max_charge_time=2, damage=20,
                                maximum_range=10, accuracy=70, mode='damage', name='Laser Turret', color='light red')
    turret1 = entity.Entity(None, None, '#', 'yellow', 'Laser Turret', render_order=RenderOrder.ITEM,
                            ai=ai.TurretAI(), item=item_component1)
    inventory_component.items.append(turret1)

    item_component2 = item.Item(use_function=item_functions.target_shot, targeting='auto_on',
                                targeting_message=targetmessage, quantity=50, max_charge_time=2, damage=20,
                                maximum_range=10, accuracy=70, mode='damage', name='Laser Turret', color='light red')
    turret2 = entity.Entity(None, None, '#', 'yellow', 'Laser Turret', render_order=RenderOrder.ITEM,
                            ai=ai.TurretAI(), item=item_component2)
    inventory_component.items.append(turret2)

    item_component3 = item.Item(use_function=item_functions.target_shot, targeting='auto_on',
                                targeting_message=targetmessage, quantity=50, max_charge_time=2, damage=20,
                                maximum_range=10, accuracy=70, mode='damage', name='Laser Turret', color='light red')
    turret3 = entity.Entity(None, None, '#', 'yellow', 'Laser Turret', render_order=RenderOrder.ITEM,
                            ai=ai.TurretAI(), item=item_component3)
    inventory_component.items.append(turret3)

    finalship = entity.Entity(0, 0, '@', 'white', 'Player', blocks=True, render_order=RenderOrder.ACTOR,
                              combatship=combatship_component, inventory=inventory_component)
    return finalship