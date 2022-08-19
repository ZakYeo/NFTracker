import discord
from discord.ext import commands
from discord.commands import Option
import aiohttp
from json import dumps
import datetime
     

class OpenseaTracker(commands.Cog):
    """
    Opensea Tracking Translation Bot
    """

    def __init__(self, bot): 
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.headers = {
            "Accept": "application/json",
                    "X-API-KEY": self.bot.auth_key
        }

    @discord.slash_command(name="stats", description="View the statistics for a collection!")
    async def stats(self,ctx,
        collection: Option(str, "Enter the collection to view the stats for", required=True),
    ):
        
        async with self.session.get(f"https://api.opensea.io/api/v1/collection/{collection}",
                headers=self.headers) as r:
            if(r.status != 200):
                await ctx.interaction.response.send_message(embed=await self.get_error_embed(
                    f"Please check the collection name/slug and try again.\n **Error code {r.status}**"))
                return
            json = await r.json()
            #await self.create_stats_embed(json)
        await ctx.respond(embed=await self.get_stats_embed(json))
 
    async def create_stats_embed(self,json):
        with open("stats.txt", "w+") as f:
            f.write(dumps(json,indent=4))
    
    async def get_error_embed(self, message):
        return discord.Embed(title="An error has occurred", description=message, color=discord.Color.red())

    async def get_stats_embed(self, json):
        link = json["collection"]["primary_asset_contracts"][0]["external_link"]
        img = json["collection"]["primary_asset_contracts"][0]["image_url"]
        stats = json["collection"]["stats"]
        one_day_volume = stats["one_day_volume"]
        one_day_change = stats["one_day_change"]
        one_day_sales = stats["one_day_sales"]
        one_day_average_price = stats["one_day_average_price"]

        seven_day_volume = stats["seven_day_volume"]
        seven_day_change = stats["seven_day_change"]
        seven_day_sales = stats["seven_day_sales"]
        seven_day_average_price = stats["seven_day_average_price"]

        thirty_day_volume = stats["thirty_day_volume"]
        thirty_day_change = stats["thirty_day_change"]
        thirty_day_sales = stats["thirty_day_sales"]
        thirty_day_average_price = stats["thirty_day_average_price"]

        total_volume = stats["total_volume"]
        total_sales = stats["total_sales"]
        total_supply = stats["total_supply"]
        num_owners = stats["num_owners"]
        average_price = stats["average_price"]
        market_cap = stats["market_cap"]
        floor = stats["floor_price"]
        total_supply = stats["total_supply"]

        name = json["collection"]["primary_asset_contracts"][0]["name"]

        with open("test.txt", "w+") as f:
            f.write(dumps(json, indent=4))

        embed = discord.Embed(description=json["collection"]["primary_asset_contracts"][0]["description"],
                            color=discord.Color.blue())
        #embed.set_thumbnail(url=img)
        if(link is None):
            embed.set_author(name=name,icon_url=img)
        else:
            embed.set_author(name=name, url=link, icon_url=img)
        embed.set_thumbnail(
                            url="https://i.imgur.com/A4k4uCi.png")
        embed.add_field(name="__One Day Metrics__", value="**Volume:** {:.2f}\n**Sales:** {:.0f}\n**Change:** {:.2%}\n**Avg. Price:** {:.2f}".format(
            one_day_volume, one_day_sales, one_day_change, one_day_average_price
        ))
        embed.add_field(name="__Seven Day Metrics__", value="**Volume:** {:.2f}\n**Sales:** {:.0f}\n**Change:** {:.2%}\n**Avg. Price:** {:.2f}".format(
            seven_day_volume, seven_day_sales, seven_day_change, seven_day_average_price
        ))

        embed.add_field(name="__Thirty Day Metrics__", value="**Volume:** {:.2f}\n**Sales:** {:.0f}\n**Change:** {:.2%}\n**Avg. Price:** {:.2f}".format(
            thirty_day_volume, thirty_day_sales, thirty_day_change, thirty_day_average_price
        ), inline=True)
        embed.add_field(name="__Total Volume__", value="{:.2f}E".format(total_volume))
        embed.add_field(name="__Total Sales__", value="{:.2f}E".format(total_sales))
        embed.add_field(name="__Total Supply__", value="{}".format(total_supply))
        embed.add_field(name="__Average Price__", value="{:.2f}E".format(average_price))
        embed.add_field(name="__Market Cap__", value="{:.2f}E".format(market_cap))
        embed.add_field(name="__Unique Owners__", value="{}".format(num_owners))
        #embed.add_field(name="__Total Metrics__", value="**Volume:** {:.2f}\n**Sales:** {:.0f}\n**Unique Owners:** {:.0f}\n**Avg. Price:** {:.2f}\n**Market Cap:** {:.2f}\n**Floor:**{:.2f}".format(
        #    total_volume, total_sales, num_owners, average_price, market_cap, floor
        #), inline=False)

        #embed.set_image(url=img)
        embed.set_footer(text="FungiBot | {}".format(datetime.datetime.utcnow().strftime('%H:%M:%S')))

        return embed

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(OpenseaTracker(bot)) # add the cog to the bot