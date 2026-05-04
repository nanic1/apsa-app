from playwright.sync_api import sync_playwright
import time
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import requests
from zoneinfo import ZoneInfo

load_dotenv()

email = os.getenv("EMAIL_LINKEDIN")
senha = os.getenv("SENHA_LINKEDIN")

ARQUIVO_IDS = "ids_salvos_linkedin.json"
TOKEN = os.getenv("TOKEN_TELEGRAM")
GROUP_ID_WHATS = os.getenv("ID_WHATS")
GROUP_ID_TELEGRAM = os.getenv("ID_TELEGRAM")

def carregar_ids():
    try:
        with open(ARQUIVO_IDS, "r") as f:
            return json.load(f)
    except:
        return {}

ultimos_ids = {}

def salvar_ids():
    try:
        with open(ARQUIVO_IDS, "w", encoding="utf-8") as f:
            json.dump(ultimos_ids, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID_TELEGRAM,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def pegar_post(page, url):
    if "sortBy=recent" not in url:
        if "?" in url:
            url += "&sortBy=recent"
        else:
            url += "?sortBy=recent"

    page.goto(url)
    time.sleep(10)

    posts = page.locator("div.feed-shared-update-v2")

    if posts.count == 0:
        return None, None
    
    post = posts.first

    post_id = post.get_attribute("data-urn")

    if post_id:
        activity_id = post_id.split(":")[-1]
        link_post = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}"
    else:
        link_post = url

    if not post_id:
        try:
            post_id = link_post.split("activity-")[-1]
        except:
            return None, None

    return post_id, link_post

# default loop
with open("linkedin.json", "r", encoding="utf-8") as f:
    data = json.load(f)

empresas = data["linkedin"]

ultimos_ids = carregar_ids()

with sync_playwright() as pw:   
    driver = pw.chromium.launch(headless=True)
    context = driver.new_context(
        storage_state="state.json",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()
    page.goto("https://www.linkedin.com/feed/")
    time.sleep(30)
    print("Monitorando posts...")

    while True:
        for empresa in empresas:
            nome = empresa["nome"]
            url = empresa["url"]

            try:
                post_id, link_post = pegar_post(page, url)

                if not post_id:
                    continue
                
                if nome not in ultimos_ids:
                    ultimos_ids[nome] = post_id
                    salvar_ids()
                    print(f"[INIT] {nome}")

                elif ultimos_ids[nome] != post_id:
                    today = datetime.now(ZoneInfo("America/Sao_Paulo"))
                    data = today.strftime("%d/%m/%Y")
                    horas = today.strftime("%H:%M:%S")
                    print(
                        "🛎️ <b>NOVA POSTAGEM!</b> 🛎️\n"
                        f"🏣 <b>EMPRESA:</b> {nome}\n"
                        f"🗓️ <b>DATA</b> {data}\n"
                        f"🕐 <b>HORA</b> {horas}\n"
                        f"🔗 <b>LINK:</b> {link_post}"
                        )
                    enviar_telegram(
                        "🛎️ <b>NOVA POSTAGEM!</b> 🛎️\n"
                        f"🏣 <b>EMPRESA:</b> {nome}\n"
                        f"🗓️ <b>DATA</b> {data}\n"
                        f"🕐 <b>HORA</b> {horas}\n"
                        f"🔗 <b>LINK:</b> {link_post}"
                        )
                    
                    ultimos_ids[nome] = post_id
                    salvar_ids()

            except Exception as e:
                print(f"Erro em {nome}: {e}")

        today = datetime.now()
        horas = today.strftime("%H:%M:%S")
        print(f"Varredura completa as [{horas}], reiniciando varredura.\n")
        time.sleep(5)