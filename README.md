# rte-L3
Script to download from the RTÉ Player using the recent L3 decryptor. Only works on Windows. Decryptor is not included.

# Prerequisites

1. `pip install -r requirements.txt`

2. In the "content_key_decryption.js" file on line 102, replace it with `document.write("WidevineDecryptor: Found key: " + toHexString(decryptedKey) + " (KID=" + toHexString(keyId) + ")");`.

# How to use
`rtel3.py "URL"`

# Disclaimer
This is for educational purposes only. Downloading copyrighted material from streaming services may violate their Terms of Service. Use at your own risk.
