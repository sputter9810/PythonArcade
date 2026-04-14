# Packaging

## Goal

Distribute Arcade to friends as an easy-to-run desktop application.

## Packaging target order

1. Windows standalone build
2. Portable zip release
3. Optional installer later
4. Optional Mac/Linux builds later

## Recommended tool

Use **PyInstaller** once the app reaches a stable alpha.

## Packaging requirements

Before packaging:
- all assets must be loaded through a central asset loader
- no absolute file paths
- one entry point (`run.py`)
- version number present
- app icon prepared
- README for players included
- crash-safe handling for missing assets if possible

## Build artifacts to prepare later

- executable
- assets folder if required by build format
- changelog
- license
- simple controls sheet
- release notes

## Future release flow

1. Tag version
2. Run tests
3. Build executable
4. Test on a clean machine
5. Zip release package
6. Share with friends
