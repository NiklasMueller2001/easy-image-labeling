from __future__ import annotations
from dataclasses import dataclass
import pandas as pd


class DataSchema:
    ImageId = "ImageId"
    Dataset = "Dataset"
    ImageName = "ImageName"
    DatasetID = "DatasetID"
    LabelName = "LabelName"


@dataclass
class DataSource:
    _data: pd.DataFrame

    @property
    def all_datasets(self) -> list[str]:
        return self._data[DataSchema.Dataset].unique().tolist()

    @property
    def row_count(self) -> int:
        return self._data.shape[0]

    def filter_by_datasets(self, datasets: list[str]) -> DataSource:
        return DataSource(self._data[self._data[DataSchema.Dataset].isin(datasets)])

    def get_size_of_groups(self, by: str, *other_by: str) -> pd.DataFrame:
        return (
            self._data.groupby([by, *other_by]).size().to_frame("count").reset_index()
        )
