from datetime import datetime
import random
import sys
import os

from table2ascii import table2ascii, Alignment
from discord.ext.commands import bot
import discord

from misc import configs, utils

CONFIG     = configs.CONFIG
LOGGER     = configs.LOGGER
TOKEN      = CONFIG.bot_token

NOW        = datetime.now()
Y, M, D    = NOW.year, NOW.month, NOW.day

DB     = utils.SalesDB(db_name = 'DoveNest')


today      = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

intents = discord.Intents.default()
bot     = bot.Bot(command_prefix='!', intents = intents)


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)


## 봇 기동 후 준비가 완료되었을 때 실행되는 함수
@bot.event
async def on_ready(): 

    try:
        LOGGER.info(f'[INFO] logged in as {bot.user}')

    except Exception as e:
        LOGGER.error(f'[ERR.Dc.002] 봇에 연결하지 못했습니다. {e}')


## 전서구한테 인사하는 함수
@bot.command(name = '안녕', aliases = ['hello', 'hi'])
async def hello(ctx):
    try: await ctx.reply('안녕하세요, 저는 전서구입니다.')
    except Exception as e:

        LOGGER.error(f'[ERR.Dc.001] 메시지를 전송하지 못했습니다. {e}')
        await ctx.reply('잠시 후 다시 이용바랍니다. ')


## MySQL 서버에 저장되어 있는 할인 정보를 쿼리를 통해서 불러온 후 보내주는 함수
## !할인, !세일, !discount, !sale 등으로 사용가능
## e.g.) !할인 steam 1 5 percent -> steam 할인 정보 중 0 ~ 5번째까지 percent를 기준으로 정렬해서 보여줌.
@bot.command(name = '할인', aliases = ['세일', 'discount', 'sale'], help = '!할인 [platform | (steam, nintendo)] [page] [n_contents] [query | (idx, percent, name)]')
async def discount(ctx, platform = 'steam', page = 1, n_contents = 5, query = None):

    sorting_ = query if query != None else 'idx'
    desc     = True  if sorting_ in ['percent', 'name'] else False

    ## MySQL 서버에서 쿼리에 맞게 데이터를 불러오는 부분
    ## 자세한 코드는 misc/utils.py 코드에 있음.
    db_datas = DB.search_table(table_name  = 'discount_info', how_many = n_contents * page, platform = platform, 
                               conditions  = ['date', today], desc = desc, sorting_col = sorting_)

    ## page 인자값의 클 수록 조회해야하는 데이터 수가 많아서 시간이 오래걸림,, -> 개선 필요함.
    db_datas = db_datas[n_contents*(page - 1) : n_contents*page]

    try:

        header = ['#', 'id', 'title', 'original', 'discounted', 'percent']
        body   = [[data[0], data[1], data[2], data[4], data[5].strip(), f'-{data[3]}%']
                  for data in db_datas]

        ## 리스트를 ascii 형식의 표로 만들어주는 부분
        output = table2ascii(header            = header, 
                             body              = body,
                             alignments        = Alignment.LEFT,
                             first_col_heading = True)

        ## 메시지 전송
        await ctx.reply(output)
    
    except Exception as e:

        LOGGER.error(f'[ERR.Dc.001] 메시지를 전송하지 못했습니다. {e}')
        await ctx.reply('잠시 후 다시 이용바랍니다.')


@bot.command(name = '출시 정보', aliases = ['출시', '발매', 'release', 'launch'])
async def release(ctx, platform = 'steam', page = 1, n_contents = 5):

    db_datas = DB.search_table(table_name = 'release_info', how_many = n_contents * page, 
                                platform = platform, conditions = ['date', today], sorting_col = 'idx')

    db_datas = db_datas[n_contents * (page - 1) : n_contents * page]

    try:
        header = ['#', 'title', 'rel_date', 'developer', 'platform']
        body   = [data[:5] for data in db_datas]

        output = table2ascii(header            = header,
                             body              = body,    
                             alignmnets        = Alignment.LEFT,
                             first_col_heading = True)

        await ctx.reply(output)

    except Exception as e:
        LOGGER.error(f'[ERR.Dc.001] 메시지를 전송하지 못했습니다. {e}')
        await ctx.reply('잠시 후 다시 이용바랍니다.')


## 프로그램 재시작 함수
## Django처럼 코드를 수정하면 reloading이 되지않아 명령어를 입력하면
## 프로그램을 재시작하도록 구성
@bot.command(name = '재시작', aliases = ['restart'])
async def restart(ctx):
    try:
        await ctx.send('Restarting bot...')
        restart_bot()

    except Exception as e:
        LOGGER.error(f'[ERR.Dc.001] 메시지를 전송하지 못했습니다. {e}')
        await ctx.reply('잠시 후 다시 이용바랍니다. ')

bot.run(TOKEN)