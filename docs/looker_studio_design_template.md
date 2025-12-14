# Looker Studio Design Template for ABCDC Dashboards

## Design System Overview

This document provides comprehensive design guidelines for creating consistent, professional, and accessible Looker Studio dashboards for the ABCDC Harvard Allston Project.

---

## Typography

### Font Families

**Primary Font (Headings & Titles):**
- **Font:** Roboto, Arial, or Helvetica
- **Usage:** Dashboard titles, section headers, KPI labels
- **Weights:** Bold (700) for titles, Semi-bold (600) for subtitles

**Secondary Font (Body Text):**
- **Font:** Roboto, Arial, or Open Sans
- **Usage:** Chart labels, table text, descriptions
- **Weights:** Regular (400) for body, Medium (500) for emphasis

**Monospace Font (Numbers & Data):**
- **Font:** Roboto Mono, Courier New, or Consolas
- **Usage:** Scorecards, large numbers, data tables
- **Weight:** Regular (400) or Medium (500)

### Font Sizes

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| Dashboard Title | 32-36px | Bold (700) | Main page title |
| Section Headers | 24-28px | Semi-bold (600) | Chart section titles |
| Chart Titles | 18-20px | Medium (500) | Individual chart titles |
| KPI Numbers | 48-64px | Bold (700) | Scorecard values |
| KPI Labels | 14-16px | Medium (500) | Scorecard descriptions |
| Axis Labels | 12-14px | Regular (400) | Chart axes |
| Table Headers | 14px | Semi-bold (600) | Table column headers |
| Table Body | 13px | Regular (400) | Table data |
| Footnotes | 11-12px | Regular (400) | Data source notes |

### Line Height

- **Headings:** 1.2-1.3
- **Body Text:** 1.5-1.6
- **Tables:** 1.4

---

## Color Palette

### Primary Colors

**ABCDC Brand Colors:**

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| Primary Blue | `#2b6cb0` | rgb(43, 108, 176) | Primary actions, headers, key metrics |
| Secondary Purple | `#764ba2` | rgb(118, 75, 162) | Secondary elements, accents |
| Dark Navy | `#1e293b` | rgb(30, 41, 59) | Backgrounds, text on light |
| Slate Gray | `#334155` | rgb(51, 65, 85) | Secondary backgrounds |

### Data Visualization Colors

**Sequential Color Scheme (for quantitative data):**

| Color | Hex Code | Usage |
|-------|----------|-------|
| Light Blue | `#e0f2fe` | Lowest values |
| Blue | `#3b82f6` | Low-medium values |
| Primary Blue | `#2b6cb0` | Medium values |
| Dark Blue | `#1e40af` | High values |
| Navy | `#1e293b` | Highest values |

**Categorical Color Scheme (for qualitative data):**

| Color | Hex Code | Usage |
|-------|----------|-------|
| Primary Blue | `#2b6cb0` | Category 1 (e.g., Ward 21) |
| Secondary Purple | `#764ba2` | Category 2 (e.g., Ward 22) |
| Teal | `#14b8a6` | Category 3 (e.g., Age 62-69) |
| Orange | `#f97316` | Category 4 (e.g., Age 70-79) |
| Red | `#ef4444` | Category 5 (e.g., Age 80+) |
| Green | `#22c55e` | Positive indicators |
| Amber | `#f59e0b` | Warnings/attention |

**Semantic Colors:**

| Color | Hex Code | Usage |
|-------|----------|-------|
| Success Green | `#22c55e` | Positive metrics, increases |
| Warning Amber | `#f59e0b` | Caution, moderate values |
| Error Red | `#ef4444` | Critical issues, decreases |
| Info Blue | `#3b82f6` | Informational elements |

### Neutral Colors

| Color | Hex Code | Usage |
|-------|----------|-------|
| White | `#ffffff` | Background, text on dark |
| Light Gray | `#f8fafc` | Subtle backgrounds |
| Medium Gray | `#e2e8f0` | Borders, dividers |
| Dark Gray | `#64748b` | Secondary text |
| Black | `#0f172a` | Primary text |

### Accessibility

- **Contrast Ratio:** Minimum 4.5:1 for normal text, 3:1 for large text
- **Color Blind Friendly:** Use patterns, shapes, or labels in addition to color
- **Test Colors:** Use tools like WebAIM Contrast Checker

---

## Layout & Spacing

### Page Dimensions

