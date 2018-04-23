from random import randint
import libtcodpy as libtcod

from map_objects import diamond, tile
from spaceships import enemyships


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.asteroids = []
        self.asteroid_pts = []
        self.entities_pts = []
        self.tiles = self.initialize_tiles()
        self.stars_pts = []

    def initialize_tiles(self):
        tiles = [[tile.Tile(False) for y in range(self.height)] for x in range(self.width)]

        #block off the border for now
        for x in range(self.width):
            tiles[x][self.height-1].blocked = True
            tiles[x][self.height-1].block_sight = True
            tiles[x][0].blocked = True
            tiles[x][0].block_sight = True
        for y in range(self.height):
            tiles[self.width-1][y].blocked = True
            tiles[self.width-1][y].block_sight = True
            tiles[0][y].blocked = True
            tiles[0][y].block_sight = True
        return tiles

    def make_map(self, max_asteroids, max_asteroid_radius, entities,
                 max_enemies_per_screen, max_items_per_screen, max_stars_per_screen):
        for r in range(max_asteroids):
            # random radius and center
            r = randint(2, max_asteroid_radius)
            cent = [randint(0, self.width - r), randint(0, self.height - r)]

            new_ast = diamond.Diamond(cent, r)

            # run through the other asteroids and see if they intersect with this one
            for other_ast in self.asteroids:
                if new_ast.intersect(other_ast.points):
                    break
            else:
                # this means there are no intersections, so this asteroid is valid
                # "paint" it to the map's tiles
                self.create_asteroid(new_ast)
        self.place_stars(max_stars_per_screen)
        self.place_entities(entities, max_enemies_per_screen, max_items_per_screen)
        playerx ,playery = self.random_entity_location()
        for entity in entities:
            if entity.name in ['Player', 'TargetingCursor']:
                entity.x = playerx
                entity.y = playery

    def random_entity_location(self):
        found = False
        while not found:
            x, y = randint(0, self.width - 1), randint(0, self.height - 1)
            if not self.is_blocked(x, y):
                return x, y

    def place_stars(self, max_stars_per_screen):
        hue = ['grey', 'red', 'flame', 'orange', 'amber', 'yellow', 'lime', 'chartreuse', 'green', 'sea', 'turquoise',
               'cyan', 'sky', 'azure', 'blue', 'han', 'violet', 'purple', 'fuchsia', 'magenta', 'pink', 'crimson',
               'transparent']
        brightness = ['lightest', 'lighter', 'light', 'dark', 'darker', 'darkest']

        for x in range(0, max_stars_per_screen):
            clr = brightness[libtcod.random_get_int(0, 0, len(brightness) - 1)] + ' ' + \
                  hue[libtcod.random_get_int(0, 0, len(hue) - 1)]
            x, y = self.random_entity_location()
            self.stars_pts.append([x, y, clr])

    def create_asteroid(self, asteroid):
        # go through the tiles in the asteroid and make them not passable
        for x, y in asteroid.points:
                self.tiles[x][y].blocked = True
                self.tiles[x][y].block_sight = True

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, entities, max_enemies_per_screen, max_items_per_screen):
        # number_of_items = randint(1, max_items_per_screen)

        for i in range(max_enemies_per_screen):
            # Choose a random location in the room
            x, y = self.random_entity_location()

            if randint(0, 100) < 70:
                enemy = enemyships.cruiser(x, y)
            else:
                enemy = enemyships.battleship(x, y)
            entities.append(enemy)

        '''
        for i in range(number_of_items):
            item_chance = libtcod.random_get_int(None, 0, 100)
            x, y = self.random_entity_location(entities)

            if item_chance < 5:
                item_component = Item(use_function=heal, amount=4)
                item = Entity(x, y, '!', 'violet', 'Nanopaste', render_order=RenderOrder.ITEM,
                          item=item_component)
            elif item_chance < 50:
                targetmessage = Message('Use the mouse or keyboard to target the enemy!',
                                        'light cyan')
                item_component = Item(use_function=antimatter_warhead, targeting=True, targeting_message=targetmessage,
                                      damage=12, radius=3)
                item = Entity(x, y, '#', 'darker red', 'AM Warhead Launcher', render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_chance < 100:
                targetmessage = Message('Use the mouse or keyboard to target the enemy!',
                                        'light cyan')
                item_component = Item(use_function=upload_virus, targeting=True, targeting_message=targetmessage)
                item = Entity(x, y, '#', 'light pink', 'Virus Module', render_order=RenderOrder.ITEM,
                              item=item_component)
            else:
                item_component = Item(use_function=tesla_bolt, damage=20, maximum_range=5)
                item = Entity(x, y, '#', 'yellow', 'Tesla Module', render_order=RenderOrder.ITEM,
                              item=item_component)
            entities.append(item)
        '''
    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False