from dash import Dash, html, dcc
from easy_image_labeling.plotlydash.components import ids
from easy_image_labeling.plotlydash.components import sidebar
from easy_image_labeling.plotlydash.components import pie_chart


def render(app: Dash):
    _location = dcc.Location(id=ids.URL, pathname="/analytics", refresh=False)
    _data_store = dcc.Store(id=ids.DATA_STORE, storage_type="session")
    _side_bar = sidebar.render(app)
    _pie_chart = pie_chart.render(app)
    return html.Div(
        [_location, _data_store, _side_bar, _pie_chart],
        id=ids.LAYOUT,
    )