- **Standard Dashboard Size:** 1200px × 800px (default)
- **Full Width:** Use 100% width for responsive dashboards
- **Padding:** 20-24px around page edges

### Grid System

- **Columns:** Use 12-column grid system
- **Gutter Width:** 16-20px between elements
- **Chart Spacing:** 24-32px between chart sections

### Spacing Scale

| Size | Pixels | Usage |
|------|--------|-------|
| XS | 4px | Tight spacing within elements |
| S | 8px | Close related items |
| M | 16px | Standard spacing |
| L | 24px | Section spacing |
| XL | 32px | Major section breaks |
| XXL | 48px | Page-level spacing |

---

## Component Styles

### Scorecards (KPI Cards)

**Style Settings:**
- **Background:** White (`#ffffff`) or light gray (`#f8fafc`)
- **Border:** 1px solid `#e2e8f0`, rounded corners (8px)
- **Padding:** 20-24px
- **Number Size:** 48-64px, Bold
- **Label Size:** 14-16px, Medium
- **Alignment:** Center or left-aligned
- **Shadow:** Subtle shadow (0 2px 4px rgba(0,0,0,0.1))

**Color Coding:**
- Use semantic colors for trend indicators (green for positive, red for negative)
- Primary blue for main metrics

### Bar Charts

**Style Settings:**
- **Bar Width:** 40-60px for standard bars
- **Spacing:** 8-12px between bars
- **Colors:** Use categorical color scheme
- **Grid Lines:** Light gray (`#e2e8f0`), 1px
- **Axis:** Dark gray (`#64748b`), 12-14px
- **Border:** No border on bars

### Line Charts

**Style Settings:**
- **Line Width:** 2-3px
- **Point Size:** 6-8px (if showing points)
- **Colors:** Primary blue, secondary purple, teal
- **Grid Lines:** Light gray, dashed
- **Area Fill:** 20-30% opacity if using area charts

### Pie/Donut Charts

**Style Settings:**
- **Colors:** Categorical color scheme
- **Border:** 2px white border between segments
- **Labels:** Outside with leader lines, 12-14px
- **Legend:** Right side or bottom, 12-14px

### Tables

**Style Settings:**
- **Header Background:** Light gray (`#f8fafc`) or primary blue (`#2b6cb0`)
- **Header Text:** White (on blue) or dark gray (on light)
- **Row Alternation:** Subtle gray (`#f8fafc`) for even rows
- **Border:** 1px solid `#e2e8f0`
- **Padding:** 12px horizontal, 10px vertical
- **Font:** 13px regular for body, 14px semi-bold for headers

### Maps (Geo Charts)

**Style Settings:**
- **Base Map:** Light theme
- **Fill Colors:** Sequential color scheme
- **Border:** 1px white or light gray
- **Legend:** Bottom or right side
- **Tooltip:** Dark background with white text

### Filters & Controls

**Style Settings:**
- **Background:** White
- **Border:** 1px solid `#e2e8f0`
- **Border Radius:** 6-8px
- **Padding:** 8-12px
- **Font:** 14px regular
- **Dropdown Arrow:** Primary blue

---

## Dashboard Themes

### Light Theme (Default)

- **Background:** White (`#ffffff`) or very light gray (`#fafafa`)
- **Text:** Dark gray (`#0f172a`) or black
- **Cards:** White with subtle shadow
- **Borders:** Light gray (`#e2e8f0`)

### Dark Theme (Optional)

- **Background:** Dark navy (`#1e293b`)
- **Text:** White or light gray (`#f8fafc`)
- **Cards:** Slate gray (`#334155`)
- **Borders:** Medium gray (`#475569`)

---

## Chart-Specific Guidelines

### Elderly Population Dashboard

**Color Mapping:**
- Ward 21: Primary Blue (`#2b6cb0`)
- Ward 22: Secondary Purple (`#764ba2`)
- Age Groups:
  - 62-69: Teal (`#14b8a6`)
  - 70-79: Orange (`#f97316`)
  - 80-89: Red (`#ef4444`)
  - 90+: Dark Red (`#dc2626`)

### Income Analysis Dashboard

**Color Mapping:**
- Use sequential blue scale for income ranges
- Low Income: Light Blue (`#e0f2fe`)
- Medium Income: Blue (`#3b82f6`)
- High Income: Dark Blue (`#1e40af`)

### Building Analysis Dashboard

