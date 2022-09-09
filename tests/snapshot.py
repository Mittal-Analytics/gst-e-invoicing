import io
import os


class SnapshotChanged(Exception):
    pass


def compare_snapshot(output, snapshot_file):
    existing = ""
    if os.path.isfile(snapshot_file):
        with io.open(snapshot_file, "r", encoding="utf8") as tmp:
            existing = tmp.read()
    if existing == output:
        return True
    with open(snapshot_file, "wb") as tmp:
        if isinstance(output, str):
            tmp.write(output.encode("utf8", errors="ignore"))
        else:
            # output response from django is in bytes
            tmp.write(output)

    abs_path = "file://{}".format(os.path.abspath(snapshot_file))
    try:
        import webbrowser

        webbrowser.open(abs_path)
    except:
        pass
    raise SnapshotChanged("Snapshot has been updated")
