# TCAD Neighborhood Scraper

Scrapes property-level data from the Travis Central Appraisal District (TCAD) website for a list of streets and saves the results to a single CSV file.

|                |                     |
|----------------|---------------------|
| **Language**   | Python 3.10 +       |
| **Automation** | Selenium + Chrome   |
| **Output**     | `tcad_neighborhood_analysis_final.csv` |

---

## ✨ What the script does

1. **Searches** each street name you provide on the TCAD “Property Search” page.  
2. **Scrolls** through the infinite-scroll grid to collect all matching *Account IDs*.  
3. **Visits** every account’s detail page and extracts:  
   - Address  
   - Builder (heuristic from deed history)  
   - Most common **Class CD** and first **Year Built** appearing in the “Improvements” table  
   - 2025 Net/Appraised values and Value-Limitation adjustment  
   - Direct TCAD link for traceability  
4. **Saves** one row per property to a CSV (column order set in the script).  
5. **Reports** any street names that returned zero results.

---

## 📁 Project structure (suggested)

```

tcad-scraper/
├─ scraper.py              # <— the script you pasted
├─ requirements.txt
└─ README.md

````

---

## 🔧 Requirements

| Dependency | Purpose |
|------------|---------|
| `pandas`   | parse fallback HTML tables & build the final DataFrame |
| `selenium` | browser automation |
| **Chrome** (latest) | browser used by Selenium |
| **ChromeDriver** matching your Chrome version | WebDriver bridge |

> **Tip:** `webdriver-manager` can auto-download/patch the correct ChromeDriver.  
> Replace `webdriver.Chrome()` with `webdriver.Chrome(service=Service(ChromeDriverManager().install()))` if you’d like to remove manual driver upkeep.

---

## 🛠 Installation

```bash
# 1. Clone or copy the repo
git clone <YOUR-REPO-URL>
cd tcad-scraper

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt
````

`requirements.txt`

```
pandas>=2.1
selenium>=4.21
webdriver-manager>=4.0  # optional (see tip above)
```

---

## 🚀 Running the scraper

```bash
python scraper.py
```

### CLI flags (quick edits)

For now configuration is in-file:

```python
STREETS_TO_SEARCH = [
    "Spillman Ranch Loop",
    "Bat Falcon Dr",
    ...
]
OUTPUT_FILE = "tcad_neighborhood_analysis_final.csv"
```

1. **Add / remove / rename** streets in `STREETS_TO_SEARCH`.
2. **Rename** `OUTPUT_FILE` if you need a different filename.

> To run completely head-less, uncomment the `options.add_argument("--headless")` line.

---

## 📝 Output

The resulting CSV contains (one row per property):

| address | builder | class\_cd | year\_built | net\_appraised\_value | appraised\_value | value\_limit\_adjustment | tcad\_link | account\_id |
| ------- | ------- | --------- | ----------- | --------------------- | ---------------- | ------------------------ | ---------- | ----------- |

---

## ⚠️ Common issues & troubleshooting

| Symptom                                                     | Likely cause                            | Fix                                                                         |
| ----------------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| **“selenium.common.exceptions.SessionNotCreatedException”** | ChromeDriver ↔ Chrome version mismatch. | Update Chrome **or** download matching driver (or use `webdriver-manager`). |
| **“ElementClickInterceptedException”** early in run         | TCAD changed page layout.               | Update the CSS/XPath selectors in `click_element_robustly()`.               |
| Empty CSV / “No data was collected”                         | All searches returned zero results.     | Check spelling & formatting of street names.                                |

---

## 🤝 Contributing

1. Fork the repo.
2. Create a branch (`git checkout -b feature/my-fix`).
3. Commit your changes (`git commit -am 'Fix something'`).
4. Push and open a pull request.

---

## 📜 License

MIT — see `LICENSE` for details.

---

## 🙋‍♂️ Author

**Eduardo Treviño** – [@eatrevin](mailto:eatrevin@cs.cmu.edu)
Feel free to reach out with questions or improvements!

```

---

### Next steps

* Drop the snippet into `README.md` and commit.  
* If you’d like a refined badge table, GIF demo, or configuration via environment variables instead of in-file edits, let me know and we can iterate on this.
```
**Creating the README**

