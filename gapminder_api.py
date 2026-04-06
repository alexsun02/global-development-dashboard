'''
API Layer - Data loading, processing, and filtering
'''

import os
import pandas as pd
import plotly.express as px

# constants
DATA_FILE_PATH = "gapminder.csv"
YEAR_COL = "year"
COUNTRY_COL = "country"
CONTINENT_COL = "continent"
POP_COL = "pop"
GDP_COL = "gdpPercap"
LIFE_COL = "lifeExp"
LEFT_LAYER_COL_NAME = CONTINENT_COL
RIGHT_LAYER_COL_NAMES = ["gdp_group", "life_group"]

class GapminderAPI:
    def __init__(self, filename):
        """Load data from CSV"""
        self.filename = filename
        self.df = None

    def process_data(self):
        """Clean data, bin columns, handle missing values."""
        # load data
        if os.path.exists(self.filename):
            df = pd.read_csv(self.filename)
        else:
            df = px.data.gapminder().copy()
            df.to_csv(self.filename, index=False)
        # Clean data
        df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors="coerce")
        df[POP_COL] = pd.to_numeric(df[POP_COL], errors="coerce")
        df[GDP_COL] = pd.to_numeric(df[GDP_COL], errors="coerce")
        df[LIFE_COL] = pd.to_numeric(df[LIFE_COL], errors="coerce")
        df = df.dropna(subset=[YEAR_COL, COUNTRY_COL, CONTINENT_COL, POP_COL, GDP_COL, LIFE_COL])
        df[YEAR_COL] = df[YEAR_COL].astype(int)

        # Create bins for the Sankey diagram
        df["gdp_group"] = df[GDP_COL].apply(self._bin_gdp)
        df["life_group"] = df[LIFE_COL].apply(self._bin_life)
        self.df = df

    def get_continents(self):
        """Return list of continents for dropdown"""
        return ["All"] + sorted(self.df[CONTINENT_COL].unique().tolist())

    def get_year_bounds(self):
        return int(self.df[YEAR_COL].min()), int(self.df[YEAR_COL].max())

    def get_pop_bounds(self):
        return int(self.df[POP_COL].min()), int(self.df[POP_COL].max())

    def get_countries(self, continent="All"):
        df = self.df
        if continent != "All":
            df = df[df[CONTINENT_COL] == continent]
        return sorted(df[COUNTRY_COL].unique().tolist())

    def get_subset(self, continent="All", year=None, min_population=0):
        """Return subset df"""
        df = self.df

        if continent != "All":
            df = df[df[CONTINENT_COL] == continent]

        if year is not None:
            df = df[df[YEAR_COL] == int(year)]

        df = df[df[POP_COL] >= int(min_population)]
        return df

    def get_flow(self, continent="All", left_layer=LEFT_LAYER_COL_NAME,
                 right_layer="gdp_group", min_population=0, year=None):
        """
        Filter and aggregate data for sankey diagram
        """
        df = self.get_subset(continent=continent, year=year, min_population=min_population)

        flow_df = (
            df.groupby([left_layer, right_layer])[COUNTRY_COL]
              .nunique()
              .reset_index(name="count")
        )
        return flow_df

    # create bins
    def _bin_gdp(self, x):
        if x < 2000: return "Low GDP"
        if x < 8000: return "Medium GDP"
        if x < 20000: return "High GDP"
        return "Very High GDP"

    def _bin_life(self, x):
        if x < 55: return "Low Life Expectancy"
        if x < 65: return "Medium Life Expectancy"
        if x < 75: return "High Life Expectancy"
        return "Very High Life Expectancy"

