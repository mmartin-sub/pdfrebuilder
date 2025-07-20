"""
PSD layer effects handling for the Multi-Format Document Engine.

This module provides utilities for parsing and representing PSD layer effects
in the Universal IDM format.
"""

import logging
from typing import Any

from .universal_idm import Color

logger = logging.getLogger(__name__)


class PSDEffectType:
    """Constants for PSD effect types"""

    DROP_SHADOW = "dropShadow"
    INNER_SHADOW = "innerShadow"
    OUTER_GLOW = "outerGlow"
    INNER_GLOW = "innerGlow"
    BEVEL = "bevel"
    SATIN = "satin"
    COLOR_OVERLAY = "colorOverlay"
    GRADIENT_OVERLAY = "gradientOverlay"
    PATTERN_OVERLAY = "patternOverlay"
    STROKE = "stroke"


class PSDBlendMode:
    """Constants for PSD blend modes"""

    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "softLight"
    HARD_LIGHT = "hardLight"
    COLOR_DODGE = "colorDodge"
    COLOR_BURN = "colorBurn"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"
    HUE = "hue"
    SATURATION = "saturation"
    COLOR = "color"
    LUMINOSITY = "luminosity"

    @staticmethod
    def to_universal_blend_mode(psd_blend_mode: str) -> str:
        """Convert PSD blend mode to Universal IDM blend mode"""
        # Map of PSD blend modes to Universal IDM blend modes
        blend_mode_map = {
            PSDBlendMode.NORMAL: "Normal",
            PSDBlendMode.MULTIPLY: "Multiply",
            PSDBlendMode.SCREEN: "Screen",
            PSDBlendMode.OVERLAY: "Overlay",
            PSDBlendMode.SOFT_LIGHT: "Soft Light",
            PSDBlendMode.HARD_LIGHT: "Hard Light",
            PSDBlendMode.COLOR_DODGE: "Color Dodge",
            PSDBlendMode.COLOR_BURN: "Color Burn",
            PSDBlendMode.DARKEN: "Darken",
            PSDBlendMode.LIGHTEN: "Lighten",
            PSDBlendMode.DIFFERENCE: "Difference",
            PSDBlendMode.EXCLUSION: "Exclusion",
            # These don't have direct equivalents in the Universal IDM
            PSDBlendMode.HUE: "Normal",
            PSDBlendMode.SATURATION: "Normal",
            PSDBlendMode.COLOR: "Normal",
            PSDBlendMode.LUMINOSITY: "Normal",
        }

        return blend_mode_map.get(psd_blend_mode, "Normal")


class DropShadowEffect:
    """Drop shadow effect"""

    def __init__(
        self,
        enabled: bool = True,
        blend_mode: str = PSDBlendMode.MULTIPLY,
        color: Color | None = None,
        opacity: float = 0.75,
        angle: float = 120.0,
        distance: float = 5.0,
        spread: float = 0.0,
        size: float = 5.0,
        noise: float = 0.0,
        layer_knocks_out: bool = True,
    ):
        self.enabled = enabled
        self.blend_mode = blend_mode
        self.color = color or Color(0, 0, 0)  # Default to black
        self.opacity = opacity
        self.angle = angle
        self.distance = distance
        self.spread = spread
        self.size = size
        self.noise = noise
        self.layer_knocks_out = layer_knocks_out

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.DROP_SHADOW,
            "enabled": self.enabled,
            "blend_mode": self.blend_mode,
            "color": self.color.to_rgba_tuple(),
            "opacity": self.opacity,
            "angle": self.angle,
            "distance": self.distance,
            "spread": self.spread,
            "size": self.size,
            "noise": self.noise,
            "layer_knocks_out": self.layer_knocks_out,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DropShadowEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            blend_mode=data.get("blend_mode", PSDBlendMode.MULTIPLY),
            color=Color.from_rgba_tuple(data.get("color", (0, 0, 0, 1))),
            opacity=data.get("opacity", 0.75),
            angle=data.get("angle", 120.0),
            distance=data.get("distance", 5.0),
            spread=data.get("spread", 0.0),
            size=data.get("size", 5.0),
            noise=data.get("noise", 0.0),
            layer_knocks_out=data.get("layer_knocks_out", True),
        )


