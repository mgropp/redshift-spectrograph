Redshift Spectrograph
=====================

A very unfinished program to visualize Redshift query plans.

## Usage
The program uses [uv](https://github.com/astral-sh/uv).
After installing uv, you can run the program with:

```sh
uv run spectrograph.py --help
```

First, export the query plan to a "JSON" file.
Then, run the program with:

```sh
uv run spectrograph.py --graph query_plan.pdf query_plan.json
```
