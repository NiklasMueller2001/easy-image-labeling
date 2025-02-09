from pathlib import Path


class Dataset:
    dataset_root_folder: str

    def __init__(self, address: str | Path) -> None:
        address = Path(address)
        address.is_relative_to
        if not (
            address.is_dir() and address.is_relative_to(Dataset.dataset_root_folder)
        ):
            raise ValueError("Invalid dataset path.")
        self.address = address
        self.files = list(self.address.glob("*"))

    @property
    def num_files(self) -> int:
        return len(self.files)


class DatasetManager:
    _instance = None
    managed_datasets: set[Dataset] = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatasetManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def add(cls, dataset: Dataset) -> None:
        cls.managed_datasets.add(dataset)

    @classmethod
    def remove(cls, dataset: Dataset) -> None:
        return cls.managed_datasets.remove(dataset)

    def __len__(self) -> int:
        return len(self.managed_datasets)

    def __str__(self) -> str:
        s = f"DatasetManager holding {len(self)} datasets:\n"
        for dataset in self.managed_datasets:
            s += f"{dataset.address} ({dataset.num_files} images)\n"
        return s
