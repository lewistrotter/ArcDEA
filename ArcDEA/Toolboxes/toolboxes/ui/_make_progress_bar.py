
# imports
import arcpy

from typing import Any
from dask.callbacks import Callback


class ArcProgressBar(Callback):
    """Custom ArcGIS Pro progress bar class."""

    def __init__(self):
        self.i = 0

    def _posttask(self, key, result, dsk, state, worker_id):
        n_done = len(state['finished'])
        n_task = sum(len(state[k]) for k in ['ready', 'waiting', 'running']) + n_done

        if n_done <= n_task:
            prg = int((n_done / n_task) * 100)

            if prg > self.i:
                self.i = prg
                arcpy.SetProgressorPosition(prg)

    def _finish(self, dsk, state, failed):
        self.i = 0


def make_progress_bar() -> Any:
    """
    Constructs a custom ArcGIS Pro progress bar for the UI.
    :return: ArcProgressBar object.
    """

    return ArcProgressBar()
