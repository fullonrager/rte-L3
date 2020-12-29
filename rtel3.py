# -*- coding: utf-8 -*-
import seleniumwire
import selenium
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from random import randint
from collections import Counter
import time
from bs4 import BeautifulSoup
import codecs
import re
import requests
import sys
import os

os.system('cls')
print("***  RTÉ Player Downloader (rte-L3 v1.0.4)  ***")
print("***        Developed by fullonrager         ***")
print()

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

def download_video():
    print("Downloading video...")
    os.system('python -m youtube_dl --fixup never -f bestvideo --output "temp/'+temp_title+'.mp4" ' + '"'+video_mpd+'"')
    print("Video downloaded successfully.")
    print("Downloading audio...")
    os.system('python -m youtube_dl --fixup never -f bestaudio --output "temp/'+temp_title+'.m4a" ' + '"'+video_mpd+'"')
    print("Audio downloaded successfully.")

def cleanup():
    print("Removing leftover files...")
    if os.path.isfile('temp/'+temp_title+'.mp4.part_urls'):
        os.remove('temp/'+temp_title+'.mp4.part_urls')
    if os.path.isfile('temp/'+temp_title+'.m4a.part_urls'):
        os.remove('temp/'+temp_title+'.m4a.part_urls')
    if os.path.isfile('temp/'+temp_title+'.mp4.part_urls.txt'):
        os.remove('temp/'+temp_title+'.mp4.part_urls.txt')
    if os.path.isfile('temp/'+temp_title+'.m4a.part_urls.txt'):
        os.remove('temp/'+temp_title+'.m4a.part_urls.txt')
    if os.path.isfile('temp/'+temp_title+'.m4a'):
        os.remove('temp/'+temp_title+'.m4a')
    if os.path.isfile('temp/'+temp_title+'.mp4'):
        os.remove('temp/'+temp_title+'.mp4')
    if os.path.isfile('temp/'+temp_title+'-out.mp4'):
        os.remove('temp/'+temp_title+'-out.mp4')
    if os.path.isfile('temp/'+temp_title+'-out.m4a'):
        os.remove('temp/'+temp_title+'-out.m4a')
    if os.path.isfile('Downloads/'+temp_title+'.mkv'):
        os.remove('Downloads/'+temp_title+'.mkv')

video_mpd = ""
video_xml = ""
keys = []
# Generate random temporary video title to prevent issues with certain characters
temp_title = "rte_video_"+str(randint(1, 999))

if not os.path.isfile("decryptor.crx"):
    print("Error: Cannot run script, decryptor is not in folder. Please read the README.")
    print("If you do have it, ensure it's titled 'decryptor.crx'.")
    sys.exit(1)

try:
    url = sys.argv[1]
except IndexError:
    print("Error: Please enter an RTÉ Player URL to download.")
    sys.exit(2)

if not os.path.isdir('temp'):
    os.mkdir('temp')
if not os.path.isdir('Downloads'):
    os.mkdir('Downloads')

print("Loading page...")

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_extension("decryptor.crx")
driver = webdriver.Chrome(options=options)
driver.get(url)

try:
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'onetrust-policy-text')))
except selenium.common.exceptions.TimeoutException:
    print("Request timed out, try again later.")
    sys.exit(3)

print("Accepting necessary cookies...")
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'onetrust-pc-btn-handler')))
    driver.find_element_by_class_name('cookie-setting-link').click()
    time.sleep(0.5)
    driver.find_element_by_class_name('save-preference-btn-handler').click()
except selenium.common.exceptions.TimeoutException:
    driver.quit()
    print("Request timed out, try again.")
    sys.exit(4)

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn')))

# Play the video
print("Attempting to click play button...")
time.sleep(4)
try:
    driver.find_elements_by_class_name('ic-play-white')[0].click()
except selenium.common.exceptions.NoSuchElementException:
    print("Request timed out, try again later.")
    sys.exit(5)
time.sleep(2)

# Bypass mature content pop-up if needed
try:
    driver.find_element_by_class_name('modal-body').text
    driver.find_element_by_class_name('col-lg-18').click()
except selenium.common.exceptions.NoSuchElementException:
    pass

time.sleep(3)

regex_xml = re.compile(r"(https\:\/\/link\.eu\.theplatform\.com\/s\/).+(&formats=(mpeg-dash|m3u))")
for request in driver.requests:
    if regex_xml.match(str(request)):
        video_xml = request.url
        break

