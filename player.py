from subprocess import Popen, PIPE, DEVNULL


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