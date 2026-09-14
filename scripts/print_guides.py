"""Export guide HTML to PDF with an installed Chrome/Chromium browser."""

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


def export(directory, browser):
    for name in ("assembly", "colouring"):
        source = directory / f"{name}.html"
        target = directory / f"{name}.pdf"
        if target.exists():
            print(f"Keeping existing {target}", flush=True)
            continue
        with tempfile.TemporaryDirectory(prefix="mosaic-print-") as profile:
            process = subprocess.Popen(
                [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                 f"--user-data-dir={profile}", f"--print-to-pdf={target}", source.as_uri()],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                # Some Chrome builds keep running after writing their PDF.
                for _ in range(100):
                    if target.exists() and target.read_bytes().rstrip().endswith(b"%%EOF"):
                        print(target, flush=True)
                        break
                    if process.poll() is not None:
                        raise RuntimeError(f"Browser exited before exporting {target}")
                    time.sleep(.25)
                else:
                    raise RuntimeError(f"PDF export timed out: {target}")
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+")
    parser.add_argument("--browser", default=shutil.which("chromium") or shutil.which("google-chrome")
                        or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    args = parser.parse_args()
    for directory in args.directories:
        export(Path(directory).resolve(), args.browser)
