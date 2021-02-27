import argparse

from corona.load import download, load
from corona.process import process, plot

parser = argparse.ArgumentParser(description='Generate a plot of Covid deaths in the UK over time')
parser.add_argument('-f', '--fetch', action='store_true', help='Fetch latest data over HTTPS')
parser.add_argument('-d', '--date', default=None, help='Use a particular date')
args = parser.parse_args()

if args.fetch:
    download(date=args.date)

df_load = load(date=args.date)
df_process = process(df_load)
plot(df_process)
