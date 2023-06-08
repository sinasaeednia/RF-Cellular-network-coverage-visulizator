# function make_KML

def make_KML(location, distance_map):
    import numpy as np
    import math
    from scipy.interpolate import interp1d

    with open(location+'.kml', 'w') as kmlfile:
        lat = 53.408426
        long = 29.472164
        azimuth = 352.7
        scale = 0.5
        tower_hieght = 24
        pie_chunks = 6
        offset = 0
        span = 120
        b_interpolate = True
        alpha = 100
        earthRadius = 6367  # radius in km
        # distance_map = [0.4, 0.7, 1.1, 1.5, 1.8, 2.2, 2.5, 2.9, 3.3, 3.6, 4.4, 5.1, 5.8, 6.5, 7.3, 8.0, 8.7, 9.4, 10.2, 10.9,
        #                 12.0, 13.1, 14.1, 15.2, 16.3, 17.4, 18.5, 19.6, 20.7, 21.8, 23.2, 24.7, 26.1, 27.6, 29.0, 30.5, 31.9,
        #                 33.4, 34.8, 36.3]
        coverage = [0, 0, 6, 578, 23, 0, 1775, 1061, 0, 0, 6, 2, 1, 0, 0, 0, 60, 2911, 225, 257, 0, 3, 149, 0, 0, 0, 0,
                    0, 0, 0,
                    0, 0, 1, 90, 616, 0, 0, 7, 1, 1]

        def calculateCoord(origin, brng, arcLength):
            # convert degree to radian
            # arcLength /= 2.4
            lat1 = origin[0] * math.pi / 180
            lon1 = origin[1] * math.pi / 180

            centralAngle = arcLength / earthRadius

            lat2 = math.asin(
                math.sin(lat1) * math.cos(centralAngle) + math.cos(lat1) * math.sin(centralAngle) * math.cos(
                    math.pi / 180 * (brng)));
            lon2 = lon1 + math.atan2(math.sin(math.pi / 180 * (brng)) * math.sin(centralAngle) * math.cos(lat1),
                                     math.cos(centralAngle) - math.sin(lat1) * math.sin(lat2)) / 2

            return [lat2 * 180 / math.pi, lon2 * 180 / math.pi]

        if b_interpolate == True:
            xnew = np.linspace(0, len(coverage) * 350, num=len(coverage), endpoint=True)
            f2 = interp1d(np.linspace(0, len(coverage) * 350, num=len(coverage), endpoint=True), coverage, kind='cubic')
            coverage2 = f2(xnew)
            coverage = coverage2

        coverage_sum = sum(coverage)
        a = np.array(coverage)
        b = (a / coverage_sum * 100)
        coverage_percent = b.tolist()
        coverage_percent = [(i > 0) * i for i in coverage_percent]

        def color(percent, alpha=alpha, abs_value=id(0)):
            Red = 0xff
            Green = 0xff
            Blue = 0xff
            Red2 = 0
            Green2 = 0
            Blue2 = 0
            # if not (abs_value == id(0)):
            # z = np.arange(0, 105, 5)
            # color = np.int64([0, 0, 0, 0.333333333, 0.666666667, 1, 0.833333333, 21846, 43691.16667, 65536.33333, 54613.5,
            #          43690.66667, 32768, 21845.33333, 10959.2381, 73.14285714, 109.7142857, 146.2857143, 182.8571429,
            #          219.4285714, 256])
            # f2 = interp1d(z, color, kind='cubic')
            # output = hex(int(f2(percent))) if int(f2(np.int64(percent))) >= 0 else 0x0
            # return hex(int(alpha)).replace("0x", "").zfill(2) + f'{output:0>8}'.replace('0x', '')[-6:]
            # else:
            if percent < 50:
                percent *= 2
                Red2 = (100 - percent) / 100 * Red
                Green2 = percent / 100 * Green
            else:
                percent = (percent - 50) * 2
                Green2 = (100 - percent) / 100 * Green
                Blue2 = percent / 100 * Blue

            # https: // developers.google.com / kml / documentation / kmlreference  # colorstyle
            return hex(int(alpha)).replace("0x", "").zfill(2) + \
                   hex(int(Blue2)).replace("0x", "").zfill(2) + \
                   hex(int(Green2)).replace("0x", "").zfill(2) + \
                   hex(int(Red2)).replace("0x", "").zfill(2)

        def kml_shape_create(lat, long, azimuth=0, diameter=distance_map[len(coverage) - 1], pie_chunks=5, span=120,
                             reverse=False):
            polygon_inner = []
            polygon_outer = []
            # polygon_inner.append([[lat], [long]])

            if reverse == False:
                for i in range(0, pie_chunks + 1):
                    j = 90 - azimuth + i * span / pie_chunks - span / 2
                    # rotation_matrix = [[math.cos(j * math.pi / 180), -1 * math.sin(j * math.pi / 180)], \
                    #                    [math.sin(j * math.pi / 180), math.cos(j * math.pi / 180), ]]
                    # polygon_inner.append(
                    #     (np.add(np.matmul(rotation_matrix, [[diameter], [diameter]]).tolist(), [[lat], [long]])).tolist())
                    polygon_inner.append(calculateCoord([lat, long], j, diameter))
            else:
                for i in range(0, pie_chunks + 1):
                    j = 90 - azimuth - i * span / pie_chunks + span / 2
                    # rotation_matrix = [[math.cos(j * math.pi / 180), -1 * math.sin(j * math.pi / 180)],
                    #                    [math.sin(j * math.pi / 180), math.cos(j * math.pi / 180), ]]
                    # polygon_inner.append(
                    #     (np.add(np.matmul(rotation_matrix, [[diameter], [diameter]]).tolist(), [[lat], [long]])).tolist())
                    polygon_inner.append(calculateCoord([lat, long], j, diameter))

            # polygon_inner.append([[lat], [long]])
            # polygon_inner.append([[lat], [long]])
            return polygon_inner

        descript = ""
        kmlfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\">")
        kmlfile.write("<Document>")

        for TTL in range(0, len(coverage) - 1):
            kmlfile.write("<Placemark>")
            kmlfile.write("<Style> ")
            kmlfile.write("\t<LineStyle>")
            kmlfile.write(f"\t\t<color> {color(abs(coverage_percent[TTL] * 100 / max(coverage_percent)), alpha=0)} \
                          </color>")
            # kmlfile.write("\t\t<width>", 4, "</width>")
            kmlfile.write("\t</LineStyle>")
            kmlfile.write(f"\t<PolyStyle>\n\t\t<color> {color(abs(coverage_percent[TTL] * 100 / max(coverage_percent)))} \
                          </color>")
            kmlfile.write("\t\t<fill>" + str(1) + "</fill>\n\t</PolyStyle>")
            kmlfile.write("</Style>")

            kmlfile.write(f"\t<name> {location} </name> \n<description><![CDATA[")
            kmlfile.write(descript)
            kmlfile.write("]]></description>")
            kmlfile.write("<Polygon>")
            kmlfile.write(f"\t\t<extrude> {scale * tower_hieght * coverage_percent[TTL]} </extrude>")
            kmlfile.write("\t\t<tessellate>" + str(1) + "</tessellate>\t\t")
            kmlfile.write(f"\t\t<altitudeMode> {'ClampedToGround' if offset == 0 else 'relativeToGround'} \
                          </altitudeMode>")  # "absolute"
            kmlfile.write("\t\t<outerBoundaryIs>\n\t\t<LinearRing>\n\t\t<coordinates>")

            tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL + 1], pie_chunks=pie_chunks, span=span)

            # kmlfile.write(str(tmp).replace("]], [[",
            #                        "," + str(offset + scale * tower_hieght * abs(coverage_percent[TTL])) + "\n").replace("], [",
            #                                                                                                              ",").replace(
            #     "[[[", "").replace("]]]", "," + str(offset + scale * tower_hieght * abs(coverage_percent[TTL]))))
            kmlfile.write(str(tmp).replace("], [",
                                           "," + str(offset + scale * tower_hieght * abs(
                                               coverage_percent[TTL])) + "\n").replace("], [",
                                                                                       ",").replace(
                "[[", "").replace("]]", "," + str(offset + scale * tower_hieght * abs(coverage_percent[TTL]))).replace(
                ", ", ","
                ))
            # kmlfile.write("</coordinates>\n\t\t</LinearRing>\n\t\t</outerBoundaryIs>")

            if TTL * 330 != 0:
                # kmlfile.write("\t\t<innerBoundaryIs>\n\t\t<LinearRing>\n\t\t<coordinates>")
                tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL], pie_chunks=pie_chunks, span=span,
                                       reverse=True)
                kmlfile.write(str(tmp).replace("], [",
                                               "," + str(offset + scale * tower_hieght * abs(
                                                   coverage_percent[TTL])) + "\n").replace(
                    "], [",
                    ",").replace(
                    "[[", "").replace("]]",
                                      "," + str(offset + scale * tower_hieght * abs(coverage_percent[TTL]))).replace(
                    ", ",
                    ","
                    ))
            else:
                tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL], pie_chunks=pie_chunks, span=60,
                                       reverse=True)
            kmlfile.write("</coordinates>\n\t\t</LinearRing>\n\t\t</outerBoundaryIs>")

            kmlfile.write("</Polygon>")
            kmlfile.write("</Placemark>")

        kmlfile.write("</Document>")
        kmlfile.write("</kml>")

        # a = kml_shape_create(51.9392601099981, 29.5558191927263, azimuth=120, diameter=0.0002, pie_chunks=4, span=60)
        # kmlfile.write(str(a).replace("]], [[", "\n").replace("], [", ",").replace("[[[", "").replace("]]]", ""))
