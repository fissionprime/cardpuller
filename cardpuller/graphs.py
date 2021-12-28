import plotly.graph_objects as go
from plotly.io import to_html
import plotly.express as px


class BoxHist(go.Figure):
    """Create a histogram with integer bins in the range (0,box_size] and
    returns the figure as an HTML string. An optional theoretical probability
    distribution may be included. This theoretical distribution is assumed to
    be normalized to a value of 1."""

    def __init__(
        self,
        data,
        box_size,
        theoretical=None,
        legend=False,
        name="Simulated",
        id=None,
        cdn=False,
        cumulative=False
    ):
        super().__init__()
        self._config = {"displaylogo": False, "editable": False, "showLink": False}
        self._cdn = "cdn" if cdn else False
        self._id = id if id else None
        self.add_trace(
            go.Histogram(
                x=data,
                xbins=dict(start=1, end=box_size + 1, size=1),
                autobinx=False,
                histnorm="percent",
                showlegend=legend,
                name=name,
                cumulative_enabled=cumulative
            )
        )
        if theoretical:
            bins = [i for i in range(1, box_size + 1)]
            theoretical = [i * 100 for i in theoretical]  # convert values to percent
            self.add_trace(
                go.Scatter(
                    y=theoretical,
                    x=bins,
                    name="Theoretical",
                    showlegend=legend,
                    mode="lines",
                )
            )

    def to_html(self):
        return to_html(
            self,
            config=self._config,
            include_plotlyjs=self._cdn,
            full_html=False,
            div_id=self._id,
        )


def cdf_plot(data, box_size, theoretical):
    config = {"displaylogo": False, "editable": False, "showLink": False}
    fig = px.ecdf(x=data)
    return to_html(fig, config=config, include_plotlyjs=False, full_html=False)


"""Aggregate results page with stats for each rarity in each box size across all trials (compared to theoretical)
dark mode
change session to cookies
look into https"""
