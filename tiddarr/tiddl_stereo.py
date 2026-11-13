"""Run the tiddl CLI, but always ask Tidal for the stereo stream.

For tracks that exist in stereo and Dolby Atmos, Tidal hands out the Atmos
stream whatever quality is requested, and tiddl's default Atmos filter then
skips the track. Tidal's own clients send `immersiveaudio=false` to get the
stereo master instead, so we add that to tiddl's stream request.

Quality fallback: Tidal answers a stream request with a valid body only when
the requested quality is actually offered for that track. If the stereo master
is not available at the requested quality, we retry with the next lower quality
instead of letting the track fail. (A track that has no stereo master at all,
e.g. an Atmos-only release, still fails on every rung — there is nothing to
fall back to.)

Usage: python3 -m tiddarr.tiddl_stereo download ...  (same arguments as tiddl)
"""
import sys

from tiddl.core.api import api as tiddl_api
from tiddl.core.api.api import DO_NOT_CACHE, TrackStream

# Tidal audio qualities, highest to lowest.
_QUALITY_ORDER = ["HI_RES_LOSSLESS", "LOSSLESS", "HIGH", "LOW"]


def _request_stereo(self, track_id, quality):
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


def _get_track_stream(self, track_id, quality):
    # Start at the requested quality and walk down to lower ones on failure.
    try:
        start = _QUALITY_ORDER.index(quality)
    except ValueError:
        start = 0

    last_error = None
    for q in _QUALITY_ORDER[start:]:
        try:
            stream = _request_stereo(self, track_id, q)
            if q != quality:
                print(
                    f"[tiddl_stereo] track {track_id}: no stereo stream at "
                    f"{quality}, fell back to {q}",
                    file=sys.stderr,
                    flush=True,
                )
            return stream
        except Exception as e:  # ApiError / JSON decode / network
            last_error = e

    # No stereo stream at any quality (e.g. an Atmos-only track).
    raise last_error


tiddl_api.TidalAPI.get_track_stream = _get_track_stream

if __name__ == "__main__":
    from tiddl.cli.app import app

    sys.argv[0] = "tiddl"
    sys.exit(app())
