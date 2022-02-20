"""Clean parsed gaming revenue data from pdfs (csvs)."""
import datetime
from pathlib import Path
from typing import List

import pandas as pd
from parso import parse

DATA_DIRECTORY = Path(__file__).parent.resolve().parent / "data"
GAME_KEYS = ["locations", "units", "win_amount", "change", "win_percent"]


def load_tables(directory=DATA_DIRECTORY):
    """Load parsed pdfs in the form of csvs."""
    data_map = {}
    for pdf in (directory / "csvs").iterdir():
        file_name = str(pdf).split("/")[-1]
        month_year = "_".join(str(file_name).split("_")[0:2])
        if month_year not in ["APR_2020", "MAY_2020"]:
            df = pd.read_csv(pdf)
            data_map[month_year] = df
    return data_map


def parse_tables(month_dfs):
    clean_data_map = {}
    for month, df in month_dfs.items():
        if month in ["APR_2021", "MAY_2021"]:
            clean_data_map[month] = clean_game_data_recent(df, shift=True)
        try:
            clean_data_map[month] = clean_game_data(df)
        except:
            clean_data_map[month] = clean_game_data_recent(df)
    return clean_data_map


def clean_data_records(clean_data_map):
    games_of_interest = [
        "tables_twenty_one",
        "tables_craps",
        "tables_roulette",
        "tables_baccarat",
        "slots_1_cent",
        "slots_5_cent",
        "slots_25_cent",
        "slots_1_dollar",
        "slots_5_dollar",
        "slots_25_dollar",
        "slots_100_dollar",
        "slots_multi_denomination",
    ]
    fuzzy_games = ["slots_total", "tables_total"]
    cleaned_data_records = []
    for month, games in clean_data_map.items():
        record = {"month": clean_month(month)}
        for game, stats in games.items():
            if game in games_of_interest:
                record.update({game: clean_amount(stats["win_amount"])})
            for key in fuzzy_games:
                if key in game:
                    record.update({game: clean_amount(stats["win_amount"])})
        cleaned_data_records.append(record)
    return cleaned_data_records


def clean_game(game: str, game_type: str):
    """Clean game string.

    These vary over the years, hence all the if-else's.
    """
    clean_game = (
        game_type
        + "_"
        + str(game)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("dollars", "dollar")
    )
    if (
        clean_game == "tables_total_games_&_tables"
        or clean_game == "tables_total_games"
    ):
        clean_game = "tables_total"
    if clean_game == "slots_total_slot_machines":
        clean_game = "slots_total"
    if "total_gaming" in clean_game:
        clean_game = "total"
    return clean_game


def clean_game_data(df: pd.DataFrame) -> dict:
    """Extract game data from tables."""
    month_game_data = {}
    rows = df.to_dict("list")["0"]
    game_type = "tables"
    for row in rows:
        current_month = row.split("|")
        if len(current_month) >= 2:
            game = current_month[0]
            if "slot" in game.lower() or "cent" in game.lower():
                game_type = "slots"
            current_month_data = [
                point for point in current_month[1].strip().split(" ") if point != ""
            ]
            if len(current_month_data) == 5 and game:
                month_game_data[clean_game(game, game_type)] = dict(
                    zip(GAME_KEYS, current_month_data)
                )
    return month_game_data


def clean_game_data_recent(df: pd.DataFrame, shift=False) -> dict:
    """Clean game data post mid-2018.

    Follows a slightly different format than pre-2018 data.
    """
    month_game_data = {}
    game_type = "tables"
    if shift == True:  # APR_2021, MAY_2021 had no %diff, so we need to shift
        add = 1
    else:
        add = 0
    for row in df.to_records("list"):
        row_list = list(row)
        game = row_list[1 + add]
        if "slot" in str(game).lower() or "cent" in str(game).lower():
            game_type = "slots"
        month_game_data[clean_game(game, game_type)] = dict(
            zip(GAME_KEYS, row_list[2 + add : 7 + add])
        )
    return month_game_data


def clean_amount(amount_str: str):
    """Convert amount string to integer and multiply by 1k."""
    if "(" in amount_str:
        return (
            -int(amount_str.replace(",", "").replace("(", "").replace(")", "")) * 1000
        )
    else:
        return int(amount_str.replace(",", "")) * 1000


def clean_month(month_str: str):
    """Standardize month name to number.

    Ex. SEPT -> SEP -> 9
    Ex. JUN -> 6
    """
    month_name, year = month_str.split("_")
    print(month_name, year)
    month_num = datetime.datetime.strptime(month_name[0:3], "%b").month
    return year + str(month_num).zfill(2)


def append_covid_months(cleaned_data_records: List) -> List:
    """Add zero-ed out covid month data."""
    manual_zero_months = ["202004", "202005"]
    for month in manual_zero_months:
        manual = cleaned_data_records[0].copy()
        manual["month"] = month
        for key in manual.keys():
            if key != "month":
                manual[key] = 0
        cleaned_data_records.append(manual)
    return cleaned_data_records


def create_df(clean_records):
    df = pd.DataFrame.from_records(clean_records)
    df["total"] = df["slots_total"] + df["tables_total"]
    df = df.sort_values(["month"]).reset_index(drop=True)
    df["year"] = df["month"].apply(lambda x: str(x)[:-2])
    df["month"] = df["month"].apply(lambda x: str(x)[-2:])
    df["year_month"] = df["year"] + "/" + df["month"]  # helpful for R
    return df


def main():
    month_tables = load_tables()
    print("Data loaded.")
    clean_data_map = parse_tables(month_tables)
    print("Data parsed.")
    clean_records = clean_data_records(clean_data_map)
    clean_records = append_covid_months(clean_records)
    print("Data cleaned.")
    df = create_df(clean_records)
    outfile_name = "cleaned_vegas_revenues.csv"
    df.to_csv(outfile_name, index=None)
    print(f"Written to {outfile_name}")


if __name__ == "__main__":
    main()
