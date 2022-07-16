#    Copyright (C) DevsExpo 2020-2021
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import asyncio
import os
import better_profanity
from pyrogram import filters
from Shikimori.modules.helper_funcs.chat_status import is_user_admin
from better_profanity import profanity
from google_trans_new import google_translator
from telethon import events
from telethon.tl.types import ChatBannedRights
from Shikimori.modules.nsfwscan import get_file_id_from_message
from Shikimori import dispatcher
from Shikimori.mongo import db
import Shikimori.modules.sql.nsfw_sql as sql
from Shikimori.pyrogramee.telethonbasics import is_admin
from Shikimori.events import register
from Shikimori import telethn as tbot, arq, pbot
from Shikimori.modules.log_channel import loggable

translator = google_translator()
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# This Module is ported from https://github.com/MissJuliaRobot/MissJuliaRobot
# This hardwork was completely done by MissJuliaRobot
# Full Credits goes to MissJuliaRobot

bot_name = f"{dispatcher.bot.first_name}"

antinsfw_chats = db.antinsfw
antislang_chats = db.antislang

CMD_STARTERS = "/"
better_profanity.profanity.load_censor_words_from_file("./Shikimori/Extras/profanity_wordlist.txt")


@register(pattern="^/antinsfw(?: |$)(.*)")
async def antinsfw(event):
    if event.fwd_from:
        return
    if not event.is_group:
        await event.reply("You Can Only antinsfw in Groups.")
        return
    event.pattern_match.group(1)
    if await is_admin(event, event.message.sender_id):
        input = event.pattern_match.group(1)
        chats = antinsfw_chats.find({})
        if not input:
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                    )
                    return
            await event.reply(
                "Please provide some input yes or no.\n\nCurrent setting is : **off**"
            )
            return
        if input == "on":
            if event.is_group:
                chats = antinsfw_chats.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        await event.reply(
                            "NSFW filter is already activated for this chat."
                        )
                        return
                antinsfw_chats.insert_one({"id": event.chat_id})
                await event.reply("NSFW filter turned on for this chat.")
        elif input == "off":
            if event.is_group:
                chats = antinsfw_chats.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        antinsfw_chats.delete_one({"id": event.chat_id})
                        await event.reply("NSFW filter turned off for this chat.")
                        return
            await event.reply("NSFW filter isn't turned on for this chat.")
        else:
            await event.reply("I only understand by on or off")
            return
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return

# @loggable
# @tbot.on(events.NewMessage(pattern=None))
# async def del_nsfw(event):
#     if event.is_private:
#         return
#     msg = str(event.text)
#     sender = await event.get_sender()
#     # let = sender.username
#     if await is_admin(event, event.message.sender_id):
#         return
#     chats = antinsfw_chats.find({})
#     for c in chats:
#         if not event.text:
#             is_nsfw = sql.is_nsfw(c["id"])
#             if not is_nsfw:
#                 return
#             if event.chat_id == c["id"]:
#                 if event.photo:
#                     file = await event.client.download_media(event.photo, "nudes.jpg")
#                     file = "./nudes.jpg"
#                     await event.respond("hmm")
#                 elif event.document:
#                     file = await event.client.download_media(event.document, "nudes.pdf")
#                     file = "./nudes.pdf"
#                 elif event.animation:
#                     file = await event.client.download_media(event.animation, "nude.gif")
#                     file = "./nudes.gif"
#                 elif event.sticker:
#                     file = await event.client.download_media(event.sticker, "nude.png")
#                     file = "./nudes.png"
#                 else:
#                     return
#                 try:
#                     results = await arq.nsfw_scan(file=file)
#                     await event.respond("hmm")
#                     if results.ok:
#                         return
#                     await event.respond(f"{results.porn}")
#                     check = f"{results.is_nsfw}"

