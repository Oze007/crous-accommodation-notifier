import argparse
import logging
import time
from typing import List

import telepot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.parser import Parser
from src.models import UserConf
from src.notification_builder import NotificationBuilder
from src.settings import Settings
from src.telegram_notifier import TelegramNotifier

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
logger = logging.getLogger("accommodation_notifier")


def load_users_conf() -> List[UserConf]:
    # Configuration multi-villes avec tes URLs exactes
    return [
        UserConf(
            conf_title="Metz",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url="https://trouverunlogement.lescrous.fr/tools/45/search?maxPrice=310&occupationModes=alone&bounds=6.1360042_49.1487955_6.256451_49.0608244&locationName=Metz",  
            ignored_ids=[],
        ),
        UserConf(
            conf_title="Caen",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url="https://trouverunlogement.lescrous.fr/tools/45/search?maxPrice=300&bounds=-0.413777_49.2162655_-0.3307282_49.1530145&locationName=Caen+%2814000%29",  
            ignored_ids=[],
        ),
        UserConf(
            conf_title="Rennes",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url="https://trouverunlogement.lescrous.fr/tools/45/search?occupationModes=alone&bounds=-1.7525876_48.1549705_-1.6244045_48.0769155&locationName=Rennes",  
            ignored_ids=[],
        ),
        UserConf(
            conf_title="Aix-en-Provence",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url="https://trouverunlogement.lescrous.fr/tools/45/search?occupationModes=alone&bounds=5.2694745_43.6259224_5.5063013_43.4461058&locationName=Aix-en-Provence",  
            ignored_ids=[],
        )
    ]


def create_driver(headless: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if headless:
        logging.info("Running in headless mode")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
    else:
        logging.info("Running in non-headless mode")

    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # Initialisation de Chrome avec les options de sécurité
    return webdriver.Chrome(options=chrome_options)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the script in headless mode or not."
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run the script without headless mode",
    )

    args = parser.parse_args()

    # Chargement des paramètres (depuis Render)
    settings = Settings()
    bot = telepot.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.getMe() 

    user_confs = load_users_conf()

    while True:
        try:
            driver = create_driver(headless=not args.no_headless)
            
            # Mode "Visiteur" sécurisé
            parser_obj = Parser(driver)
            notification_builder = NotificationBuilder()
            notifier = TelegramNotifier(bot)

            for conf in user_confs:
                logging.info(f"Recherche en cours pour : {conf.conf_title}")
                search_results = parser_obj.get_accommodations(conf.search_url)
                notification = notification_builder.search_results_notification(search_results)
                if notification:
                    notifier.send_notification(conf.telegram_id, notification)

            # Fermeture propre du navigateur après la vérification des 4 villes
            driver.quit()
        
        except Exception as e:
            logging.error(f"Une erreur est survenue lors de l'exécution : {e}")
            try:
                driver.quit()
            except:
                pass
        
        logging.info("Recherche terminée pour les 4 villes. Attente de 10 minutes (600 secondes) pour éviter le blocage...")
        time.sleep(600)
