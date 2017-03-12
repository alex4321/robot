from subprocess import Popen, PIPE, DEVNULL
from pydub import AudioSegment
from io import BytesIO


def play(content):
    """
    Play sound
    :param content: sound bytes
    :type content: bytes
    """
    proc = Popen(["mplayer", "-cache", "1024", "-"], stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)
    proc.stdin.write(content)
    proc.stdin.flush()
    proc.stdin.close()
    proc.wait()


def play_list(records):
    """
    Play list of MP3 records
    :param records: list of sound bytes
    :type records: list[bytes]
    """
    def _record_segment(record):
        container = BytesIO()
        container.write(record)
        container.seek(0)
        return AudioSegment.from_mp3(container)

    if len(records) == 0:
        return

    audio = _record_segment(records[0])
    for i in range(1, len(records)):
        audio += _record_segment(records[i])
    container = BytesIO()
    audio.export(container, "mp3")
    container.seek(0)
    play(container.read())