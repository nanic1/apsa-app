import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

email = os.getenv("EMAIL_INSTAGRAM")
senha = os.getenv("SENHA_INSTAGRAM")

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

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def login(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(7)

    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "pass").send_keys(senha)
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div/div[1]/div/div[3]/div/div/div').click()

    time.sleep(10)

    # fechar popups
    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'Agora não')]").click()
        time.sleep(3)
        driver.find_element(By.XPATH, "//button[contains(text(),'Agora não')]").click()
    except:
        pass


def pegar_post(driver, url):
    driver.get(url)
    time.sleep(5)

    # pegar container dos posts
    posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")

    if not posts:
        return None, None, None

    post = posts[0]

    link_post = post.get_attribute("href")

    if not link_post:
        return None, None, None

    link_post_embed = link_post.replace("www.instagram.com", "www.toinstagram.com")

    # ID do post vem da URL
    try:
        post_id = link_post.split("/p/")[1].split("/")[0]
    except:
        return None, None, None

    # abrir post pra pegar texto
    driver.get(link_post)
    time.sleep(5)


    return post_id, link_post, link_post_embed

# carregar JSON
with open("instagram.json", "r", encoding="utf-8") as f:
    data = json.load(f)

empresas = data["instagram"]

ultimos_ids = carregar_ids()

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
login(driver)

print("Monitorando posts...\n")

while True:
    for empresa in empresas:
        nome = empresa["nome"]
        url = empresa["url"]

        try:
            post_id, link_post, link_post_embed = pegar_post(driver, url)
            
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
                    f"🔗 <b>LINK:</b> {link_post_embed}"
                    )

                ultimos_ids[nome] = post_id
                salvar_ids()

        except Exception as e:
            print(f"Erro em {nome}: {e}")

    today = datetime.now()
    horas = today.strftime("%H:%M:%S")
    print(f"Varredura completa as [{horas}], reiniciando varredura.\n")
    time.sleep(5)