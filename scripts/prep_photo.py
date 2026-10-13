"""Isolate Edson's supplied portrait, crop it, and boost grayscale detail.

The foreground seeds below match profile-photo.jpg; adjust them for a new photo.
No model download or background-removal service is required.
"""

from pathlib import Path
import argparse

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def prepare(source, output):
    rgb = np.array(ImageOps.exif_transpose(Image.open(source)).convert("RGB"))
    height, width = rgb.shape[:2]
    # Coordinates are normalized to the original 960 x 1280 photo.
    scale = np.array([width / 960, height / 1280])
    outline = np.array([
        [216, 456], [244, 385], [330, 341], [453, 327], [525, 333],
        [587, 381], [589, 449], [566, 512], [594, 567], [584, 635],
        [640, 676], [670, 755], [804, 808], [866, 871], [941, 1070],
        [959, 1279], [131, 1279], [102, 1110], [93, 966], [128, 876],
        [185, 827], [236, 806], [244, 728], [264, 665], [247, 589],
        [248, 524],
    ])
    mask = np.full((height, width), cv2.GC_BGD, dtype=np.uint8)
    cv2.fillPoly(mask, [(outline * scale).astype(np.int32)], cv2.GC_PR_FGD)
    cv2.ellipse(mask, tuple((np.array([421, 580]) * scale).astype(int)),
                tuple((np.array([119, 210]) * scale).astype(int)),
                -8, 0, 360, cv2.GC_FGD, -1)
    cv2.rectangle(mask, tuple((np.array([315, 880]) * scale).astype(int)),
                  tuple((np.array([745, 1260]) * scale).astype(int)), cv2.GC_FGD, -1)
    cv2.setRNGSeed(7)
    cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, None,
                np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64),
                5, cv2.GC_INIT_WITH_MASK)
    foreground = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
    foreground = cv2.GaussianBlur(foreground, (3, 3), 0) / 255.0
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8)).apply(gray)
    gray = np.clip((gray.astype(float) - 25) * 1.18, 0, 255)
    composed = (gray * foreground + 255 * (1 - foreground)).astype("uint8")
    # Focus on the face and shoulders; omit the busy lettering on the hoodie.
    crop = tuple(int(v) for v in np.array([85, 303, 950, 1105]) * np.tile(scale, 2))
    Image.fromarray(composed).crop(crop).save(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=ROOT / "profile-photo.jpg")
    parser.add_argument("--output", type=Path, default=ROOT / "data/source-prepped.png")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    prepare(args.source, args.output)
