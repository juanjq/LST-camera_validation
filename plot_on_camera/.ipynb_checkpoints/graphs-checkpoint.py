import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy             as np
import math

from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2                          import PdfFileMerger 
from scipy.stats                     import norm

# trying to import ctapipe import (needed the lstchain environament)
try:
    from ctapipe.visualization import CameraDisplay
    from ctapipe.coordinates   import EngineeringCameraFrame
    from ctapipe.instrument    import CameraGeometry
except:
    pass


INDEX_ORDER_PX = [0,3,2,1,6,5,4,33,16,17,34,56,55,32,24,44,43,23,10,11,25,119,84,85,120,160,159,118,101,139,138,100,69,70,102,259,206,207,260,318,317,258,232,288,287,231,182,183,233,453,382,383,454,530,529,452,417,491,490,416,349,350,418,701,612,613,702,796,795,700,656,748,747,655,570,571,657,1003,896,897,1004,1116,1115,1002,949,1059,1058,948,845,846,950,1359,1234,1235,1360,1490,1489,1358,1296,1424,1423,1295,1174,1175,1297,1707,1607,1608,1708,1785,1784,1706,1659,1749,1748,1658,1550,1551,1660,30,29,14,15,31,52,51,82,53,54,83,117,116,81,27,47,26,12,13,28,48,204,157,158,205,257,256,203,72,104,71,45,46,73,105,380,315,316,381,451,450,379,141,185,184,140,103,142,186,610,527,528,611,699,698,609,290,352,351,289,234,235,291,894,793,794,895,1001,1000,893,493,573,572,492,419,420,494,1232,1113,1114,1233,1357,1356,1231,750,848,847,749,658,659,751,1605,1487,1488,1606,1705,1704,1604,1061,1177,1176,1060,951,952,1062,1832,1782,1783,1833,1852,1851,1831,1426,1553,1552,1425,1298,1299,1427,1751,1814,1813,1750,1661,1662,1752,21,22,40,39,20,8,9,36,7,19,60,59,35,18,67,99,98,66,41,42,68,87,58,88,123,122,86,57,180,230,229,179,136,137,181,162,121,163,210,209,208,161,347,415,414,346,285,286,348,320,261,262,321,385,384,319,568,654,653,567,488,489,569,532,455,456,533,615,614,531,843,947,946,842,745,746,844,798,703,704,799,899,898,797,1172,1294,1293,1171,1056,1057,1173,1118,1005,1006,1119,1237,1236,1117,1548,1657,1656,1547,1421,1422,1549,1492,1361,1362,1493,1610,1609,1491,1811,1846,1845,1810,1746,1747,1812,1787,1709,1710,1788,1835,1834,1786,113,112,79,80,114,153,152,155,154,115,156,202,201,200,77,76,49,50,78,111,110,313,254,255,314,378,377,312,107,145,106,74,75,108,146,525,448,449,526,608,607,524,188,238,187,143,144,189,239,791,696,697,792,892,891,790,293,355,292,236,237,294,356,1111,998,999,1112,1230,1229,1110,422,496,421,353,354,423,497,1485,1354,1355,1486,1603,1602,1484,575,661,660,574,495,576,662,1780,1702,1703,1781,1830,1829,1779,850,954,953,849,752,753,851,1179,1301,1300,1178,1063,1064,1180,1555,1664,1663,1554,1428,1429,1556,95,96,132,131,94,64,65,62,63,93,92,61,37,38,134,178,177,176,133,97,135,125,90,126,167,166,124,89,283,345,344,282,227,228,284,212,165,213,266,265,211,164,486,566,565,485,412,413,487,323,264,324,389,388,322,263,743,841,840,742,651,652,744,458,387,459,536,535,457,386,1054,1170,1169,1053,944,945,1055,617,534,618,707,706,705,616,1419,1546,1545,1418,1291,1292,1420,901,800,801,902,1008,1007,900,1744,1809,1808,1743,1654,1655,1745,1239,1120,1121,1240,1364,1363,1238,1612,1494,1495,1613,1712,1711,1611,250,249,198,199,251,308,307,310,309,252,253,311,374,373,196,195,150,151,197,248,247,446,375,376,447,523,522,445,148,192,147,109,149,194,193,694,605,606,695,789,788,693,241,297,240,190,191,242,298,996,889,890,997,1109,1108,995,358,426,357,295,296,359,427,1352,1227,1228,1353,1483,1482,1351,499,579,498,424,425,500,580,1700,1600,1601,1701,1778,1777,1699,664,756,663,577,578,665,757,853,957,852,754,755,854,958,1066,1182,1065,955,956,1067,1183,1303,1431,1430,1302,1181,1304,1432,223,224,278,277,222,174,175,172,173,221,220,171,129,130,280,281,341,340,279,225,226,127,128,170,169,216,168,91,410,484,483,409,342,343,411,268,215,269,328,327,267,214,649,741,740,648,563,564,650,391,326,392,463,462,390,325,942,1052,1051,941,838,839,943,538,461,539,622,621,537,460,1289,1417,1416,1288,1167,1168,1290,709,620,710,805,804,708,619,1652,1742,1741,1651,1543,1544,1653,904,803,905,1012,1011,903,802,1123,1010,1124,1243,1242,1122,1009,1366,1241,1367,1498,1497,1496,1365,441,440,371,372,442,517,516,519,518,443,444,520,601,600,369,368,305,306,370,439,438,603,602,521,604,692,691,690,303,302,245,246,304,367,366,887,786,787,888,994,993,886,300,362,299,243,244,301,363,1225,1106,1107,1226,1350,1349,1224,429,503,428,360,361,430,504,1598,1480,1481,1599,1698,1697,1597,582,668,581,501,502,583,669,759,857,758,666,667,760,858,960,1070,959,855,856,961,1071,1185,1307,1184,1068,1069,1186,1308,1434,1557,1433,1305,1306,1435,1558,405,406,478,477,404,338,339,336,337,403,402,335,275,276,480,481,559,558,479,407,408,273,274,334,333,272,218,219,561,647,646,645,560,482,562,330,217,271,396,395,329,270,836,940,939,835,738,739,837,465,394,466,543,542,464,393,1165,1287,1286,1164,1049,1050,1166,624,541,625,714,713,623,540,1541,1650,1649,1540,1414,1415,1542,807,712,808,909,908,806,711,1014,907,1015,1128,1127,1013,906,1245,1126,1246,1371,1370,1244,1125,1500,1369,1501,1615,1614,1499,1368,686,685,598,599,687,780,779,782,781,688,689,783,882,881,596,595,514,515,597,684,683,884,883,784,785,885,990,989,512,511,436,437,513,594,593,1104,991,992,1105,1223,1222,1103,434,433,364,365,435,510,509,1478,1347,1348,1479,1596,1595,1477,506,586,505,431,432,507,587,671,763,670,584,585,672,764,860,964,859,761,762,861,965,1073,1189,1072,962,963,1074,1190,1310,1438,1309,1187,1188,1311,1439,1560,1665,1559,1436,1437,1561,1666,641,642,732,731,640,556,557,554,555,639,638,553,475,476,734,735,831,830,733,643,644,473,474,552,551,472,400,401,833,834,936,935,832,736,737,398,399,471,470,397,331,332,1047,1163,1162,1046,937,938,1048,545,468,546,629,628,544,467,1412,1539,1538,1411,1284,1285,1413,716,627,717,812,811,715,626,911,810,912,1019,1018,910,809,1130,1017,1131,1250,1249,1129,1016,1373,1248,1374,1505,1504,1372,1247,1617,1503,1618,1714,1713,1616,1502,985,984,879,880,986,1097,1096,1099,1098,987,988,1100,1217,1216,877,876,777,778,878,983,982,1219,1218,1101,1102,1220,1343,1342,775,774,681,682,776,875,874,1345,1344,1221,1346,1476,1475,1474,679,678,591,592,680,773,772,589,675,588,508,590,677,676,766,864,765,673,674,767,865,967,1077,966,862,863,968,1078,1192,1314,1191,1075,1076,1193,1315,1441,1564,1440,1312,1313,1442,1565,1668,1753,1667,1562,1563,1669,1754,931,932,1040,1039,930,828,829,826,827,929,928,825,729,730,1042,1043,1157,1156,1041,933,934,727,728,824,823,726,636,637,1159,1160,1280,1279,1158,1044,1045,634,635,725,724,633,549,550,1282,1410,1409,1408,1281,1161,1283,547,548,632,631,720,630,469,814,719,815,916,915,813,718,1021,914,1022,1135,1134,1020,913,1252,1133,1253,1378,1377,1251,1132,1507,1376,1508,1622,1621,1506,1375,1716,1620,1717,1790,1789,1715,1619,1338,1337,1214,1215,1339,1468,1467,1470,1469,1340,1341,1471,1591,1590,1212,1211,1094,1095,1213,1336,1335,1593,1592,1472,1473,1594,1696,1695,1092,1091,980,981,1093,1210,1209,978,977,872,873,979,1090,1089,870,869,770,771,871,976,975,867,971,866,768,769,868,972,1080,1196,1079,969,970,1081,1197,1317,1445,1316,1194,1195,1318,1446,1567,1672,1566,1443,1444,1568,1673,1756,1815,1755,1670,1671,1757,1816,1275,1276,1402,1401,1274,1154,1155,1152,1153,1273,1272,1151,1037,1038,1404,1405,1534,1533,1403,1277,1278,1035,1036,1150,1149,1034,926,927,1536,1537,1648,1647,1535,1406,1407,924,925,1033,1032,923,821,822,819,820,922,921,818,722,723,918,721,817,1026,1025,917,816,1137,1024,1138,1257,1256,1136,1023,1380,1255,1381,1512,1511,1379,1254,1624,1510,1625,1721,1720,1623,1509,1792,1719,1793,1837,1836,1791,1718,1691,1690,1588,1589,1692,1773,1772,1775,1774,1693,1694,1776,1828,1827,1586,1585,1465,1466,1587,1689,1688,1463,1462,1333,1334,1464,1584,1583,1331,1330,1207,1208,1332,1461,1460,1205,1204,1087,1088,1206,1329,1328,1085,1084,973,974,1086,1203,1202,1199,1321,1198,1082,1083,1200,1322,1448,1571,1447,1319,1320,1449,1572,1675,1760,1674,1569,1570,1676,1761,1818,1847,1817,1758,1759,1819,1848,1643,1644,1737,1736,1642,1531,1532,1529,1530,1641,1640,1528,1399,1400,1739,1740,1807,1806,1738,1645,1646,1397,1398,1527,1526,1396,1270,1271,1268,1269,1395,1394,1267,1147,1148,1145,1146,1266,1265,1144,1030,1031,1028,1029,1143,1142,1027,919,920,1259,1140,1260,1385,1384,1258,1139,1514,1383,1515,1629,1628,1513,1382,1723,1627,1724,1797,1796,1722,1626,1839,1795,1840,1854,1853,1838,1794,1825,1824,1770,1771,1826,1850,1849,1768,1767,1686,1687,1769,1823,1822,1684,1683,1581,1582,1685,1766,1765,1579,1578,1458,1459,1580,1682,1681,1456,1455,1326,1327,1457,1577,1576,1324,1452,1323,1201,1325,1454,1453,1574,1679,1573,1450,1451,1575,1680,1763,1820,1762,1677,1678,1764,1821,1804,1805,1844,1843,1803,1734,1735,1732,1733,1802,1801,1731,1638,1639,1636,1637,1730,1729,1635,1524,1525,1522,1523,1634,1633,1521,1392,1393,1390,1391,1520,1519,1389,1263,1264,1261,1262,1388,1387,1518,1386,1141,1631,1517,1632,1728,1727,1630,1516,1799,1726,1800,1842,1841,1798,1725]