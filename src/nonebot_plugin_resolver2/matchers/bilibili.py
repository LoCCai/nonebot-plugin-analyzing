import asyncio
from pathlib import Path
import re

from nonebot import logger, on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.params import CommandArg

from ..config import DURATION_MAXIMUM, NEED_UPLOAD, NICKNAME, plugin_cache_dir
from ..download import (
    download_file_by_stream,
    download_img,
    download_imgs_without_raise,
    download_video,
    encode_video_to_h264,
    merge_av,
)
from ..download.utils import keep_zh_en_num
from ..exception import ParseException, handle_exception
from ..parsers import BilibiliParser, get_redirect_url
from .filter import is_not_in_disabled_groups
from .helper import get_file_seg, get_img_seg, get_record_seg, get_video_seg, send_segments
from .preprocess import ExtractText, Keyword, r_keywords

bilibili = on_message(
    rule=is_not_in_disabled_groups & r_keywords("bilibili", "bili2233", "b23", "BV", "av"),
    priority=5,
)

bili_music = on_command(cmd="bm", block=True)

PATTERNS: dict[str, re.Pattern] = {
    "BV": re.compile(r"(BV[1-9a-zA-Z]{10})(?:\s)?(\d{1,3})?"),
    "av": re.compile(r"av(\d{6,})(?:\s)?(\d{1,3})?"),
    "/BV": re.compile(r"/(BV[1-9a-zA-Z]{10})()"),
    "/av": re.compile(r"/av(\d{6,})()"),
    "b23": re.compile(r"https?://b23\.tv/[A-Za-z\d\._?%&+\-=/#]+()()"),
    "bili2233": re.compile(r"https?://bili2233\.cn/[A-Za-z\d\._?%&+\-=/#]+()()"),
    "bilibili": re.compile(r"https?://(?:space|www|live|m|t)?\.?bilibili\.com/[A-Za-z\d\._?%&+\-=/#]+()()"),
}

parser = BilibiliParser()


