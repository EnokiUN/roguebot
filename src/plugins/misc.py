import disnake as disneyK
from disnake.ext import plugins

plugin = plugins.Plugin(name="Miscellaneous", logger="misc plugin")


@plugin.slash_command(description="Pongs you back!")
async def ping(inter: disneyK.CommandInteraction):
    await inter.send("Pong!")


setup, teardown = plugin.create_extension_handlers()
