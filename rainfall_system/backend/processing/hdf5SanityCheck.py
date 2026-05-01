import h5py

file = r"F:\Saurabh\dashboard\GPM\3B-HHR-L.MS.MRG.3IMERG.20251015-S000000-E002959.0000.V07B.HDF5"

def print_structure(name, obj):
    print(name)

with h5py.File(file, 'r') as f:
    f.visititems(print_structure)