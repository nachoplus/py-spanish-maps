#!/usr/bin/python
#-*- coding: latin-1 -*-

import argparse
from cuadriculaMNT import *
from slippy_map  import *

TiposDeMapas=('MTN-RASTER','PNOA-ORTO','OPENSTREETMAP')
TiposDeMapasStr='[' 
for tipo in TiposDeMapas:
	TiposDeMapasStr= TiposDeMapasStr+tipo+'|'

TiposDeMapasStr=TiposDeMapasStr[0:-1]
TiposDeMapasStr= TiposDeMapasStr+']'


parser = argparse.ArgumentParser(description='Descarga las teselas de los mapas los datos mapas RASTER del Instituto Geográfico Nacional, mapas del OpenStreetMap o composiciones de ortofotos basados en PNOA',epilog='2011. Nacho Mas')

parser.add_argument('-t', action='store', dest='tipo_mapa',help='Mapas disponibles:'+TiposDeMapasStr)
parser.add_argument('-n', action='store', dest='numtiles20',default=1,help='Area expresada en numero de teselas del zoom=20')
parser.add_argument('lat',action='store',help='Latitud y longitud del punto central',type=float)
parser.add_argument('lon',action='store',help='Latitud y longitud del punto central',type=float)


args = parser.parse_args()

print args

#defino el tipo de mapa a generar
if args.tipo_mapa in (TiposDeMapas):
	if args.tipo_mapa=='MTN-RASTER':
		zoomsNativos=(15,13,10)
		restOfZoom=range(10,15)
	if args.tipo_mapa=='PNOA-ORTO':
		zoomsNativos=(20,13)
		restOfZoom=range(10,20)
	mapa=cuadricula_slippy(args.tipo_mapa)
else:
	print "Tipos de mapas disponibles " + TiposDeMapasStr
	quit()





#Descargo los nativos
for zoom in zoomsNativos:
	n=int(args.numtiles20)/2**(20-zoom)	
	print "Zoom:",zoom,"Tiles",n
	(xtile0,ytile0)=mapa.deg2num(args.lon,args.lat, zoom)
	for xtile in range(xtile0-n,xtile0+n):
		for ytile in range(ytile0-n,ytile0+n):
			mapa.get(xtile,ytile,zoom)

#Descargo el resto
print restOfZoom
for zoom in restOfZoom:
	n=int(args.numtiles20)/2**(20-zoom)	
	print "Zoom:",zoom,"Tiles",n
	(xtile0,ytile0)=mapa.deg2num(args.lon,args.lat, zoom)
	for xtile in range(xtile0-n,xtile0+n):
		for ytile in range(ytile0-n,ytile0+n):
			mapa.get(xtile,ytile,zoom)
