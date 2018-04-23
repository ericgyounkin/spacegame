import libtcodpy as libtcod
from bearlibterminal import terminal


def menu(header, options, width, screen_width, screen_height, position=None, type=None):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(0, 0, 0, width, screen_height, header)
    height = len(options) + header_height + 2

    # create an offscreen console that represents the menu's window
    terminal.layer(2)
    terminal.clear_area(0, 0, screen_width, screen_height)

    if type == 'main':
        x = int(screen_width / 2 - 9)
        y = int(screen_height / 2 + 5 + height)
    elif type == 'inventory':
        x = int(screen_width / 2 + 25)
        y = int(screen_height / 2)
    else:
        x = int(screen_width / 2)
        y = int(screen_height / 2)

    #while True:
    terminal.print_(x + 1, y, '[color=white]' + header)

    # print all the options
    h = header_height
    letter_index = ord('a')
    run = 0
    for option_text in options:
        text = option_text
        if position is not None:
            if run == position:
                terminal.print_(x + 1, h + y + 1, '[color=yellow]' + text)
            else:
                terminal.print_(x + 1, h + y + 1, '[color=white]' + text)
        else:
            terminal.print_(x + 1, h + y + 1, '[color=white]' + text)
        h += 1
        letter_index += 1
        run += 1

    # present the root console to the player and wait for keypress
    terminal.refresh()


def message_box(header, width, screen_width, screen_height):
    menu(header, [], width, screen_width, screen_height)


def inventory_menu(header, inventory, inventory_width, screen_width, screen_height, inventory_index):
    # show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(header, options, inventory_width, screen_width, screen_height, position=inventory_index, type='inventory')
