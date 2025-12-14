#!/bin/bash

TEX_FILE="Elderly_Housing_Analysis_Report.tex"
BUILD_DIR="build"

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Run pdflatex twice to resolve references
echo "Building PDF report..."
pdflatex -output-directory="$BUILD_DIR" "$TEX_FILE" > /dev/null 2>&1
pdflatex -output-directory="$BUILD_DIR" "$TEX_FILE" > /dev/null 2>&1

# Check if PDF was created
if [ -f "$BUILD_DIR/${TEX_FILE%.tex}.pdf" ]; then
    cp "$BUILD_DIR/${TEX_FILE%.tex}.pdf" .
    echo "✅ PDF created successfully: ${TEX_FILE%.tex}.pdf"
    echo "📁 Auxiliary files are in: $BUILD_DIR/"
    echo ""
    echo "To view the PDF:"
    echo "  open ${TEX_FILE%.tex}.pdf"
else
    echo "❌ Error: PDF was not created. Check build logs in $BUILD_DIR/"
    exit 1
fi