class InnerShadowEffect:
    """Inner shadow effect"""

    def __init__(
        self,
        enabled: bool = True,
        blend_mode: str = PSDBlendMode.MULTIPLY,
        color: Color | None = None,
        opacity: float = 0.75,
        angle: float = 120.0,
        distance: float = 5.0,
        choke: float = 0.0,
        size: float = 5.0,
        noise: float = 0.0,
    ):
        self.enabled = enabled
        self.blend_mode = blend_mode
        self.color = color or Color(0, 0, 0)  # Default to black
        self.opacity = opacity
        self.angle = angle
        self.distance = distance
        self.choke = choke
        self.size = size
        self.noise = noise

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.INNER_SHADOW,
            "enabled": self.enabled,
            "blend_mode": self.blend_mode,
            "color": self.color.to_rgba_tuple(),
            "opacity": self.opacity,
            "angle": self.angle,
            "distance": self.distance,
            "choke": self.choke,
            "size": self.size,
            "noise": self.noise,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InnerShadowEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            blend_mode=data.get("blend_mode", PSDBlendMode.MULTIPLY),
            color=Color.from_rgba_tuple(data.get("color", (0, 0, 0, 1))),
            opacity=data.get("opacity", 0.75),
            angle=data.get("angle", 120.0),
            distance=data.get("distance", 5.0),
            choke=data.get("choke", 0.0),
            size=data.get("size", 5.0),
            noise=data.get("noise", 0.0),
        )


class OuterGlowEffect:
    """Outer glow effect"""

    def __init__(
        self,
        enabled: bool = True,
        blend_mode: str = PSDBlendMode.SCREEN,
        color: Color | None = None,
        opacity: float = 0.75,
        spread: float = 0.0,
        size: float = 5.0,
        noise: float = 0.0,
    ):
        self.enabled = enabled
        self.blend_mode = blend_mode
        self.color = color or Color(1, 1, 0)  # Default to yellow
        self.opacity = opacity
        self.spread = spread
        self.size = size
        self.noise = noise

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.OUTER_GLOW,
            "enabled": self.enabled,
            "blend_mode": self.blend_mode,
            "color": self.color.to_rgba_tuple(),
            "opacity": self.opacity,
            "spread": self.spread,
            "size": self.size,
            "noise": self.noise,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OuterGlowEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            blend_mode=data.get("blend_mode", PSDBlendMode.SCREEN),
            color=Color.from_rgba_tuple(data.get("color", (1, 1, 0, 1))),
            opacity=data.get("opacity", 0.75),
            spread=data.get("spread", 0.0),
            size=data.get("size", 5.0),
            noise=data.get("noise", 0.0),
        )


class InnerGlowEffect:
    """Inner glow effect"""

    def __init__(
        self,
        enabled: bool = True,
        blend_mode: str = PSDBlendMode.SCREEN,
        color: Color | None = None,
        opacity: float = 0.75,
        choke: float = 0.0,
        size: float = 5.0,
        noise: float = 0.0,
        source: str = "center",  # "center" or "edge"
    ):
        self.enabled = enabled
        self.blend_mode = blend_mode
        self.color = color or Color(1, 1, 0)  # Default to yellow
        self.opacity = opacity
        self.choke = choke
        self.size = size
        self.noise = noise
        self.source = source

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.INNER_GLOW,
            "enabled": self.enabled,
            "blend_mode": self.blend_mode,
            "color": self.color.to_rgba_tuple(),
            "opacity": self.opacity,
            "choke": self.choke,
            "size": self.size,
            "noise": self.noise,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InnerGlowEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            blend_mode=data.get("blend_mode", PSDBlendMode.SCREEN),
            color=Color.from_rgba_tuple(data.get("color", (1, 1, 0, 1))),
            opacity=data.get("opacity", 0.75),
            choke=data.get("choke", 0.0),
            size=data.get("size", 5.0),
            noise=data.get("noise", 0.0),
            source=data.get("source", "center"),
        )


