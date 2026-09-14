"""Authored straight-line adaptation of the generated winter-window reference.

Coordinates are the art: each distinct vertex will become one numbered dot.
All strokes are visible in source.svg; there is no latent raster answer layer.
"""


def artwork():
    strokes=[]
    def line(name, xy, close=False):
        if close: xy=xy+[xy[0]]
        strokes.append({'name':name,'xy':xy})
    # Outer body and angular head. Long lines intentionally have no in-between dots.
    line('body and ear tufts',[(470,360),(420,490),(375,690),(330,960),(350,1100),
         (385,1090),(450,1110),(600,1010),(680,860),(745,755),(790,590),(800,465),(780,365),
         (790,250),(830,90),(740,175),(655,160),(575,175),(485,90),(510,235),(480,300)],True)
    line('facial disc',[(510,235),(560,210),(655,230),(740,210),(790,250),(760,345),
         (705,400),(655,440),(590,395),(470,360)])
    line('left brow',[(485,90),(555,230),(625,290),(655,315)])
    line('right brow',[(830,90),(750,230),(685,290),(655,315)])
    line('forehead planes',[(575,175),(655,230),(740,175)])
    line('left eye',[(520,280),(555,255),(605,278),(615,305),(590,332),(555,340),(525,315)],True)
    line('left pupil',[(553,277),(575,275),(585,294),(573,311),(550,304)],True)
    line('right eye',[(690,278),(738,250),(770,280),(766,310),(737,335),(709,332),(685,305)],True)
    line('right pupil',[(727,273),(748,273),(758,293),(745,309),(723,303)],True)
    line('beak',[(655,315),(675,355),(652,398),(637,355)],True)
    line('left cheek planes',[(480,300),(525,315),(535,355),(590,395),(615,305)])
    line('right cheek planes',[(766,310),(775,355),(705,400),(685,305)])
    line('face to breast',[(470,360),(540,375),(590,395),(575,475),(655,535),(725,470),(705,400),(780,365)])
    line('left wing boundary',[(590,395),(510,510),(450,675),(405,880),(350,1100)])
    line('right wing boundary',[(705,400),(725,580),(680,760),(600,1010)])
    line('breast chevrons',[(575,475),(620,610),(685,675),(725,580),(725,470)])
    line('feather 1',[(420,490),(510,510),(480,590),(405,700),(375,690)])
    line('feather 2',[(450,675),(535,585),(510,760),(405,880)])
    line('feather 3',[(510,760),(590,660),(565,840),(460,1000),(450,1110)])
    line('feather 4',[(565,840),(630,770),(610,910),(550,1045)])
    line('feather 5',[(620,610),(630,770),(680,760),(745,755)])
    line('wing facets',[(790,590),(725,580),(765,510),(800,465)])
    # Feet and branch are genuine additional strokes; they are not decoy dots.
    line('branch upper',[(90,1030),(305,945),(405,900),(650,800),(870,690),(1110,540)])
    line('branch lower',[(90,1095),(305,1010),(405,970),(650,865),(900,750),(1110,605)])
    line('left talons',[(495,865),(505,820),(535,800),(565,820),(570,860),(548,900),(540,840),(520,825),(505,820)])
    line('right talons',[(595,830),(610,790),(640,775),(665,792),(675,830),(650,865),(645,815),(625,795),(610,790)])
    # Rectangular scene, with no empty field around a subject silhouette.
    line('frame',[(90,90),(1110,90),(1110,1110),(90,1110)],True)
    line('upper mountains',[(90,410),(195,315),(290,435),(385,330),(420,490)])
    line('right mountains',[(800,465),(890,365),(950,435),(1035,310),(1110,420)])
    line('mountain facets',[(890,365),(920,495),(1035,310),(1060,470)])
    line('right horizon',[(790,590),(920,495),(1110,470)])
    line('background upper left',[(90,90),(270,190),(485,90)])
    line('background top',[(270,90),(270,190),(510,235)])
    line('background upper right',[(830,90),(945,175),(1110,90)])
    line('background right',[(945,175),(1110,265),(950,435)])
    line('moon',[(1000,150),(960,175),(950,220),(980,250),(1025,245),(1045,225),(1005,230),(982,207),(982,178)],True)
    line('left background facet',[(90,550),(280,650),(375,690)])
    line('lower background facet',[(90,775),(255,880),(305,945)])
    line('bottom background facet',[(90,1110),(230,1065),(290,1110)])
    line('right background facet',[(900,750),(990,855),(1110,785)])
    line('lower right facet',[(680,860),(835,960),(890,1110)])
    line('tail backdrop',[(600,1010),(680,1110)])
    # A few large pine sprays: bent polygons rather than dense regular contour sampling.
    line('pine upper stem',[(120,125),(270,245),(350,300)])
    line('pine upper needles',[(120,125),(145,240),(180,210),(185,295),(220,255),
         (240,335),(270,285),(310,355),(295,275),(370,300),(330,245),(370,240),
         (285,215),(310,175),(220,175),(230,140),(120,125)])
    line('pine lower stem',[(930,820),(1030,950),(1070,1080)])
    line('pine lower needles',[(930,820),(900,920),(960,885),(935,990),(995,940),
         (975,1060),(1030,1005),(1070,1080),(1060,980),(1110,1030),(1080,930),
         (1110,940),(1040,860),(1045,820),(970,835),(930,820)])
    spray=[(0,0),(10,45),(30,25),(45,85),(60,50),(90,115),(90,65),
           (135,95),(110,45),(145,50),(100,15),(130,5),(75,-5),(60,-25),(40,-5)]
    for name,origin in [('left middle spray',(105,565)),('left lower spray',(135,800)),
                        ('right middle spray',(845,500)),('left upper middle spray',(95,430))]:
        ox,oy=origin
        line(name,[(ox+x,oy+y) for x,y in spray],True)
    return strokes
