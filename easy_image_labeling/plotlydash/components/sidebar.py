import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from easy_image_labeling.plotlydash.components import ids

from easy_image_labeling.plotlydash.data.data_loader import load_data_from_store


def render(app: Dash) -> html.Div:
    @app.callback(Output(ids.SIDEBAR, "children"), Input(ids.DATA_STORE, "data"))
    def update_sidebar(json_data: str) -> html.Div:
        data_source = load_data_from_store(json_data)
        sidebar = html.Div(
            [
                html.H2(
                    app.title,
                    className="display-4",
                    style={"textAlign": "center", "font-variant": "small-caps"},
                ),
                html.H3(
                    "Labeling Analytics",
                    className="display-8",
                    style={"textAlign": "center"},
                ),
                html.Hr(),
                dbc.Nav(
                    [
                        html.A("Home", href="/", className="btn btn-primary"),
                        dcc.Dropdown(
                            options=[
                                {"label": value, "value": value}
                                for value in data_source.all_datasets
                            ],
                            multi=False,
                            id=ids.DATASET_DROPDOWN,
                            placeholder="Select dataset...",
                        ),
                    ],
                    vertical=True,  # well, that means not horizontically
                    pills=True,  # adds a blue square around the active selection
                ),
            ],
            id=ids.SIDEBAR,
            className="sidebar",
        )
        return sidebar

    return html.Div(id=ids.SIDEBAR)
