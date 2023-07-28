# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""PASTIS datamodule."""

import abc
from typing import Any, Optional, Sequence

import torch
from torch import Tensor

from ..datasets.pastis import (
    PASTIS,
    PASTISInstanceSegmentation,
    PASTISSemanticSegmentation,
)
from .geo import NonGeoDataModule


def collate_fn(batch: list[dict[str, Tensor]]) -> dict[str, Any]:
    """Custom object detection collate fn to handle variable number of boxes.

    Args:
        batch: list of sample dicts return by dataset
    Returns:
        batch dict output
    """
    output: dict[str, Any] = {}
    output["image"] = [sample["image"] for sample in batch]
    output["mask"] = [sample["mask"] for sample in batch]
    if "boxes" in batch[0]:
        output["boxes"] = [sample["boxes"] for sample in batch]
        output["label"] = [sample["label"] for sample in batch]
    return output


class PASTISDataModule(NonGeoDataModule, abc.ABC):
    """LightningDataModule implementation for the PASTIS dataset."""

    # (S1A, S1D, S2)
    band_means = torch.tensor(
        [
            -10.930951118469238,
            -17.348514556884766,
            6.417511940002441,
            -11.105852127075195,
            -17.502077102661133,
            6.407216548919678,
            1165.9398193359375,
            1375.6534423828125,
            1429.2191162109375,
            1764.798828125,
            2719.273193359375,
            3063.61181640625,
            3205.90185546875,
            3319.109619140625,
            2422.904296875,
            1639.370361328125,
        ]
    )
    band_stds = torch.tensor(
        [
            3.285966396331787,
            3.2129523754119873,
            3.3421084880828857,
            3.376193046569824,
            3.1705307960510254,
            3.34938383102417,
            1942.6156005859375,
            1881.9234619140625,
            1959.3798828125,
            1867.2239990234375,
            1754.5850830078125,
            1769.4046630859375,
            1784.860595703125,
            1767.7100830078125,
            1458.963623046875,
            1299.2833251953125,
        ]
    )

    def __init__(
        self,
        dataset_class: type[PASTIS],
        batch_size: int = 64,
        num_workers: int = 0,
        train_folds: Sequence[int] = (0, 1, 2),
        val_folds: Sequence[int] = (3,),
        test_folds: Sequence[int] = (4,),
        **kwargs: Any,
    ) -> None:
        """Initialize a LightningDataModule for PASTIS based DataLoaders.

        Args:
            dataset_class: Either `PASTISSemanticSegmentation` or
                `PASTISInstanceSegmentation`
            batch_size: Size of each mini-batch.
            num_workers: Number of workers for parallel data loading.
            train_folds: Which folds to use for training
            val_folds: Which folds to use for validation
            test_folds: Which folds to use for testing
            **kwargs: Additional keyword arguments passed to
                :class:`~torchgeo.datasets.PASTIS`.
        """
        if "folds" in kwargs:
            print("`folds` was specified but will be ignored, use `*_folds` instead.")
        super().__init__(dataset_class, batch_size, num_workers, **kwargs)
        self.train_folds = train_folds
        self.val_folds = val_folds
        self.test_folds = test_folds

    def setup(self, stage: Optional[str] = None) -> None:
        """Initialize the main ``Dataset`` objects.

        This method is called once per GPU per run.

        Args:
            stage: stage to set up
        """
        raise NotImplementedError


class PASTISSemanticSegmentationDataModule(PASTISDataModule):
    """LightningDataModule implementation for the PASTISSemanticSegmentation dataset."""

    def __init__(self, **kwargs: Any) -> None:
        """Initializes a LightningDataModule for PASTISSemanticSegmentation."""
        super().__init__(PASTISSemanticSegmentation, **kwargs)
        self.collate_fn = collate_fn

    def setup(self, stage: Optional[str] = None) -> None:
        """Initialize the main ``Dataset`` objects.

        This method is called once per GPU per run.

        Args:
            stage: stage to set up
        """
        self.train_dataset = PASTISSemanticSegmentation(
            **self.kwargs, folds=self.train_folds
        )
        self.val_dataset = PASTISSemanticSegmentation(
            **self.kwargs, folds=self.val_folds
        )
        self.test_dataset = PASTISSemanticSegmentation(
            **self.kwargs, folds=self.test_folds
        )


class PASTISInstanceSegmentationDataModule(PASTISDataModule):
    """LightningDataModule implementation for the PASTISInstanceSegmentation dataset."""

    def __init__(self, **kwargs: Any) -> None:
        """Initializes a LightningDataModule for PASTISInstanceSegmentation."""
        if "folds" in kwargs:
            print("Folds was specified, but will be ignored.")
            del kwargs["folds"]
        super().__init__(PASTISInstanceSegmentation, **kwargs)
        self.collate_fn = collate_fn

    def setup(self, stage: Optional[str] = None) -> None:
        """Initialize the main ``Dataset`` objects.

        This method is called once per GPU per run.

        Args:
            stage: stage to set up
        """
        self.train_dataset = PASTISInstanceSegmentation(
            **self.kwargs, folds=self.train_folds
        )
        self.val_dataset = PASTISInstanceSegmentation(
            **self.kwargs, folds=self.val_folds
        )
        self.test_dataset = PASTISInstanceSegmentation(
            **self.kwargs, folds=self.test_folds
        )
