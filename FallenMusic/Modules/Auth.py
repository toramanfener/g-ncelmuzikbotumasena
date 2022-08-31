from pyrogram import Client, filters
from pyrogram.types import Message

from FallenMusic import app
from FallenMusic.Cache.admins import AdminActual
from FallenMusic.Helpers.Changers import int_to_alpha
from FallenMusic.Helpers.Database import (_get_authusers, delete_authuser, get_authuser,
                            get_authuser_count, get_authuser_names,
                            save_authuser)


__MODULE__ = "Aᴜᴛʜ"


@app.on_message(filters.command("auth") & filters.group)
@AdminActual
async def auth(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**» bir kullanıcının mesajını yanıtlama veya kullanıcı adı / kullanıcı kimliği ver.**"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        user_id = message.from_user.id
        token = await int_to_alpha(user.id)
        from_user_name = message.from_user.first_name
        from_user_id = message.from_user.id
        _check = await get_authuser_names(message.chat.id)
        count = 0
        for smex in _check:
            count += 1
        if int(count) == 15:
            return await message.reply_text(
                "**» Sadece 15 Kullanıcı Ekliyebilirsiniz.**"
            )
        if token not in _check:
            assis = {
                "auth_user_id": user.id,
                "auth_name": user.first_name,
                "admin_id": from_user_id,
                "admin_name": from_user_name,
            }
            await save_authuser(message.chat.id, token, assis)
            await message.reply_text(
                f"**» Başarıyla.Eklendi {user.first_name} grubun yetkili kullanıcı listesine.**"
            )
            return
        else:
            await message.reply_text(f"**» {user.first_name} zaten yetkili kullanıcılar listesinde.**")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.first_name
    token = await int_to_alpha(user_id)
    from_user_name = message.from_user.first_name
    _check = await get_authuser_names(message.chat.id)
    count = 0
    for smex in _check:
        count += 1
    if int(count) == 15:
        return await message.reply_text(
            "**» Sadece 15 Kullanıcı Ekliyebilirsiniz.**"
        )
    if token not in _check:
        assis = {
            "auth_user_id": user_id,
            "auth_name": user_name,
            "admin_id": from_user_id,
            "admin_name": from_user_name,
        }
        await save_authuser(message.chat.id, token, assis)
        await message.reply_text(
            f"**» Başarıyla Eklendi {user_name} Grubun yetkili kullanıcılar listesine.**"
        )
        return
    else:
        await message.reply_text(f"**» {user_name} Zaten Grubun Yetkili Kullanicılar Listesinde.**")


@app.on_message(filters.command("unauth") & filters.group)
@AdminActual
async def unauth_fe(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**» bir kullanıcının mesajını yanıtlama veya kullanıcı adı / kullanıcı kimliği ver.**"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        token = await int_to_alpha(user.id)
        deleted = await delete_authuser(message.chat.id, token)
        if deleted:
            return await message.reply_text(
                f"**» Silindi {user.first_name} Geubun Yetkili Kullanıcılar Listesinden**"
            )
        else:
            return await message.reply_text("**» Yetkili Kullanıcılar Listesinde Yok.**")
    user_id = message.reply_to_message.from_user.id
    token = await int_to_alpha(user_id)
    deleted = await delete_authuser(message.chat.id, token)
    if deleted:
        return await message.reply_text(
            f"**» Silindi {message.reply_to_message.from_user.first_name} Yetkili Kullanıcılar Listesinden.**"
        )
    else:
        return await message.reply_text("**» Yetkili Kullanıcilar Listesinde Ylk.**")


@app.on_message(filters.command("authusers") & filters.group)
async def authusers(_, message: Message):
    _playlist = await get_authuser_names(message.chat.id)
    if not _playlist:
        return await message.reply_text(
            "**» bu grupta yetkili kullanıcı bulunamadı.**"
        )
    else:
        j = 0
        m = await message.reply_text(
            "**» Veri Tabanından yetkili kullanıcı listesi alma...**"
        )
        msg = "**🥀 Yetkili Kullanıcılar Listesi :**\n\n"
        for note in _playlist:
            _note = await get_authuser(message.chat.id, note)
            user_id = _note["auth_user_id"]
            user_name = _note["auth_name"]
            admin_id = _note["admin_id"]
            admin_name = _note["admin_name"]
            try:
                user = await app.get_users(user_id)
                user = user.first_name
                j += 1
            except Exception:
                continue
            msg += f"{j}➤ {user}[`{user_id}`]\n"
            msg += f"    ┗ Ekleyen : {admin_name}[`{admin_id}`]\n\n"
        await m.edit_text(msg)
