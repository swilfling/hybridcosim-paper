import os
from DataImport.dataimport import DataImport


def test_add_extension():
    # Extend filename
    filename = os.path.join("Data","Data","data")
    fname_new = DataImport.add_extension(filename,"txt")
    assert(fname_new == os.path.join("Data","Data","data.txt"))
    # No extension
    filename = os.path.join("Data", "Data", "data.hd5")
    fname_new = DataImport.add_extension(filename, "hd5")
    assert (fname_new == filename)
    # Change extension
    filename = os.path.join("Data", "Data", "data.hd5")
    fname_new = DataImport.add_extension(filename, "txt")
    assert (fname_new == os.path.join("Data","Data","data.txt"))


if __name__ == '__main__':
    test_add_extension()