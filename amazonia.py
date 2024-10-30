import numpy as np
from PIL import Image
import sentinelhub
import myCopernicusCredentials

# SentinelHub Configuration Setup
config = sentinelhub.SHConfig()
config.sh_client_id = myCopernicusCredentials.client_id
config.sh_client_secret = myCopernicusCredentials.client_secret
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.save("cdse")  # Save this configuration under the name "cdse"

config = sentinelhub.SHConfig("cdse")  # Load the saved configuration

# Request bounding box coordinates for Area of Interest (AOI)
print("Enter the coordinates for the bounding box (AOI):")
print("For the Rondonia forest : (-63.97, -10.72, -64.47, -10.37)")
max_lon = float(input("Maximum Longitude: "))
min_lat = float(input("Minimum Latitude: "))
min_lon = float(input("Minimum Longitude: "))
max_lat = float(input("Maximum Latitude: "))
aoi_bbox = [max_lon, min_lat, min_lon, max_lat]

# Define AOI as a bounding box object in SentinelHub
aoi_bbox_sh = sentinelhub.BBox(bbox=aoi_bbox, crs=sentinelhub.CRS.WGS84)
resolution = 25  # Spatial resolution in meters
aoi_size = sentinelhub.bbox_to_dimensions(aoi_bbox_sh, resolution=resolution)

# SentinelHub Catalog instance for querying data
catalog = sentinelhub.SentinelHubCatalog(config=config)

# Define an evaluation script to retrieve true color (RGB) imagery
evalscript_true_color = """
    //VERSION=3
    function setup() {
        return {
            input: [{ bands: ["B02", "B03", "B04"] }],
            output: { bands: 3 }
        };
    }
    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02];
    }
"""

# Define date ranges for the data requests (before and after the change)
start_date_before = "2017-01-01"
end_date_before = "2017-06-30"
start_date_after = "2024-02-01"
end_date_after = "2024-07-17"

# Function to request, adjust brightness, save, and display images
def request_save(evalscript, aoi_bbox, start_date, end_date, resolution=25, brightness_factor=1, output_image_name=None):
    config = sentinelhub.SHConfig("cdse")
    aoi_bbox_sh = sentinelhub.BBox(bbox=aoi_bbox, crs=sentinelhub.CRS.WGS84)
    aoi_size = sentinelhub.bbox_to_dimensions(aoi_bbox_sh, resolution=resolution)

    # SentinelHub request
    request = sentinelhub.SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            sentinelhub.SentinelHubRequest.input_data(
                data_collection=sentinelhub.DataCollection.SENTINEL2_L2A.define_from(
                    name="s2", service_url="https://sh.dataspace.copernicus.eu"
                ),
                time_interval=(start_date, end_date),
                other_args={"dataFilter": {"mosaickingOrder": "leastCC"}}
            )
        ],
        responses=[sentinelhub.SentinelHubRequest.output_response("default", sentinelhub.MimeType.TIFF)],
        bbox=aoi_bbox_sh,
        size=aoi_size,  # WARNING: output size should be < (2500,2500)
        config=config,
    )
    imgs = request.get_data()

    # Apply brightness adjustment if needed
    if brightness_factor != 1:
        bright_image = np.uint8((imgs[0].astype(np.uint32) * brightness_factor).clip(0, 255))
    else:
        bright_image = imgs[0]
    
    # Convert to PIL Image and save if filename is specified
    pil_image = Image.fromarray(bright_image)
    if output_image_name is not None:
        pil_image.save(output_image_name)
    return bright_image

# Request and save/display true color images before and after change
true_color_before_array = request_save(
    evalscript_true_color, aoi_bbox, start_date_before, end_date_before, output_image_name="true_color_before.png", brightness_factor=6
)

true_color_after_array = request_save(
    evalscript_true_color, aoi_bbox, start_date_after, end_date_after, output_image_name="true_color_after.png", brightness_factor=6
)

# Define NDVI calculation script with color visualization
evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["B04", "B08", "dataMask"]
    }],
    output: { bands: 4 }
  };
}

const whiteGreen = [
  [1.000, 0xFFFFFF],  // White for low NDVI values
  [0.500, 0x000000],  // Black for mid-range values
  [0.000, 0x00FF00]   // Green for high NDVI values
]
  
let viz = new ColorGradientVisualizer(whiteGreen, -1.0, 1.0);

function evaluatePixel(samples) {
    let val =  ((samples.B08 + samples.B04)==0) ? 0 : ((samples.B08 - samples.B04) / (samples.B08 + samples.B04));  // NDVI calculation
    val = viz.process(val);
    val.push(samples.dataMask);
    return val;
}
"""

# Make NDVI requests for before and after change
request_ndvi_color = sentinelhub.SentinelHubRequest(
    evalscript=evalscript_ndvi,
    input_data=[
        sentinelhub.SentinelHubRequest.input_data(
            data_collection=sentinelhub.DataCollection.SENTINEL2_L2A.define_from(
                name="s2", service_url="https://sh.dataspace.copernicus.eu"
            ),
            time_interval=(start_date_after, end_date_after),
            other_args={"dataFilter": {"mosaickingOrder": "leastCC"}}
        )
    ],
    responses=[sentinelhub.SentinelHubRequest.output_response("default", sentinelhub.MimeType.PNG)],
    bbox=aoi_bbox_sh,
    size=aoi_size,  # WARNING: output size should be < (2500,2500)
    config=config,
)

ndvi_color_imgs = request_ndvi_color.get_data()

ndvi_before_array = request_save(
    evalscript_ndvi, aoi_bbox, start_date_before, end_date_before, output_image_name="ndvi_before.png", brightness_factor=0.8
)

ndvi_after_array = request_save(
    evalscript_ndvi, aoi_bbox, start_date_after, end_date_after, output_image_name="ndvi_after.png", brightness_factor=0.8
)

# Load NDVI images as numpy arrays for comparison
image1 = ndvi_before_array
image2 = ndvi_after_array

# Convert to numpy format for pixel manipulation
np_image1 = np.array(image1)
np_image2 = np.array(image2)

# Set NDVI threshold for detecting vegetation
threshold = 177  # Adjust as needed (0-255)

# Create masks for pixels above the vegetation threshold in both images
mask_image1 = np_image1[:, :, 1] < threshold  # Vegetation in the 'before' image
mask_image2 = np_image2[:, :, 1] < threshold  # Vegetation in the 'after' image

# Calculate the change in vegetation by counting pixels where vegetation disappeared
pixels_changed_count = np.abs(mask_image2.sum() - mask_image1.sum())

# Calculate area affected by vegetation loss
pixel_area_m2 = 25 * 25  # Each pixel represents 25x25 meters
area_lost_m2 = pixels_changed_count * pixel_area_m2
area_lost_ha = area_lost_m2 * 0.0001  # Convert m² to hectares

# Display vegetation loss metrics
print(f"Number of pixels with vegetation loss: {pixels_changed_count}")
print(f"Area of vegetation loss in square meters: {area_lost_m2}")
print(f"Area of vegetation loss in hectares: {area_lost_ha}")
print(f"Percentage of vegetation loss: {(mask_image2.sum() - mask_image1.sum()) * 100 / (2183 * 1557):.2f}%")