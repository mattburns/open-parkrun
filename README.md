# Open Parkrun

A simple Python script to fetch and save parkrun results as JSON files. This project is intended for fun and personal use, helping to create an open dataset of parkrun results.

## 🏃‍♂️ About

This script fetches results from parkrun's website and saves them as JSON files. It's designed to be:
- Polite to parkrun's servers
- Easy to use
- Efficient (caches results locally)

## 🤝 Community Guidelines

We love parkrun! Please be respectful when using this script:

1. **Be Nice to parkrun's Servers**
   - Don't modify the delays to make it faster
   - Don't run multiple instances simultaneously

2. **Share Your Results**
   - If you've fetched results for your local parkrun, consider submitting a PR
   - This helps build a community dataset without everyone hitting parkrun's servers
   - Include the JSON files in your PR

3. **Personal Use Only**
   - This is for fun and personal use
   - Don't use it for commercial purposes
   - Don't redistribute the data without permission

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install .
   ```

2. Run the script:
   ```bash
   python parkrun.py <event-name>
   ```
   For example: `python parkrun.py eastville`

3. Results will be saved in `data/json/<event-name>/`

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This is an unofficial project and is not affiliated with parkrun. Use responsibly and respect parkrun's servers and terms of service.

## Project Structure

```
.
├── data/
│   ├── html/          # Raw HTML files (not committed to git)
│   │   └── {event}/
│   └── json/          # Processed JSON files
│       └── {event}/
├── parkrun.py         # Main script
└── pyproject.toml     # Project configuration
```

The HTML files are stored locally but not committed to git. Only the processed JSON files are tracked in version control.
