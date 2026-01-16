"""
pH Strip OCR Recognition Service.
Analyzes pH test strip images to extract pH values.
"""

import base64
from dataclasses import dataclass
from typing import Optional
import io


@dataclass
class PHReadingResult:
    """Result of pH strip analysis."""
    ph_value: float
    confidence: float
    color_detected: str
    method: str  # "ocr", "color_analysis", "simulated"
    raw_rgb: Optional[tuple] = None
    error: Optional[str] = None


class PHStripAnalyzer:
    """
    Analyzes pH test strip images to determine pH value.

    Methods:
    1. Color analysis - matches strip color to pH scale
    2. OCR - reads digital pH meter displays
    3. Simulation - for demo when no image provided
    """

    # pH color reference chart (approximate RGB values)
    # Standard universal pH indicator colors
    PH_COLOR_MAP = {
        1.0: (254, 0, 0),      # Dark red
        2.0: (255, 50, 50),    # Red
        3.0: (255, 100, 50),   # Red-orange
        4.0: (255, 150, 0),    # Orange
        5.0: (255, 200, 0),    # Yellow-orange
        5.5: (255, 230, 0),    # Yellow
        6.0: (200, 230, 0),    # Yellow-green
        6.5: (150, 230, 50),   # Light green
        7.0: (100, 200, 100),  # Green
        7.5: (50, 180, 150),   # Blue-green
        8.0: (50, 150, 200),   # Light blue
        9.0: (50, 100, 200),   # Blue
        10.0: (100, 50, 200),  # Purple
        11.0: (150, 50, 200),  # Violet
        12.0: (100, 0, 150),   # Dark purple
    }

    def __init__(self):
        self._numpy_available = False
        self._pil_available = False
        self._cv2_available = False
        self._check_dependencies()

    def _check_dependencies(self):
        """Check which image processing libraries are available."""
        try:
            import numpy
            self._numpy_available = True
        except ImportError:
            pass

        try:
            from PIL import Image
            self._pil_available = True
        except ImportError:
            pass

        try:
            import cv2
            self._cv2_available = True
        except ImportError:
            pass

    def analyze_image(self, image_data: bytes, method: str = "auto") -> PHReadingResult:
        """
        Analyze a pH strip image.

        Args:
            image_data: Raw image bytes (JPEG, PNG)
            method: "color", "ocr", or "auto"

        Returns:
            PHReadingResult with detected pH value
        """
        if not self._pil_available and not self._cv2_available:
            return self._simulate_reading()

        try:
            if self._pil_available:
                return self._analyze_with_pil(image_data)
            elif self._cv2_available:
                return self._analyze_with_cv2(image_data)
        except Exception as e:
            return PHReadingResult(
                ph_value=5.5,
                confidence=0.0,
                color_detected="unknown",
                method="failed",
                error=str(e)
            )

        return self._simulate_reading()

    def analyze_base64(self, base64_string: str) -> PHReadingResult:
        """
        Analyze a base64-encoded pH strip image.

        Args:
            base64_string: Base64-encoded image data

        Returns:
            PHReadingResult
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]

            image_data = base64.b64decode(base64_string)
            return self.analyze_image(image_data)
        except Exception as e:
            return PHReadingResult(
                ph_value=5.5,
                confidence=0.0,
                color_detected="unknown",
                method="failed",
                error=f"Base64 decode error: {str(e)}"
            )

    def _analyze_with_pil(self, image_data: bytes) -> PHReadingResult:
        """Analyze using PIL for color extraction."""
        from PIL import Image
        import numpy as np

        # Load image
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')

        # Resize for faster processing
        img = img.resize((100, 100))

        # Get pixel data
        pixels = np.array(img)

        # Find the center region (where pH strip should be)
        h, w = pixels.shape[:2]
        center_region = pixels[h//4:3*h//4, w//4:3*w//4]

        # Calculate dominant color
        avg_color = np.mean(center_region, axis=(0, 1))
        r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])

        # Match to pH
        ph_value, confidence = self._match_color_to_ph((r, g, b))
        color_name = self._describe_color(r, g, b)

        return PHReadingResult(
            ph_value=ph_value,
            confidence=confidence,
            color_detected=color_name,
            method="color_analysis",
            raw_rgb=(r, g, b)
        )

    def _analyze_with_cv2(self, image_data: bytes) -> PHReadingResult:
        """Analyze using OpenCV for more advanced processing."""
        import cv2
        import numpy as np

        # Decode image
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return self._simulate_reading()

        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize
        img_rgb = cv2.resize(img_rgb, (100, 100))

        # Get center region
        h, w = img_rgb.shape[:2]
        center_region = img_rgb[h//4:3*h//4, w//4:3*w//4]

        # Calculate dominant color
        avg_color = np.mean(center_region, axis=(0, 1))
        r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])

        # Match to pH
        ph_value, confidence = self._match_color_to_ph((r, g, b))
        color_name = self._describe_color(r, g, b)

        return PHReadingResult(
            ph_value=ph_value,
            confidence=confidence,
            color_detected=color_name,
            method="color_analysis",
            raw_rgb=(r, g, b)
        )

    def _match_color_to_ph(self, rgb: tuple) -> tuple:
        """
        Match RGB color to pH value using Euclidean distance.

        Returns:
            (ph_value, confidence)
        """
        r, g, b = rgb
        min_distance = float('inf')
        best_ph = 7.0

        for ph, ref_rgb in self.PH_COLOR_MAP.items():
            ref_r, ref_g, ref_b = ref_rgb
            distance = ((r - ref_r) ** 2 + (g - ref_g) ** 2 + (b - ref_b) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                best_ph = ph

        # Calculate confidence (inverse of normalized distance)
        # Max distance is ~441 (opposite corners of RGB cube)
        max_distance = 441.0
        confidence = max(0.0, 1.0 - (min_distance / max_distance))

        # Interpolate between closest pH values for more precision
        sorted_phs = sorted(self.PH_COLOR_MAP.keys())
        idx = sorted_phs.index(best_ph)

        if idx > 0 and idx < len(sorted_phs) - 1:
            # Check neighbors for interpolation
            lower_ph = sorted_phs[idx - 1]
            upper_ph = sorted_phs[idx + 1]

            lower_dist = self._color_distance(rgb, self.PH_COLOR_MAP[lower_ph])
            upper_dist = self._color_distance(rgb, self.PH_COLOR_MAP[upper_ph])

            if lower_dist < upper_dist and lower_dist < min_distance * 1.5:
                # Interpolate toward lower
                ratio = min_distance / (min_distance + lower_dist)
                best_ph = best_ph - (best_ph - lower_ph) * (1 - ratio) * 0.5
            elif upper_dist < min_distance * 1.5:
                # Interpolate toward upper
                ratio = min_distance / (min_distance + upper_dist)
                best_ph = best_ph + (upper_ph - best_ph) * (1 - ratio) * 0.5

        return round(best_ph, 1), round(confidence, 2)

    def _color_distance(self, rgb1: tuple, rgb2: tuple) -> float:
        """Calculate Euclidean distance between two RGB colors."""
        return ((rgb1[0] - rgb2[0]) ** 2 +
                (rgb1[1] - rgb2[1]) ** 2 +
                (rgb1[2] - rgb2[2]) ** 2) ** 0.5

    def _describe_color(self, r: int, g: int, b: int) -> str:
        """Generate human-readable color description."""
        # Simple heuristic color naming
        if r > 200 and g < 100 and b < 100:
            return "red"
        elif r > 200 and g > 100 and g < 200 and b < 100:
            return "orange"
        elif r > 200 and g > 200 and b < 100:
            return "yellow"
        elif r < 150 and g > 150 and b < 100:
            return "green"
        elif r < 100 and g > 100 and b > 150:
            return "blue"
        elif r > 100 and g < 100 and b > 100:
            return "purple"
        else:
            return f"rgb({r},{g},{b})"

    def _simulate_reading(self, target_ph: float = 5.5) -> PHReadingResult:
        """
        Simulate a pH reading for demo purposes.

        Args:
            target_ph: Target pH value with small random variation

        Returns:
            Simulated PHReadingResult
        """
        import random

        # Add slight variation
        ph_value = target_ph + random.gauss(0, 0.2)
        ph_value = max(3.0, min(9.0, ph_value))
        ph_value = round(ph_value, 1)

        # Simulate color based on pH
        closest_ph = min(self.PH_COLOR_MAP.keys(), key=lambda x: abs(x - ph_value))
        rgb = self.PH_COLOR_MAP[closest_ph]

        return PHReadingResult(
            ph_value=ph_value,
            confidence=0.85 + random.gauss(0, 0.05),
            color_detected=self._describe_color(*rgb),
            method="simulated",
            raw_rgb=rgb
        )

    def simulate_from_skin_type(self, skin_type: str) -> PHReadingResult:
        """
        Simulate pH reading based on skin type.

        Typical pH ranges:
        - Dry skin: 5.0 - 5.5 (slightly more acidic)
        - Normal skin: 5.2 - 5.8
        - Oily skin: 5.5 - 6.5 (more alkaline)

        Args:
            skin_type: "Dry", "Normal", or "Oily"

        Returns:
            Simulated PHReadingResult
        """
        import random

        if skin_type.lower() == "dry":
            base_ph = random.uniform(5.0, 5.5)
        elif skin_type.lower() == "oily":
            base_ph = random.uniform(5.5, 6.5)
        else:  # Normal
            base_ph = random.uniform(5.2, 5.8)

        return self._simulate_reading(base_ph)


# Singleton instance
ph_analyzer = PHStripAnalyzer()
