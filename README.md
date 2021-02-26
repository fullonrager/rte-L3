# rte-L3
Script to download from the RTÉ Player, TG4 Player, and Virgin Media Player using the recent L3 decryptor. Only works on Windows. This script requires tomer8007's [widevine-l3-decryptor](https://github.com/tomer8007/widevine-l3-decryptor/tree/ed8a97745c69b8cc0fc7f59cec9474b216b49e16).

# Prerequisites
1. `pip install -r requirements.txt`

2. Download the Selenium Chrome WebDriver [here](https://chromedriver.chromium.org/downloads) and paste it in the rte-L3 folder. You must have Google Chrome installed and ensure that the version of the webdriver matches that of the Chrome version you have installed.

3. In the decryptor's "content_key_decryption.js" file on line 102, replace it with `document.write("WidevineDecryptor: Found key: " + toHexString(decryptedKey) + " (KID=" + toHexString(keyId) + ")");`.

4. In Chrome, go to the Extensions page and click "Pack extension". Enter the location of the widevine decryptor folder with the modified content_key_decryption.js.

5. Paste the outputted .crx file in the rte-L3 folder and rename it to "decryptor.crx".

# How to use
`python rtel3.py "URL"`

# Disclaimer
This is for educational purposes only. According to RTÉ's terms of service, "You may not broadcast, copy, download, frame, reproduce, republish, post, transmit, merge, edit, adapt, resell, re-use, produce summaries or otherwise use RTÉ.ie and/or its content in any way **except for your own personal, non-commercial, non- business use**." Use at your own risk.
