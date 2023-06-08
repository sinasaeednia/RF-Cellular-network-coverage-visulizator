# function propagation

def propagation_to_KML(location, propagation,
                       destination_path=None,
                       lat=53.408426,
                       long=29.472164,
                       azimuth=352.7,
                       tower_hieght=24,
                       scale=0.5,
                       pie_chunks=6,
                       offset=0,
                       span=120,
                       alpha=100,
                       acceptable_max_min_percentage=None,
                       acceptable_max_min_absolute=None,
                              chunk_name_part=None
                       ):
    import numpy as np
    import io
    import base64
    import os
    import math
    from scipy.interpolate import interp1d
    from matplotlib import pyplot as plt

    # check boundaries of accepted values to be shown in output KML shapes
    if (not acceptable_max_min_percentage) and (not acceptable_max_min_absolute):
        pass # in this case program should throw an error

    distance_map_standard = [0.4, 0.7, 1.1, 1.5, 1.8, 2.2, 2.5, 2.9, 3.3, 3.6, 4.4, 5.1, 5.8, 6.5, 7.3, 8.0, 8.7, 9.4, 10.2,
                    10.9, 12.0, 13.1, 14.1, 15.2, 16.3, 17.4, 18.5, 19.6, 20.7, 21.8, 23.2, 24.7, 26.1, 27.6, 29.0,
                    30.5, 31.9, 33.4, 34.8, 36.3]
    # Compensating 36.3 KM that was shown as 33.682
    distance_map = [i * 1.154 for i in distance_map_standard]

    b_interpolate = True
    interpolation_factor = 1

    earth_radius = 6367  # radius in km

    # destination_path = (destination_path + "\\").replace("\\\\\\", "\\\\").replace("\\\\", "\\")
    if destination_path:
        destination = (destination_path + "\\" + location).replace("\\\\", "\\")
    else:
        destination = location

    if b_interpolate and (interpolation_factor > 1):
        xnew = np.linspace(0, distance_map[-1] * 1000, num=len(distance_map) * interpolation_factor, endpoint=True)
        my_interp = interp1d(np.linspace(0, distance_map[-1] * 1000, num=len(distance_map), endpoint=True), propagation,
                             kind='cubic')
        propagation2 = my_interp(xnew)
        propagation = [i if i > 0 else 0 for i in propagation2]
        my_interp = interp1d(np.linspace(0, distance_map[-1] * 1000, num=len(distance_map), endpoint=True),
                             distance_map,
                             kind='cubic')
        distance_map = my_interp(xnew)

    propagation_total = sum(propagation)
    a = np.array(propagation)
    b = (a / propagation_total * 100)
    propagation_percent = b.tolist()
    propagation_percent_max = max(propagation_percent)
    propagation_percent_cumsum=np.cumsum(propagation_percent)


    def calculateCoord(origin, brng, arc_length):
        # convert degree to radian
        # arc_length /= 2.4
        lat1 = origin[0] * math.pi / 180
        lon1 = origin[1] * math.pi / 180

        central_angle = arc_length / earth_radius

        lat2 = math.asin(
            math.sin(lat1) * math.cos(central_angle) + math.cos(lat1) * math.sin(central_angle) * math.cos(
                math.pi / 180 * brng))
        lon2 = lon1 + math.atan2(math.sin(math.pi / 180 * brng) * math.sin(central_angle) * math.cos(lat1),
                                 math.cos(central_angle) - math.sin(lat1) * math.sin(lat2)) / 2

        return [lat2 * 180 / math.pi, lon2 * 180 / math.pi]

    def color(percent, alpha=alpha,usecase="KML"):
        # Color_Legend is based on RGB (for web and applications)
        # but for google earth uses aBGR they use propagation list percentage
        X = [0, 30, 45, 70, 80, 90, 100]
        Y = [0xc0c0c0, 0xb0000, 0xFF0000, 0xffaa00, 0xffff3a, 0x3ada79, 0x006e3c]
        my_interp = interp1d(X, Y, kind='zero')
        Y2 = my_interp(percent)
        print(str(percent) + "\t" + hex(int(alpha)).replace("0x", "").zfill(2) + str(
            hex(int(my_interp(percent).item(0)))).replace("0x", "").zfill(6))
        if usecase == "KML":
            return hex(int(alpha)).replace("0x", "").zfill(2) + (str(hex(int(Y2.item(0)))).replace("0x","").zfill(6)[-2:]+str(hex(int(Y2.item(0)))).replace("0x","").zfill(6)[-4:-2]+str(hex(int(Y2.item(0)))).replace("0x","").zfill(6)[-6:-4]).zfill(6)
        else:
            return str(hex(int(Y2.item(0)))).replace("0x", "").zfill(6)

    def kml_shape_create(lat, long, azimuth=0, diameter=distance_map[len(propagation) - 1], pie_chunks=5, span=120,
                         reverse=False):
        polygon_inner = []
        # polygon_outer = []
        # polygon_inner.append([[lat], [long]])

        if not reverse:
            for i in range(0, pie_chunks + 1):
                j = 90 - azimuth + i * span / pie_chunks - span / 2
                # rotation_matrix = [[math.cos(j * math.pi / 180), -1 * math.sin(j * math.pi / 180)], \
                #          [math.sin(j * math.pi / 180), math.cos(j * math.pi / 180), ]]
                # polygon_inner.append(
                #   (np.add(np.matmul(rotation_matrix, [[diameter], [diameter]]).tolist(), [[lat], [long]])).tolist())
                polygon_inner.append(calculateCoord([lat, long], j, diameter))
        else:
            for i in range(0, pie_chunks + 1):
                j = 90 - azimuth - i * span / pie_chunks + span / 2
                # rotation_matrix = [[math.cos(j * math.pi / 180), -1 * math.sin(j * math.pi / 180)],
                #          [math.sin(j * math.pi / 180), math.cos(j * math.pi / 180), ]]
                # polygon_inner.append(
                #   (np.add(np.matmul(rotation_matrix, [[diameter], [diameter]]).tolist(), [[lat], [long]])).tolist())
                polygon_inner.append(calculateCoord([lat, long], j, diameter))

        # polygon_inner.append([[lat], [long]])
        # polygon_inner.append([[lat], [long]])
        return polygon_inner

    if destination_path:
        destination = (destination_path + "\\" + location).replace("\\\\", "\\")
    else:
        destination = location

    # Adding points for each chape
    with open(destination, 'a') as kml_file:


        kml_file.write(
            "<Style id=\"normalPlacemark\"><IconStyle><color>ffbe6400</color><scale>0.5</scale><Icon><href>http://kml-icons.actix.com/Dot.png</href></Icon></IconStyle></Style>")
        kml_file.write(f"<Placemark>\n<name>{chunk_name_part}</name><description>")

        # creates plot in base64 PNG format
        plt.ioff()
        plt.plot([i/10 for i in distance_map_standard], list(np.array(propagation) / max(propagation) * 100), color='r')
        plt.plot([i/10 for i in distance_map_standard], np.cumsum([i / sum(propagation) * 100 for i in propagation]), color='g')
        plt.ylim([0, 110])
        plt.xlim([0, max([i/10 for i in distance_map_standard])])
        pic_IObytes = io.BytesIO()
        plt.savefig(pic_IObytes, format='PNG')
        plt.clf()
        pic_IObytes.seek(0)
        pic_hash = "data:image/png;base64,"+base64.b64encode(pic_IObytes.read()).decode("utf-8")
        kml_file.write(f"<img width=\"100%\" src=\"{pic_hash}\" /><br/>")

        # creates description
        kml_file.write(
            "<table border=\"1\"><tr><td>Distance</td><td>propagation</td><td>percent of prop</td><td>cumsum</td></tr>")
        for d,i, j,c in zip(distance_map_standard,propagation, propagation_percent,propagation_percent_cumsum):
            if acceptable_max_min_percentage and (j*100 < acceptable_max_min_percentage[0]):
                kml_file.write(f"<tr><td>{d}km</td><td>{i}</td><td>{round(j,2)}%</td><td>{round(c,2)}%</td></tr>")
            else:
                kml_file.write(f"<tr bgcolor=\"#{color(j/propagation_percent_max*100,usecase='HTML')[-6:]}\"><td>{d}km</td><td>{i}</td><td>{round(j,2)}%</td><td>{round(c,2)}%</td></tr>")
        kml_file.write("</table>")
        kml_file.write("</description>\n<styleUrl>normalPlacemark</styleUrl>")
        kml_file.write("<Point>")
        kml_file.write(f"<coordinates> {lat},{long} </coordinates>")
        kml_file.write("</Point>")
        kml_file.write("</Placemark>")

    with open(destination, 'a') as kml_file:
        descript = ""
        # kml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\">")
        # kml_file.write("<Document>")

        for TTL in range(0, len(propagation) - 1):
            # filter output shapes based on acceptable_max_min_percentage & acceptable_max_min_absolute
            if acceptable_max_min_percentage != None:
                if (propagation_percent[TTL]  < acceptable_max_min_percentage[0]) or\
                        (propagation_percent[TTL]  > acceptable_max_min_percentage[1]): continue
            if acceptable_max_min_absolute != None:
                if (propagation_percent[TTL]  < acceptable_max_min_absolute[0]) or\
                        (propagation_percent[TTL]  > acceptable_max_min_absolute[1]): continue

            # starts creating shapes
            kml_file.write("<Placemark>")
            kml_file.write("<Style> ")
            kml_file.write("\t<LineStyle>")
            kml_file.write(
                f"\t\t<color> {color(propagation_percent[TTL]/propagation_percent_max*100, alpha=0,usecase='KML')} </color>")
            # print("\t\t<width>", 4, "</width>")
            kml_file.write("\t</LineStyle>")
            kml_file.write(
                f"\t<PolyStyle>\n\t\t<color> {color(propagation_percent[TTL]/propagation_percent_max*100, alpha=alpha,usecase='KML')} </color>")
            kml_file.write(f"\t\t<fill> {1} </fill>\n\t</PolyStyle>")
            kml_file.write("</Style>")

            kml_file.write(f"\t<name> {location}_{chunk_name_part} </name> \n<description><![CDATA[")
            kml_file.write(descript)
            kml_file.write("]]></description>")
            kml_file.write("<Polygon>")
            kml_file.write(f"\t\t<extrude> {scale * tower_hieght * propagation_percent[TTL]} </extrude>")
            kml_file.write(f"\t\t<tessellate> {1} </tessellate>\t\t")
            kml_file.write(
                f"\t\t<altitudeMode> {'ClampedToGround' if offset == 0 else 'relativeToGround'} </altitudeMode>")  # "absolute"
            kml_file.write("\t\t<outerBoundaryIs>\n\t\t<LinearRing>\n\t\t<coordinates>")
            tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL + 1], pie_chunks=pie_chunks, span=span)

            # kml_file.write(str(tmp).replace("]], [[",            #            "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL])) + "\n").replace("], [",            #                                                       ",").replace(            #   "[[[", "").replace("]]]", "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL]))))
            kml_file.write(str(tmp).replace("], [", "," + str(
                offset + scale * tower_hieght * abs(propagation_percent[TTL])) + "\n").replace("], [", ",").replace(
                "[[", "").replace("]]",
                                  "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL]))).replace(
                ", ", ",") + "\n\n")

            # print("</coordinates>\n\t\t</LinearRing>\n\t\t</outerBoundaryIs>")

            if TTL != 0:
                # print("\t\t<innerBoundaryIs>\n\t\t<LinearRing>\n\t\t<coordinates>")

                tmp = kml_shape_create(lat, long, azimuth, diameter=distance_map[TTL], pie_chunks=pie_chunks, span=span,
                                       reverse=True)
            else:
                tmp = kml_shape_create(lat, long, azimuth, diameter=0, pie_chunks=1, span=span,
                                       reverse=True)
            kml_file.write(str(tmp).replace("], [",
                                            "," + str(
                                                offset + scale * tower_hieght * abs(
                                                    propagation_percent[TTL])) + "\n").replace(
                "], [",
                ",").replace(
                "[[", "").replace("]]",
                                  "," + str(offset + scale * tower_hieght * abs(propagation_percent[TTL]))).replace(
                ", ",
                ","
            ))

            kml_file.write("</coordinates>\n\t\t</LinearRing>\n\t\t</outerBoundaryIs>")
            kml_file.write("</Polygon>")
            kml_file.write("</Placemark>")

        # a = kml_shape_create(51.9392601099981, 29.5558191927263, azimuth=120, diameter=0.0002, pie_chunks=4, span=60)
        # print(str(a).replace("]], [[", "\n").replace("], [", ",").replace("[[[", "").replace("]]]", ""))
