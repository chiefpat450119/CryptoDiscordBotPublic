import hikari
import lightbulb
import json
from pycoingecko import CoinGeckoAPI
import locale
from datetime import datetime, timedelta, timezone

bot = lightbulb.BotApp(prefix="&p", token="************",
                       intents=hikari.Intents.ALL_UNPRIVILEGED)


@bot.listen(hikari.ShardReadyEvent)
async def ready_listener(_):
	print("Bot is ready")


local_timezone = timezone(timedelta(hours=8))
locale.setlocale(locale.LC_ALL, 'en_US.utf8')


def coin_converter(name):
	return "-".join(name.split(" "))


# Crypto price checker by ticker
@bot.command()
@lightbulb.option("type", "Whether you are checking by name or by ticker", str, required=False, default="ticker")
@lightbulb.option("coin", "The coin or token for which you want to check price", str, required=True)
@lightbulb.command("price", "Checks the price of a cryptocurrency", aliases=["$", "pc"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def price(ctx: lightbulb.Context):
	cg = CoinGeckoAPI()
	currency = "usd"
	coin = None

	if ctx.options.type == "ticker":
		with open("ticker_to_id.json", "r") as jsonfile:
			coin_dict = json.load(jsonfile)
			coin = coin_dict[ctx.options.coin.lower()]
	elif ctx.options.type == "n":
		coin = coin_converter(ctx.options.coin.lower())

	info_dict = cg.get_price(ids=coin, vs_currencies=currency, include_market_cap='true', include_24hr_change='true',
	                         include_last_updated_at='true')[coin]
	current_price = info_dict[currency]

	mkt_cap = info_dict[f'{currency}_market_cap']
	readable_m_cap = locale.format_string("%d", int(round(mkt_cap, 0)), grouping=True)

	change = info_dict[f'{currency}_24h_change']

	ts = float(info_dict['last_updated_at'])
	local_time = datetime.fromtimestamp(ts, local_timezone)
	update_time = local_time.strftime("%Y-%m-%d %H:%M:%S (%Z)")

	await ctx.respond(
		f'The current price of **{ctx.options.coin.upper()}** is **{round(current_price, 2)}** {currency.upper()} with a market cap of {readable_m_cap} {currency.upper()}.')
	await ctx.respond(f'The price has changed by **{round(change, 2)}%** in the past 24 hours.')
	await ctx.respond(f'Last updated {update_time}.')


def set_img(embed, days=0):
	diff = timedelta(days=days)
	date = datetime.now() - diff
	reformatted = f"{date.strftime('%Y')}-{int(date.strftime('%m'))}-{int(date.strftime('%d'))}"
	embed.set_image(f"https://alternative.me/images/fng/crypto-fear-and-greed-index-{reformatted}.png")
	embed.set_footer(date.strftime("%A, %d %B %Y"))


# Crypto fear and greed index
@bot.command()
@lightbulb.option("date", "Date for which you want to see the index", str, default="today", required=False,
                  modifier=lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.command("index", "Shows the fear and greed index", aliases=["ind", "idx"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def index(ctx: lightbulb.Context):
	embed = hikari.Embed()
	if ctx.options.date.lower() == "today":
		set_img(embed, 0)
	elif ctx.options.date.lower() == "yesterday":
		set_img(embed, 1)
	elif ctx.options.date.lower() == "last week":
		set_img(embed, 7)
	elif ctx.options.date.lower() == "last month":
		set_img(embed, 30)
	else:
		date = datetime.strptime(ctx.options.date, "%d/%m/%y")
		reformatted = f"{date.strftime('%Y')}-{int(date.strftime('%m'))}-{int(date.strftime('%d'))}"
		embed.set_image(f"https://alternative.me/images/fng/crypto-fear-and-greed-index-{reformatted}.png")
		embed.set_footer(date.strftime("%A, %d %B %Y"))
	await ctx.respond(embed)


bot.run()
