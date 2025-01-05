using System;
using System.Windows.Media;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;

namespace ArcDEA
{
    internal class AggregateGallery : Gallery
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

            Add(new GalleryItem(text: "Resample (Time)",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Resample a cube by its time dimension."));

            _isInitialized = true;
        }

        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            if (item.Text == "Resample (Time)")
            {
                toolname = "ArcDEA.AggregateResampleTime";
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
