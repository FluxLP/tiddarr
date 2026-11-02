"""Run the tiddl CLI, but always ask Tidal for the stereo stream.

For tracks that exist in stereo and Dolby Atmos, Tidal hands out the Atmos
stream whatever quality is requested, and tiddl's default Atmos filter then
skips the track. Tidal's own clients send `immersiveaudio=false` to get the
stereo master instead, so we add that to tiddl's stream request.

Usage: python3 -m tiddarr.tiddl_stereo download ...  (same arguments as tiddl)
"""
import sys

from tiddl.core.api import api as tiddl_api
from tiddl.core.api.api import DO_NOT_CACHE, TrackStream


def _get_track_stream(self, track_id, quality):
    return self.client.fetch(
        TrackStream,
        f"tracks/{track_id}/playbackinfopostpaywall",
        {
            "audioquality": quality,
            "playbackmode": "STREAM",
            "assetpresentation": "FULL",
            "immersiveaudio": "false",
        },
        expire_after=DO_NOT_CACHE,
    )


tiddl_api.TidalAPI.get_track_stream = _get_track_stream

if __name__ == "__main__":
    from tiddl.cli.app import app

    sys.argv[0] = "tiddl"
    sys.exit(app())