class BevelEffect:
    """Bevel effect"""

    def __init__(
        self,
        enabled: bool = True,
        style: str = "outer_bevel",  # "outer_bevel", "inner_bevel", "emboss", "pillow_emboss"
        technique: str = "smooth",  # "smooth", "chisel_hard", "chisel_soft"
        depth: float = 100.0,
        direction: str = "up",  # "up" or "down"
        size: float = 5.0,
        soften: float = 0.0,
        angle: float = 120.0,
        altitude: float = 30.0,
        highlight_mode: str = PSDBlendMode.SCREEN,
        highlight_color: Color | None = None,
        highlight_opacity: float = 0.75,
        shadow_mode: str = PSDBlendMode.MULTIPLY,
        shadow_color: Color | None = None,
        shadow_opacity: float = 0.75,
    ):
        self.enabled = enabled
        self.style = style
        self.technique = technique
        self.depth = depth
        self.direction = direction
        self.size = size
        self.soften = soften
        self.angle = angle
        self.altitude = altitude
        self.highlight_mode = highlight_mode
        self.highlight_color = highlight_color or Color(1, 1, 1)  # Default to white
        self.highlight_opacity = highlight_opacity
        self.shadow_mode = shadow_mode
        self.shadow_color = shadow_color or Color(0, 0, 0)  # Default to black
        self.shadow_opacity = shadow_opacity

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.BEVEL,
            "enabled": self.enabled,
            "style": self.style,
            "technique": self.technique,
            "depth": self.depth,
            "direction": self.direction,
            "size": self.size,
            "soften": self.soften,
            "angle": self.angle,
            "altitude": self.altitude,
            "highlight_mode": self.highlight_mode,
            "highlight_color": self.highlight_color.to_rgba_tuple(),
            "highlight_opacity": self.highlight_opacity,
            "shadow_mode": self.shadow_mode,
            "shadow_color": self.shadow_color.to_rgba_tuple(),
            "shadow_opacity": self.shadow_opacity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BevelEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            style=data.get("style", "outer_bevel"),
            technique=data.get("technique", "smooth"),
            depth=data.get("depth", 100.0),
            direction=data.get("direction", "up"),
            size=data.get("size", 5.0),
            soften=data.get("soften", 0.0),
            angle=data.get("angle", 120.0),
            altitude=data.get("altitude", 30.0),
            highlight_mode=data.get("highlight_mode", PSDBlendMode.SCREEN),
            highlight_color=Color.from_rgba_tuple(data.get("highlight_color", (1, 1, 1, 1))),
            highlight_opacity=data.get("highlight_opacity", 0.75),
            shadow_mode=data.get("shadow_mode", PSDBlendMode.MULTIPLY),
            shadow_color=Color.from_rgba_tuple(data.get("shadow_color", (0, 0, 0, 1))),
            shadow_opacity=data.get("shadow_opacity", 0.75),
        )


class ColorOverlayEffect:
    """Color overlay effect"""

    def __init__(
        self,
        enabled: bool = True,
        blend_mode: str = PSDBlendMode.NORMAL,
        color: Color | None = None,
        opacity: float = 1.0,
    ):
        self.enabled = enabled
        self.blend_mode = blend_mode
        self.color = color or Color(1, 0, 0)  # Default to red
        self.opacity = opacity

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.COLOR_OVERLAY,
            "enabled": self.enabled,
            "blend_mode": self.blend_mode,
            "color": self.color.to_rgba_tuple(),
            "opacity": self.opacity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ColorOverlayEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            blend_mode=data.get("blend_mode", PSDBlendMode.NORMAL),
            color=Color.from_rgba_tuple(data.get("color", (1, 0, 0, 1))),
            opacity=data.get("opacity", 1.0),
        )


class StrokeEffect:
    """Stroke effect"""

    def __init__(
        self,
        enabled: bool = True,
        position: str = "outside",  # "inside", "center", "outside"
        fill_type: str = "color",  # "color", "gradient", "pattern"
        blend_mode: str = PSDBlendMode.NORMAL,
        color: Color | None = None,
        opacity: float = 1.0,
        size: float = 3.0,
    ):
        self.enabled = enabled
        self.position = position
        self.fill_type = fill_type
        self.blend_mode = blend_mode
        self.color = color or Color(0, 0, 0)  # Default to black
        self.opacity = opacity
        self.size = size

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": PSDEffectType.STROKE,
            "enabled": self.enabled,
            "position": self.position,
            "fill_type": self.fill_type,
            "blend_mode": self.blend_mode,
            "color": self.color.to_rgba_tuple(),
            "opacity": self.opacity,
            "size": self.size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StrokeEffect":
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            position=data.get("position", "outside"),
            fill_type=data.get("fill_type", "color"),
            blend_mode=data.get("blend_mode", PSDBlendMode.NORMAL),
            color=Color.from_rgba_tuple(data.get("color", (0, 0, 0, 1))),
            opacity=data.get("opacity", 1.0),
            size=data.get("size", 3.0),
        )


def create_effect_from_dict(data: dict[str, Any]) -> Any:
    """Create an effect object from a dictionary"""
    effect_type = data.get("type")

    if effect_type == PSDEffectType.DROP_SHADOW:
        return DropShadowEffect.from_dict(data)
    elif effect_type == PSDEffectType.INNER_SHADOW:
        return InnerShadowEffect.from_dict(data)
    elif effect_type == PSDEffectType.OUTER_GLOW:
        return OuterGlowEffect.from_dict(data)
    elif effect_type == PSDEffectType.INNER_GLOW:
        return InnerGlowEffect.from_dict(data)
    elif effect_type == PSDEffectType.BEVEL:
        return BevelEffect.from_dict(data)
    elif effect_type == PSDEffectType.COLOR_OVERLAY:
        return ColorOverlayEffect.from_dict(data)
    elif effect_type == PSDEffectType.STROKE:
        return StrokeEffect.from_dict(data)
    else:
        logger.warning(f"Unknown effect type: {effect_type}")
        return None
