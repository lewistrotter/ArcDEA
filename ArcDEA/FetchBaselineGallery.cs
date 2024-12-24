using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;
using ArcGIS.Desktop.Framework.Dialogs;
using System;
using System.Windows;
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
            Add(new GalleryItem(text: "Landsat Collection 3 (Baseline)", 
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null, 
                                tooltip: "Landsat 5, 7, 8 and 9 NBART Collection 3."));

            // Create Landsat Collection 3 (GeoMAD) gallery item
            Add(new GalleryItem(text: "Landsat Collection 3 (GeoMAD)",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Landsat 5, 7, 8 and 9 NBART Collection 3 GeoMAD."));

            // Create Sentinel 2A, 2B Collection 3 gallery item
            Add(new GalleryItem(text: "Sentinel 2 Collection 3 (Baseline)", 
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Sentinel 2A and 2B NBART Collection 3."));

            _isInitialized = true;
        }

        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            if (item.Text == "Landsat Collection 3 (Baseline)")
            {
                toolname = "ArcDEA.FetchLandsatBaselineData";
            }

            else if (item.Text == "Landsat Collection 3 (GeoMAD)")
            {
                toolname = "ArcDEA.FetchLandsatGeomedData";
            }

            else if (item.Text == "Sentinel 2 Collection 3 (Baseline)")
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
