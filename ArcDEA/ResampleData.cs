using ArcGIS.Core.CIM;
using ArcGIS.Core.Data;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Catalog;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Editing;
using ArcGIS.Desktop.Extensions;
using ArcGIS.Desktop.Framework;
using ArcGIS.Desktop.Framework.Contracts;
using ArcGIS.Desktop.Framework.Dialogs;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Layouts;
using ArcGIS.Desktop.Mapping;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ArcDEA
{
    internal class ResampleData : Button
    {
        protected override void OnClick()
        {
            string toolname = "ArcDEA.ResampleData";

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
