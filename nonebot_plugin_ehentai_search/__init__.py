from nonebot import (
    get_driver,
    on_command, 
    on_regex, 
    get_plugin_config, 
    logger,
)
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata 
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg,ArgPlainText,RegexGroup

from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    MessageSegment
)

import httpx

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from re import I
from typing import Tuple

from .metadata import metadata
from .config import Config


__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ehentai-search",
    description="致力于ehentai网站的搜索",
    usage="输入ehbz_help获取帮助",
    type="application",
    homepage="https://github.com/N791/nonebot-plugin-ehentai-search",
    supported_adapters={"~onebot.v11"}
)

driver = get_driver()
config = get_plugin_config(Config)

@driver.on_startup
async def startup():
    global p,browser,context
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )

f_cat_value = config.FCATS['NULL']
f_cat_key = config.NEW_FCATS[0]
success_type = True
limit_num = 5

ehbz_help = on_command("ehbz_help",block=True,priority=10)
ehbz_search = on_command("ehbz_search",block=True,priority=20)
ehbz_regex = on_regex(config.search_regex,block=True,priority=30,flags=I)
ehbz_num = on_command("ehbz_num",block=True,priority=10,permission=SUPERUSER)
ehbz_select = on_command("ehbz_select",block=True,priority=10,permission=SUPERUSER)
ehbz_status = on_command("ehbz_status",block=True,priority=10)

@ehbz_help.handle()
async def get_help():
    help_str = ("ehentai搜索器帮助:\n"
               +"1.ehbz+(数字)+关键词  指定类型(数字)和关键词进行搜索任务\n"
               +"2.ehbz_search+关键词  在ehentai中搜索关键词内容(使用全局搜索类型)\n"
               +"3.ehbz_status  获取当前设置的状态\n"
               +"4.ehbz_num  (管理员)设置每次搜索返回的条数(默认5条, 最高12条)\n"
               +"5.ehbz_select  (管理员)设置全局搜索类型(默认NULL类型)\n"
               +"注:搜索方式参考 https://ehwiki.org/wiki/Gallery_Searching/Chinese 中的内容")
    await ehbz_help.finish(help_str)

@ehbz_num.handle()
async def get_limit_num(num_matcher: Matcher, num_args: Message = CommandArg()):
    if num_args.extract_plain_text():
        num_matcher.set_arg("got_num", num_args)
    else:
        await ehbz_num.finish("输入为空，请重新输入")
        
@ehbz_num.got("got_num",prompt="请输入数字")
async def set_limit_num(got_num: str = ArgPlainText()):
    get_num = int(got_num)
    global limit_num
    if get_num > 12:
        get_num = 12
    limit_num = get_num
    await ehbz_num.finish(f"设置成功，当前限制搜索条数最多展示{limit_num}条")
    
@ehbz_select.handle()
async def send_select():
    global f_cat_key
    send_str = (f"当前类型设置为{f_cat_key},当前支持的类型:\n"
               +"0.NULL\n"
               +"1.Doujinshi\n"
               +"2.Manga\n"
               +"3.Artist-CG\n"
               +"4.Game-CG\n"
               +"5.Western\n"
               +"6.Non-H\n"
               +"7.Image-Set\n"
               +"8.Cosplay\n"
               +"9.Asian-Porn\n"
               +"10.Misc"
    )
    await ehbz_select.send(send_str)

@ehbz_select.got("keymod",prompt="请输入数字以切换类型")
async def set_mod(keymod: str = ArgPlainText()):
    global f_cat_value,f_cat_key
    setmod = int(keymod)
    if(setmod<0|setmod>10):
         await ehbz_select.finish("输入错误，请重新设置")
    f_cat_value = config.FCATS_LIST[setmod]
    f_cat_key = config.NEW_FCATS[f_cat_value]
    await ehbz_select.finish(f"设置成功，当前搜索类型为{f_cat_key}")
    
@ehbz_status.handle()
async def get_ehbz_status():
    global f_cat_key,limit_num
    status_str = (f"当前类型设置为{f_cat_key},每次搜索返回的结果数量为{limit_num},当前支持的类型:\n"
               +"0.NULL\n"
               +"1.Doujinshi\n"
               +"2.Manga\n"
               +"3.Artist-CG\n"
               +"4.Game-CG\n"
               +"5.Western\n"
               +"6.Non-H\n"
               +"7.Image-Set\n"
               +"8.Cosplay\n"
               +"9.Asian-Porn\n"
               +"10.Misc"
    )
    await ehbz_status.finish(status_str)
    