The user wants a README for their Python project. I’m considering drafting the content directly here, since they haven’t explicitly asked for it to be in a canvas for iteration. I know that a README typically benefits from easy revisions, so using a canvas could make sense, but I’m not 100% sure they want that. Since I’m not seeing a clear call for it, I’ll proceed carefully and stick to creating the content directly here for now.

Thought for 6 seconds

Below is a ready-to-paste **README.md** that documents what the script does, how to set it up, and how to run it. Feel free to tweak any section names or wording to match your team’s style.

---

```markdown
# TCAD Neighborhood Scraper

Scrapes property-level data from the Travis Central Appraisal District (TCAD) website for a list of streets and saves the results to a single CSV file.

|                |                     |
|----------------|---------------------|
| **Language**   | Python 3.10 +       |
| **Automation** | Selenium + Chrome   |
| **Output**     | `tcad_neighborhood_analysis_final.csv` |

---

## ✨ What the script does

1. **Searches** each street name you provide on the TCAD “Property Search” page.  
2. **Scrolls** through the infinite-scroll grid to collect all matching *Account IDs*.  
3. **Visits** every account’s detail page and extracts:  
   - Address  
   - Builder (heuristic from deed history)  
   - Most common **Class CD** and first **Year Built** appearing in the “Improvements” table  
   - 2025 Net/Appraised values and Value-Limitation adjustment  
   - Direct TCAD link for traceability  
4. **Saves** one row per property to a CSV (column order set in the script).  
5. **Reports** any street names that returned zero results.

---

## 📁 Project structure (suggested)

```

tcad-scraper/
├─ scraper.py              # <— the script you pasted
├─ requirements.txt
└─ README.md

````

---

## 🔧 Requirements

| Dependency | Purpose |
|------------|---------|
| `pandas`   | parse fallback HTML tables & build the final DataFrame |
| `selenium` | browser automation |
| **Chrome** (latest) | browser used by Selenium |
| **ChromeDriver** matching your Chrome version | WebDriver bridge |

> **Tip:** `webdriver-manager` can auto-download/patch the correct ChromeDriver.  
> Replace `webdriver.Chrome()` with `webdriver.Chrome(service=Service(ChromeDriverManager().install()))` if you’d like to remove manual driver upkeep.

---

## 🛠 Installation

```bash
# 1. Clone or copy the repo
git clone <YOUR-REPO-URL>
cd tcad-scraper

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt
````

`requirements.txt`

```
pandas>=2.1
selenium>=4.21
webdriver-manager>=4.0  # optional (see tip above)
```

---

## 🚀 Running the scraper

```bash
python scraper.py
```

### CLI flags (quick edits)

For now configuration is in-file:

```python
STREETS_TO_SEARCH = [
    "Spillman Ranch Loop",
    "Bat Falcon Dr",
    ...
]
OUTPUT_FILE = "tcad_neighborhood_analysis_final.csv"
```

1. **Add / remove / rename** streets in `STREETS_TO_SEARCH`.
2. **Rename** `OUTPUT_FILE` if you need a different filename.

> To run completely head-less, uncomment the `options.add_argument("--headless")` line.

---

## 📝 Output

The resulting CSV contains (one row per property):

| address | builder | class\_cd | year\_built | net\_appraised\_value | appraised\_value | value\_limit\_adjustment | tcad\_link | account\_id |
| ------- | ------- | --------- | ----------- | --------------------- | ---------------- | ------------------------ | ---------- | ----------- |

---

## ⚠️ Common issues & troubleshooting

| Symptom                                                     | Likely cause                            | Fix                                                                         |
| ----------------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| **“selenium.common.exceptions.SessionNotCreatedException”** | ChromeDriver ↔ Chrome version mismatch. | Update Chrome **or** download matching driver (or use `webdriver-manager`). |
| **“ElementClickInterceptedException”** early in run         | TCAD changed page layout.               | Update the CSS/XPath selectors in `click_element_robustly()`.               |
| Empty CSV / “No data was collected”                         | All searches returned zero results.     | Check spelling & formatting of street names.                                |

---

## 🤝 Contributing

1. Fork the repo.
2. Create a branch (`git checkout -b feature/my-fix`).
3. Commit your changes (`git commit -am 'Fix something'`).
4. Push and open a pull request.

---

## 📜 License

MIT — see `LICENSE` for details.

---

## 🙋‍♂️ Author

**Eduardo Treviño** – [@eatrevin](mailto:eatrevin@cs.cmu.edu)
Feel free to reach out with questions or improvements!

```
