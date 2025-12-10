#!/usr/bin/env python3
"""
Screen capture and API test script.

Captures full screen and sends to /analyze_screen endpoint.
"""

import time
import requests
from mss import mss
from PIL import Image
from io import BytesIO
import json


API_URL = "http://127.0.0.1:8000/api/v1/analyze_screen"


def capture_screen() -> bytes:
    """Capture full screen and return as PNG bytes."""
    with mss() as sct:
        # Capture primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)

        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

        # Save to bytes
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


def main():
    """Main test function."""
    print("=" * 70)
    print("SCREEN CAPTURE & API TEST")
    print("=" * 70)
    print()
    print(f"Target API: {API_URL}")
    print()
    print("Capturing screen in 3 seconds...")
    print("(Switch to the window you want to analyze)")
    print()

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("Capturing...")
    img_bytes = capture_screen()
    print(f"[OK] Captured {len(img_bytes)} bytes")
    print()

    print("Sending to API...")
    try:
        files = {"file": ("screenshot.png", img_bytes, "image/png")}
        response = requests.post(API_URL, files=files, timeout=30)

        print(f"Status: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("=" * 70)
            print("ANALYSIS RESULT")
            print("=" * 70)
            print()
            print(f"Summary: {result.get('summary', 'N/A')}")
            print()
            print(f"Elements detected: {len(result.get('elements', []))}")
            for i, elem in enumerate(result.get('elements', [])[:5], 1):
                print(f"  {i}. {elem.get('type', '?')}: {elem.get('text', 'N/A')}")
            print()
            print(f"Processing time: {result.get('processing_time', 0):.2f}s")
            print()

            # Save full result
            with open("last_analysis.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("[OK] Full result saved to: last_analysis.json")

        else:
            print("[ERROR] API returned error:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to API")
        print("Make sure the server is running:")
        print("  cd C:/Users/07013/Desktop/vlm-gui-automation/backend")
        print("  C:/Users/07013/miniconda3/envs/vlm-gui/python.exe -m uvicorn main:app --reload")
    except requests.exceptions.Timeout:
        print("[ERROR] API request timed out")
        print("VLM inference may be taking longer than expected")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
