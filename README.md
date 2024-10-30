# Deforestation-in-Rondinia

# SentinelHub Vegetation Analysis Script

This Python script performs a vegetation analysis using SentinelHub's API to retrieve satellite imagery, calculate the Normalized Difference Vegetation Index (NDVI), and quantify vegetation loss in a given area over time. The script is configured to connect to the Copernicus Data Space Ecosystem and requires SentinelHub and Copernicus credentials for access.

## Requirements

- Python 3.10+
- Libraries:
  - `numpy`
  - `PIL` (from `Pillow`)
  - `sentinelhub-py`
  - Custom `myCopernicusCredentials` module (contains Copernicus client credentials)

## Setup

1. **Copernicus Credentials**: Ensure your `myCopernicusCredentials.py` file contains valid Copernicus credentials:
   ```python
   client_id = "YOUR_CLIENT_ID"
   client_secret = "YOUR_CLIENT_SECRET"
    ```
    
2.**Install Required Libraries**:
   ```bash
   pip install numpy pillow sentinelhub
   ```

3.**Configure SentinelHub**: The script configures SentinelHub to use the Copernicus Data Space Ecosystem as the data source.

## Usage

1.**Define Area of Interest (AOI):**

- Input the bounding box coordinates for the target AOI. For example, the coordinates for the Rondonia forest are (-63.97, -10.72, -64.47, -10.37).

2.**Retrieve True Color and NDVI Imagery:**

- The script fetches "before" and "after" imagery of the AOI for two specific time periods:
    - Before: 2017-01-01 to 2017-06-30
    - After: 2024-02-01 to 2024-07-17
- The images are saved as true_color_before.png, true_color_after.png, ndvi_before.png, and ndvi_after.png.

3.**Calculate Vegetation Loss:**

- NDVI values are calculated for each pixel, and a custom threshold is used to detect vegetation presence or loss.
- The script quantifies vegetation loss by counting the number of pixels where vegetation is no longer present and converting this count to an area measurement (in square meters and hectares).

## Outputs
- Images: True color and NDVI images (.png files) for each time period.
- Vegetation Loss Metrics:
    - Number of pixels with vegetation loss
    - Total area of vegetation loss in square meters and hectares
    - Percentage of vegetation loss

## Example Run

```bash
python amazonia.py
```

On running the script, the metrics will display the estimated vegetation loss in the defined AOI, enabling you to observe changes in vegetation cover over time.
