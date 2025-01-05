using System;
using System.Windows.Media;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;

namespace ArcDEA
{
    internal class RemoveOutliersGallery : Gallery
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

            // Create Hampel Filter gallery item
            //Add(new GalleryItem(text: "Hampel Filter",
                                //icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                //tooltip: "Detect, remove and fill outliers via Hampel Filter."));

            // Create Spike Filter gallery item
            Add(new GalleryItem(text: "Spike Filter",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Detect, remove and fill outliers via Spike Filter."));

            // Create Zscore Filter gallery item
            Add(new GalleryItem(text: "Z-score Filter",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Detect, remove and fill outliers via Hampel Filter."));

            _isInitialized = true;

        }

        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            //if (item.Text == "Hampel Filter")
            //{
                //toolname = "ArcDEA.OutliersHampelFilter";
            //}
            if (item.Text == "Spike Filter")
            {
                toolname = "ArcDEA.OutliersSpikeFilter";
            }
            else if (item.Text == "Z-score Filter")
            {
                toolname = "ArcDEA.OutliersZscoreFilter";
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
