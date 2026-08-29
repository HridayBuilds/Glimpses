import io
import zipfile


def _is_junk_entry(filename):
    basename = filename.rsplit("/", 1)[-1]
    return filename.startswith("__MACOSX/") or basename.startswith("._") or basename == ".DS_Store"


def extract_entries(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for info in archive.infolist():
            if info.is_dir() or _is_junk_entry(info.filename):
                continue
            yield info.filename, archive.read(info.filename)
