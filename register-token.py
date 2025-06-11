from requests_pkcs12 import Pkcs12Adapter  # type: ignore
import requests
import argparse
import base64
from pathlib import Path
import uuid
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import qrcode  # type: ignore


def register_token(token: bytes, mobile_id: str) -> bytes:
    # We use the PKCS12 certificate directly from the Fortitoken application
    s = requests.Session()
    s.mount(
        "https://globalftm.fortinet.net",
        Pkcs12Adapter(pkcs12_filename="ftm.ks", pkcs12_password="Terran2023"),
    )

    # Prepare our payload
    payload = {
        "mobile_id": mobile_id,
        "__type": "SoftToken.MobileProvisionRequest",
        "token_activation_code": token.hex(),
    }

    r = s.post(
        "https://globalftm.fortinet.net/SoftToken/Provisioning.asmx/Mobile",
        json={"d": payload},
    )

    if r.status_code != 200:
        print(r.text, file=sys.stderr)
        raise Exception("Error from globalftm.fortinet.net")

    response = r.json()["d"]
    if "error" in response and response["error"] is not None:
        print(response["error"], file=sys.stderr)
        raise Exception("Could not register token")

    # TODO: Additional verification, such as mobile_id_hash
    return decrypt_seed(response["seed"], mobile_id)


def decrypt_seed(encrypted_seed, mobile_id):
    # IV must be exactly 16 bytes for AES CBC mode
    iv_string = "fortitokenmobile"
    iv = iv_string.ljust(16, "\x00").encode("utf-8")  # Pad to exactly 16 bytes

    # Ensure mobile_id is exactly 16 bytes for AES-128
    key = bytes(mobile_id, "utf-8")
    if len(key) != 16:
        # Pad or truncate to 16 bytes
        key = key[:16].ljust(16, b"\x00")

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = (
        decryptor.update(base64.b64decode(encrypted_seed)) + decryptor.finalize()
    )
    decrypted_truncated = decrypted[0:40]  # Truncate trailing null bytes
    return bytes.fromhex(decrypted_truncated.decode("utf-8"))


def parse_token(token):
    raw_token = base64.b32decode(token)
    if raw_token[0:2] not in [b"\x21\x00", b"\x21\x10"]:
        # Tokens may start with \x21\x00 or \x21\x10, likely version identifiers
        print(f"Token did not begin with expected prefix, got: {raw_token[0:2].hex()}")
    if len(raw_token) != 10:
        print(f"Token was not 10 bytes, got: {len(raw_token)} bytes")
    return raw_token[2:]


def parse_raw_token(token):
    raw_token = bytes.fromhex(token)

    if len(raw_token) != 8:
        print("Decoded token was not 8 bytes")

    return raw_token


def get_mobile_id():
    p = Path("config.txt")
    if not p.is_file():
        mobile_id = uuid.uuid4().hex[0:16]
        print(f"Generated new Mobile ID: {mobile_id}")
        print(
            "This has been saved to config.txt. Please keep it safe if you want to be able to re-register your token again."
        )
        p.write_text(mobile_id)
    return p.read_text()


def generate_qr_code(otpauth_url):
    """Generate and display QR code in terminal"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(otpauth_url)
    qr.make(fit=True)
    qr.print_ascii()


def main(args):
    if not args.raw_token:
        token = parse_token(args.token)
    else:
        token = parse_raw_token(args.token)

    if args.mobile_id:
        mobile_id = args.mobile_id
    else:
        mobile_id = get_mobile_id()

    totp = register_token(token, mobile_id)
    base32_secret = base64.b32encode(totp).decode("utf-8")
    period = 60 if args.fortigate else 30
    otpauth_url = f"otpauth://totp/FortiToken:Mobile?secret={base32_secret}&issuer=FortiToken&period={period}"

    print(f"Token registered: {totp.hex()} (base32: {base32_secret})")
    print(f"To generate a token now, run: oathtool --totp {totp.hex()}")
    print()
    print(otpauth_url)

    if args.qr:
        print()
        print("QR Code:")
        generate_qr_code(otpauth_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "token", help="Base32 encoded token data, e.g. EEAEVVEYZSERRHEM"
    )
    parser.add_argument("-m", "--mobile-id", default=None)
    parser.add_argument(
        "-r",
        "--raw-token",
        action=argparse.BooleanOptionalAction,
        help="Parse the token as raw hexadecimal bytes with no prefix, e.g. 7A2AAEE00A56C569",
    )
    parser.add_argument(
        "-qr",
        "--qr",
        action="store_true",
        help="Generate and display QR code in terminal for easy import into authenticator apps",
    )
    parser.add_argument(
        "--fortigate",
        action="store_true",
        help="Use 60-second period for FortiGate compatibility (default: 30 seconds)",
    )

    args = parser.parse_args()
    main(args)
