# # this was a Download method
# def get_percent_overlap_with_bbox(
#         self,
#         query_bbox: tuple[float, float, float, float],
#         query_epsg: int,
# ) -> float:
#     """
#     Calculates the percentage in which the download's feature
#     extent intersects with a query bbox area.
#     :param query_bbox: Tuple of floats representing user bbox.
#     :param query_epsg: Integer representing user bbox EPSG code.
#     :return: Float indicating percentage features overlap.
#     """
#
#     query_poly = Conversions.convert_bbox_to_poly(query_bbox, query_epsg)
#     download_poly = Conversions.convert_coords_to_poly(self.coordinates, 4326)
#
#     intersect = query_poly.intersect(download_poly, 4)  # 4 represents polygon
#     percent_intersect = intersect.area / query_poly.area * 100
#
#     return percent_intersect


# this doesn't work well, dea bboxes don't match actual pixel extents well
# instead, count 0s in mask band before invalid are counted
# downloads = Web.remove_inadequate_overlaps(downloads,
# stac_bbox,
# 4326,
# in_min_percentage_overlap)