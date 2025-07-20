# Font Management Directory

This directory contains fonts used by the PDF processing system, organized into two subdirectories:

## Directory Structure

```
fonts/
├── manual/     # Human-managed fonts (manually added by users)
├── auto/       # Library-managed fonts (automatically downloaded)
└── README.md   # This file
```

## Subdirectories

### `manual/` - Human-Managed Fonts

- Contains fonts manually added by users
- These fonts take priority over auto-downloaded fonts
- Safe to add custom `.ttf` and `.otf` files here
- Will not be automatically modified by the system
- Recommended for:
  - Custom corporate fonts
  - Licensed fonts
  - Fonts with specific requirements

### `auto/` - Library-Managed Fonts

- Contains fonts automatically downloaded from Google Fonts
- Managed entirely by the system
- May be cleared/updated automatically
- Do not manually add fonts here
- Used for:
  - Google Fonts downloads
  - Automatic font fallbacks
  - System-managed font cache

## Font Priority

The system searches for fonts in this order:

1. Standard PDF fonts (built-in)
2. Manual fonts (`manual/` directory)
3. Auto-downloaded fonts (`auto/` directory)
4. Google Fonts download (saved to `auto/`)
5. Fallback to default font

## Usage

- Place custom fonts in the `manual/` directory
- The system will automatically create and manage the `auto/` directory
- Both directories support `.ttf` and `.otf` font files
- Font names are detected automatically from font metadata

## Safety

- The cleanup script protects the entire `fonts/` directory from deletion
- Manual fonts are never automatically removed
- Auto fonts may be refreshed during system updates
