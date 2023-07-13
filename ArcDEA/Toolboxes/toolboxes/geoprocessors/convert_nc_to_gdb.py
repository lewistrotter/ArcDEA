
def execute(
        parameters
        # messages  # TODO: use messages input?
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    # data_folder: str,
    # gdb: str,
    # product_name: str,
    # assets: Union[str, list],
    # epsg: int

    # gdb_path = os.path.dirname(gdb)
    # gdb_name = os.path.basename(gdb)
    #
    # arcpy.management.CreateFileGDB(out_folder_path=gdb_path,
    #                                out_name=gdb_name)
    #
    # arcpy.management.CreateMosaicDataset(in_workspace=gdb,
    #                                      in_mosaicdataset_name='ArcDEADataset',
    #                                      coordinate_system=epsg,
    #                                      product_definition='CUSTOM',
    #                                      product_band_definitions=assets)
    #
    # gdb_dataset = os.path.join(gdb, 'ArcDEADataset')
    # arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset=gdb_dataset,
    #                                            raster_type='Raster Dataset',
    #                                            input_path=data_folder,
    #                                            build_pyramids='BUILD_PYRAMIDS',
    #                                            calculate_statistics='CALCULATE_STATISTICS')
    #
    # arcpy.management.CalculateField(in_table=gdb_dataset,
    #                                 field='ProductName',
    #                                 expression=f"'{product_name}'")
    #
    # arcpy.management.AddField(in_table=gdb_dataset,
    #                           field_name='StdTime',
    #                           field_type='DATE')
    #
    # arcpy.management.CalculateField(in_table=gdb_dataset,
    #                                 field='StdTime',
    #                                 expression="datetime.datetime.strptime(!Name!.replace('R', ''), '%Y-%m-%d')")
    #
    # arcpy.md.BuildMultidimensionalInfo(in_mosaic_dataset=gdb_dataset,
    #                                    variable_field='ProductName',
    #                                    dimension_fields='StdTime',
    #                                    variable_desc_units=f"'{product_name}'")

    return


execute(None)


