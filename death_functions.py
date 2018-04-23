import libtcodpy as libtcod
from render_functions import RenderOrder
from game_states import GameStates
from game_messages import Message


def kill_player(player):
    player.char = '%'
    player.color = 'dark red'

    return Message('You were destroyed!', 'red'), GameStates.PLAYER_DEAD


def kill_enemy(enemy):
    death_message = Message('{0} is destroyed!'.format(enemy.name.capitalize()), 'orange')

    enemy.char = '%'
    enemy.color = 'dark red'
    enemy.blocks = False
    enemy.combatship = None
    enemy.ai = None
    enemy.name = 'remains of ' + enemy.name
    enemy.render_order = RenderOrder.CORPSE

    return death_message