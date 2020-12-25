# -*- coding: utf-8 -*-
import seleniumwire
import selenium
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from collections import Counter
import time
from bs4 import BeautifulSoup
import re
import requests
import sys
import os

# ***** USER-CONTROLLED VARIABLES *****

# Set to 'True' to prevent GUI window, currently may prevent the decryptor from functioning.
headless = False

# *************************************
os.system('cls')
print("***  RTÉ Player Downloader (rte-L3)  ***")
print("***     Developed by fullonrager     ***")
print()

video_mpd = ""
video_xml = ""
keys = []
try:
    url = sys.argv[1]
except IndexError:
    print("Error: Please enter an RTÉ Player URL to download.")
    sys.exit()

path_to_crx = "decryptor.crx"

if not os.path.isdir('temp'):
    os.mkdir('temp')
if not os.path.isdir('Downloads'):
    os.mkdir('Downloads')

print("Loading page...")

options = webdriver.ChromeOptions()
if headless:
    options.add_argument("headless")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_extension(path_to_crx)
driver = webdriver.Chrome(options=options)
driver.get(url)

try:
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'onetrust-policy-text')))
except selenium.common.exceptions.TimeoutException:
    raise Exception("Request timed out, try again later.")

print("Accepting necessary cookies...")
try:
    driver.find_element_by_class_name('cookie-setting-link').click()
    time.sleep(0.5)
    driver.find_element_by_class_name('save-preference-btn-handler').click()
    time.sleep(0.5)
except selenium.common.exceptions.TimeoutException:
    driver.quit()
    raise Exception("Request timed out, try again.")

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn')))

# Play the video
print("Attempting to click play button...")
time.sleep(4)
try:
    driver.find_elements_by_class_name('ic-play-white')[0].click()
except selenium.common.exceptions.NoSuchElementException:
    raise Exception("Request timed out, try again later.")
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
    video_embed_xml = BeautifulSoup(req.content, "lxml")
    video_title_element = video_embed_xml.find(
            lambda tag: tag.name == "meta" and "title" in tag.attrs["name"]
        )
except requests.exceptions.MissingSchema:
    driver.quit()
    raise Exception("Request timed out, try again.")

print()
try:
    video_title = video_title_element.attrs["content"]
    print(u"Video title = " + video_title)
except AttributeError:
    video_title = "RTE-Player-Video"
    print("Unable to extract video title, using placeholder title instead.")

if video_mpd == "":
    raise Exception("MPD URL not found, try again.")
else:
    print()
    print("Found MPD URL: " + video_mpd)
    print()

# Allow time to receive decryption keys
time.sleep(5)

key_string = driver.find_element_by_tag_name("body").get_attribute("innerText")
driver.quit()

keys = re.findall(r"WidevineDecryptor: Found key: (\w+) \(KID=(\w+)\)", key_string)

# Creating a string for each of the five keys
try:
    kid_key1 = keys[0][1]+":"+keys[0][0]
    kid_key2 = keys[1][1]+":"+keys[1][0]
    kid_key3 = keys[2][1]+":"+keys[2][0]
    kid_key4 = keys[3][1]+":"+keys[3][0]
    kid_key5 = keys[4][1]+":"+keys[4][0]
except IndexError:
    raise Exception("Failed to get decryption key, try again.")

print("Obtained five possible decryption keys (KID:Key):")
print("Key 1: " + kid_key1)
print("Key 2: " + kid_key2)
print("Key 3: " + kid_key3)
print("Key 4: " + kid_key4)
print("Key 5: " + kid_key5)
print()

print("Preparing to download video segments...")
print("Downloading video...")
os.system('python -m youtube_dl --fixup never -f bestvideo --output "temp/'+video_title+'.mp4" ' + '"'+video_mpd+'"')
print("Video downloaded successfully.")
print("Downloading audio...")
os.system('python -m youtube_dl --fixup never -f bestaudio --output "temp/'+video_title+'.m4a" ' + '"'+video_mpd+'"')
print("Audio downloaded successfully.")

# Decryption stage

print("Decrypting video and audio with first key...")
os.system('binaries\mp4decrypt.exe --key '+kid_key1+' "temp/'+video_title+'.mp4" "temp/'+video_title+'-key1.mp4"')
os.system('binaries\mp4decrypt.exe --key '+kid_key1+' "temp/'+video_title+'.m4a" "temp/'+video_title+'-key1.m4a"')

