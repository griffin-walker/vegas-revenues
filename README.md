# vegas-revenues
Grabbing and cleaning revenue data published by the Nevada Gaming Control Board

Code for https://unstructur3d.substack.com/p/what-do-vegas-casinos-make-in-a-month

### What's Here

- `environment.yml` : conda environment with necessary python dependencies. R not included here.
- src/
   - `get_revenues.py`: Downloads monthly pdfs from Nevada Gaming Control Board site and captures tables from the pdfs. Writes to csvs
   - `clean_data.py`: Takes the csvs written by `get_revenues.py`, extracts the data we want and writes to a cleaned csv.
- `plotting.R`: Generates time series plots and summary tables.

### Environment Setup
```bash
conda env create -f environment.yml
conda activate vegas-revenues
```

### Usage
```bash
# from within the vegas-revenues conda env
python src/get_revenues.py
python src/clean_data.py
```

