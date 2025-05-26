# Sample Document Creation

This file provides instructions for creating sample documents to test the document import system.

## Excel Sample

Create a simple Excel file with the following structure:
1. Create a sheet named "ESD Rules"
2. Add these columns: "Rule ID", "Title", "Description", "Type", "Severity"
3. Add some sample rules:
   - Rule 1: "ESD Protection for IO", "All IO pins must have ESD protection", "ESD", "High"
   - Rule 2: "Power Clamp", "Power domains must include clamp circuits", "ESD", "Critical"
   - Rule 3: "Latchup Prevention", "Guard rings required for all NMOS", "Latchup", "Medium"

## PDF Sample

Create a PDF document with rule information:
```
Rule 1: ESD Protection
All IO pins must have ESD protection diodes with at least 2kV HBM rating.

Rule 2: Latchup Prevention
Guard rings must be used for isolation to prevent latchup conditions.

Rule 3: Power Sequencing
Proper power sequencing must be observed to prevent damage.
```

## Word Sample

Create a Word document with the following structure:

# ESD Design Rules

## Rule 1: ESD Protection for IO
All IO pins must have ESD protection diodes with at least 2kV HBM rating.

## Rule 2: Latchup Prevention
Guard rings must be used for isolation to prevent latchup conditions.

## Rule 3: Power Sequencing
Proper power sequencing must be observed to prevent damage.

# References
Include some reference information here.

Save these files in the "samples" directory as:
- sample.xlsx
- sample.pdf
- sample.docx
