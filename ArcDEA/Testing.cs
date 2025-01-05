﻿using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Contracts;
using ArcGIS.Desktop.Framework.Dialogs;
using System;

namespace ArcDEA
{
    internal class Testing : Button
    {
        protected override void OnClick()
        {
            string toolname = "ArcDEA.Testing";

            try
            {
                Geoprocessing.OpenToolDialog(toolname, null);
            }
            catch (Exception e)
            {
                MessageBox.Show("Could not find ArcDEA toolbox.");
                System.Diagnostics.Debug.WriteLine(e.Message);
            }
        }
    }
}