@ehbz_regex.handle()
async def search_key(bot: Bot, matcher: Matcher, event: GroupMessageEvent,args: Tuple = RegexGroup()):
    global success_type
    num = args[1]
    key = args[2]
    if success_type == False:
        await ehbz_regex.finish("当前已有搜索任务，请等待当前任务完成后重试")
    else:
        await ehbz_regex.send("启动搜索任务成功")
    success_type = False
    if key == None:
        await ehbz_regex.finish("关键词为空，请重新输入")
    
    resp_key = key.strip().replace("\n","").replace("\r","")
    
    if num == None:
        resp_str = f"https://e-hentai.org/?f_search={resp_key}"
    else:
        keymod = int(num)
        if(keymod < 0 | keymod > 10):
            await ehbz_select.finish("类型输入错误，请重新设置")
        cat_value = config.FCATS_LIST[keymod]
        resp_str = f"https://e-hentai.org/?f_cats={cat_value}&f_search={resp_key}"
    await search(bot,matcher,event,resp_str) #执行搜索任务
    success_type = True
        
    
    
@ehbz_search.handle()
async def get_keyword(keyword_matcher: Matcher,keyword_args:Message = CommandArg()):
    if keyword_args.extract_plain_text():
        keyword_matcher.set_arg("keyword",keyword_args)
    else:
        await ehbz_search.finish("输入为空，请重新输入")
        
@ehbz_search.got("keyword","请输入关键词")
async def search_keyword(bot: Bot, matcher: Matcher, event: GroupMessageEvent, keyword: str = ArgPlainText()):
    global success_type,f_cat_value
    if success_type == False:
        await ehbz_search.finish("当前已有搜索任务，请等待当前任务完成后重试")
    else:
        await ehbz_search.send("启动搜索任务成功")
    success_type = False
    resp_key = keyword.strip().replace("\n","").replace("\r","")
    if f_cat_value == 0:
        resp_str = f"https://e-hentai.org/?f_search={resp_key}"
    else:
        resp_str = f"https://e-hentai.org/?f_cats={f_cat_value}&f_search={resp_key}"
    await search(bot,matcher,event,resp_str)
    success_type = True
    await ehbz_search.finish()
    
async def search(bot, matcher, event, resp_str) -> None:
    global success_type
    # 获取页面源代码并处理
    try:
        page = await context.new_page()
        await page.goto(resp_str)
    except Exception as e:
        success_type = True
        await matcher.finish(
            message=f"搜索网站请求失败，错误信息{repr(e)}"
        )
    resp = await page.content()
    resp_obj = BeautifulSoup(resp,"html.parser")
    metadata_str = metadata.get_metadata(resp_obj,limit_num)
    logger.info("已获取到metadata")
    msgs = []
    i = 0
    async with httpx.AsyncClient() as client:
        for meta_item in metadata_str:
            i = i + 1
            logger.info(f"已获取到结果{i}")
            url_str = f"https://e-hentai.org/gallerytorrents.php?gid={meta_item['gid']}&t={meta_item['token']}"
            try:
                await page.goto(url_str)   
            except Exception as e:
                success_type = True
                await matcher.finish(
                    message=f"下载网站请求失败，错误信息{repr(e)}"
                )
            meta_item_url = await page.content()
            meta_link = BeautifulSoup(meta_item_url, "html.parser")
            torrent_links = [link["href"] for link in meta_link.find_all("a", href=lambda href: href and href.endswith(".torrent"))]
            re = await client.get(meta_item['thumb'], timeout=120) #获取图片
            result_str = (f"标题:{meta_item['title']}\n"
                +f"类型:{meta_item['category']}\n"
                +f"页数:{meta_item['filecount']}\n"
                +f"标签:{', '.join(str(item) for item in meta_item['tags'])}\n"
                +f"eh链接:https://e-hentai.org/g/{meta_item['gid']}/{meta_item['token']}/\n"
                +f"磁力文件:(没显示出来则没有)\n"+'\n'.join(str(link_item) for link_item in torrent_links))
            try:
                image = Image.open(BytesIO(re.content))  # 打开图片
                res_img = metadata.change_pixel(image,100)  # 修改图片以防风控
                result = Message(result_str) + MessageSegment.image(res_img)
            except Exception as e:
                result = Message(result_str)
        
            msg = {
                "type": "node",
                "data": {
                    "name": "search_bot",
                    "uin": bot.self_id,
                    "content": result,
                    },
                }
            msgs.append(msg)
    
        try:
            await bot.call_api(
                            "send_group_forward_msg",
                            group_id=event.group_id,
                            messages=msgs,
                        )
        except Exception as e:
            success_type = True
            await matcher.finish(
                message=f"消息可能被风控了，发不出来，错误信息{repr(e)}"
            )
            
