
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import piexif
import os
import pandas as pd
import plotly.express as px
import webbrowser
import re
import ctypes

# Utility functions

def dms_to_deg(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def deg_to_dms_rational(deg_float):
    deg_abs = abs(deg_float)
    minutes, seconds = divmod(deg_abs * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    return [
        (int(degrees), 1),
        (int(minutes), 1),
        (int(seconds * 100), 100)
    ]

def extract_gps(image_path):
    try:
        exif_dict = piexif.load(image_path)
        gps = exif_dict.get("GPS", {})
        if gps:
            lat = dms_to_deg(gps[piexif.GPSIFD.GPSLatitude], gps[piexif.GPSIFD.GPSLatitudeRef].decode())
            lon = dms_to_deg(gps[piexif.GPSIFD.GPSLongitude], gps[piexif.GPSIFD.GPSLongitudeRef].decode())
            return lat, lon
    except Exception:
        pass
    return None, None

def geotag_image(image_path, lat, lon):
    try:
        exif_dict = piexif.load(image_path)
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: deg_to_dms_rational(lat),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: deg_to_dms_rational(lon),
        }
        exif_dict['GPS'] = gps_ifd
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_map(lat, lon):
    try:
        df = pd.DataFrame({
            "Latitude": [lat],
            "Longitude": [lon],
            "Label": [f"Photo Location: ({lat:.5f}, {lon:.5f})"]
        })
        fig = px.scatter_mapbox(
            df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Label",
            zoom=10,
            height=500
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        map_file = "map_preview.html"
        fig.write_html(map_file)
        webbrowser.open(map_file)
    except Exception as e:
        messagebox.showerror("Map Error", str(e))

def extract_lat_long_from_gmap(link):
    match = re.search(r'@([\d.\-]+),([\d.\-]+)', link)
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return lat, lon
        except Exception:
            return None, None
    match = re.search(r'!3d([\d.\-]+)!4d([\d.\-]+)', link)
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return lat, lon
        except Exception:
            return None, None
    return None, None

def has_no_gps_data(image_path):
    try:
        exif_dict = piexif.load(image_path)
        gps = exif_dict.get("GPS", {})
        return not (piexif.GPSIFD.GPSLatitude in gps and piexif.GPSIFD.GPSLongitude in gps)
    except Exception:
        return True

# GUI setup
ctypes.windll.shcore.SetProcessDpiAwareness(1) 
root = tk.Tk()
root.title("Multi-Photo Geotagger with Google Maps Extractor")

# Section 1
frame1 = tk.LabelFrame(root, text="Section 1: Single Photo Info", padx=10, pady=10)
frame1.pack(padx=10, pady=5, fill="x")
entry_single_path = tk.Entry(frame1, width=50)
entry_single_path.grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame1, text="Browse", command=lambda: browse_single()).grid(row=0, column=1, padx=5)
label_lat = tk.Label(frame1, text="Latitude: NA")
label_lat.grid(row=1, column=0, sticky="w")
label_lon = tk.Label(frame1, text="Longitude: NA")
label_lon.grid(row=2, column=0, sticky="w")

def browse_single():
    file_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg;*.jpeg")])
    if file_path:
        entry_single_path.delete(0, tk.END)
        entry_single_path.insert(0, file_path)
        lat, lon = extract_gps(file_path)
        label_lat.config(text=f"Latitude: {lat:.5f}" if lat is not None else "Latitude: NA")
        label_lon.config(text=f"Longitude: {lon:.5f}" if lon is not None else "Longitude: NA")
        if lat is not None and lon is not None:
            show_map(lat, lon)

# Section 2
frame2 = tk.LabelFrame(root, text="Section 2: Geotag Multiple Photos", padx=10, pady=10)
frame2.pack(padx=10, pady=5, fill="x")
entry_multi_paths = tk.Entry(frame2, width=50)
entry_multi_paths.grid(row=0, column=0, padx=5, pady=5)

tk.Button(frame2, text="Browse Photos", command=lambda: browse_multiple()).grid(row=0, column=1, padx=5)
entry_lat = tk.Entry(frame2)
entry_lat.grid(row=1, column=0, padx=5, pady=5)
entry_lat.insert(0, "Enter Latitude")

entry_lon = tk.Entry(frame2)
entry_lon.grid(row=2, column=0, padx=5, pady=5)
entry_lon.insert(0, "Enter Longitude")

def browse_multiple():
    files = filedialog.askopenfilenames(filetypes=[("JPEG files", "*.jpg;*.jpeg")])
    if files:
        entry_multi_paths.delete(0, tk.END)
        entry_multi_paths.insert(0, ";".join(files))

def assign_to_all():
    try:
        paths = entry_multi_paths.get().split(";")
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
        for path in paths:
            if os.path.exists(path):
                geotag_image(path, lat, lon)
        messagebox.showinfo("Success", "Geotagging completed for all selected photos.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(frame2, text="Assign Lat/Long to All", command=assign_to_all).grid(row=3, column=0, pady=10)

# Section 3
frame3 = tk.LabelFrame(root, text="Section 3: Extract Lat/Long from Google Maps Link", padx=10, pady=10)
frame3.pack(padx=10, pady=5, fill="x")

entry_gmap = tk.Entry(frame3, width=70)
entry_gmap.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
entry_gmap.insert(0, "Paste Google Maps link here")

label_gmap_lat = tk.Label(frame3, text="Latitude: NA")
label_gmap_lat.grid(row=1, column=0, sticky="w")

label_gmap_lon = tk.Label(frame3, text="Longitude: NA")
label_gmap_lon.grid(row=2, column=0, sticky="w")

def extract_gmap_latlon():
    link = entry_gmap.get()
    lat, lon = extract_lat_long_from_gmap(link)
    label_gmap_lat.config(text=f"Latitude: {lat:.7f}" if lat is not None else "Latitude: NA")
    label_gmap_lon.config(text=f"Longitude: {lon:.7f}" if lon is not None else "Longitude: NA")
    return lat, lon

def copy_gmap_to_section2():
    lat, lon = extract_gmap_latlon()
    if lat is not None and lon is not None:
        entry_lat.delete(0, tk.END)
        entry_lat.insert(0, str(lat))
        entry_lon.delete(0, tk.END)
        entry_lon.insert(0, str(lon))
    else:
        messagebox.showinfo("Info", "No valid latitude/longitude found in the link.")

tk.Button(frame3, text="Extract Lat/Long", command=extract_gmap_latlon).grid(row=0, column=2, padx=5)
tk.Button(frame3, text="Copy to Section 2", command=copy_gmap_to_section2).grid(row=3, column=0, pady=10)

# Section 4
frame4 = tk.LabelFrame(root, text="Section 4: List Photos Without GPS Data", padx=10, pady=10)
frame4.pack(padx=10, pady=5, fill="x")
entry_folder = tk.Entry(frame4, width=50)
entry_folder.grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame4, text="Browse Folder", command=lambda: browse_folder()).grid(row=0, column=1, padx=5)
listbox_files = tk.Listbox(frame4, width=60, height=10)
listbox_files.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

label_file_count = tk.Label(frame4, text="File Count: 0")
label_file_count.grid(row=2, column=0, sticky="w")

status_label = tk.Label(frame4, text="")
status_label.grid(row=3, column=0, sticky="w")

def browse_folder():
    folder_path = filedialog.askdirectory()
    no_gps_count = 0
    if not os.path.isdir(folder_path):
        messagebox.showerror("Invalid Folder", "The selected path is not a valid folder.")
        return
    entry_folder.delete(0, tk.END)
    entry_folder.insert(0, folder_path)
    listbox_files.delete(0, tk.END)
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            full_path = os.path.join(folder_path, filename)
            if has_no_gps_data(full_path):
                listbox_files.insert(tk.END, filename)
                no_gps_count += 1
                
    label_file_count.config(text=f"File Count: {no_gps_count}" if no_gps_count is not None else "File Count: 0")
    
root.mainloop()
