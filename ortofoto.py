#!/usr/bin/python
#-*- coding: latin-1 -*-


import argparse
from slippy_map  import *

TiposDeMapas=('MTN-RASTER','PNOA-ORTO','OPENSTREETMAP')
TiposDeMapasStr='[' 
for tipo in TiposDeMapas:
	TiposDeMapasStr= TiposDeMapasStr+tipo+'|'

TiposDeMapasStr=TiposDeMapasStr[0:-1]
TiposDeMapasStr= TiposDeMapasStr+']'


parser = argparse.ArgumentParser(description='Descarga las teselas de los mapas los datos mapas RASTER del Instituto Geográfico Nacional, mapas del OpenStreetMap o composiciones de ortofotos basados en PNOA',epilog='2011. Nacho Mas')

parser.add_argument('-t', action='store', dest='tipo_mapa',help='Mapas disponibles:'+TiposDeMapasStr)
parser.add_argument('-o', action='store', dest='nombre',help='Nombre del fichero de salida')
parser.add_argument('-factor', action='store', dest='factor',default=1,help='0.1 milesimas de grado a cada lado del punto central',type=float)
parser.add_argument('lat',action='store',help='Latitud y longitud del punto central',type=float)
parser.add_argument('lon',action='store',help='Latitud y longitud del punto central',type=float)


args = parser.parse_args()

print args

#defino el tipo de mapa a generar
if args.tipo_mapa in (TiposDeMapas):
	if args.tipo_mapa=='MTN-RASTER':
		zoom=15
	if args.tipo_mapa=='PNOA-ORTO':
		zoom=20
	mapa=cuadricula_slippy(args.tipo_mapa)
else:
	print "Tipos de mapas disponibles " + TiposDeMapasStr
	quit()


(sex,sey)=(args.lon+0.0001*args.factor/math.sin(args.lat*math.pi/180),args.lat-0.0001*args.factor)
(nox,noy)=(args.lon-0.0001*args.factor/math.sin(args.lat*math.pi/180),args.lat+0.0001*args.factor)


m=mapa.get_bbox_lonlat((nox,noy),(sex,sey),zoom)
m.save(args.nombre+'.jpg','JPEG')


