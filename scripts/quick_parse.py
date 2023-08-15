import argparse
import sqlite3
import pandas as pd


def main(args):
    con = sqlite3.connect(args.path)
    cur = con.cursor()
    result = cur.execute("SELECT * FROM apartments")
    data = result.fetchall()

    df = pd.DataFrame(data, columns=["id", "date", "apt_id", "price"])
    print(df.tail(args.count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, type=str, help="Path to SQLite DB")
    parser.add_argument("--count", default=10, type=int, help="How many tail entries to display")
    cmdargs = parser.parse_args()
    main(cmdargs)