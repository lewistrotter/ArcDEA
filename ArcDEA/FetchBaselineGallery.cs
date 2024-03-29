﻿using ArcGIS.Desktop.Core.Geoprocessing;
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

            // Create Landsat 5, 7, 8, 9 Collection 3 gallery item
            Add(new GalleryItem(text: "Landsat Baseline Collection 3", 
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null, 
                                tooltip: "Landsat 5, 7, 8, 9 Analysis Ready Data."));

            // Create Sentinel 2A, 2B Collection 3 gallery item
            Add(new GalleryItem(text:"Sentinel 2 Baseline Collection 3", 
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Sentinel 2A, 2B Analysis Ready Data."));

            _isInitialized = true;
        }

        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            if (item.Text == "Landsat Baseline Collection 3")
            {
                toolname = "ArcDEA.FetchLandsatBaselineData";
            }
            else if (item.Text == "Sentinel 2 Baseline Collection 3")
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
