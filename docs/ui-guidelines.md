# UI Guidelines

## Main objective

The UI must be:
- clean
- readable
- aligned
- non-overlapping
- consistent across all games

## Layout rules

### 1. Design to a base resolution
Use a primary design target of **1600x900**.

### 2. Use screen regions
Every scene should respect:
- Header area
- Content area
- Footer area

### 3. Avoid random placement
Do not scatter text/buttons with arbitrary coordinates unless there is a gameplay-specific reason.

Use:
- grid layouts
- centered panels
- consistent margins
- fixed gaps between items

### 4. Maintain spacing tokens
Use shared spacing values from `ui/theme.py`.

### 5. Typography rules
Use only a small set of text styles:
- Title
- Heading
- Body
- Caption

### 6. Card grid rules for launcher
The launcher will begin as a **4x4 grid**.
Each card should include:
- game title
- optional icon later
- short subtitle/description
- hover/focus state later
- consistent padding

### 7. Truncation policy
Long descriptions should be shortened rather than overflowing cards.

### 8. Buttons
All buttons should share:
- padding
- font sizing
- border radius
- selected/hover styling
- disabled styling

## Accessibility / usability goals

- High contrast text against background
- Keyboard navigation support
- Clear back/escape prompts
- Avoid tiny text
- Avoid placing critical UI in extreme corners

## Quality checklist

Before accepting any new screen:
- Is all text visible at 1600x900?
- Are margins consistent?
- Do buttons align properly?
- Does anything overlap?
- Does escape/back behaviour exist?
- Is the scene readable within 3 seconds of viewing?
