from discord.ext import commands, tasks
import re
import json
import random
from time import sleep
from win11toast import toast_async
import PyUtls as logger

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['token']

command_prefix = ';'
channelToFarmID = config['channelID']

bot = commands.Bot(command_prefix=command_prefix,
                   help_command=None)


def extract_emoji_name(emoji_string: str):
    start = emoji_string.find(':') + 1
    end = emoji_string.rfind(':')
    emoji_name = emoji_string[start:end]
    return emoji_name


def extract_poke_name(des: str):
    pattern = r'\*\*([A-Za-z]+)\*\*'

    match = re.search(pattern, des)
    try:
        x = match.group(1).lower()
    except:
        x = None
    return x


def check(m):
    return m.author.id == 664508672713424926 and m.channel.id == channelToFarmID


@tasks.loop(seconds=random.randint(
    config['delayInbetween'][0], config['delayInbetween'][1]))
async def mainLoop():
    channelToFarm = bot.get_channel(channelToFarmID)
    async for command in channelToFarm.slash_commands():
        if command.name == 'pokemon':
            response = await command.__call__(channel=channelToFarm)
            await bot.wait_for("message", check=check, timeout=15)
            if len(response.message.embeds) > 0:
                if response.message.embeds[0].title == 'A wild Captcha appeared!':
                    for i in range(10):
                        logger.warn('CAPTCHA REQ, GET BACK')
                        await toast_async('PokeMeow Alert', 'Captcha Reqired')
                        sleep(.5)
                pokemonName = extract_poke_name(
                    response.message.embeds[0].description)
                pokeType = response.message.embeds[0].footer.text.split()[
                    0].lower()
                for button in response.message.components[0].children:
                    if str(button.type) == 'ComponentType.button':
                        ballType = extract_emoji_name(
                            str(button.emoji))
                        if pokeType in config[ballType]:
                            try:
                                await button.click()
                                logger.success(
                                    f'Clicked {ballType} for a {pokemonName} - {pokeType}')
                            except:
                                logger.fail('Failed to use ball (discord)')
                                pass
                            break
                        logger.fail('Failed to use ball (no balls)')
            elif 'wait' in response.message.content:
                logger.log('Need to waiting')
            else:
                try:
                    logger.error(response.message.embeds[0].description)
                except:
                    logger.error(response.message.content)
mainLoop.change_interval(seconds=random.randint(
    config['delayInbetween'][0], config['delayInbetween'][1]))


@bot.listen()
async def on_error(event):
    logger.error(event)
    pass


@bot.event
async def on_ready():
    mainLoop.start()
    print('Started')

bot.run(TOKEN)
