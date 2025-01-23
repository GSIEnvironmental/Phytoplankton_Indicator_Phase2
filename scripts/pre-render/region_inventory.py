#!/usr/bin/env python

# This script generates the region pages for the inventory section of the website.
# The output of this script is not rendered in the final website, but is used as input.

import logging
import os
import re
import sys
from pathlib import Path

import jinja2
import polars as pl

# https://quarto.org/docs/projects/scripts.html#pre-and-post-render
if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
    exit()

# Configure logging to print to stdout
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)
logging.info(f"Running pre-render script {Path(__file__).name}")


# Path to the output directory from the project root
workdir = Path("content/inventory/regions")
logging.info("Workdir is set to %s", workdir)


# Specify the jinja environment. The jinja template(s) live in the static/ folder
logging.info("Configuring jinja environment")
environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(workdir),
    autoescape=jinja2.select_autoescape(["html", "xml"]),
)
# Template to use for each region page
template = environment.get_template("region_template.jinja")


# Get the regions from the database
logging.info("Querying regions from the project database")
uri = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DATABASE")}'
regions = {
    region: re.sub(r"\W+", "-", region.lower().strip())
    for region in (
        pl.read_database_uri(
            "select area_id from d_area order by area_id;",  # limit 1;", 
            uri,
            engine="connectorx",
        )
        .to_series()
        .to_list()
    )
}

# Assign an index to the regions so that we can order them
region_order = {region: i + 1 for i, region in enumerate(sorted(regions.keys()))}
regions["Global"] = "global"


# Generate data type/grouping tuples (e.g. "(Bottle: ChlorophyllA)", or "(CTD, Temperature)")
# using the groupings.csv file.
logging.info("Reading groupings from groupings.csv")
groupings = [
    (row["data_type"], row["parameter"])
    for row in pl.read_csv(Path(workdir, "groupings.csv"))
    .sort(["data_type", "parameter"])
    .to_dicts()
]


# Render the region pages
for region, region_slug in regions.items():
    logging.info(f"Generating region page for {region}")
    with open(Path(workdir, f"{region_slug}.qmd"), "w") as f:
        f.write(
            template.render(
                region=region,
                region_slug=region_slug,
                groupings=groupings,
                order=0 if region_slug == "global" else region_order[region],
            )
        )