**Color Mapping:**
- Building Value: Sequential color scale
- Elderly Concentration: Red to green scale
- Building Type: Categorical colors

---

## Text & Labels

### Dashboard Title

```
Font: Roboto Bold, 32-36px
Color: #1e293b (Dark Navy)
Alignment: Left or Center
Padding: 24px top, 16px bottom
```

### Section Headers

```
Font: Roboto Semi-bold, 24-28px
Color: #1e293b
Spacing: 32px above section
```

### Chart Titles

```
Font: Roboto Medium, 18-20px
Color: #334155 (Slate Gray)
Position: Above chart, left-aligned
```

### Data Labels

```
Font: Roboto Regular, 12-14px
Color: #64748b (Dark Gray)
Position: On or near data points
```

### Footnotes

```
Font: Roboto Regular, 11-12px
Color: #94a3b8 (Light Gray)
Position: Bottom of dashboard
Format: "Data Source: [source] | Last Updated: [date]"
```

---

## Best Practices

### Consistency

- ✅ Use the same color for the same metric across all dashboards
- ✅ Maintain consistent spacing and alignment
- ✅ Use the same font sizes for similar elements
- ✅ Keep chart types consistent for similar data

### Clarity

- ✅ Use clear, descriptive titles
- ✅ Add brief descriptions where needed
- ✅ Include data source and date information
- ✅ Use appropriate chart types for data

### Accessibility

- ✅ Ensure sufficient color contrast
- ✅ Don't rely solely on color to convey information
- ✅ Use clear labels and legends
- ✅ Provide alternative text for charts

### Performance

- ✅ Limit data points in charts (use filters)
- ✅ Use data extracts for large datasets
- ✅ Optimize chart complexity
- ✅ Test dashboard load times

---

## Looker Studio Theme Settings

### To Apply Theme in Looker Studio:

1. **Go to Theme and Layout** (paintbrush icon)
2. **Theme Colors:**
   - Primary: `#2b6cb0`
   - Secondary: `#764ba2`
   - Background: `#ffffff`
   - Text: `#0f172a`

3. **Chart Defaults:**
   - Set default colors to match color palette
   - Apply consistent font settings

4. **Page Settings:**
   - Page width: 1200px (or 100% for responsive)
   - Background: White or light gray
   - Padding: 20-24px

---

## Example Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  ABCDC Elderly Population Analysis Dashboard                │
│  [32px Roboto Bold, #1e293b]                                │
├─────────────────────────────────────────────────────────────┤
│  [Filters: Ward ▼] [Precinct ▼] [Age Range ▼]              │
│  [16px spacing]                                              │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Total       │  Ward 21     │  Ward 22     │  Avg Age      │
│  Elderly     │  Elderly     │  Elderly     │               │
│  7,396       │  4,199       │  3,197       │  72.5         │
│  [48px Bold] │  [48px Bold] │  [48px Bold] │  [48px Bold] │
├──────────────┴──────────────┴──────────────┴───────────────┤
│                                                              │
│  Elderly Population by Precinct                           │
│  [24px Semi-bold]                                           │
│  [Bar Chart - Primary Blue & Purple]                        │
│                                                              │
├──────────────────────────┬──────────────────────────────────┤
│  Age Distribution         │  Top Buildings by Elderly Count │
│  [Pie Chart]              │  [Table]                        │
│  [Categorical Colors]     │  [Alternating Rows]             │
└──────────────────────────┴──────────────────────────────────┘
│  Data Source: Boston Voter List | Last Updated: [Date]      │
│  [11px, #94a3b8]                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### Font Stack
```
Primary: 'Roboto', 'Arial', 'Helvetica', sans-serif
Monospace: 'Roboto Mono', 'Courier New', monospace
```

### Color Quick Reference
```
Primary: #2b6cb0
Secondary: #764ba2
Success: #22c55e
Warning: #f59e0b
Error: #ef4444
Text: #0f172a
Background: #ffffff
Border: #e2e8f0
```

### Spacing Quick Reference
```
XS: 4px
S: 8px
M: 16px
L: 24px
XL: 32px
XXL: 48px
```

---

## Resources

- [Looker Studio Help - Themes](https://support.google.com/looker-studio/answer/6311514)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Google Fonts - Roboto](https://fonts.google.com/specimen/Roboto)
- [ABCDC Brand Guidelines](link-if-available)

---

*Last Updated: [Current Date]*
*Template Version: 1.0*