print("Searching for MPD URL...")
regex_vod = re.compile(r"https://vod\.rte\.ie/rte/vod/RTE_Prod_-_Prod/\d*/\d*/\w*/.+\.ism.\.mpd?.*&hls_fmp4=true")
regex_vod_d = re.compile(r"https://vod\.rte\.ie/rte/vod-d/RTE_Prod_-_Prod/\d*/\d*/\w*/.+\.ism.\.mpd?.*&hls_fmp4=true")
for request in driver.requests:
    if regex_vod.match(request.url):
        video_mpd = request.url
        break
    if regex_vod_d.match(request.url):
        video_mpd = request.url
        break

try:
    req = requests.get(video_xml, allow_redirects=True)
    html = codecs.decode(req.content, "utf-8")
    video_embed_xml = BeautifulSoup(html, "lxml")
    video_title_element = video_embed_xml.find(lambda tag: tag.name == "meta" and "title" in tag.attrs["name"])
except requests.exceptions.MissingSchema:
    driver.quit()
    print("Request timed out, try again.")
    sys.exit(6)

print()
try:
    video_title = video_title_element.attrs["content"]
    print(u"Video title = " + video_title)
    # Remove characters forbidden on Windows
    video_title = re.sub(r'[\\/*?:"<>|]',"",video_title)
except AttributeError:
    video_title = "RTE-Player-Video"
    print("Unable to extract video title, using placeholder title instead.")
    print("I strongly encourage you to rename this file after it downloads as it may be overwritten.")

if video_mpd == "":
    print("MPD URL not found, try again.")
    sys.exit(7)
else:
    print()
    print("Found MPD URL: " + video_mpd)
    print()

# Allow time to receive decryption keys
time.sleep(5)

key_string = driver.find_element_by_tag_name("body").get_attribute("innerText")
driver.quit()

keys = re.findall(r"WidevineDecryptor: Found key: (\w+) \(KID=(\w+)\)", key_string)

# Create a string for each of the five keys
try:
    kid_key1 = keys[0][1]+":"+keys[0][0]
    kid_key2 = keys[1][1]+":"+keys[1][0]
    kid_key3 = keys[2][1]+":"+keys[2][0]
    kid_key4 = keys[3][1]+":"+keys[3][0]
    kid_key5 = keys[4][1]+":"+keys[4][0]
except IndexError:
    print("Failed to get decryption key.")
    print("It's possible that this media streams unencrypted.")
    print()
    if yes_or_no("Would you like to download anyway?"):
        download_video()
        print("Merging videos together...")
        os.system(r'binaries\mkvmerge.exe -o "Downloads/'+temp_title+'.mkv" "temp/'+temp_title+'.mp4" "temp/'+temp_title+'.m4a"')
        cleanup()
        print("Finished!")
        sys.exit(0)
    else:
        print("Okay, exiting.")
        sys.exit(8)

print("Obtained five possible decryption keys (KID:Key):")
print("Key 1: " + kid_key1)
print("Key 2: " + kid_key2)
print("Key 3: " + kid_key3)
print("Key 4: " + kid_key4)
print("Key 5: " + kid_key5)
print()

download_video()

# Decryption stage
print("Decrypting video and audio...")
os.system(r'binaries\mp4decrypt.exe --key '+kid_key1+' --key '+kid_key2+' --key '+kid_key3+' --key '+kid_key4+' --key '+kid_key5+' "temp/'+temp_title+'.mp4" "temp/'+temp_title+'-out.mp4"')
os.system(r'binaries\mp4decrypt.exe --key '+kid_key1+' --key '+kid_key2+' --key '+kid_key3+' --key '+kid_key4+' --key '+kid_key5+' "temp/'+temp_title+'.m4a" "temp/'+temp_title+'-out.m4a"')

# Merge video and audio into Matroska
print("Merging video and audio together...")
os.system(r'binaries\mkvmerge.exe -o "Downloads/'+temp_title+'.mkv" "temp/'+temp_title+'-out.mp4" "temp/'+temp_title+'-out.m4a"')
try:
    os.rename('Downloads/'+temp_title+'.mkv', 'Downloads/'+video_title+'.mkv')
except FileExistsError:
    print()
    print("A video with this filename already exists.")
    if video_title == "RTE-Player-Video":
        print("WARNING: It's possible you may overwrite a different video. Please check the file before proceeding.")
    if yes_or_no("Do you want to overwrite it?"):
        os.remove('Downloads/'+video_title+'.mkv')
        os.rename('Downloads/'+temp_title+'.mkv', 'Downloads/'+video_title+'.mkv')
    else:
        print("Okay, exiting.")
        cleanup()
        sys.exit(9)

print("Saved as: "+video_title+".mkv")

# Clean up leftover files
cleanup()
print("Finished!")
sys.exit(0)