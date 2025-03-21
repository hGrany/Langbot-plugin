from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from pkg.platform.types import *
from lxml import etree
import requests

# 注册插件
@register(name="LangBotPlugin", description="Plugin", version="0.1", author="Alex")
class LangBotPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        pass

    # 异步初始化
    async def initialize(self):
        pass

    # 当收到个人普通消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        if msg == "hello":  # 如果消息为hello

            # 输出调试信息
            self.ap.logger.debug("hello, {}".format(ctx.event.sender_id))

            # 回复消息 "hello, <发送者id>!"
            ctx.add_return("reply", ["hello, {}!".format(ctx.event.sender_id)])

            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()

    # 当收到个人消息时触发
    @handler(PersonMessageReceived)
    async def person_message_received(self, ctx: EventContext):
        source_platform_object = ctx.event.query.message_event.source_platform_object
        if source_platform_object["Data"]["MsgType"] == 49:
            # 输出调试信息
            self.ap.logger.debug("source_platform_object: {}".format(source_platform_object))
            for item in ctx.event.message_chain:
                if isinstance(item, Plain):
                    root = etree.XML(item.text)
                    msg_body = {
                        "title": root.xpath("//finderFeed/desc")[0].text,
                        "url": root.xpath("//finderFeed/mediaList/media/url")[0].text,
                        "id": root.xpath("//finderFeed/objectId")[0].text,
                        "nonce_id": root.xpath("//finderFeed/objectId")[0].text,
                        "nickname": root.xpath("//finderFeed/nickname")[0].text, 
                    }
                    self.ap.logger.info("[{}] transcription video message. info={}".format(ctx.event.sender_id, msg_body))

                    service_url = "https://u185166-9a3e-d53e77a0.westc.gpuhub.com:8443/api/excel/api/wechat/parser"
                    params = {
                        "video_info": item.text
                    }
                    response = requests.post(service_url, json=params)
                    if response.status_code != 200: 
                        self.ap.logger.warning("[{}] unable to transcription video to text. code={}".format(ctx.event.sender_id, response.status_code))
                    else:
                        result = response.json()
                        self.ap.logger.info("[{}] transcription succ: {}".format(ctx.event.sender_id, result))
                        await ctx.reply(MessageChain([Plain("Plain Text={}".format(result['desc']))]))

            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 GroupNormalMessageReceived 的对象
        if msg == "hello":  # 如果消息为hello

            # 输出调试信息
            self.ap.logger.debug("hello, {}".format(ctx.event.sender_id))

            # 回复消息 "hello, everyone!"
            ctx.add_return("reply", ["hello, everyone!"])

            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()

    # 插件卸载时触发
    def __del__(self):
        pass