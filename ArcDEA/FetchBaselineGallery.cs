using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;
using System;
using System.Windows.Media;

namespace ArcDEA
{
    internal class FetchBaselineGallery : Gallery
    {
        private bool _isInitialized;

        protected override void OnDropDownOpened()
        {
            Initialize();
            AlwaysFireOnClick = true;
        }

        private void Initialize()
        {
            if (_isInitialized)
                return;

            // Create Landsat Collection 3 (baseline) gallery item
            Add(new GalleryItem(text: "DEA Landsat Surface Reflectance", 
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null, 
                                tooltip: "Landsat 5, 7, 8 and 9 NBART Collection 3."));

            // Create Landsat Collection 3 (GeoMAD) gallery item
            Add(new GalleryItem(text: "DEA Landsat Surface Reflectance (GeoMAD)",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Landsat 5, 7, 8 and 9 NBART Collection 3 GeoMAD."));

            // Create Sentinel 2A, 2B Collection 3 gallery item
            Add(new GalleryItem(text: "DEA Sentinel 2 Surface Reflectance", 
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Sentinel 2A and 2B NBART Collection 3."));

            _isInitialized = true;
        }

        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            if (item.Text == "DEA Landsat Surface Reflectance")
            {
                toolname = "ArcDEA.FetchLandsatBaselineData";
            }

            else if (item.Text == "DEA Landsat Surface Reflectance (GeoMAD)")
            {
                toolname = "ArcDEA.FetchLandsatGeomedData";
            }

            else if (item.Text == "DEA Sentinel 2 Surface Reflectance")
            {
                toolname = "ArcDEA.FetchSentinel2BaselineData";
            }
            
            try
            {
                Geoprocessing.OpenToolDialog(toolname, null);
            }
            catch (Exception e)
            {
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Could not find ArcDEA toolbox.");
                System.Diagnostics.Debug.WriteLine(e.Message);
            }
        }
    }
}
