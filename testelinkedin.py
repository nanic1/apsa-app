import pywhatkit as kit

def enviar_whatsapp(msg):
    kit.sendwhatmsg_to_group_instantly(
        "DW8NpQaqpBKDbXyW9D15ll",
        msg,
        wait_time=15,
        tab_close=True
    )

enviar_whatsapp(
                    "🛎️ *NOVA POSTAGEM!* 🛎️\n"
                    f"🏣 *EMPRESA:* a\n"
                    f"🗓️ *DATA* b\n"
                    f"🕐 *HORA* c\n"
                    f"🔗 *LINK:* d"
                    )