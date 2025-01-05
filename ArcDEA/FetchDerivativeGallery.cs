using System;
using System.Windows.Media;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;

namespace ArcDEA
{
    internal class FetchDerivativeGallery : Gallery
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

            // Create Landsat Fractional Cover Version 2.5.0 gallery item
            Add(new GalleryItem(text: "DEA Landsat Fractional Cover",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Landsat Fractional Cover Version 2.5.0."));

            // Create Landsat Mangroves Version 4.0.0 gallery item
            Add(new GalleryItem(text: "DEA Landsat Mangrove Cover",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Landsat Magrove Cover Version 4.0.0."));

            _isInitialized = true;

        }
        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            if (item.Text == "DEA Landsat Fractional Cover")
            {
                toolname = "ArcDEA.FetchDeriveLandsatFractionCoverData";
            }

            else if (item.Text == "DEA Landsat Mangrove Cover")
            {
                toolname = "ArcDEA.FetchDeriveLandsatMangroveData";
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
