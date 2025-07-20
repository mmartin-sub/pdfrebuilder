# psd_effects

PSD layer effects handling for the Multi-Format Document Engine.

This module provides utilities for parsing and representing PSD layer effects
in the Universal IDM format.

## Classes

### PSDEffectType

Constants for PSD effect types

### PSDBlendMode

Constants for PSD blend modes

#### Methods

##### to_universal_blend_mode(psd_blend_mode)

Convert PSD blend mode to Universal IDM blend mode

### DropShadowEffect

Drop shadow effect

#### Methods

##### __init__(enabled, blend_mode, color, opacity, angle, distance, spread, size, noise, layer_knocks_out)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

### InnerShadowEffect

Inner shadow effect

#### Methods

##### __init__(enabled, blend_mode, color, opacity, angle, distance, choke, size, noise)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

### OuterGlowEffect

Outer glow effect

#### Methods

##### __init__(enabled, blend_mode, color, opacity, spread, size, noise)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

### InnerGlowEffect

Inner glow effect

#### Methods

##### __init__(enabled, blend_mode, color, opacity, choke, size, noise, source)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

### BevelEffect

Bevel effect

#### Methods

##### __init__(enabled, style, technique, depth, direction, size, soften, angle, altitude, highlight_mode, highlight_color, highlight_opacity, shadow_mode, shadow_color, shadow_opacity)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

### ColorOverlayEffect

Color overlay effect

#### Methods

##### __init__(enabled, blend_mode, color, opacity)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

### StrokeEffect

Stroke effect

#### Methods

##### __init__(enabled, position, fill_type, blend_mode, color, opacity, size)

##### to_dict()

Convert to dictionary

##### from_dict(cls, data)

Create from dictionary

## Functions

### create_effect_from_dict(data)

Create an effect object from a dictionary
