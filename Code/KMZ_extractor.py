import xml.sax
import xml.sax.handler
import xml.dom.minidom
from zipfile import ZipFile
import PlacemarkHandler
import sqlite3
import re
import datetime

filename = 'R6 & R9 FDD 2021-June-13 MVO ver.kmz'

# Open the KMZ (google earth's standard zip files with all accompanying files
kmz = ZipFile(filename, 'r')

# Read the 3G transmitters to extract transmitters' data then convert it to type str (UTF-8) from byte
kml = kmz.open('files/transmittersUMTS.kml', 'r').read().decode('UTF-8')
doc = xml.dom.minidom.parseString(kml)

print(doc.nodeName)

for a in doc.getElementsByTagName("Style"):
    a.parentNode.removeChild(a)

for a in doc.getElementsByTagName("Polygon"):
    a.parentNode.removeChild(a)

# # writes the modified xml into new file
# with open('E:/Optimization/R6 & R9 FDD 2021-June-13 MVO ver/files/transmittersUMTS2.kml','w') as xml_file:
#     doc.writexml(xml_file)
with sqlite3.connect('E:/Optimization/R6 & R9 FDD 2021-June-13 MVO ver/files/UMTStransmitter.sq3') as con:
    for placemark in doc.getElementsByTagName("Placemark"):
        UMTStransmitter_nodename = placemark.getElementsByTagName("name")[0].childNodes[0].nodeValue
        UMTStransmitter_description = placemark.getElementsByTagName("description")[0].childNodes[0].nodeValue.replace(
            '<b>', '').replace('</b>', '').replace('<br>', '')
        re_co = re.compile('(.*)[(].*[)].*:(.*)')
        lines_of_description = [
            i if not re_co.search(i) else re_co.search(i).group(1) + ':' + re_co.search(i).group(2) for i in
            UMTStransmitter_description.split("\n")]
        dict = {j.split(":")[0].strip().lower().replace(' ', '-'): j.split(":")[1].strip() for j in lines_of_description
                if j != ''}
        columns = list(dict.keys()) + ['date']
        values = list(dict.values()) + [datetime.datetime.now().date().strftime('%d/%m/%Y')]
        sql_str = f"INSERT INTO TABLE transmitters ({columns}) values " \
                  f"({values})".replace("(['", "('").replace("'])", "')")

        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        cur.execute(sql_str)
        print('d')
