from  selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv
import time
import re



driver_path = 'C:\Program Files (x86)\chromedriver.exe'
browser = webdriver.Chrome(executable_path=driver_path)

firstFight = int(input("Upisi prvu bitku"))
numberOfFights = int(input("Upisi broj bitaka"))


sources = []
allPlayerNames = []
tableMap = {}
old_page = []

#for source in sources:
#    print("https://www.warcraftlogs.com/reports/ZBK1pvArgNGdMDT4#fight=22" + "&type=resources&spell=110&source={}".format(source))
allSpells = ["Azeroth's Radiance",
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
fightUrl = input("Upisi Url")
sanityString = input("Upisi datum fajta")
browser.get(fightUrl + "/#fight={}".format(firstFight))
getElements  = browser.find_elements_by_xpath("//*[@id='table-container']/div[2]/table/tbody/tr/td[2]/span/a")
for element in getElements:
    sourceNumber = re.search('1,(\d+),',element.get_attribute("onclick")).group(1)
    allPlayerNames.append(element.text)
    sources.append(sourceNumber)
#//*[@id="summary-damage-done-0"]/tbody/tr[1]/td[1]/a
#for fightNumber in range((re.search('d+',bossFightNumber.text))).group():
sourcesLength = len(sources)
safe = True;
for fight in range(firstFight,numberOfFights+firstFight):
    numberOfPlayersParsed = 1
    for spellName in allSpells:
        tableMap[spellName] = [0]
    source = 0
    while source < sourcesLength:
        browser.get(fightUrl + "/#fight={}".format(fight) + "&type=resources&spell=110&source={}".format(sources[source]))

        if safe:
            try:
                elementi = WebDriverWait(browser,10).until(
                        lambda browser: browser.execute_script("return jQuery.active==0")
                    )
            except TimeoutException:
                print("cekah zauvek")
                time.sleep(10)

        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@id='main-table-0_wrapper']"))
            )
        except:
            safe = False
            time.sleep(10)
            browser.refresh()
            print("ispisah Nikog")

            continue
        safe = True
        source+=1


        spellNames =  browser.find_elements_by_xpath("//table[@class='summary-table dataTable no-footer']/tbody/tr/td[1]/a[2]/span")
        values = browser.find_elements_by_xpath("//table[@class='summary-table dataTable no-footer']/tbody/tr/td[4]")
        #playerName = browser.find_element_by_xpath("//*[@id='filter-source-text']/span")

        #print(playerName.text)
        #if(playerName.text not in allPlayerNames):
        #    allPlayerNames.append(playerName.text)
        i=0
        for spellName in spellNames:
            if(len(tableMap[spellName.text])-1 == numberOfPlayersParsed):
                tableMap[spellName.text].append(int(values[i].text))
            else:
                tableMap[spellName.text][numberOfPlayersParsed-1]+=int(values[i].text)
            print(spellName.text+" " + values[i].text)
            i+=1
        print("----------")

        for spellName in allSpells:
            if len(tableMap[spellName])-1 != numberOfPlayersParsed:
                tableMap[spellName].append(0)                  #every time
        numberOfPlayersParsed+=1
    for spellName in allSpells:
        del tableMap[spellName][numberOfPlayersParsed-1]
#C:\Users\Nikola\Google Drive\WowDrive\sanityTable.csv
    with open(r"C:\Users\Nikola\Google Drive\WowDrive\\"+sanityString, 'a+', newline='') as csvfile:
        #spamwriter.writerow([playerName.text])
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if(fight == firstFight):
            spamwriter.writerow(["Pull:{}".format(fight),]+allPlayerNames)
        else:
            spamwriter.writerow(["Pull:{}".format(fight),])
        for key in tableMap:
            spamwriter.writerow([key,]+tableMap[key])
    print(tableMap)
    tableMap.clear()

        #get_table  = browser.find_elements_by_css_selector("tr")
        #for sanity in get_table:
        #    print(sanity.get_attribute("td").text)
        #print("---------")

browser.close()
