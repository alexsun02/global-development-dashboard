"""
UI Layer
Aspects that form the front end of the dashboard
Dashboard goals:
Plot -- Scatter: GDP vs Life Expectancy
Plot -- Sankey Diagram: Continent to GDP or Life Expectancy
- Dropdown -- continent picker
- IntSlider -- year picker
- IntSlider -- minimum population
- RadioGroup -- see GDP vs life expectancy
"""

import panel as pn
import plotly.express as px
import sankey as sk
import gapminder_api as gm

# Dimensions
CARD_WIDTH = 320

api = gm.GapminderAPI(gm.DATA_FILE_PATH)

def prettify(text):
    return text.replace("_", " ").title()

# CALLBACK FUNCTIONS
def get_scatter(continent, year, min_pop):
    '''Return Scatter plot'''
    df = api.get_subset(continent=continent, year=year, min_population=min_pop)

    fig = px.scatter(
        df,
        x=gm.GDP_COL,
        y=gm.LIFE_COL,
        size=gm.POP_COL,
        hover_name=gm.COUNTRY_COL,
        log_x=True,
        title=f"GDP vs Life Expectancy ({year})",
        labels={gm.GDP_COL: "GDP per Capita", gm.LIFE_COL: "Life Expectancy"},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig

def get_sankey(continent, year, min_pop, right, width, height):
    '''Return Sankey diagram'''
    if right == "GDP":
        right_col = "gdp_group"
    else:
        right_col = "life_group"

    flow_df = api.get_flow(
        continent=continent,
        left_layer=gm.LEFT_LAYER_COL_NAME,
        right_layer=right_col,
        min_population=min_pop,
        year=year
    )

    fig = sk.make_sankey(flow_df, gm.LEFT_LAYER_COL_NAME, right_col, "count", width=width, height=height)
    return fig

def main():
    # Loads javascript dependencies and configures Panel
    pn.extension("plotly")

    # Initialize API
    global api
    api.process_data()

    ymin, ymax = api.get_year_bounds()
    pmin, pmax = api.get_pop_bounds()

    # WIDGET DECLARATIONS
    # Filter widgets
    continent_slct = pn.widgets.Select(name="Continent", options=api.get_continents(), value="All")
    year_sldr = pn.widgets.IntSlider(name="Year", start=ymin, end=ymax, step=5, value=ymax)
    minpop_sldr = pn.widgets.IntSlider(
        name="Min Population",
        start=0,
        end=pmax,
        step=max(1, pmax // 50),
        value=0
    )

    right_cols_pretty = ["GDP", "Life Expectancy"]
    right_btns = pn.widgets.RadioButtonGroup(name="Sankey Right Layer", options=right_cols_pretty, value=right_cols_pretty[0])

    # Plotting widgets
    width_sldr = pn.widgets.IntSlider(name="Sankey Width", start=600, end=1500, step=100, value=900)
    height_sldr = pn.widgets.IntSlider(name="Sankey Height", start=450, end=1000, step=50, value=550)

    # CALLBACK BINDINGS (Connecting widgets to callback functions)
    scatter_plot = pn.bind(get_scatter, continent_slct, year_sldr, minpop_sldr)
    sankey_plot = pn.bind(get_sankey, continent_slct, year_sldr, minpop_sldr, right_btns, width_sldr, height_sldr)

    # DASHBOARD WIDGET CONTAINERS ("CARDS")
    search_card = pn.Card(
        pn.Column(
            continent_slct,
            year_sldr,
            minpop_sldr,
            right_btns
        ),
        title="Filters",
        width=CARD_WIDTH,
        collapsed=False
    )

    plot_card = pn.Card(
        pn.Column(
            width_sldr,
            height_sldr
        ),
        title="Sankey Dimensions",
        width=CARD_WIDTH,
        collapsed=True
    )

    # LAYOUT
    layout = pn.template.FastListTemplate(
        title="Gapminder Explorer Dashboard",
        sidebar=[search_card, plot_card],
        theme_toggle=False,
        main=[
            pn.Tabs(
                ("Scatter", scatter_plot),
                ("Sankey", sankey_plot),
                active=0
            )
        ],
        header_background="sienna"
    )
    return layout

app = main()
app.servable()

if __name__ == "__main__":
    app.show()