# function propagation

def propagation_to_KML(location, propagation):
    import numpy as np
    import math
    from scipy.interpolate import interp1d

    distance_map = [0.4, 0.7, 1.1, 1.5, 1.8, 2.2, 2.5, 2.9, 3.3, 3.6, 4.4, 5.1, 5.8, 6.5, 7.3, 8.0, 8.7, 9.4, 10.2, 10.9,                    12.0, 13.1, 14.1, 15.2, 16.3, 17.4, 18.5, 19.6, 20.7, 21.8, 23.2, 24.7, 26.1, 27.6, 29.0, 30.5, 31.9,                    33.4, 34.8, 36.3]

    # Compensating 36.3 KM that was shown as 33.682
    distance_map = [i * 1.154 for i in distance_map]

    lat = 53.408426
    long = 29.472164
    azimuth = 352.7
    scale = 0.5
    tower_hieght = 24
    pie_chunks = 6
    offset = 0
    span = 120
    b_interpolate = True
    interpolation_factor=3
    alpha = 100
    earthRadius = 6367  # radius in km


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
        xnew = np.linspace(0, distance_map[-1]*1000, num=len(distance_map)*interpolation_factor, endpoint=True)
        my_interp = interp1d(np.linspace(0, distance_map[-1]*1000, num=len(distance_map), endpoint=True), propagation,
                      kind='cubic')
        propagation2 = my_interp(xnew)
        propagation = [i if i > 0 else 0 for i in propagation2]
        my_interp=interp1d(np.linspace(0, distance_map[-1]*1000, num=len(distance_map), endpoint=True), distance_map,
                      kind='cubic')
        distance_map = my_interp(xnew)

    propagation_sum = sum(propagation)
    a = np.array(propagation)
    b = (a / propagation_sum * 100)
    propagation_percent = b.tolist()
    propagation_percent = [(i > 0) * i for i in propagation_percent]


    def color(percent, alpha=alpha):
        Red = 255
        Green = 255
        Blue = 255
        Red2 = 0
        Green2 = 0
        Blue2 = 0
        if percent < 50:
            percent *= 2
            Red2 = (100 - percent) / 100 * Red
            Green2 = percent / 100 * Green
        else:
            percent = (percent - 50) * 2
            Green2 = (100 - percent) / 100 * Green
            Blue2 = percent / 100 * Blue

        # https: // developers.google.com / kml / documentation / kmlreference  # colorstyle
        return hex(int(alpha)).replace("0x", "").zfill(2) + hex(int(Blue2)).replace("0x", "").zfill(2) + hex(
            int(Green2)).replace("0x", "").zfill(2) + hex(
            int(Red2)).replace("0x", "").zfill(2)


    def kml_shape_create(lat, long, azimuth=0, diameter=distance_map[len(propagation) - 1], pie_chunks=5, span=120,
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
    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\">")
    print("<Document>")

    for TTL in range(0, len(propagation) - 1):
        print("<Placemark>")
        print("<Style> ")
        print("\t<LineStyle>")
        print("\t\t<color>", color(abs(propagation_percent[TTL] * 100 / max(propagation_percent)), alpha=0), "</color>")
        # print("\t\t<width>", 4, "</width>")
        print("\t</LineStyle>")
        print("\t<PolyStyle>\n\t\t<color>", color(abs(propagation_percent[TTL] * 100 / max(propagation_percent))),
              "</color>")
        print("\t\t<fill>", 1, "</fill>\n\t</PolyStyle>")
        print("</Style>")

        print(f"\t<name>", {location}, "</name> \n<description><![CDATA[")
        print(descript)
        print("]]></description>")
        print("<Polygon>")
        print("\t\t<extrude>", scale * tower_hieght * propagation_percent[TTL], "</extrude>")
        print("\t\t<tessellate>", 1, "</tessellate>\t\t")
        print('\t\t<altitudeMode>', "ClampedToGround" if offset == 0 else "relativeToGround",
              "</altitudeMode>")  # "absolute"
        print("\t\t<outerBoundaryIs>\n\t\t<LinearRing>\n\t\t<coordinates>")
        tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL + 1], pie_chunks=pie_chunks, span=span)

        # print(str(tmp).replace("]], [[",
        #                        "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL])) + "\n").replace("], [",
        #                                                                                                              ",").replace(
        #     "[[[", "").replace("]]]", "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL]))))
        print(str(tmp).replace("], [",
                               "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL])) + "\n").replace(
            "], [",
            ",").replace(
            "[[", "").replace("]]", "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL]))).replace(", ",
                                                                                                                      ","
                                                                                                                      ))
        # print("</coordinates>\n\t\t</LinearRing>\n\t\t</outerBoundaryIs>")

        if TTL * 330 != 0:
            # print("\t\t<innerBoundaryIs>\n\t\t<LinearRing>\n\t\t<coordinates>")
            tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL], pie_chunks=pie_chunks, span=span,
                                   reverse=True)
        else:
            tmp = kml_shape_create(lat, long, azimuth, diameter=0, pie_chunks=1, span=span,
                                   reverse=True)
        print(str(tmp).replace("], [",
                               "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL])) + "\n").replace(
            "], [",
            ",").replace(
            "[[", "").replace("]]", "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL]))).replace(", ",
                                                                                                                      ","
                                                                                                                      ))

        print("</coordinates>\n\t\t</LinearRing>\n\t\t</outerBoundaryIs>")

        print("</Polygon>")
        print("</Placemark>")

    print("</Document>")
    print("</kml>")

    # a = kml_shape_create(51.9392601099981, 29.5558191927263, azimuth=120, diameter=0.0002, pie_chunks=4, span=60)
    # print(str(a).replace("]], [[", "\n").replace("], [", ",").replace("[[[", "").replace("]]]", ""))
