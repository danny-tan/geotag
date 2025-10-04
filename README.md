# Multi-Photo Geotagger with Google Maps Extractor

A Python desktop application built with **Tkinter** for efficiently managing and adding GPS (geotagging) data to multiple JPEG photos using **EXIF** metadata. It includes utility functions to convert between DMS (Degrees, Minutes, Seconds) and decimal degrees, extract coordinates from Google Maps links, and list photos in a directory that are missing GPS data.

## Features

* **Single Photo Info:** View existing latitude and longitude for a selected JPEG and display its location on an interactive map.
* **Batch Geotagging:** Assign a single latitude and longitude to multiple selected JPEG files.
* **Google Maps Link Extraction:** Paste a Google Maps share link to automatically parse and extract the latitude and longitude.
* **Copy Coordinates:** Easily transfer the extracted coordinates from the Google Maps section to the batch geotagging section.
* **GPS-Missing File Lister:** Scan a selected folder and list all JPEG files that do not currently contain GPS data in their EXIF metadata.

---

## ⚙️ Installation

To run this application, you must have **Python 3.x** installed on your system.

### Prerequisites

You'll need to install the necessary Python libraries. Open your terminal or command prompt and run:

```bash
pip install pillow piexif pandas plotly
