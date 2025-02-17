﻿using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;
using System;
using System.Windows.Media;

namespace ArcDEA
{
    internal class ConvertersGallery : Gallery
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

            // Create Convert NetCDF to Rasters gallery item
            Add(new GalleryItem(text: "Cube to Rasters",
                                icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                tooltip: "Convert a NetCDF to a folder of rasters."));

            // Create Convert NetCDF to Cloud Raster gallery item
            //Add(new GalleryItem(text: "Cube to Cloud Raster Format",
                                //icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
                                //tooltip: "Convert a NetCDF to the ESRI Cloud Raster Format."));

            //// Create Convert NetCDF to Geodatabase gallery item
            //Add(new GalleryItem(text: "NetCDF to Geodatabase",
            //                    icon: this.LargeImage != null ? ((ImageSource)this.LargeImage).Clone() : null,
            //                    tooltip: "Sentinel 2A, 2B Analysis Ready Data."));

            _isInitialized = true;

        }

        protected override void OnClick(GalleryItem item)
        {
            string toolname = null;

            if (item.Text == "Cube to Rasters")
            {
                toolname = "ArcDEA.ConvertNetCDFToRasters";
            }
            //else if (item.Text == "Cube to Cloud Raster Format")
            //{
                //toolname = "ArcDEA.ConvertNetCDFToCloudRaster";
            //}
            // else if (item.Text == "NetCDF to Geodatabase") {}

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
