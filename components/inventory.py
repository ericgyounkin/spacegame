import libtcodpy as libtcod
from game_messages import Message


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({'item_added': None,
                            'message': Message('You cannot carry any more, your cargo is full', 'yellow')
                            })
        else:
            results.append({'item_added': item,
                            'message': Message("The {} is brought into your ship's cargo!".format(item.name), 'blue')
                            })
            self.items.append(item)
        return results

    def use(self, item_entity, **kwargs):
        results = []
        item_component = item_entity.item
        inventory_enter_key = kwargs.get('inventory_enter_key')

        if item_component.use_function is None:
            results.append({'message': Message('The {} cannot be used'.format(item_entity.name), 'yellow')})
        else:
            if item_component.targeting == 'manual' and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            elif item_component.targeting in ['auto_on', 'auto_off'] and inventory_enter_key:
                results.append({'toggle_turret': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)
                for item_use_result in item_use_results:
                    if item_use_result:
                        if item_use_result.get('consumed'):
                            item_component.charge_time = item_component.max_charge_time
                            item_component.quantity -= 1
                            if item_component.quantity <= 0:
                                self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item,
                        'message': Message('The {} is shot into space!'.format(item.name), 'yellow')})
        return results