@bilibili.handle()
@handle_exception()
async def _(text: str = ExtractText(), keyword: str = Keyword()):
    pub_prefix = f"{NICKNAME}解析 | 哔哩哔哩 - "
    matched = PATTERNS[keyword].search(text)
    if not matched:
        logger.info(f"{text} 中的链接或 BV/av 号无效, 忽略")
        return
    url, video_id, page_num = str(matched.group(0)), str(matched.group(1)), matched.group(2)
    # 是否附加链接
    need_join_link = keyword != "bilibili"
    # 短链重定向地址
    if keyword in ("b23", "bili2233"):
        b23url = url
        url = await get_redirect_url(url, parser.headers)
        if url == b23url:
            logger.info(f"链接 {url} 无效，忽略")
            return

    # 链接中是否包含BV，av号
    if id_type := next((i for i in ("/BV", "/av") if i in url), None):
        if matched := PATTERNS[id_type].search(url):
            keyword = id_type
            video_id = str(matched.group(1))
    # 预发送消息列表
    segs: list[Message | MessageSegment | str] = []
    # 如果不是视频
    if not video_id:
        # 动态
        if "t.bilibili.com" in url or "/opus" in url:
            matched = re.search(r"/(\d+)", url)
            if not matched:
                logger.info(f"链接 {url} 无效 - 没有获取到动态 id, 忽略")
                return
            opus_id = int(matched.group(1))
            img_lst, text = await parser.parse_opus(opus_id)
            await bilibili.send(f"{pub_prefix}动态")
            segs = [text]
            if img_lst:
                paths = await download_imgs_without_raise(img_lst)
                segs.extend(get_img_seg(path) for path in paths)
            await send_segments(segs)
            await bilibili.finish()
        # 直播间解析
        elif "/live" in url:
            # https://live.bilibili.com/30528999?hotRank=0
            matched = re.search(r"/(\d+)", url)
            if not matched:
                logger.info(f"链接 {url} 无效 - 没有获取到直播间 id, 忽略")
                return
            room_id = int(matched.group(1))
            title, cover, keyframe = await parser.parse_live(room_id)
            if not title:
                await bilibili.finish(f"{pub_prefix}直播 - 未找到直播间信息")
            res = f"{pub_prefix}直播 {title}"
            res += get_img_seg(await download_img(cover)) if cover else ""
            res += get_img_seg(await download_img(keyframe)) if keyframe else ""
            await bilibili.finish(res)
        # 专栏解析
        elif "/read" in url:
            matched = re.search(r"read/cv(\d+)", url)
            if not matched:
                logger.info(f"链接 {url} 无效 - 没有获取到专栏 id, 忽略")
                return
            read_id = int(matched.group(1))
            texts, urls = await parser.parse_read(read_id)
            await bilibili.send(f"{pub_prefix}专栏")
            # 并发下载
            paths = await download_imgs_without_raise(urls)
            # 反转路径列表，pop 时，则为原始顺序，提高性能
            paths.reverse()
            segs = []
            for text in texts:
                if text:
                    segs.append(text)
                else:
                    segs.append(get_img_seg(paths.pop()))
            if segs:
                await send_segments(segs)
                await bilibili.finish()
        # 收藏夹解析
        elif "/favlist" in url:
            # https://space.bilibili.com/22990202/favlist?fid=2344812202
            matched = re.search(r"favlist\?fid=(\d+)", url)
            if not matched:
                logger.info(f"链接 {url} 无效 - 没有获取到收藏夹 id, 忽略")
                return
            fav_id = int(matched.group(1))
            # 获取收藏夹内容，并下载封面
            texts, urls = await parser.parse_favlist(fav_id)
            await bilibili.send(f"{pub_prefix}收藏夹\n正在为你找出相关链接请稍等...")
            paths: list[Path] = await download_imgs_without_raise(urls)
            segs = []
            # 组合 text 和 image
            for path, text in zip(paths, texts):
                segs.append(get_img_seg(path) + text)
            await send_segments(segs)
            await bilibili.finish()
        else:
            logger.info(f"不支持的链接: {url}")
            await bilibili.finish()

    join_link = ""
    if need_join_link:
        url_id = f"av{video_id}" if keyword in ("av", "/av") else video_id
        join_link = f" https://www.bilibili.com/video/{url_id}"
    await bilibili.send(f"{pub_prefix}视频{join_link}")
    # 获取分集数
    page_num = int(page_num) if page_num else 1
    if url and (matched := re.search(r"(?:&|\?)p=(\d{1,3})", url)):
        page_num = int(matched.group(1))
    # 视频
    id_arg = {}
    if keyword in ("av", "/av"):
        id_arg["avid"] = int(video_id)
    else:
        id_arg["bvid"] = video_id
    video_info = await parser.parse_video_info(**id_arg, page_num=page_num)

    segs = [
        video_info.title,
        get_img_seg(await download_img(video_info.cover_url)),
        video_info.display_info,
        video_info.ai_summary,
    ]
    if video_info.video_duration > DURATION_MAXIMUM:
        segs.append(
            f"⚠️ 当前视频时长 {video_info.video_duration // 60} 分钟, "
            f"超过管理员设置的最长时间 {DURATION_MAXIMUM // 60} 分钟!"
        )
    await send_segments(segs)

    if video_info.video_duration > DURATION_MAXIMUM:
        logger.info(f"video duration > {DURATION_MAXIMUM}, ignore download")
        return
    # 下载视频和音频
    file_name = f"{video_id}-{page_num}"
    video_path = plugin_cache_dir / f"{file_name}.mp4"

    if not video_path.exists():
        # 下载视频和音频
        if video_info.audio_url:
            v_path, a_path = await asyncio.gather(
                download_file_by_stream(
                    video_info.video_url, file_name=f"{file_name}-video.m4s", ext_headers=parser.headers
                ),
                download_file_by_stream(
                    video_info.audio_url, file_name=f"{file_name}-audio.m4s", ext_headers=parser.headers
                ),
            )
            await merge_av(v_path=v_path, a_path=a_path, output_path=video_path)
        else:
            video_path = await download_video(
                video_info.video_url, video_name=f"{file_name}.mp4", ext_headers=parser.headers
            )

    # 发送视频
    try:
        await bilibili.send(get_video_seg(video_path))
    except ActionFailed as e:
        message: str = e.info.get("message", "")
        # 无缩略图
        if not message.endswith(".png'"):
            raise
        # 重新编码为 h264
        logger.warning("视频上传出现无缩略图错误，将重新编码为 h264 进行上传")
        h264_video_path = await encode_video_to_h264(video_path)
        await bilibili.send(get_video_seg(h264_video_path))


@bili_music.handle()
@handle_exception()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    text = args.extract_plain_text().strip()
    matched = re.match(r"^(BV[1-9a-zA-Z]{10})(?:\s)?(\d{1,3})?$", text)
    if not matched:
        await bili_music.finish("命令格式: bm BV1LpD3YsETa [集数](中括号表示可选)")

    # 回应用户
    await bot.call_api("set_msg_emoji_like", message_id=event.message_id, emoji_id="282")
    bvid, p_num = str(matched.group(1)), matched.group(2)

    # 处理分 p
    p_num = int(p_num) if p_num else 1
    video_info = await parser.parse_video_info(bvid=bvid, page_num=p_num)
    if not video_info.audio_url:
        raise ParseException("没有可供下载的音频流")
    # 音频文件名
    video_title = keep_zh_en_num(video_info.title)
    audio_name = f"{video_title}.mp3"
    audio_path = plugin_cache_dir / audio_name
    # 下载
    if not audio_path.exists():
        await download_file_by_stream(video_info.audio_url, file_name=audio_name, ext_headers=parser.headers)

    # 发送音频
    await bili_music.send(get_record_seg(audio_path))
    # 上传音频
    if NEED_UPLOAD:
        await bili_music.send(get_file_seg(audio_path))
