"""A single authored winter village, in shared 1500-unit scene coordinates."""
import math
import random
from dot_to_dot.winter_scene import artwork as owl_art


def artwork():
    paths=[];rng=random.Random(2512)
    def line(xy, priority=0):
        paths.append({'xy':xy,'priority':priority})
    def polygon(xy, priority=0):line(xy+[xy[0]],priority)
    def curve(xy, priority=0, closed=False, steps=3):
        # Catmull–Rom control knots become real straight dot-to-dot segments.
        result=[]
        pts=([xy[-1]]+xy+[xy[0],xy[1]]) if closed else ([xy[0]]+xy+[xy[-1]])
        for i in range(1,len(pts)-2):
            a,b,c,d=pts[i-1:i+3]
            for j in range(steps):
                t=j/steps
                result.append(tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in (0,1)))
        result.append(xy[0] if closed else xy[-1]);line(result,priority)
    def organic(xy, priority=0):curve(xy,priority,closed=True,steps=2)
    def rect(x,y,w,h,p=0):polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],p)
    def oval(x,y,rx,ry,n=20,p=0):polygon([(x+rx*math.cos(i*2*math.pi/n),y+ry*math.sin(i*2*math.pi/n)) for i in range(n)],p)
    def star(x,y,r,p=1):polygon([(x+(r if i%2==0 else r*.43)*math.sin(i*math.pi/5),y-(r if i%2==0 else r*.43)*math.cos(i*math.pi/5)) for i in range(10)],p)
    def window(x,y,w,h):
        rect(x,y,w,h,1);line([(x+w/2,y),(x+w/2,y+h)],1);line([(x,y+h/2),(x+w,y+h/2)],1)
        line([(x-4,y+h+5),(x+w+4,y+h+5)],2)
    def house(x,y,w,h):
        roof=y-h*.38;peak=x+w*.5
        polygon([(x-12,y),(peak,roof),(x+w+12,y)],0)
        line([(x,y),(x,y+h*.62),(x+w,y+h*.62),(x+w,y)],0)
        rect(x+w*.7,roof+8,w*.12,h*.16,1)
        rect(x+w*.42,y+h*.25,w*.18,h*.37,1)
        window(x+w*.1,y+h*.12,w*.21,h*.25);window(x+w*.7,y+h*.12,w*.2,h*.25)
        window(x+w*.43,roof+h*.16,w*.14,h*.14)
        curve([(x-12,y),(x+10,y-9),(peak,roof-7),(x+w-7,y-9),(x+w+12,y)],1,steps=2)
        # Diamond roof tiles, shutters, wreaths, and doorstep masonry.
        for t in [.36,.57,.78]:
            yy=roof+(y-roof)*t
            for xx in range(round(peak-w*.35*t),round(peak+w*.35*t),18):
                polygon([(xx,yy-7),(xx+8,yy),(xx,yy+7),(xx-8,yy)],2)
        oval(x+w*.51,y+h*.38,w*.06,h*.06,10,1)
        for yy in [y+h*.12,y+h*.22,y+h*.32]:
            line([(x+w*.03,yy),(x+w*.08,yy)],2)
            line([(x+w*.33,yy),(x+w*.38,yy)],2)
            line([(x+w*.63,yy),(x+w*.68,yy)],2)
            line([(x+w*.92,yy),(x+w*.97,yy)],2)
        line([(x+w*.36,y+h*.63),(x+w*.68,y+h*.63),(x+w*.72,y+h*.68),(x+w*.32,y+h*.68),(x+w*.36,y+h*.63)],1)
        for t in [.25,.5,.75]:
            yy=roof+(y-roof)*t;half=w*.5*t
            line([(peak-half,yy),(peak+half,yy)],2)
        for yy in [y+h*.43,y+h*.53]:line([(x,yy),(x+w*.42,yy)],2);line([(x+w*.6,yy),(x+w,yy)],2)
    def pine(x,y,w,h,decorated=False):
        points=[(x,y-h)];levels=5
        for i in range(1,levels+1):
            points.extend([(x+w*.5*i/levels,y-h+h*.88*i/levels),(x+w*.28*i/levels,y-h+h*.88*i/levels)])
        points.extend([(x+w*.09,y),(x-w*.09,y)])
        for i in range(levels,0,-1):
            points.extend([(x-w*.28*i/levels,y-h+h*.88*i/levels),(x-w*.5*i/levels,y-h+h*.88*i/levels)])
        organic(points)
        for i in range(1,5):
            yy=y-h+h*.88*i/levels
            curve([(x-w*.38*i/levels,yy+9),(x,yy+20),(x+w*.38*i/levels,yy+9)],1)
        if decorated:
            star(x,y-h-12,24,0)
            for i in range(1,6):
                yy=y-h+h*.83*i/6
                half=w*.34*i/6
                curve([(x-half,yy),(x-half*.4,yy+20),(x+half*.35,yy+29),(x+half,yy+14)],1)
                for sign in [-1,1]:oval(x+sign*half*.7,yy+35,8,10,6,1)
    # Mountain skyline and ice planes run through several calendar sheets.
    line([(0,335),(80,265),(158,300),(288,120),(410,252),(503,200),(614,323),(780,165),(923,315),(1030,209),(1145,278),(1275,142),(1420,280),(1500,223)])
    for x,y,w in [(288,120,155),(780,165,150),(1275,142,145),(80,265,80),(1030,209,100)]:
        line([(x-w*.45,y+w*.58),(x-w*.12,y+w*.43),(x,y),(x+w*.14,y+w*.5),(x+w*.35,y+w*.32)],1)
        line([(x,y),(x+w*.14,y+w*.5),(x+w*.35,y+w)],1)
    # Crescent, stars, and corner boughs enrich the upper sheets.
    polygon([(966,37),(925,45),(902,72),(900,111),(923,139),(961,145),(987,129),(954,131),(931,114),(925,86),(938,56)])
    for x,y,r in [(112,100,24),(436,75,22),(707,65,22),(1120,65,20),(1405,110,23),(540,144,15),(830,90,14),(1210,105,12)]:star(x,y,r)
    def bough(x,y,s,flip=1):
        line([(x,y),(x+flip*s*.45,y+s*.15),(x+flip*s,y+s*.38)],0)
        for i in range(7):
            a=i/7;sx=x+flip*s*a;sy=y+s*.38*a
            for side in [-1,1]:
                polygon([(sx,sy),(sx+flip*s*.1,sy+side*s*.14),(sx+flip*s*.13,sy+side*s*.05),(sx+flip*s*.2,sy+side*s*.2),(sx+flip*s*.19,sy+side*s*.02),(sx+flip*s*.3,sy+side*s*.08),(sx+flip*s*.2,sy)],1)
    bough(0,15,340);bough(1500,8,275,-1)
    # Village behind the square: towers and two staggered streets.
    for args in [(38,465,153,180),(207,416,147,161),(394,460,155,175),(695,427,165,180),(883,470,149,183),(1190,438,153,190),(1355,466,150,178)]:house(*args)
    # Tall clock tower, deliberately crossing a horizontal sheet seam.
    polygon([(558,521),(558,264),(539,264),(607,140),(674,264),(655,264),(655,521)])
    line([(607,140),(607,107),(622,113),(607,120)],1)
    line([(546,253),(668,253)],1);rect(568,275,77,86,1)
    oval(606,315,31,32,12,0);line([(606,292),(606,315),(625,325)],0)
    for y in [385,447]:window(582,y,48,39)
    line([(550,509),(663,509)],1)
    # Chapel's tower, nave, and rose window.
    polygon([(1073,479),(1073,250),(1055,250),(1104,119),(1153,250),(1135,250),(1135,479)])
    line([(1104,119),(1104,81)],0);line([(1090,94),(1118,94)],0)
    window(1090,281,30,56);oval(1104,381,24,24,10,1)
    polygon([(1047,479),(1047,429),(975,429),(1038,354),(1073,395)],0)
    # Foreground house row, with open town square between left and right banks.
    for args in [(12,686,180,184),(207,631,160,208),(395,661,194,200),(951,654,225,216),(1231,658,246,233)]:house(*args)
    # Stone streets and snow banks are continuous, not individual tile borders.
    for xy in [[(0,843),(202,813),(358,802),(585,837),(720,809),(914,815),(1185,840),(1500,817)],
               [(0,590),(212,568),(429,578),(635,572),(839,557),(1037,583),(1235,564),(1500,588)],
               [(691,558),(734,630),(711,727),(768,809)],
               [(827,558),(799,653),(850,737),(893,809)]]:curve(xy,1,steps=3)
    # Market stalls with striped awnings and wares.
    def stall(x,y,w):
        polygon([(x,y),(x+22,y-53),(x+w-22,y-53),(x+w,y)],0)
        for i in range(1,7):line([(x+22+(w-44)*i/7,y-53),(x+w*i/7,y)],1)
        line([(x+8,y),(x+8,y+106),(x+w-8,y+106),(x+w-8,y)],0)
        rect(x,y+57,w,35,0)
        for i in range(6):oval(x+18+i*(w-36)/5,y+42,10,13,6,1)
        for xx in [x+20,x+w-20]:line([(xx,y+92),(xx,y+118)],1)
    stall(665,1000,188);stall(909,1000,180);stall(1206,1000,197)
    # Garland joins stalls across the square.
    line([(632,852),(728,882),(816,887),(908,852)],1)
    for x,y in [(657,862),(706,875),(756,885),(806,887),(855,876),(892,860)]:star(x,y+15,10,2)
    pine(206,1225,358,490,True)
    pine(1461,1190,173,420)
    # Snowman stays recognizable within day 17.
    snow_start=len(paths)
    oval(525,1152,78,91,24);oval(525,1044,51,53,20)
    polygon([(467,1005),(581,1005),(581,994),(560,994),(556,947),(493,947),(490,994),(467,994)])
    line([(494,1054),(549,1060),(521,1077)],0)
    for x in [510,540]:oval(x,1031,4,4,4,1)
    for y in [1110,1147,1184]:oval(525,y,6,6,6,1)
    polygon([(480,1076),(528,1089),(571,1072),(574,1090),(534,1106),(524,1140),(507,1137),(514,1104),(481,1095)],1)
    line([(455,1137),(404,1096),(383,1065)],0);line([(404,1096),(376,1091)],1)
    line([(595,1130),(648,1077),(666,1048)],0);line([(648,1077),(680,1080)],1)
    for path in paths[snow_start:]:
        path['xy']=[(480+(x-525)*.9,1032+(y-1044)*.7) for x,y in path['xy']]
        path['priority']=min(path['priority'],-1)
    # Curving frozen river and bridge. River edges continue through the foreground.
    curve([(922,1038),(887,1093),(868,1157),(913,1235),(890,1309),(837,1390),(831,1500)])
    curve([(1047,1038),(1030,1099),(1013,1160),(1080,1235),(1036,1316),(1000,1418),(1025,1500)])
    polygon([(740,1197),(740,1149),(841,1123),(949,1119),(1060,1144),(1104,1167),(1104,1215),(1052,1189),(948,1167),(846,1172)])
    for i in range(9):
        x=755+i*40;y=1145-24*math.sin(i*math.pi/8)
        line([(x,y),(x,y+42)],1)
    line([(735,1148),(833,1117),(946,1113),(1070,1140),(1111,1166)],1)
    for x,y,w in [(936,1087,58),(943,1257,52),(941,1338,64),(912,1420,65),(978,1462,42)]:line([(x-w/2,y),(x,y-6),(x+w/2,y)],2)
    # Parcels, sled and a patterned blanket in the lower left.
    def gift(x,y,w,h):
        rect(x,y,w,h);rect(x+w*.43,y,w*.15,h,1);line([(x,y+h*.3),(x+w,y+h*.3)],1)
        polygon([(x+w*.5,y),(x+w*.17,y-24),(x+w*.12,y-8),(x+w*.5,y),(x+w*.82,y-24),(x+w*.9,y-7)],1)
        for px in [x+w*.19,x+w*.78]:
            for py in [y+h*.14,y+h*.5,y+h*.8]:star(px,py,min(w,h)*.07,2)
    for args in [(22,1362,94,105),(132,1315,98,153),(247,1380,120,91),(52,1253,103,102),(332,1319,105,136)]:gift(*args)
    sled_start=len(paths)
    polygon([(476,1429),(484,1365),(543,1380),(625,1368),(693,1380),(688,1429)])
    line([(475,1429),(487,1468),(705,1468),(733,1442),(730,1418)],0)
    line([(516,1430),(516,1468)],1);line([(660,1430),(660,1468)],1)
    for i in range(6):line([(493+i*31,1378),(503+i*31,1398),(493+i*31,1424)],2)
    gift(510,1300,92,71);gift(599,1313,74,56)
    for path in paths[sled_start:]:
        path['xy']=[(385+(x-476)*.75,y) for x,y in path['xy']]
    # Perched owl: reuse the approved authored anatomy, without its rectangular frame.
    for stroke in owl_art()[:23]:
        curve([(1230+(x-330)*.43,1220+(y-90)*.25) for x,y in stroke['xy']],-1,steps=2 if 'body' in stroke['name'] or 'facial' in stroke['name'] else 1)
    line([(1029,1490),(1200,1441),(1395,1432),(1500,1393)],0)
    line([(1050,1500),(1220,1461),(1401,1453),(1500,1414)],0)
    bough(1500,1483,200,-1)
    # Large holly sprays and ice crystals add interior marks to snow areas.
    def holly(x,y,s):
        for sign in [-1,1]:
            polygon([(x,y),(x+sign*s*.25,y-s*.3),(x+sign*s*.22,y-s*.6),(x+sign*s*.5,y-s*.52),(x+sign*s*.7,y-s),(x+sign*s*.8,y-s*.5),(x+sign*s,y-s*.35),(x+sign*s*.65,y-s*.25),(x+sign*s*.6,y),(x+sign*s*.25,y-s*.05)],1)
            line([(x,y),(x+sign*s*.7,y-s)],2)
        for dx,dy in [(-9,0),(10,0),(0,15)]:oval(x+dx,y+dy,10,10,6,1)
    for args in [(73,1151,63),(358,1223,54),(1182,1112,55)]:holly(*args)
    # Snow textures follow broad ground contours; every mark belongs to the art.
    for x,y,w in [(36,1215,51),(342,1280,70),(681,1228,80),(592,1263,72),(1131,1275,65),(1310,1180,69),(1448,1245,58),(400,1482,52),(741,1470,61)]:
        line([(x,y),(x+w*.4,y-9),(x+w,y-3)],2)
    # Daily focal motifs: all remain in-world (boughs, hanging decorations,
    # street furniture and wildlife), while scenery continues across page seams.
    def bird(x,y,s=1):
        def pts(values):return [(x+a*s,y+b*s) for a,b in values]
        organic(pts([(-54,9),(-45,-17),(-18,-29),(0,-49),(28,-47),(41,-28),(44,-5),(33,22),(9,40),(-20,33),(-45,22),(-75,38),(-62,12)]),-2)
        curve(pts([(-40,0),(-17,-5),(13,12),(-4,26),(-31,17)]),-2)
        polygon(pts([(40,-29),(59,-21),(42,-14)]),-2)
        oval(x+24*s,y-30*s,4*s,4*s,6,-2)
        for dx in [-10,10]:line(pts([(dx,34),(dx+2,53),(dx+13,55)]),-2)
    bird(156,162,.9)
    curve([(0,218),(104,207),(184,209),(287,184),(354,170)],-1)
    # Two bells hang from a bough in day 2.
    curve([(308,43),(430,54),(540,29),(643,48)],-1)
    for x,y in [(414,148),(493,169)]:
        curve([(x-29,y+24),(x-23,y-10),(x-17,y-33),(x,y-44),(x+18,y-32),(x+24,y-10),(x+30,y+24)],-2)
        oval(x,y+24,32,9,14,-2);oval(x,y+35,7,8,8,-2)
        curve([(x,y-44),(x-5,y-70),(447,57)],-2)
    organic([(447,61),(412,38),(400,54),(415,72),(447,61),(475,35),(486,50),(470,67)],-2)
    # A dove crosses the sky above the village (day 3).
    organic([(669,162),(704,143),(703,96),(722,112),(736,145),(776,132),(811,94),(803,127),(827,113),(806,149),(787,167),(756,177),(733,194),(706,191),(689,179)],-2)
    curve([(704,143),(738,163),(773,155)],-2)
    polygon([(684,166),(670,163),(680,176)],-2);oval(697,167,3,3,6,-2)
    # The existing moon is day 4's focal point; add a soft cloud below it.
    curve([(959,216),(979,203),(997,205),(1008,183),(1032,182),(1048,198),(1071,193),(1092,211),(1110,217)],-1)
    # Pine cone hanging naturally from the upper-right branch (day 5).
    curve([(1362,49),(1359,88),(1353,112)],-2)
    organic([(1353,112),(1326,123),(1315,151),(1320,186),(1341,219),(1356,229),(1380,199),(1390,166),(1385,132)],-2)
    for yy,half in [(134,20),(153,29),(173,28),(193,20)]:
        curve([(1353-half,yy),(1353-10,yy+7),(1353,yy+15),(1365,yy+8),(1353+half,yy)],-2,steps=2)
    # Lamppost on the central path: day 13 has a subject, not just paving.
    line([(785,842),(790,699),(779,695),(763,651),(811,651),(800,695),(790,699)],-2)
    curve([(763,651),(775,636),(787,626),(800,637),(811,651)],-2)
    line([(787,626),(787,611)],-2);line([(779,656),(783,687),(794,687),(798,656)],-2)
    curve([(771,845),(784,837),(799,845)],-2)
    # Large hanging bauble gives the tree's middle sheet its own complete detail.
    oval(149,1060,33,42,20,-2);rect(138,1009,22,12,-2)
    curve([(143,1009),(140,995),(150,989),(157,1002),(154,1009)],-2)
    curve([(119,1043),(145,1053),(180,1042)],-2)
    curve([(119,1071),(150,1081),(180,1068)],-2)
    # A duck swimming on the foreground stream, day 23.
    organic([(715,1353),(720,1330),(746,1320),(771,1326),(780,1310),(777,1296),(785,1282),(804,1286),(813,1302),(809,1326),(828,1338),(813,1356),(777,1371),(740,1371)],-2)
    polygon([(808,1297),(828,1303),(811,1310)],-2);oval(799,1297,3,3,6,-2)
    curve([(736,1335),(771,1336),(790,1350),(757,1354),(736,1335)],-2)
    curve([(694,1378),(728,1384),(779,1385),(835,1375)],-1)
    # A rabbit on the snowy bank, day 24.
    organic([(1022,1434),(1011,1411),(1021,1382),(1046,1367),(1064,1368),(1063,1342),(1050,1305),(1055,1284),(1068,1291),(1080,1335),(1087,1307),(1100,1296),(1107,1308),(1095,1349),(1109,1367),(1103,1390),(1084,1400),(1085,1431),(1064,1442)],-2)
    curve([(1035,1426),(1033,1408),(1049,1394),(1065,1398),(1070,1417),(1058,1432)],-2)
    oval(1093,1367,3,3,6,-2);oval(1017,1412,12,12,12,-2)
    line([(1104,1383),(1120,1379)],-2)
    # Small crystalline snow marks fill the surrounding air and ground. Their
    # positions are chosen over the whole composition, independently of page cuts.
    # Keep them clear of existing linework and the principal subject interiors.
    import numpy as np
    from scipy.spatial import cKDTree
    samples=[]
    for path in paths:
        for a,b in zip(path['xy'],path['xy'][1:]):
            n=max(2,int(math.dist(a,b)/6))
            samples.extend((a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1))
    tree=cKDTree(samples)
    for y0 in range(32,1480,29):
        for x0 in range(26,1490,32):
            x=x0+rng.uniform(-14,14);y=y0+rng.uniform(-12,12)
            if tree.query((x,y))[0]<(28 if y<340 else 17):continue
            # Angular ice marks, with pen lifts; these are actual source strokes.
            r=rng.choice([7,9,12])
            if y<340:
                line([(x-r,y),(x,y-r),(x+r,y),(x,y+r),(x-r,y)],3)
                line([(x,y-r-6),(x,y+r+6)],3)
                line([(x-r-6,y),(x+r+6,y)],3)
                for sign in [-1,1]:
                    line([(x-4,y+sign*(r+3)),(x,y+sign*(r-1)),(x+4,y+sign*(r+3))],3)
            elif 580<y<810 and 686<x<890:
                polygon([(x-r,y),(x,y-7),(x+r,y),(x,y+5)],3)
            elif y>810:
                if rng.random()<.55:
                    polygon([(x-r,y),(x-3,y-5),(x+3,y-5),(x+r,y),(x+3,y+5),(x-3,y+5)],3)
                    line([(x-3,y-5),(x+3,y+5)],3)
                else:
                    line([(x-r,y+3),(x,y-r/2),(x+r,y),(x+r*1.7,y-3)],3)
    return paths
