"""A single authored winter village, in shared 1500-unit scene coordinates."""
import math
import random
from dot_to_dot.winter_scene import artwork as owl_art


def artwork():
    paths=[];rng=random.Random(2512)
    def line(xy, priority=0):
        paths.append({'xy':xy,'priority':priority})
    def polygon(xy, priority=0):line(xy+[xy[0]],priority)
    def rect(x,y,w,h,p=0):polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],p)
    def oval(x,y,rx,ry,n=12,p=0):polygon([(x+rx*math.cos(i*2*math.pi/n),y+ry*math.sin(i*2*math.pi/n)) for i in range(n)],p)
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
        line([(x-12,y),(x+10,y-9),(peak,roof-7),(x+w-7,y-9),(x+w+12,y)],1)
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
        polygon(points)
        for i in range(1,5):
            yy=y-h+h*.88*i/levels
            line([(x-w*.38*i/levels,yy+9),(x,yy+20),(x+w*.38*i/levels,yy+9)],1)
        if decorated:
            star(x,y-h-12,24,0)
            for i in range(1,6):
                yy=y-h+h*.83*i/6
                half=w*.34*i/6
                line([(x-half,yy),(x-half*.4,yy+20),(x+half*.35,yy+29),(x+half,yy+14)],1)
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
    for args in [(12,686,180,184),(215,631,202,208),(458,661,194,200),(951,654,225,216),(1231,658,246,233)]:house(*args)
    # Stone streets and snow banks are continuous, not individual tile borders.
    for xy in [[(0,843),(202,813),(358,802),(585,837),(720,809),(914,815),(1185,840),(1500,817)],
               [(0,590),(212,568),(429,578),(635,572),(839,557),(1037,583),(1235,564),(1500,588)],
               [(691,558),(734,630),(711,727),(768,809)],
               [(827,558),(799,653),(850,737),(893,809)]]:line(xy,1)
    # Market stalls with striped awnings and wares.
    def stall(x,y,w):
        polygon([(x,y),(x+22,y-53),(x+w-22,y-53),(x+w,y)],0)
        for i in range(1,7):line([(x+22+(w-44)*i/7,y-53),(x+w*i/7,y)],1)
        line([(x+8,y),(x+8,y+106),(x+w-8,y+106),(x+w-8,y)],0)
        rect(x,y+57,w,35,0)
        for i in range(6):oval(x+18+i*(w-36)/5,y+42,10,13,6,1)
        for xx in [x+20,x+w-20]:line([(xx,y+92),(xx,y+118)],1)
    stall(665,947,188);stall(909,924,180);stall(1206,937,197)
    # Garland joins stalls across the square.
    line([(632,852),(728,882),(816,887),(908,852)],1)
    for x,y in [(657,862),(706,875),(756,885),(806,887),(855,876),(892,860)]:star(x,y+15,10,2)
    pine(206,1225,358,490,True)
    pine(1461,1190,173,420)
    # Snowman with hat, scarf, twig arms and a lantern nearby.
    oval(525,1152,78,91,16);oval(525,1044,51,53,12)
    polygon([(467,1005),(581,1005),(581,994),(560,994),(556,947),(493,947),(490,994),(467,994)])
    line([(494,1054),(549,1060),(521,1077)],0)
    for x in [510,540]:oval(x,1031,4,4,4,1)
    for y in [1110,1147,1184]:oval(525,y,6,6,6,1)
    polygon([(480,1076),(528,1089),(571,1072),(574,1090),(534,1106),(524,1140),(507,1137),(514,1104),(481,1095)],1)
    line([(455,1137),(404,1096),(383,1065)],0);line([(404,1096),(376,1091)],1)
    line([(595,1130),(648,1077),(666,1048)],0);line([(648,1077),(680,1080)],1)
    # Curving frozen river and bridge. River edges continue through the foreground.
    line([(922,1038),(887,1093),(868,1157),(913,1235),(890,1309),(837,1390),(831,1500)])
    line([(1047,1038),(1030,1099),(1013,1160),(1080,1235),(1036,1316),(1000,1418),(1025,1500)])
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
    polygon([(476,1429),(484,1365),(543,1380),(625,1368),(693,1380),(688,1429)])
    line([(475,1429),(487,1468),(705,1468),(733,1442),(730,1418)],0)
    line([(516,1430),(516,1468)],1);line([(660,1430),(660,1468)],1)
    for i in range(6):line([(493+i*31,1378),(503+i*31,1398),(493+i*31,1424)],2)
    gift(510,1300,92,71);gift(599,1313,74,56)
    # Perched owl: reuse the approved authored anatomy, without its rectangular frame.
    for stroke in owl_art()[:23]:
        line([(1095+(x-330)*.53,1210+(y-90)*.25) for x,y in stroke['xy']],0 if 'body' in stroke['name'] else 1)
    line([(1029,1490),(1200,1441),(1395,1432),(1500,1393)],0)
    line([(1050,1500),(1220,1461),(1401,1453),(1500,1414)],0)
    bough(1500,1483,200,-1)
    # Large holly sprays and ice crystals add interior marks to snow areas.
    def holly(x,y,s):
        for sign in [-1,1]:
            polygon([(x,y),(x+sign*s*.25,y-s*.3),(x+sign*s*.22,y-s*.6),(x+sign*s*.5,y-s*.52),(x+sign*s*.7,y-s),(x+sign*s*.8,y-s*.5),(x+sign*s,y-s*.35),(x+sign*s*.65,y-s*.25),(x+sign*s*.6,y),(x+sign*s*.25,y-s*.05)],1)
            line([(x,y),(x+sign*s*.7,y-s)],2)
        for dx,dy in [(-9,0),(10,0),(0,15)]:oval(x+dx,y+dy,10,10,6,1)
    for args in [(73,1151,63),(358,1223,54),(729,1351,59),(1408,1312,62),(1182,1112,55)]:holly(*args)
    # Snow textures follow broad ground contours; every mark belongs to the art.
    for x,y,w in [(36,1215,51),(342,1280,70),(681,1228,80),(592,1263,72),(1131,1275,65),(1310,1180,69),(1448,1245,58),(400,1482,52),(741,1470,61)]:
        line([(x,y),(x+w*.4,y-9),(x+w,y-3)],2)
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
            if tree.query((x,y))[0]<(22 if y<810 else 17):continue
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
