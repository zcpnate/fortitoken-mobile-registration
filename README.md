Fortinet Token Registration
===========================

This script will emulate [FortiToken Mobile](https://play.google.com/store/apps/details?id=com.fortinet.android.ftm) to "register" a token, converting it into a raw TOTP code you can import into any other application, including a password manager.

Example:

```bash
$ python3 register-token.py EEAEVVEYZSERRHEM --mobile-id e248e1e9527f20ff
Token registered: 986f4ba5ea241a9dce10cc14e4c142b248999ed9 (base32: TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ)
To generate a token now, run: oathtool --totp 986f4ba5ea241a9dce10cc14e4c142b248999ed9

otpauth://totp/FortiToken:Mobile?secret=TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ&issuer=FortiToken&period=30
```

Mobile ID Auto-Generation
--------------------------

If you don't provide a mobile ID with `--mobile-id`, the script will automatically generate one for you:

```bash
$ python3 register-token.py EEAEVVEYZSERRHEM
Generated new Mobile ID: a1b2c3d4e5f6g7h8
This has been saved to config.txt. Please keep it safe if you want to be able to re-register your token again.
Token registered: 986f4ba5ea241a9dce10cc14e4c142b248999ed9 (base32: TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ)
...
```

The generated mobile ID is:

- **Automatically saved** to `config.txt` for future use
- **Reused automatically** on subsequent runs (if `config.txt` exists)
- **Required for re-registration** if you ever need to register the same token again

**Important**: Keep the `config.txt` file safe! If you lose it, you won't be able to re-register the same token with the same mobile ID.

FortiGate Compatibility
-----------------------

For FortiGate compatibility, use the `--fortigate` flag to set the TOTP period to 60 seconds instead of the default 30 seconds:

```bash
$ python3 register-token.py EEAEVVEYZSERRHEM --fortigate
Token registered: 986f4ba5ea241a9dce10cc14e4c142b248999ed9 (base32: TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ)
To generate a token now, run: oathtool --totp 986f4ba5ea241a9dce10cc14e4c142b248999ed9

otpauth://totp/FortiToken:Mobile?secret=TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ&issuer=FortiToken&period=60
```

QR Code Support
---------------

You can generate a QR code for easy import into authenticator apps by adding the `--qr` flag:

```bash
$ python3 register-token.py EEAEVVEYZSERRHEM --qr
Token registered: 986f4ba5ea241a9dce10cc14e4c142b248999ed9 (base32: TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ)
To generate a token now, run: oathtool --totp 986f4ba5ea241a9dce10cc14e4c142b248999ed9

otpauth://totp/FortiToken:Mobile?secret=TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ&issuer=FortiToken&period=30

QR Code:
█▀▀▀▀▀█ ▀▄▀█ ▀ █▀▀▀▀▀█
█ ███ █ ██▄█▄▄█ █ ███ █
█ ▀▀▀ █ ▀█▄ █▀▄ █ ▀▀▀ █
▀▀▀▀▀▀▀ ▀▄█▄█▄█ ▀▀▀▀▀▀▀
█▀█▀█▀▀▄▄▄ ▀█▀█▄▄█▄▄▄▀█
▄█ ▄▀ ▀▄█▄█▄▀▄▀▄█▄█▀▄▄█
█▀▀▀▀▀█ █ ▀█▄▄█ ▀ ▀█▄▀▄
█ ███ █ ▄▀▄▀█▄▄█▀██▄█▄█
█ ▀▀▀ █ ▀█▄▀ ▀▀█▄▀▄▄▀▄█
▀▀▀▀▀▀▀ ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
```

You can also combine both flags for FortiGate-compatible tokens with QR codes:

```bash
python3 register-token.py EEAEVVEYZSERRHEM --fortigate --qr
```

The QR code can be scanned by any authenticator app including:

- 1Password
- Google Authenticator  
- Microsoft Authenticator
- Authy
- And many others

Automatic FortiGate Detection
-----------------------------

The script can automatically detect FortiGate tokens based on their prefix and set the appropriate 60-second period:

```bash
$ python3 register-token.py EEAEVVEYZSERRHEM
Auto-detected FortiGate token - using 60-second period
Token registered: 986f4ba5ea241a9dce10cc14e4c142b248999ed9 (base32: TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ)
To generate a token now, run: oathtool --totp 986f4ba5ea241a9dce10cc14e4c142b248999ed9

otpauth://totp/FortiToken:Mobile?secret=TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ&issuer=FortiToken&period=60
```

The detection works by analyzing the token prefix:

- `\x21\x00`: Standard FortiToken (30-second period)
- `\x21\x10`: FortiGate token (60-second period)

You can disable automatic detection if needed:

```bash
python3 register-token.py EEAEVVEYZSERRHEM --no-auto-detect
```

Or override it by explicitly using `--fortigate`:

```bash
python3 register-token.py EEAEVVEYZSERRHEM --fortigate
```

Verbose Mode
------------

Use the `--verbose` (or `-v`) flag to see detailed information about the token parsing and registration process:

```bash
$ python3 register-token.py -v EEAEVVEYZSERRHEM
INFO: Starting FortiToken registration process
INFO: Parsing base32 token: EEAEVVEYZSERRHEM
DEBUG: Raw token bytes: 210010aa15964912211a
DEBUG: Raw token length: 10 bytes
DEBUG: Token prefix: 2100
INFO: Token prefix indicates standard FortiToken format
DEBUG: Token data (without prefix): 10aa15964912211a
INFO: Using existing Mobile ID from config.txt: a1b2c3d4e5f6g7h8
INFO: Registering token with FortiNet servers...
DEBUG: Token bytes: 10aa15964912211a
DEBUG: Request payload: {'mobile_id': 'a1b2c3d4e5f6g7h8', '__type': 'SoftToken.MobileProvisionRequest', 'token_activation_code': '10aa15964912211a'}
DEBUG: Response status code: 200
INFO: Token registration successful
DEBUG: Encrypted seed received: [encrypted_data]
DEBUG: Final TOTP seed: 986f4ba5ea241a9dce10cc14e4c142b248999ed9
INFO: Using period: 30 seconds (Standard mode)
Token registered: 986f4ba5ea241a9dce10cc14e4c142b248999ed9 (base32: TBXUXJPKEQNJ3TQQZQKOJQKCWJEJTHWZ)
...
```

Verbose mode is helpful for:

- **Debugging token parsing issues**
- **Understanding the registration process**
- **Verifying automatic FortiGate detection**
- **Troubleshooting connection problems**

You can combine verbose mode with other flags:

```bash
# Verbose with QR code
python3 register-token.py -v --qr EEAEVVEYZSERRHEM

# Verbose with manual FortiGate mode
python3 register-token.py -v --fortigate EEAEVVEYZSERRHEM
```

Installation
------------

Set up a virtual environment, install the dependencies, and run it:

```sh
python3 -mvenv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

What does registration mean?
----------------------------

FortiToken allows you to register a token once. The first mobile device that registers a token is bound to it and no one else can use the registration token unless it is transfered to another user by the person who first registered it.
This is done through a unique identifier Android assigns to each device. This means if we are careful, we can pick an ID once and re-use it so the token can be recovered or transfered in future.
If you want to maintain compatibility with your real mobile phone, simply use the same ID as your phone already has:

```sh
android:/ # cat /data/system/users/0/settings_ssaid.xml | grep com.fortinet.android.ftm
  <setting id="19" name="10187" value="e248e1e9527f20ff" package="com.fortinet.android.ftm" defaultValue="e248e1e9527f20ff" defaultSysSet="false" tag="null" />
```

By using this ID (`e248e1e9527f20ff`), we can transfer a token using the real application on a phone.

References
----------

<https://jonstoler.me/blog/extracting-fortitoken-mobile-totp-secret>
