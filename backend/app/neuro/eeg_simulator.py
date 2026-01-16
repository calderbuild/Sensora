"""
EEG Signal Simulator for Demo and Testing.
Generates realistic valence-arousal signals based on user input patterns.
"""

import random
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class EEGSignal:
    """Processed EEG signal with valence-arousal mapping."""
    valence: float  # -1 (negative) to 1 (positive)
    arousal: float  # 0 (calm) to 1 (excited)
    confidence: float  # 0 to 1
    raw_alpha: float  # Alpha band power (8-13 Hz)
    raw_beta: float  # Beta band power (13-30 Hz)
    raw_theta: float  # Theta band power (4-8 Hz)
    timestamp: float
    emotion_label: str


class EEGSimulator:
    """
    Simulates EEG signals for demo purposes.

    Based on the circumplex model of affect:
    - Valence: frontal alpha asymmetry (F3-F4)
    - Arousal: beta/alpha ratio

    Real EEG processing would use MNE-Python with actual electrode data.
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self._baseline_alpha = 10.0  # microvolts
        self._baseline_beta = 5.0
        self._baseline_theta = 8.0

    def simulate_from_text(self, text_input: str) -> EEGSignal:
        """
        Simulate EEG response based on text emotional content.

        Uses keyword analysis to generate plausible EEG patterns.

        Args:
            text_input: User's scent description or emotional prompt

        Returns:
            Simulated EEGSignal
        """
        text_lower = text_input.lower()

        # Keyword-based emotion detection
        valence_score = 0.0
        arousal_score = 0.5  # Neutral baseline

        # Positive valence keywords
        positive_keywords = {
            'happy': 0.3, 'joy': 0.35, 'love': 0.4, 'beautiful': 0.25,
            'fresh': 0.2, 'bright': 0.2, 'warm': 0.15, 'soft': 0.1,
            'peaceful': 0.25, 'calm': 0.2, 'serene': 0.25, 'gentle': 0.15,
            'sweet': 0.2, 'romantic': 0.3, 'dreamy': 0.2, 'cozy': 0.2,
            'spring': 0.2, 'summer': 0.15, 'morning': 0.15, 'sunshine': 0.25,
            'garden': 0.15, 'flowers': 0.2, 'rain': 0.1, 'ocean': 0.15
        }

        # Negative valence keywords
        negative_keywords = {
            'sad': -0.3, 'dark': -0.15, 'cold': -0.1, 'lonely': -0.25,
            'intense': -0.1, 'mysterious': -0.05, 'deep': -0.05,
            'smoky': -0.1, 'heavy': -0.15
        }

        # High arousal keywords
        high_arousal_keywords = {
            'energy': 0.3, 'exciting': 0.35, 'vibrant': 0.3, 'powerful': 0.25,
            'intense': 0.25, 'bold': 0.2, 'strong': 0.2, 'spicy': 0.15,
            'citrus': 0.15, 'electric': 0.3, 'party': 0.3, 'dance': 0.25
        }

        # Low arousal keywords
        low_arousal_keywords = {
            'calm': -0.25, 'peaceful': -0.3, 'relaxing': -0.35, 'quiet': -0.2,
            'soft': -0.15, 'gentle': -0.2, 'meditative': -0.35, 'sleep': -0.4,
            'tranquil': -0.3, 'serene': -0.3, 'evening': -0.15, 'night': -0.2
        }

        # Calculate scores
        for word, score in positive_keywords.items():
            if word in text_lower:
                valence_score += score

        for word, score in negative_keywords.items():
            if word in text_lower:
                valence_score += score

        for word, score in high_arousal_keywords.items():
            if word in text_lower:
                arousal_score += score

        for word, score in low_arousal_keywords.items():
            if word in text_lower:
                arousal_score += score

        # Clamp values
        valence = max(-1.0, min(1.0, valence_score))
        arousal = max(0.0, min(1.0, arousal_score))

        # Add slight noise for realism
        valence += random.gauss(0, 0.05)
        arousal += random.gauss(0, 0.03)

        valence = max(-1.0, min(1.0, valence))
        arousal = max(0.0, min(1.0, arousal))

        return self._generate_signal(valence, arousal)

    def simulate_random(self, quadrant: Optional[str] = None) -> EEGSignal:
        """
        Generate random EEG signal, optionally constrained to a quadrant.

        Args:
            quadrant: Optional - "happy", "excited", "calm", "sad"

        Returns:
            Simulated EEGSignal
        """
        if quadrant == "happy":
            # High valence, low arousal
            valence = random.uniform(0.3, 0.8)
            arousal = random.uniform(0.2, 0.5)
        elif quadrant == "excited":
            # High valence, high arousal
            valence = random.uniform(0.3, 0.8)
            arousal = random.uniform(0.6, 0.9)
        elif quadrant == "calm":
            # Neutral valence, low arousal
            valence = random.uniform(-0.2, 0.3)
            arousal = random.uniform(0.1, 0.4)
        elif quadrant == "sad":
            # Low valence, low arousal
            valence = random.uniform(-0.6, -0.1)
            arousal = random.uniform(0.2, 0.5)
        else:
            # Random
            valence = random.uniform(-0.5, 0.7)
            arousal = random.uniform(0.2, 0.8)

        return self._generate_signal(valence, arousal)

    def _generate_signal(self, valence: float, arousal: float) -> EEGSignal:
        """Generate EEG signal components from valence-arousal."""
        import time

        # Simulate raw band powers based on V-A
        # Frontal alpha asymmetry correlates with valence
        # (more right alpha = positive valence)
        alpha_asymmetry = valence * 2.0  # -2 to 2 range
        raw_alpha = self._baseline_alpha * (1.0 + alpha_asymmetry * 0.2)

        # Beta/alpha ratio correlates with arousal
        beta_alpha_ratio = 0.5 + arousal * 0.8
        raw_beta = raw_alpha * beta_alpha_ratio

        # Theta increases with drowsiness (inverse arousal)
        raw_theta = self._baseline_theta * (1.5 - arousal * 0.5)

        # Add measurement noise
        raw_alpha += random.gauss(0, 0.5)
        raw_beta += random.gauss(0, 0.3)
        raw_theta += random.gauss(0, 0.4)

        # Ensure positive
        raw_alpha = max(1.0, raw_alpha)
        raw_beta = max(0.5, raw_beta)
        raw_theta = max(1.0, raw_theta)

        # Confidence based on signal quality
        confidence = 0.85 + random.gauss(0, 0.05)
        confidence = max(0.6, min(0.98, confidence))

        # Emotion label from quadrant
        emotion_label = self._get_emotion_label(valence, arousal)

        return EEGSignal(
            valence=round(valence, 3),
            arousal=round(arousal, 3),
            confidence=round(confidence, 3),
            raw_alpha=round(raw_alpha, 2),
            raw_beta=round(raw_beta, 2),
            raw_theta=round(raw_theta, 2),
            timestamp=time.time(),
            emotion_label=emotion_label
        )

    def _get_emotion_label(self, valence: float, arousal: float) -> str:
        """Map valence-arousal to emotion quadrant label."""
        if valence >= 0:
            if arousal >= 0.5:
                return "excited/happy"
            else:
                return "relaxed/content"
        else:
            if arousal >= 0.5:
                return "stressed/anxious"
            else:
                return "sad/melancholic"

    def generate_time_series(
        self,
        duration_seconds: float,
        sample_rate: int = 256,
        base_valence: float = 0.3,
        base_arousal: float = 0.5
    ) -> list[EEGSignal]:
        """
        Generate a time series of EEG signals with natural variation.

        Args:
            duration_seconds: Total duration
            sample_rate: Samples per second (typical EEG: 256 Hz)
            base_valence: Center valence value
            base_arousal: Center arousal value

        Returns:
            List of EEGSignal at regular intervals
        """
        signals = []
        num_samples = int(duration_seconds * sample_rate)

        # Generate smooth variation using sine waves
        t = np.linspace(0, duration_seconds, num_samples)

        # Slow oscillations in valence/arousal
        valence_variation = 0.1 * np.sin(2 * np.pi * 0.05 * t)  # 0.05 Hz
        arousal_variation = 0.08 * np.sin(2 * np.pi * 0.03 * t + 0.5)  # 0.03 Hz

        # Sample at 1 Hz for output (not full 256 Hz)
        output_interval = sample_rate
        for i in range(0, num_samples, output_interval):
            v = base_valence + valence_variation[i] + random.gauss(0, 0.02)
            a = base_arousal + arousal_variation[i] + random.gauss(0, 0.02)

            v = max(-1.0, min(1.0, v))
            a = max(0.0, min(1.0, a))

            signals.append(self._generate_signal(v, a))

        return signals


# Singleton instance
eeg_simulator = EEGSimulator(seed=42)
