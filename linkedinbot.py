import json
import time
from dotenv import load_dotenv
import os
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

load_dotenv()

email = os.getenv("EMAIL_LINKEDIN")
senha = os.getenv("SENHA_LINKEDIN")

ARQUIVO_IDS = "ids_salvos_linkedin.json"
TOKEN = os.getenv("TOKEN_TELEGRAM")
GROUP_ID = os.getenv("ID_TELEGRAM")

# guarda último ID
ultimos_ids = {}

def carregar_ids():
    try:
        with open(ARQUIVO_IDS, "r") as f:
            return json.load(f)
    except:
        return {}


def salvar_ids():
    try:
        with open(ARQUIVO_IDS, "w", encoding="utf-8") as f:
            json.dump(ultimos_ids, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def enviar_mensagem(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def login(driver):
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)

    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(senha)
    driver.find_element(By.XPATH, '//*[@type="submit"]').click()

    time.sleep(45)


def pegar_post(driver, url):
    if "sortBy=recent" not in url:
        if "?" in url:
            url += "&sortBy=recent"
        else:
            url += "?sortBy=recent"

    driver.get(url)
    time.sleep(5)

    posts = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")

    if not posts:
        return None, None, None

    post = posts[0]

    # pegar ID
    post_id = post.get_attribute("data-urn")

    if post_id:
        activity_id = post_id.split(":")[-1]
        link_post = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}"
    else:
        link_post = url

    # pegar ID
    post_id = post.get_attribute("data-urn")

    if not post_id:
        try:
            post_id = link_post.split("activity-")[-1]
        except:
            return None, None, None

    return post_id, link_post

# carregar JSON
with open("linkedin.json", "r", encoding="utf-8") as f:
    data = json.load(f)

empresas = data["linkedin"]

ultimos_ids = carregar_ids()

driver = webdriver.Chrome()
login(driver)

print("Monitorando posts...\n")

while True:
    for empresa in empresas:
        nome = empresa["nome"]
        url = empresa["url"]

        try:
            post_id, link_post = pegar_post(driver, url)

            if not post_id:
                continue

            # primeira vez (não printa)
            if nome not in ultimos_ids:
                ultimos_ids[nome] = post_id
                salvar_ids()
                print(f"[INIT] {nome}")

            elif ultimos_ids[nome] != post_id:
                today = datetime.now()
                data = today.strftime("%d/%m/%Y")
                horas = today.strftime("%H:%M:%S")
                enviar_mensagem(
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