print("Decrypting video and audio with second key...")
os.system('binaries\mp4decrypt.exe --key '+kid_key2+' "temp/'+video_title+'.mp4" "temp/'+video_title+'-key2.mp4"')
os.system('binaries\mp4decrypt.exe --key '+kid_key2+' "temp/'+video_title+'.m4a" "temp/'+video_title+'-key2.m4a"')

print("Decrypting video and audio with third key...")
os.system('binaries\mp4decrypt.exe --key '+kid_key3+' "temp/'+video_title+'.mp4" "temp/'+video_title+'-key3.mp4"')
os.system('binaries\mp4decrypt.exe --key '+kid_key3+' "temp/'+video_title+'.m4a" "temp/'+video_title+'-key3.m4a"')

print("Decrypting video and audio with fourth key...")
os.system('binaries\mp4decrypt.exe --key '+kid_key4+' "temp/'+video_title+'.mp4" "temp/'+video_title+'-key4.mp4"')
os.system('binaries\mp4decrypt.exe --key '+kid_key4+' "temp/'+video_title+'.m4a" "temp/'+video_title+'-key4.m4a"')

print("Decrypting video and audio with fifth key...")
os.system('binaries\mp4decrypt.exe --key '+kid_key5+' "temp/'+video_title+'.mp4" "temp/'+video_title+'-key5.mp4"')
os.system('binaries\mp4decrypt.exe --key '+kid_key5+' "temp/'+video_title+'.m4a" "temp/'+video_title+'-key5.m4a"')

# Merging video and audio into Matroska, it will fail to merge those with invalid keys.

print("Merging videos together...")
for i in range(5):
    i += 1
    os.system('binaries\mkvmerge.exe -o "temp/'+video_title+'-out-key'+str(i)+'.mkv" "temp/'+video_title+'-key'+str(i)+'.mp4" "temp/'+video_title+'-key'+str(i)+'.m4a"')

# Cleaning up leftover files

print("Removing leftover files...")
if os.path.isfile('temp/'+video_title+'.mp4/part_urls'):
    os.remove('temp/'+video_title+'.mp4.part_urls')
if os.path.isfile('temp/'+video_title+'.m4a.part_urls'):
    os.remove('temp/'+video_title+'.m4a.part_urls')
os.remove('temp/'+video_title+'.mp4')
os.remove('temp/'+video_title+'.m4a')
for i in range(5):
    i += 1
    os.remove('temp/'+video_title+'-key'+str(i)+'.mp4')
    os.remove('temp/'+video_title+'-key'+str(i)+'.m4a')

# Compare file size of each output to determine which key was the correct one
print("Removing videos decrypted with invalid key...")
path1 = os.path.abspath('temp/'+video_title+'-out-key1.mkv')
path2 = os.path.abspath('temp/'+video_title+'-out-key2.mkv')
path3 = os.path.abspath('temp/'+video_title+'-out-key3.mkv')
path4 = os.path.abspath('temp/'+video_title+'-out-key4.mkv')
path5 = os.path.abspath('temp/'+video_title+'-out-key5.mkv')

path1_size = os.path.getsize('temp/'+video_title+'-out-key1.mkv')
path2_size = os.path.getsize('temp/'+video_title+'-out-key2.mkv')
path3_size = os.path.getsize('temp/'+video_title+'-out-key3.mkv')
path4_size = os.path.getsize('temp/'+video_title+'-out-key4.mkv')
path5_size = os.path.getsize('temp/'+video_title+'-out-key5.mkv')

sizes = [path1_size, path2_size, path3_size, path4_size, path5_size]
counter = Counter(sizes)
output = sizes.index(min(counter, key=counter.get))
print("Video "+str(output+1)+" is the correct file, removing others...")

for i in range(5):
    i += 1
    if i == output+1:
        os.rename('temp/'+video_title+'-out-key'+str(i)+'.mkv', 'temp/'+video_title+'.mkv')
    else:
        os.remove('temp/'+video_title+'-out-key'+str(i)+'.mkv')

# Move video to Downloads folder
os.rename('temp/'+video_title+'.mkv', 'Downloads/'+video_title+'.mkv')

print("Finished!")
sys.exit(0)
