# Schematic Analyzer

A web app that analyzes schematic images using AI to extract components and values.

## Features
- Upload any schematic image (PNG, JPG, etc.)
- AI-powered component extraction (resistors, capacitors, ICs, etc.)
- Clean results table with component names and values
- Built with Python (Flask) + Claude Vision API

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python app.py
```

Then open http://localhost:5000
