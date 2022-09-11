from xml.dom.minidom import Attr
import discord
from discord.ext import commands
from discord.commands import Option
import aiohttp
from json import dumps
from datetime import datetime
     

class OpenseaTracker(commands.Cog):
    """
    Opensea Tracking Translation Bot
    """

    def __init__(self, bot): 
        self.bot = bot
        self.firstTime = True
        self.headers = {
            "Accept": "application/json",
                    "X-API-KEY": self.bot.auth_key
        }
    
    @commands.Cog.listener()
    async def on_ready(self):
        if(self.firstTime):
            self.session = aiohttp.ClientSession()
            self.firstTime = False

    @discord.slash_command(name="stats", description="View the statistics for a collection!")
    async def stats(self,ctx,
        collection: Option(str, "Enter the collection to view the stats for", required=True),
    ):
        """
        Discord Stats Slash Command
        After providing a collection name, will respond with the statistics of that collection
        """
        
        data = await self.get_json_from_url(f"https://api.opensea.io/api/v1/collection/{collection}")
        if(type(data) is int):
            await ctx.interaction.response.send_message(embed=await self.get_error_embed(
                    f"Please check the collection name/slug and try again.\n **Error code {data}**"), ephemeral=False)
            return
        await ctx.respond(embed=await self.get_stats_embed(data), ephemeral=False)
    
    @discord.slash_command()
    async def sales(self, ctx,
        collection: Option(str, "Enter the collection you wish to view the activity of", required=True),
    ):  
        """
        Discord Slash Command
        Returns an embedded message including the most recent sale of specified collection.
        Includes buttons to cycle through sales
        """
        json = await self.get_json_from_url(f"https://api.opensea.io/api/v1/events?only_opensea=false&collection_slug={collection}&event_type=successful&limit=1")
        await ctx.interaction.response.send_message(embed=await self.get_sales_embed(json, 1), view=Pagination(self.bot,
            json["next"], json["previous"], collection, 1, 1, self.get_json_from_url, self.get_sales_embed, json), ephemeral=False)

    async def get_json_from_url(self, url):
        """
        Return the json content from a url asynchronously
        If status code is not 200, will return that code
        """
        try:
            async with self.session.get(url,
                    headers=self.headers) as r:
                if(r.status != 200):
                    return r.status
                json = await r.json()
        except AttributeError:
            # It's possible session did not set properly, set it now
            self.session = aiohttp.ClientSession()
            async with self.session.get(url,
                    headers=self.headers) as r:
                if(r.status != 200):
                    return r.status
                json = await r.json()
        return json
    
    async def get_sales_embed(self, json, page):
        event = json["asset_events"][0]
        asset = event["asset"]
        image_url = asset["image_url"]
        link = asset["permalink"]
        collection_name = asset["collection"]["name"]
        token_id = asset["token_id"]
        embed = discord.Embed()
        embed.set_author(name=f"{collection_name} #{token_id} Was Sold", url=link)

        if(page == 1):
            timestamp = event["event_timestamp"]
            total_price = int(event["total_price"]) / 1000000000000000000 # ETH is divisible by 18 decimal places, and I want to see x.x rather than xxxxxxx...
            seller_address = event["seller"]["address"]
            buyer_address = event["winner_account"]["address"]
            
            embed.add_field(name="Price", value=f"{total_price}E", inline=False)
            embed.add_field(name="Time of Sale", value=timestamp, inline=False)
            embed.add_field(name="Seller", value=seller_address, inline=True)
            embed.add_field(name="Buyer", value=buyer_address, inline=True)  
        elif(page == 2):
            tx_hash = event["transaction"]["transaction_hash"]
            block_hash = event["transaction"]["block_hash"]
            block_number = event["transaction"]["block_number"]
            
            embed.add_field(name="Transaction Hash", value=tx_hash, inline=False)
            embed.add_field(name="Block Hash", value=block_hash, inline=False)
            embed.add_field(name="Block Number", value=block_number, inline=False)
            embed.add_field(name="Etherscan", value=f"https://etherscan.io/block/{block_number}")

        embed.set_image(url=image_url)
        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/attachments/985963144973258804/1012639908218818620/logo.png")
        embed.set_footer(text="BotShop | {}".format(datetime.utcnow().strftime('%H:%M:%S')))
        
        
        return embed

            
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
        total_supply = stats["total_supply"]

        name = json["collection"]["primary_asset_contracts"][0]["name"]

        with open("test.txt", "w+") as f:
            f.write(dumps(json, indent=4))

        embed = discord.Embed(description=json["collection"]["primary_asset_contracts"][0]["description"],
                            color=discord.Color.blue())
        if(link is None):
            embed.set_author(name=name,icon_url=img)
        else:
            embed.set_author(name=name, url=link, icon_url=img)
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

        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/attachments/985963144973258804/1012639908218818620/logo.png")
        embed.set_footer(text="BotShop | {}".format(datetime.utcnow().strftime('%H:%M:%S')))
        
        return embed


class Pagination(discord.ui.View):
    """Acts as a View to include forward and backward buttons"""

    def __init__(self, bot, next_, previous, collection, limit, page, get_json_function, get_embed_function, json):
        self.bot = bot 
        self.json_function = get_json_function
        self.embed_function = get_embed_function
        self.next = next_
        self.previous = previous
        self.collection = collection
        self.limit = limit
        self.page = page
        self.json = json
        super().__init__(timeout=None)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="⬅️")
    async def button_callback_prev(self, button, interaction):
        if(self.previous is None):
            await interaction.response.send_message("No previous page", ephemeral=False)
            return
        await interaction.response.defer()
        self.json = await self.json_function(f"https://api.opensea.io/api/v1/events?only_opensea=false&collection_slug={self.collection}&event_type=successful&limit={self.limit}&cursor={self.previous}")
        await interaction.edit_original_message(embed=await self.embed_function(self.json, self.page)) # Send a message when the button is clicked

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="ℹ️")
    async def button_callback_more_info(self, button, interaction):
        await interaction.response.defer()
        self.page = self.page + 1
        if(self.page > 2):
            self.page = 1
        await interaction.edit_original_message(embed=await self.embed_function(self.json, self.page), view=Pagination(self.bot,
            self.json["next"], self.json["previous"], self.collection, self.limit,self.page, self.json_function, self.embed_function, self.json)) # Send a message when the button is clicked


    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="➡️")
    async def button_callback_next(self, button, interaction):
        await interaction.response.defer()
        self.json = await self.json_function(f"https://api.opensea.io/api/v1/events?only_opensea=false&collection_slug={self.collection}&event_type=successful&limit={self.limit}&cursor={self.next}")
        await interaction.edit_original_message(embed=await self.embed_function(self.json, self.page), view=Pagination(self.bot,
            self.json["next"], self.json["previous"], self.collection, self.limit,self.page, self.json_function, self.embed_function, self.json)) # Send a message when the button is clicked



def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(OpenseaTracker(bot)) # add the cog to the bot