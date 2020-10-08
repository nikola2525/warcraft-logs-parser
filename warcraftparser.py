from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv
import time
import re


driver_path = 'chromedriver.exe'
browser = webdriver.Chrome(executable_path=driver_path)


# for source in sources:
#    print("https://www.warcraftlogs.com/reports/ZBK1pvArgNGdMDT4#fight=22" + "&type=resources&spell=110&source={}".format(source))
all_spells = [
    "Azeroth's Radiance",
    "Black Volley",
    "Harvest Thoughts",
    "Corrupted Viscera",
    "Anguish",
    "Mental Decay",
    "Cataclysmic Flames",
    "Flames of Insanity",
    "Devour Thoughts",
    "Psychic Burst",
    "Manifest Madness",
    "Corrupted Mind"
]


def player_links():
    return browser.find_elements_by_xpath(
        "//*[@id='table-container']/div[2]/table/tbody/tr/td[2]/span/a")


def get_player_id(link):
    return re.search(
        r'1,(\d+),', link.get_attribute("onclick")).group(1)


def get_spell_names():
    elements = browser.find_elements_by_xpath(
        "//table[@class='summary-table dataTable no-footer']/tbody/tr/td[1]/a[2]/span")
    return map(lambda x: x.text, elements)


def get_resource_gains():
    elements = browser.find_elements_by_xpath(
        "//table[@class='summary-table dataTable no-footer']/tbody/tr/td[4]")
    return map(lambda x: int(x.text), elements)


def report_to_csv(table_map, player_names, file_name, first_fight, fight):
    with open(r".\\" + file_name + ".csv", 'a+', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if(fight == first_fight):
            spamwriter.writerow(["Pull:{}".format(fight), ]+player_names)
        else:
            spamwriter.writerow(["Pull:{}".format(fight), ])
        for key in table_map:
            spamwriter.writerow([key, ]+table_map[key])


def run(first_fight, number_of_fights, fight_url, file_name):
    sources = []
    all_player_names = []
    table_map = {}

    browser.get(fight_url + "/#fight={}".format(first_fight))

    for link in player_links():
        all_player_names.append(link.text)  # Takes out the name of the player
        sources.append(get_player_id(link))

    safe = True
    # For every fight that the user inputed iterate through them
    for fight in range(first_fight, number_of_fights+first_fight):
        number_of_players_parsed = 1
        # Initialize table_map to 0 for every spell
        for spell_name in all_spells:
            table_map[spell_name] = [0]

        # Iterates through each player (source)
        source = 0
        sources_len = len(sources)
        while source < sources_len:
            browser.get(fight_url + "/#fight={}".format(fight) +
                        "&type=resources&spell=110&source={}".format(sources[source]))

            # safeguard for checking if automatation can continue
            if safe:
                try:
                    # checking if page is loaded
                    elementi = WebDriverWait(browser, 10).until(
                        lambda browser: browser.execute_script(
                            "return jQuery.active==0")
                    )
                except TimeoutException:
                    time.sleep(5)

            # checking if table exists
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//*[@id='main-table-0_wrapper']"))
                )
            except:
                safe = False
                time.sleep(3)
                browser.refresh()
                continue
            source += 1
            safe = True

            spell_names = get_spell_names()
            values = get_resource_gains()
            gains_per_spell = zip(spell_names, values)

    # https://www.warcraftlogs.com/reports/CM6H3hX2k8qNAPZf
            for value in gains_per_spell:
                spell_name = value[0]
                gain = value[1]
                # checking if element already exists
                if(len(table_map[spell_name])-1 == number_of_players_parsed):
                    table_map[spell_name].append(gain)
                else:
                    table_map[spell_name][number_of_players_parsed - 1] += gain

            for spell_name in all_spells:
                if len(table_map[spell_name])-1 != number_of_players_parsed:
                    table_map[spell_name].append(0)  # every time
            number_of_players_parsed += 1
        # deleting zeroes
        for spell_name in all_spells:
            del table_map[spell_name][number_of_players_parsed-1]

        report_to_csv(table_map, all_player_names,
                      file_name, first_fight, fight)
        table_map.clear()  # deleting table_map

    browser.close()


if __name__ == "__main__":
    first_fight = int(input("Upisi prvu bitku"))
    number_of_fights = int(input("Upisi broj bitaka"))
    fight_url = input("Upisi Url log-a")
    file_name = input("Upisi ime fajla")
    run(first_fight, number_of_fights, fight_url, file_name)