#                     if "True" in check:
#                         await event.delete()
#                         st = sender.first_name
#                         hh = sender.id
#                         final = f"**NSFW DETECTED**\n\n[{st}](tg://user?id={hh}) your message contain NSFW content.. So, {bot_name} deleted the message\n\n **Nsfw Sender - User / Bot :** [{st}](tg://user?id={hh})  \n\n**Neutral:** `{results.neutral} %`\n**Porn:** `{results.porn} %`\n**Hentai:** `{results.hentai} %`\n**Sexy:** `{results.sexy} %`\n**Drawings:** `{results.drawings} %`\n**NSFW:** `{results.is_nsfw}` \n**#ANTI_NSFW** "
#                         dev = await event.respond(final)
#                         os.remove(file)
#                         await asyncio.sleep(10)
#                         await dev.delete()
#                         return final
#                 except Exception:
#                     return



@register(pattern="^/antislang(?: |$)(.*)")
async def antislang(event):
    if event.fwd_from:
        return
    if not event.is_group:
        await event.reply("You Can Only antislang in Groups.")
        return
    event.pattern_match.group(1)
    if await is_admin(event, event.message.sender_id):
        input = event.pattern_match.group(1)
        chats = antislang_chats.find({})
        if not input:
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                    )
                    return
            await event.reply(
                "Please provide some input yes or no.\n\nCurrent setting is : **off**"
            )
            return
        if input == "on":
            if event.is_group:
                chats = antislang_chats.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        await event.reply(
                            "Profanity filter is already activated for this chat."
                        )
                        return
                antislang_chats.insert_one({"id": event.chat_id})
                await event.reply("Profanity filter turned on for this chat.")
        elif input == "off":
            if event.is_group:
                chats = antislang_chats.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        antislang_chats.delete_one({"id": event.chat_id})
                        await event.reply("Profanity filter turned off for this chat.")
                        return
            await event.reply("Profanity filter isn't turned on for this chat.")
        else:
            await event.reply("I only understand by on or off")
            return
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return

@loggable
@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    # let = sender.username
    if await is_admin(event, event.message.sender_id):
        return
    chats = antislang_chats.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c["id"]:
                if better_profanity.profanity.contains_profanity(msg):
                    await event.delete()
                    if sender.username is None:
                        st = sender.first_name
                        hh = sender.id
                        final = f"[{st}](tg://user?id={hh}) used word: **{msg}** which is detected as a slang word and his message has been deleted."
                    else:
                        final = f"[{st}](tg://user?id={hh}) used word: **{msg}** which is detected as a slang word and his message has been deleted."
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
                    return dev

@loggable
@pbot.on_message(
    filters.all
    & filters.group
)
async def del_nsfw(_, message):
    await message.reply_text("hmm")
    try:
        sender = message.from_user
    except:
        sender = message.sender_chat
    # if is_user_admin(message, sender.id):
    #     return

    if (
        not message.document
        and not message.photo
        and not message.sticker
        and not message.animation
        and not message.video
    ):
        return
    await message.reply_text("hmm")
    chat_id = message.chat.id
    chats = antinsfw_chats.find({})
    for c in chats:
        await message.reply_text("hmm")
        is_nsfw = sql.is_nsfw(chat_id)
        # if not is_nsfw:
        #     await message.reply_text("huhmm")
        #     return
        file_id = await get_file_id_from_message(message)
        await message.reply_text("hmm")
        try:
            if not file_id:
                return await m.edit("Something wrong happened.")
            file = await pbot.download_media(file_id)
            results = await arq.nsfw_scan(file=file)
            await message.reply_text("hmm")
            # if results.ok:
            #     await message.reply_text("ygfyuhmm")
            #     return
            results = results.result
            check = f"{results.is_nsfw}"
            if "True" in check:
                await message.reply_text("hmm")
                await message.delete()
                st = sender.first_name
                hh = sender.id
                final = f"**NSFW DETECTED**\n\n[{st}](tg://user?id={hh}) your message contain NSFW content.. So, {bot_name} deleted the message\n\n **Nsfw Sender - User / Bot :** [{st}](tg://user?id={hh})  \n\n**Neutral:** `{results.neutral} %`\n**Porn:** `{results.porn} %`\n**Hentai:** `{results.hentai} %`\n**Sexy:** `{results.sexy} %`\n**Drawings:** `{results.drawings} %`\n**NSFW:** `{results.is_nsfw}` \n**#ANTI_NSFW** "
                dev = await message.reply_text(final)
                os.remove(message)
                await asyncio.sleep(10)
                await dev.delete()
                return final
        except Exception:
            await message.reply_text("hmmjgiug76677")
            return