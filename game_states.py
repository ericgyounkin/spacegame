from enum import Enum


class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    GOTO_EQUIP = 4
    DROP_EQUIP = 5
    TARGETING = 6
    EXPLOSION = 7
    EXPLOSION_FINSHED = 8
    LINESHOT = 9
    PLAYER_TURRET_TURN = 10
    ENEMY_TURRET_TURN = 11
    SET_TARGET = 12