# rte-L3 (EOL)
Script to download from the RTÉ Player, TG4 Player, and Virgin Media Player using the recent L3 decryptor. Only works on Windows. This script requires tomer8007's [widevine-l3-decryptor](https://github.com/tomer8007/widevine-l3-decryptor/tree/ed8a97745c69b8cc0fc7f59cec9474b216b49e16).

**Update (2021-06-01): Widevine have now revoked the private key used in the decryptor, so this script will no longer work. Thank you for your interest.**

<s>**Update (2021-03-28): Google have patched the decryptor in Chrome version 89 and above. You must downgrade Chrome to version 88 or below to use this script.**</s>

# Prerequisites
1. `pip install -r requirements.txt`

2. Download the Selenium Chrome WebDriver [here](https://chromedriver.chromium.org/downloads) and paste it in the rte-L3 folder. You must have Google Chrome (v88 or lower) installed and ensure that the version of the webdriver matches that of the Chrome version you have installed.

3. In the decryptor's "content_key_decryption.js" file on line 102, replace `console.log` with `document.write`.

4. In Chrome, go to the Extensions page and click "Pack extension". Enter the location of the widevine decryptor folder with the modified content_key_decryption.js.

5. Paste the outputted .crx file in the rte-L3 folder and rename it to "decryptor.crx".

# How to use
To download one video:

`python rtel3.py "URL"`

To download multiple videos in one command:

`python rtel3.py "URL1" "URL2" "URL3"`

# Disclaimer
This is for educational purposes only. According to RTÉ's terms of service, "You may not broadcast, copy, download, frame, reproduce, republish, post, transmit, merge, edit, adapt, resell, re-use, produce summaries or otherwise use RTÉ.ie and/or its content in any way **except for your own personal, non-commercial, non- business use**." Use at your own risk.
