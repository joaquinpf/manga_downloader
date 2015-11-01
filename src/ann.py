#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###################

import config


# ####################

from bs4 import BeautifulSoup
from util.util import get_source_code

# ####################

def get_ann_details(title, type):

    list_url = 'https://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=%s&search=%s' % (type.lower(), title.lower())
    source = get_source_code(list_url, config.proxy)

    soup = BeautifulSoup(source, 'xml')

    # Sample List Payload
    # <report skipped="0" listed="100">
    #     <args>
    #         <type>manga</type>
    #         <name/>
    #         <search>naruto</search>
    #     </args>
    #     <item>
    #         <id>17286</id>
    #         <gid>3700453906</gid>
    #         <type>manga</type>
    #         <name>Naruto: The Seventh Hokage and the Scarlet Spring</name>
    #         <precision>manga</precision>
    #         <vintage>2015-04-27 to 2015-07-06</vintage>
    #         <searched_title>Naruto: The Seventh Hokage and the Scarlet Spring</searched_title>
    #     </item>
    #     <item>
    #         <id>1598</id>
    #         <gid>389590229</gid>
    #         <type>manga</type>
    #         <name>Naruto</name>
    #         <precision>manga</precision>
    #         <vintage>2000-03</vintage>
    #         <searched_title>Naruto</searched_title>
    #     </item>
    # </report>

    items = soup.find_all("item")
    title_id = -1

    for item in items:
        name = item.find('name').get_text().strip().lower()
        if name == title.lower():
            title_id = item.find('id').get_text()
            break

    if title_id == -1:
        raise TitleNotFound(title)

    details_url = 'https://cdn.animenewsnetwork.com/encyclopedia/api.xml?title=' + title_id
    source = get_source_code(details_url, config.proxy)

    soup = BeautifulSoup(source, 'xml')

    # Sample details payload (shortened)
    # <ann>
    # 	<manga id="1598" gid="389590229" type="manga" name="Naruto" precision="manga" generated-on="2015-10-31T02:09:28Z">
    # 		<related-prev rel="serialized in" id="1363"/>
    # 		<related-prev rel="serialized in" id="1678"/>
    # 		<related-next id="1825" rel="adaptation"/>
    # 		<related-next id="13833" rel="spinoff"/>
    # 		<related-next id="16228" rel="spinoff"/>
    # 		<related-next id="17286" rel="sequel"/>
    # 		<related-next id="17311" rel="spinoff"/>
    # 		<related-next id="17312" rel="spinoff"/>
    # 		<related-next id="17313" rel="spinoff"/>
    # 		<related-next id="17314" rel="spinoff"/>
    # 		<related-next id="17315" rel="spinoff"/>
    # 		<related-next id="17316" rel="spinoff"/>
    # 		<related-next id="17317" rel="spinoff"/>
    # 		<info gid="2944829316" type="Picture" src="http://cdn.animenewsnetwork.com/thumbnails/fit200x200/encyc/A1598-21.jpg" width="153" height="200">
    # 			<img src="http://cdn.animenewsnetwork.com/thumbnails/fit200x200/encyc/A1598-21.jpg" width="153" height="200"/>
    # 			<img src="http://cdn.animenewsnetwork.com/thumbnails/max500x600/encyc/A1598-21.jpg" width="310" height="404"/>
    # 		</info>
    # 		<info gid="2752248348" type="Main title" lang="EN">Naruto</info>
    # 		<info gid="1060378466" type="Alternative title" lang="EN">NARUTO―ナルト―</info>
    # 		<info gid="3956804774" type="Alternative title" lang="RU">Наруто</info>
    # 		<info gid="922360632" type="Alternative title" lang="JA">ナルト</info>
    # 		<info gid="2143586567" type="Alternative title" lang="ZH-TW">火影忍者</info>
    # 		<info gid="2151904279" type="Alternative title" lang="KO">나루토</info>
    # 		<info gid="2734119770" type="Genres">action</info>
    # 		<info gid="826819009" type="Genres">comedy</info>
    # 		<info gid="1842935335" type="Genres">drama</info>
    # 		<info gid="3436210147" type="Genres">fantasy</info>
    # 		<info gid="2302158259" type="Themes">developing powers</info>
    # 		<info gid="2200330294" type="Themes">fighting</info>
    # 		<info gid="2269765241" type="Themes">ninja</info>
    # 		<info gid="1332744292" type="Themes">superpowers</info>
    # 		<info gid="3689004204" type="Themes">war</info>
    # 		<info gid="2401943722" type="Objectionable content">TA</info>
    # 		<info gid="2793726006" type="Plot Summary">
    # 			When Naruto was born the spirit of a evil nine-tailed fox was imprisoned within him, rendering him the hate of the villagers in the ninja-village of the Leaf who feared the demon in him. Countering this hate he grew into the role of the clown, trying to attract attention by making a fool of himself and his teachers. But within him dwells the dream of becoming Hokage, the strongest warrior of the village. When he graduates from the academy he’s placed in the same group as Sakura, the technician and the girl he loves and Sasuke, the strong, quiet guy and his rival for Sakura. Leader and teacher of the group are Kakashi, the strange and always late, though powerful ninja.
    # 		</info>
    # 		<info gid="1852709302" type="Number of tankoubon">72</info>
    # 		<info type="Vintage">2000-03</info>
    # 		<info gid="2016322877" type="Vintage">2003 (Poland)</info>
    # 		<info gid="2745183856" type="Vintage">
    # 			2003-01-07 (North America, serialization in Shonen Jump)
    # 		</info>
    # 		<info gid="2618427652" type="Vintage">2003-04 (Italy)</info>
    # 		<info gid="1890457820" type="Vintage">2006-10-04 (The Netherlands)</info>
    # 		<info gid="2521887225" type="Vintage">2007-04-19 (México)</info>
    # 		<info gid="1635394810" type="Vintage">2007-05-17 (Brazil)</info>
    # 		<info gid="2719357400" type="Official website" lang="EN" href="http://www.madman.com.au/actions/periodicals.do?method=home&periodicalId=328">Madman's Official Naruto (Manga) Sales Site</info>
    # 		<info gid="1538151223" type="Official website" lang="FR" href="http://www.mangakana.com/Series.cfm?Query_Code=NAR">Manga Kana Naruto Page</info>
    # 		<info gid="2028996673" type="Official website" lang="EN" href="http://www.shonenjump.com/mangatitles/n/manga_n.php">Shonen Jump - Naruto</info>
    # 		<info gid="3380090417" type="Official website" lang="EN" href="http://www.shonenjump.com/mangatitles/n/manga_n.php">Shonen Jump USA</info>
    # 		<info gid="2254069500" type="Official website" lang="JA" href="http://jump.shueisha.co.jp/naruto/">Shueisha - Naruto</info>
    # 		<ratings nb_votes="2181" weighted_score="8.0595" bayesian_score="8.059"/>
    # 		<staff gid="2617180639">
    # 			<task>Story & Art</task>
    # 			<person id="8036">Masashi Kishimoto</person>
    # 		</staff>
    # 	</manga>
    # </ann>

    details = {}
    details['vintage'] = soup.find("info", type="Vintage").get_text()
    summary_xml = soup.find("info", type="Plot Summary")
    details['summary'] = summary_xml.get_text() if summary_xml else ''

    genres_xml = soup.find_all("info", type="Genres")
    details['genres'] = []
    for genre in genres_xml:
        details['genres'].append(genre.get_text().strip().lower())

    themes_xml = soup.find_all("info", type="Themes")
    details['themes'] = []
    for theme in themes_xml:
        details['themes'].append(theme.get_text().strip().lower())

    picture = {}
    picture_xml = soup.find("info", type="Picture")
    if picture_xml:
        picture_xml = picture_xml.find_all('img')[-1]
        picture['src'] = picture_xml['src']
        picture['width'] = picture_xml['width']
        picture['height'] = picture_xml['height']

    details['picture'] = picture

    ratings = {}
    ratings['weighted'] = soup.find("ratings")['weighted_score']
    ratings['bayesian'] = soup.find("ratings")['bayesian_score']
    details['ratings'] = ratings

    return details


class TitleNotFound(Exception):

    def __init__(self, error_msg=''):
        self.error_msg = 'Title not found. %s' % error_msg

    def __str__(self):
        return self.error_msg
