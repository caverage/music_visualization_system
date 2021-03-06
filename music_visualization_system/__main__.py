""" __main__ module of music_visualization_system"""

import atexit
import logging
import os

import numpy as np  # type:ignore
import psutil  # type:ignore
import typer

import music_visualization_system as mvs
import pymvf

from . import dmx, visualizations

logging.basicConfig(filename="mvs.log", level=20)
LOGGER = logging.getLogger(__name__)


@atexit.register
def _killtree(including_parent=True):
    LOGGER.critical("Stopping")
    parent = psutil.Process(os.getpid())
    for child in parent.children(recursive=True):
        child.kill()

    if including_parent:
        parent.kill()

    LOGGER.critical("Stopped")


def main(
    led_wall_server: str = typer.Argument(..., help="HOST:PORT of the LED Wall"),
    width: int = typer.Argument(..., help="width of LED Wall in pixels"),
    height: int = typer.Argument(..., help="height of LED Wall in pixels"),
    delay: float = typer.Option(0, help="height of LED Wall in pixels"),
) -> None:
    """ Main function of music_visualization_system"""

    bin_edges = pymvf.dsp.generate_bin_edges(40, 16000, 24)
    # FIXME: this should be what we pass to pymvf, not bin_edges
    bins = []
    previous_edge = bin_edges[0]
    for edge in bin_edges[1:]:
        bins.append((previous_edge, edge))
        previous_edge = edge

    buffer_discard_qty = 10
    buffer_processor = pymvf.PyMVF(
        bin_edges=bin_edges, buffer_discard_qty=buffer_discard_qty,
    )

    led_wall = visualizations.led_wall_bar_graph.LEDWall(
        led_wall_server, width, height, delay, bins, mvs.TIME_PER_BUFFER
    )

    # spider_3x3 = visualizations.spider_3x3.Spider3X3(delay)

    while True:
        buffer = buffer_processor()

        led_wall(buffer)
        # spider_3x3(buffer.timestamp, buffer.mono_intensity)


if __name__ == "__main__":
    typer.run(main)
