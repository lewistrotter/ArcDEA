using ArcGIS.Desktop.Framework.Contracts;
using ArcGIS.Desktop.Framework.Dialogs;
using System;
using System.Diagnostics;
using System.Windows.Media;

namespace ArcDEA
{
    internal class SettingsGallery : Gallery
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


            // Create GitHub gallery item
            Add(new GalleryItem(text: "GitHub Page",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Visit the ArcDEA GitHub page. Give us a star!"));

            // Create About gallery item
            //Add(new GalleryItem(text: "About ArcDEA",
            //                    icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
            //                    tooltip: "About the ArcDEA add-in."));

            _isInitialized = true;
        }

        protected override void OnClick(GalleryItem item)
        {
            if (item.Text == "GitHub Page")
            {
                try 
                {
                    // open system browser to github page
                    string url = "https://github.com/lewistrotter/ArcDEA";
                    var process = new ProcessStartInfo(url) { UseShellExecute = true };
                    System.Diagnostics.Process.Start(process);
                }
                catch (Exception e)
                {
                    MessageBox.Show("Could not reach GitHub page.");
                    System.Diagnostics.Debug.WriteLine(e.Message);
                }
            }
        }
    }
}
