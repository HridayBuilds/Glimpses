import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Converter.zip_extractor import extract_entries


def _make_zip(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for filename, content in entries.items():
            archive.writestr(filename, content)
    return buffer.getvalue()


def test_extract_entries_skips_macosx_and_dotfiles():
    zip_bytes = _make_zip(
        {
            "Trip/IMG_1.jpg": b"real photo",
            "__MACOSX/Trip/._IMG_1.jpg": b"appledouble",
            "Trip/.DS_Store": b"finder metadata",
            "__MACOSX/Trip/._.DS_Store": b"appledouble ds_store",
        }
    )

    entries = list(extract_entries(zip_bytes))

    assert entries == [("Trip/IMG_1.jpg", b"real photo")]


def test_extract_entries_skips_cross_platform_metadata_without_dropping_photos():
    zip_bytes = _make_zip(
        {
            "Trip/IMG_1.jpg": b"first photo",
            "Trip/IMG_2.HEIC": b"second photo",
            "Trip/Thumbs.db": b"windows thumbnails",
            "Trip/Nested/THUMBS.DB": b"windows thumbnails",
            "Trip/desktop.ini": b"windows folder settings",
            "Trip/Nested/Desktop.INI": b"windows folder settings",
            "Trip/.nomedia": b"android media marker",
            "Trip/Nested/.NOMEDIA": b"android media marker",
            "Trip/IMG_1.AAE": b"ios edit sidecar",
            "Trip/Nested/IMG_2.aae": b"ios edit sidecar",
            "Trip/notes.txt": b"unrecognized file should still be processed",
        }
    )

    assert list(extract_entries(zip_bytes)) == [
        ("Trip/IMG_1.jpg", b"first photo"),
        ("Trip/IMG_2.HEIC", b"second photo"),
        ("Trip/notes.txt", b"unrecognized file should still be processed"),
    ]
