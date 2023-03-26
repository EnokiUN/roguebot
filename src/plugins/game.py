from __future__ import annotations

import math
from enum import Enum
from random import randint
from typing import Any, NamedTuple, Protocol

import disnake as disneyK
from disnake.ext import plugins
from disnake.ui.button import Button, button
from disnake.ui.view import View

plugin = plugins.Plugin(name="Game", logger="game plugin")

MAP_WIDTH = 7
MAP_HEIGHT = 7
PLAYER_DISPLAY = "<:bean:1089532689889107999>"


class Position(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)


ORIGIN = Position(0, 0)
CENTER = Position(math.floor(MAP_WIDTH / 2), math.floor(MAP_HEIGHT / 2))


class Tile(Protocol):
    name: str
    display: str
    solid: bool = False

    def interact(
        self, game: GameView, current_map: Map, position: Position # noqa: ARG002
    ):
        return None


class Stone(Tile):
    name = "Stone"
    display = "<:stone:1089362910200987688>"


class Wall(Tile):
    name = "Wall"
    display = "<:wall:1089569990832836608>"
    solid = True


class Book(Tile):
    name = "Book"
    display = "<:booktile:1089588826244124712>"
    solid = True

    def interact(self, game: GameView, current_map: Map, position: Position):
        knowledge = game.data.get("knowledge", 0) + 1
        game.data["knowledge"] = knowledge
        game.message = f"You have acquired {knowledge} knowledge."
        current_map.tiles[position] = Stone()


class Map:
    def __init__(self, position: Position = ORIGIN):
        self.pos = position

        self.tiles: dict[Position, Tile] = {}
        self.items = {}
        self.entities = {}

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if (y == 0 or y == MAP_HEIGHT - 1) and (
                    x < CENTER.x - 1 or x > CENTER.x + 1
                ):
                    self.tiles[Position(x, y)] = Wall()
                    continue
                if (x == 0 or x == MAP_WIDTH - 1) and (
                    y < CENTER.y - 1 or y > CENTER.y + 1
                ):
                    self.tiles[Position(x, y)] = Wall()
                    continue
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
    def __init__(self, starting_pos: Position = CENTER):
        self.pos = starting_pos

    def move(self, direction: Direction, game: GameView):
        new_pos = self.pos + direction
        new_map = None

        if new_pos.x == -1:
            new_map_pos = game.map.pos + Direction.Left
            new_map = game.maps.setdefault(new_map_pos, Map(new_map_pos))
            new_pos = Position(MAP_WIDTH - 1, new_pos.y)
        elif new_pos.x == MAP_WIDTH:
            new_map_pos = game.map.pos + Direction.Right
            new_map = game.maps.setdefault(new_map_pos, Map(new_map_pos))
            new_pos = Position(0, new_pos.y)

        if new_pos.y == -1:
            new_map_pos = game.map.pos + Direction.Up
            new_map = game.maps.setdefault(new_map_pos, Map(new_map_pos))
            new_pos = Position(new_pos.x, MAP_HEIGHT - 1)
        if new_pos.y == MAP_WIDTH:
            new_map_pos = game.map.pos + Direction.Down
            new_map = game.maps.setdefault(new_map_pos, Map(new_map_pos))
            new_pos = Position(new_pos.x, 0)

        if new_map:
            tile = new_map.tiles[new_pos]
            tile.interact(game, new_map, new_pos)
        else:
            tile = game.map.tiles[new_pos]
            tile.interact(game, game.map, new_pos)

        if not tile.solid:
            self.pos = new_pos
            if new_map:
                game.map = new_map


class GameView(View):
    def __init__(self, user: disneyK.Member) -> None:
        self.user = user
        self.player = Player()
        self.map = Map()
        self.maps: dict[Position, Map] = {}
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
                    map_preview += PLAYER_DISPLAY
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

    async def interaction_check(self, interaction: disneyK.MessageInteraction) -> bool:
        if interaction.author.id != self.user.id:
            await interaction.send(
                "This bean is not for you <:bean:1080551938678083674>", ephemeral=True
            )
            return False
        return True


@plugin.slash_command(description="Lets you attempt a session of a roguelike")
async def play(inter: disneyK.CommandInteraction):
    if isinstance(inter.author, disneyK.User):
        return await inter.send(
            "Make sure you're running this in a server <:bean:1080551938678083674>",
            ephemeral=True,
        )
    view = GameView(inter.author)
    await inter.send(embed=view.embed, view=view)


setup, teardown = plugin.create_extension_handlers()
