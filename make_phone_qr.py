r"""Make a QR code PNG of the Jarvis web page address on the tailnet, to scan with the phone.

    <base python> <workspace>\make_phone_qr.py [--open] [--out PATH] [--ip IP] [--port N] [--https-host NAME]

    --https-host YOUR-PC.YOUR-TAILNET.ts.net  makes the QR for the Tailscale Serve HTTPS address
    (https://NAME/?token=...), which is the one to use for the installable phone app.

!! SECURITY: phone_qr.png CONTAINS THE WEB TOKEN (the page's password). Delete it right after scanning
!! (the token itself stays valid until you run `python -m jarvis web-token --rotate`). Do not share or
!! sync it. The link only works for devices on your private Tailscale network.

The token is read from the same file Jarvis uses (default ~\.jarvis_web_token, override
with env JARVIS_WEB_TOKEN_FILE). It is never printed. QR library: qrcode[pil] installed into the
throwaway folder <workspace>\qrvenv (use the base interpreter; the venv's own python.exe is
blocked on this machine, so its site-packages is added to the path here).
--open opens the PNG in the default image viewer.
"""

import argparse
import os
import site
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
site.addsitedir(str(HERE / "qrlib314"))

DEFAULT_IP = ""  # this PC's Tailscale address; empty = ask `tailscale ip -4` (or pass --ip)
DEFAULT_PORT = 47823
DEFAULT_TOKEN_FILE = Path.home() / ".jarvis_web_token"
DEFAULT_OUT = HERE / "phone_qr.png"


def build_url(token: str, ip: str = DEFAULT_IP, port: int = DEFAULT_PORT) -> str:
    return f"http://{ip}:{port}/?token={token}"


def read_token() -> str:
    path = Path(os.environ.get("JARVIS_WEB_TOKEN_FILE") or DEFAULT_TOKEN_FILE)
    try:
        tok = path.read_text(encoding="utf-8").strip()
    except OSError:
        tok = ""
    if not tok:
        sys.exit(f"No token in {path}. Start Jarvis once (or run `python -m jarvis web-token --rotate`).")
    return tok


def make_png(url: str, out: Path) -> None:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M

    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(out)


def detect_tailnet_ip() -> str:
    """This PC's Tailscale IPv4 address from `tailscale ip -4`; exits with a hint when it cannot be found."""
    import shutil
    import subprocess
    exe = shutil.which("tailscale")
    if exe:
        try:
            out = subprocess.run([exe, "ip", "-4"], capture_output=True, text=True, timeout=10).stdout.split()
            if out:
                return out[0]
        except (OSError, subprocess.SubprocessError):
            pass
    sys.exit("Could not find this PC's Tailscale address. Install/start Tailscale, or pass --ip 100.x.y.z.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--open", action="store_true", help="open the PNG in the default image viewer")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--ip", default=DEFAULT_IP)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--https-host", default="", help="Tailscale Serve MagicDNS name: use https://NAME/ instead of http://IP:PORT/")
    args = ap.parse_args()
    ip = args.ip or ("" if args.https_host else detect_tailnet_ip())
    url = f"https://{args.https_host}/?token={read_token()}" if args.https_host else build_url(read_token(), ip, args.port)
    make_png(url, args.out)
    print(f"Wrote {args.out} (contains the web token: DELETE it after scanning).")
    if args.open:
        if hasattr(os, "startfile"):
            os.startfile(str(args.out))  # noqa: S606 - default image viewer (Windows)
        else:  # macOS: open, Linux: xdg-open (untested)
            import subprocess
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(args.out)])


if __name__ == "__main__":
    main()
