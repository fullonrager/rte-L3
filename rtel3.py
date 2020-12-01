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

# Set to 'True' for media which is intended for mature audiences.
mature = False

# Set to 'True' to prevent GUI window, currently may prevent the decryptor from functioning.
headless = False

# Ensure paths don't contain a "\", use "/" instead.
# To prevent potential errors, use a filepath with no spaces.
path_to_folder = "C:/Users/User/Desktop/rtel3"
path_to_crx = "D:/widevine-l3-decryptor.crx"

# *************************************

video_mpd = ""
video_xml = ""
keys = []
url = sys.argv[1]

if os.path.isfile(path_to_folder+'/temp'):
    os.mkdir(path_to_folder+'/temp')

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
    raise Exception("Request timed out, try again. Have you enabled the Mature variable if this is for mature audiences?")

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn')))

# Play the video
print("Attempting to click play button...")
time.sleep(4)
driver.find_elements_by_class_name('ic-play-white')[0].click()
time.sleep(2)

# Bypass mature content pop-up if needed
if mature:
    print("Accepting mature pop-up...")
    driver.find_element_by_class_name('modal-body').text
    driver.find_element_by_class_name('col-lg-18').click()
    time.sleep(1)

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
print(key_string)
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

print("Preparing to download video segments...")
print("Downloading video...")
os.system('python -m youtube_dl --fixup never -f bestvideo --output "'+video_title+'.mp4" ' + '"'+video_mpd+'"')
print("Video downloaded successfully.")
print("Downloading audio...")
os.system('python -m youtube_dl --fixup never -f bestaudio --output "'+video_title+'.m4a" ' + '"'+video_mpd+'"')
print("Audio downloaded successfully.")

# Decryption stage

print("Decrypting video with first key:kid...")
print("Attempting to execute: "+path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key1+' "'+video_title+'.mp4" "'+video_title+'-key1.mp4"')
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key1+' "'+video_title+'.mp4" "'+video_title+'-key1.mp4"')
print("Decrypting audio with first key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key1+' "'+video_title+'.m4a" "'+video_title+'-key1.m4a"')

print("Decrypting video with second key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key2+' "'+video_title+'.mp4" "'+video_title+'-key2.mp4"')
print("Decrypting audio with second key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key2+' "'+video_title+'.m4a" "'+video_title+'-key2.m4a"')

print("Decrypting video with third key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key3+' "'+video_title+'.mp4" "'+video_title+'-key3.mp4"')
print("Decrypting audio with third key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key3+' "'+video_title+'.m4a" "'+video_title+'-key3.m4a"')

print("Decrypting video with fourth key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key4+' "'+video_title+'.mp4" "'+video_title+'-key4.mp4"')
print("Decrypting audio with fourth key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key4+' "'+video_title+'.m4a" "'+video_title+'-key4.m4a"')

print("Decrypting video with fifth key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key5+' "'+video_title+'.mp4" "'+video_title+'-key5.mp4"')
print("Decrypting audio with fifth key:kid...")
os.system(path_to_folder+'/binaries/mp4decrypt.exe --key '+kid_key5+' "'+video_title+'.m4a" "'+video_title+'-key5.m4a"')

# Merging video and audio into Matroska, it will fail to merge one with invalid keys.

print("Merging videos together...")
print("Attempting to execute: "+path_to_folder+'/binaries/mkvmerge.exe -o "'+video_title+'-out-key1.mp4" "'+video_title+'-key1.mp4" "'+video_title+'-key1.m4a"')
os.system(path_to_folder+'/binaries/mkvmerge.exe -o "'+video_title+'-out-key1.mp4" "'+video_title+'-key1.mp4" "'+video_title+'-key1.m4a"')
os.system(path_to_folder+'/binaries/mkvmerge.exe -o "'+video_title+'-out-key2.mp4" "'+video_title+'-key2.mp4" "'+video_title+'-key2.m4a"')
os.system(path_to_folder+'/binaries/mkvmerge.exe -o "'+video_title+'-out-key3.mp4" "'+video_title+'-key3.mp4" "'+video_title+'-key3.m4a"')
os.system(path_to_folder+'/binaries/mkvmerge.exe -o "'+video_title+'-out-key4.mp4" "'+video_title+'-key4.mp4" "'+video_title+'-key4.m4a"')
os.system(path_to_folder+'/binaries/mkvmerge.exe -o "'+video_title+'-out-key5.mp4" "'+video_title+'-key5.mp4" "'+video_title+'-key5.m4a"')

# Cleaning up leftover files

print("Removing leftover files...")
os.remove(path_to_folder+'/'+video_title+'.mp4')
os.remove(path_to_folder+'/'+video_title+'.m4a')
os.remove(path_to_folder+'/'+video_title+'-key1.mp4')
os.remove(path_to_folder+'/'+video_title+'-key1.m4a')
os.remove(path_to_folder+'/'+video_title+'-key2.mp4')
os.remove(path_to_folder+'/'+video_title+'-key2.m4a')
os.remove(path_to_folder+'/'+video_title+'-key3.mp4')
os.remove(path_to_folder+'/'+video_title+'-key3.m4a')
os.remove(path_to_folder+'/'+video_title+'-key4.mp4')
os.remove(path_to_folder+'/'+video_title+'-key4.m4a')
os.remove(path_to_folder+'/'+video_title+'-key5.mp4')
os.remove(path_to_folder+'/'+video_title+'-key5.m4a')

# Compare file size of each output to determine which key was the correct one
print("Removing videos decrypted with invalid key...")
path1 = os.path.abspath(path_to_folder+'/'+video_title+'-out-key1.mp4')
path2 = os.path.abspath(path_to_folder+'/'+video_title+'-out-key2.mp4')
path3 = os.path.abspath(path_to_folder+'/'+video_title+'-out-key3.mp4')
path4 = os.path.abspath(path_to_folder+'/'+video_title+'-out-key4.mp4')
path5 = os.path.abspath(path_to_folder+'/'+video_title+'-out-key5.mp4')

path1_size = os.path.getsize(path_to_folder+'/'+video_title+'-out-key1.mp4')
path2_size = os.path.getsize(path_to_folder+'/'+video_title+'-out-key2.mp4')
path3_size = os.path.getsize(path_to_folder+'/'+video_title+'-out-key3.mp4')
path4_size = os.path.getsize(path_to_folder+'/'+video_title+'-out-key4.mp4')
path5_size = os.path.getsize(path_to_folder+'/'+video_title+'-out-key5.mp4')

sizes = [path1_size, path2_size, path3_size, path4_size, path5_size]
counter = Counter(sizes)
output = sizes.index(min(counter, key=counter.get))
print("Video "+str(output+1)+" is the correct file, removing others...")

for i in range(5):
    i += 1
    if i == output+1:
        os.rename(path_to_folder+'/'+video_title+'-out-key'+str(i)+'.mp4', path_to_folder+'/'+video_title+'.mp4')
    else:
        os.remove(path_to_folder+'/'+video_title+'-out-key'+str(i)+'.mp4')

print("Finished!")
sys.exit(0)
