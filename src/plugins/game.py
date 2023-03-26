from __future__ import annotations

from enum import Enum
from random import randint
from typing import Any, NamedTuple, Optional, Protocol

import disnake as disneyK
from disnake.ext import plugins
from disnake.ui.button import Button, button
from disnake.ui.view import View

plugin = plugins.Plugin(name="Game", logger="game plugin")

MAP_WIDTH = 8
MAP_HEIGHT = 8


class Position(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)


ORIGIN = Position(0, 0)


class Tile(Protocol):
    name: str
    display: str
    solid: bool = False

    def interact(self, game: GameView, position: Position):  # noqa: ARG002
        return None


class Stone(Tile):
    name = "Stone"
    display = "<:stone:1089362910200987688>"


class Book(Tile):
    name = "Book"
    display = ":book:"
    solid = True

    def interact(self, game: GameView, position: Position):
        knowledge = game.data.get("knowledge", 0) + 1
        game.data["knowledge"] = knowledge
        game.message = f"You have acquired {knowledge} knowledge."
        game.map.tiles[position] = Stone()


class Map:
    def __init__(self):
        self.tiles: dict[Position, Tile] = {}
        self.items = {}
        self.entities = {}

        self.door_up = None
        self.door_down = None
        self.door_left = None
        self.door_right = None

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if randint(0, 10) == 0:
                    self.tiles[Position(x, y)] = Book()
                    continue
                self.tiles[Position(x, y)] = Stone()


class Direction(Position, Enum):
    Up = (0, -1)
    Down = (0, 1)
    Left = (-1, 0)
    Right = (1, 0)


class Player:
    def __init__(self, starting_pos: Position = ORIGIN):
        self.pos = starting_pos

    def move(self, direction: Direction, game: GameView):
        new_pos = self.pos + direction
        new_pos = Position(
            max(min(new_pos.x, MAP_WIDTH - 1), 0),
            max(min(new_pos.y, MAP_HEIGHT - 1), 0),
        )
        tile = game.map.tiles[new_pos]
        tile.interact(game, new_pos)
        if not tile.solid:
            self.pos = new_pos


class GameView(View):
    def __init__(self) -> None:
        self.player = Player()
        self.map = Map()
        self.embed = disneyK.Embed(title="Map")
        self.message: str | None = None
        self.data: dict[str, Any] = {}
        super().__init__(timeout=None)
        self.update()

    def update(self):
        map_preview = self.message + "\n\n" if self.message else ""
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.player.pos == Position(x, y):
                    map_preview += "<:bean:1080551938678083674>"
                    continue
                map_preview += self.map.tiles[Position(x, y)].display
            map_preview += "\n"
        self.embed.description = map_preview[:-1]

    @button(label="\u200b", disabled=True, row=1)
    async def filler1(self, *_: object):
        ...

    @button(emoji="⬆️", row=1, style=disneyK.ButtonStyle.blurple)
    async def up_button(self, _: Button, inter: disneyK.MessageInteraction):
        self.player.move(Direction.Up, self)
        self.update()
        await inter.response.edit_message(embed=self.embed)

    @button(label="\u200b", disabled=True, row=1)
    async def filler2(self, *_: object):
        ...

    @button(emoji="◀️", row=2, style=disneyK.ButtonStyle.blurple)
    async def left_button(self, _: Button, inter: disneyK.MessageInteraction):
        self.player.move(Direction.Left, self)
        self.update()
        await inter.response.edit_message(embed=self.embed)

    @button(label="\u200b", disabled=True, row=2)
    async def filler3(self, *_: object):
        ...

    @button(emoji="▶️", row=2, style=disneyK.ButtonStyle.blurple)
    async def right_button(self, _: Button, inter: disneyK.MessageInteraction):
        self.player.move(Direction.Right, self)
        self.update()
        await inter.response.edit_message(embed=self.embed)

    @button(label="\u200b", disabled=True, row=3)
    async def filler4(self, *_: object):
        ...

    @button(emoji="⬇️", row=3, style=disneyK.ButtonStyle.blurple)
    async def down_button(self, _: Button, inter: disneyK.MessageInteraction):
        self.player.move(Direction.Down, self)
        self.update()
        await inter.response.edit_message(embed=self.embed)

    @button(label="\u200b", disabled=True, row=3)
    async def filler5(self, *_: object):
        ...


@plugin.slash_command(description="Lets you attempt a session of a roguelike")
async def play(inter: disneyK.CommandInteraction):
    view = GameView()
    await inter.send(embed=view.embed, view=view)


setup, teardown = plugin.create_extension_handlers()
