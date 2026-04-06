"""
Visualization Library for Sankey Diagrams
Includes wrapper functions for plots.
"""

import pandas as pd
import plotly.graph_objects as go


def _code_mapping(df, src, targ):
    """Map labels in src and targ columns to integers.
    Return the df and labels.
    """

    # collect all the unique src and target strings
    all_labels = pd.concat([df[src], df[targ]]).unique()

    # assign each one a number starting from 0

    # create a mapping (dict)
    labels = {}
    for i in range(len(all_labels)):
        labels[all_labels[i]] = i

    # update the src and targ columns in the df
    df = df.copy()
    df[src] = df[src].map(lambda val: labels[val])
    df[targ] = df[targ].map(lambda val: labels[val])
    return df, labels


def make_sankey(df, src, targ, vals, **kwargs):
    """Generate a sankey diagram from dataframe.

    Arg:
      line_width : width of line for links (optional)
      width      : figure width (default 800)
      height     : figure height (default 600)
    """
    df, mapping = _code_mapping(df, src, targ)

    line_width = kwargs.get("line_width", None)
    width = kwargs.get("width", 800)
    height = kwargs.get("height", 600)
    link = {
        "source": df[src], "target": df[targ], "value": df[vals],
        "line": {"width": line_width}}
    node = {"label": list(mapping.keys())}
    fig = go.Figure(go.Sankey(link=link, node=node))
    fig.update_layout(
        autosize=False,
        width=width,
        height=height)
    return fig