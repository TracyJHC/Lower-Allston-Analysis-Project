# Elderly Housing Analysis Report

This directory contains the LaTeX source files for the comprehensive Elderly Housing Analysis Report for Allston-Brighton.

## Files

- `Elderly_Housing_Analysis_Report.tex` - Main LaTeX document
- `build_report.sh` - Build script to compile the PDF
- `build/` - Directory for build artifacts (created automatically)
- `figures/` - Directory for figures (if needed)
- `tables/` - Directory for tables (if needed)

## Building the Report

### Using the Build Script

```bash
cd reports/latex
./build_report.sh
```

This will:
1. Create the `build/` directory if it doesn't exist
2. Run `pdflatex` twice to resolve all references
3. Copy the final PDF to the current directory
4. Display success message with file location

### Manual Build

If you prefer to build manually:

```bash
cd reports/latex
mkdir -p build
pdflatex -output-directory=build Elderly_Housing_Analysis_Report.tex
pdflatex -output-directory=build Elderly_Housing_Analysis_Report.tex
```

The PDF will be in the `build/` directory.

## Report Structure

The report includes:

1. **Introduction** - Overview of the analysis and key questions
2. **Methodology** - Data sources, analysis methods, eligibility scoring
3. **Who Are the Elderly Residents?** - Demographics and geographic distribution
4. **What Supports Are Needed?** - Eligibility analysis and barriers to housing access
5. **Market Impact Analysis** - How shifting residents affects neighborhood housing dynamics
6. **Discussion** - Synthesis of findings and policy implications
7. **Conclusions** - Key takeaways
8. **Recommendations** - Actionable next steps
9. **References** - Data sources and methodology details

## Requirements

- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Required packages (automatically handled by LaTeX):
  - `geometry`, `graphicx`, `booktabs`, `longtable`
  - `array`, `multirow`, `xcolor`, `hyperref`
  - `amsmath`, `float`, `caption`, `subcaption`
  - `fancyhdr`, `titlesec`, `enumitem`, `setspace`

## Notes

- The report uses data from the analysis notebooks and markdown documentation
- Tables are formatted using `booktabs` for professional appearance
- All figures and tables are referenced in the text
- The report follows academic paper formatting standards

## Customization

To customize the report:

1. Edit `Elderly_Housing_Analysis_Report.tex` directly
2. Modify title, author, or date in the preamble
3. Add figures by placing them in `figures/` and using `\includegraphics`
4. Modify tables by editing the table environments
5. Rebuild using `./build_report.sh`

