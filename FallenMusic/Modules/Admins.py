import os
import random
import asyncio

from pyrogram import filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, KeyboardButton, Message)
from config import get_queue
from asyncio import QueueEmpty
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream, InputStream

from FallenMusic import BOT_NAME, app, db_mem
from FallenMusic.Cache.admins import AdminRightsCheck
from FallenMusic.Cache.checker import checker, checkerCB
from FallenMusic.Helpers.Ytinfo import get_yt_info_id
from FallenMusic.Helpers.Thumbnails import thumb_init
from FallenMusic.Helpers.Changers import time_to_seconds
from FallenMusic.Helpers.PyTgCalls import Queues, Fallen
from FallenMusic.Helpers.PyTgCalls.Converter import convert
from FallenMusic.Helpers.PyTgCalls.Downloader import download
from FallenMusic.Helpers.Inline import primary_markup, close_key, audio_markup
from FallenMusic.Helpers.Database import (is_active_chat, is_music_playing, music_off,
                            music_on, remove_active_chat)


loop = asyncio.get_event_loop()


__MODULE__ = "Aᴅᴍɪɴs"


@app.on_message(
    filters.command(["dur", "gec", "atla", "devam", "son", "bitir"])
    & filters.group
)
@AdminRightsCheck
@checker
async def admins(_, message: Message):
    global get_queue
    if not len(message.command) == 1:
        return await message.reply_text("**Üzgünüm Anlamadım !**")
    if not await is_active_chat(message.chat.id):
        return await message.reply_text("**» Bir şeyin Oynatıldığı Konusunda Eminmisin ?**")
    chat_id = message.chat.id
    if message.command[0][1] == "a":
        if not await is_music_playing(message.chat.id):
            return await message.reply_text("**» Akış Zaaten Duraklatıldı.**")
        await music_off(chat_id)
        await Fallen.pytgcalls.pause_stream(chat_id)
        await message.reply_text(
            f"➻ **Akış Duraklatıldı** ☁️\n│ \n└ʙʏ : {message.from_user.first_name} 🥀",
            reply_markup=audio_markup,
        )
    if message.command[0][1] == "e":
        if await is_music_playing(message.chat.id):
            return await message.reply_text("**» Bir şeyin Oynatıldığı Konusunda Eminmisin ?**")
        await music_on(chat_id)
        await Fallen.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text(
            f"➻ **Yayın Devam Ediyor** ✨\n│ \n└ʙʏ : {message.from_user.first_name} 🥀",
            reply_markup=audio_markup,
        )
    if message.command[0][1] == "t" or message.command[0][1] == "n":
        try:
            Queues.clear(message.chat.id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await Fallen.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text(
            f"➻ **Yayın Sonlandırıldı** ❄\n│ \n└ʙʏ : {message.from_user.first_name} 🥀",
            reply_markup=close_key,
        )
    if message.command[0][1] == "k" or message.command[0][2] == "x":
        Queues.task_done(chat_id)
        if Queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await message.reply_text(
                f"➻ **Yayın atladı** 🥺\n│ \n└ʙʏ : {message.from_user.first_name} 🥀\n\n» Artık Sıraya Alınmıs Bir Parça Yok {message.chat.title}, **Sesli Sohbetten Ayrılıyor.**",
                reply_markup=close_key,
            )
            await Fallen.pytgcalls.leave_group_call(message.chat.id)
            return
        else:
            videoid = Queues.get(chat_id)["file"]
            got_queue = get_queue.get(chat_id)
            if got_queue:
                got_queue.pop(0)
            finxx = f"{videoid[0]}{videoid[1]}{videoid[2]}"
            aud = 0
            if str(finxx) != "raw":
                mystic = await message.reply_text(
                    f"**» Çalma Listesinden Bir Sonraki İndirme..**"
                )
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                await mystic.edit(
                    f"**» {BOT_NAME} İndiren**\n\n**Başlık :** {title}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                await Fallen.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            raw_path,
                        ),
                    ),
                )
                chat_title = message.chat.title
                thumb = await thumb_init(videoid)
                buttons = primary_markup(
                    videoid, message.from_user.id
                )
                await mystic.delete()
                mention = db_mem[videoid]["username"]
                final_output = await message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"<b>➻ Yayın Başladı</b>\n\n<b>✨ Başlık :</b> [{title[:40]}](https://www.youtube.com/watch?v={videoid})\n☁ <b>Süre :</b> {duration_min} Dakika\n🥀 <b>Talep Eden :</b> {mention}"
                    ),
                )
                os.remove(thumb)
            else:
                await Fallen.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            videoid,
                        ),
                    ),
                )
                afk = videoid
                title = db_mem[videoid]["title"]
                duration_min = db_mem[videoid]["duration"]
                duration_sec = int(time_to_seconds(duration_min))
                mention = db_mem[videoid]["username"]
                videoid = db_mem[videoid]["videoid"]
                if str(videoid) == "smex1":
                    buttons = buttons = primary_markup(
                        videoid,
                        message.from_user.id,
                    )
                    thumb = "FallenMusic/Utilities/Audio.jpeg"
                    aud = 1
                else:
                    _path_ = _path_ = (
                        (str(afk))
                        .replace("_", "", 1)
                        .replace("/", "", 1)
                        .replace(".", "", 1)
                    )
                    thumb = f"FallenMusic/Cache/{_path_}.png"
                    buttons = primary_markup(
                        videoid,
                        message.from_user.id,
                    )
                final_output = await message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"<b>➻ Yayın Başladı</b>\n\n<b>✨ Başlık :</b> {title[:40]}\n☁ <b>Süre :</b> {duration_min} Dakika\n🥀 <b>Talep Eden :</b> {mention}",
                )
