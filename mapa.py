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

TiposDeCalibracion=('kml','txt','imp')
TiposDeCalibracionStr='[' 
for tipo in TiposDeCalibracion:
	TiposDeCalibracionStr= TiposDeCalibracionStr+tipo+'|'

TiposDeCalibracionStr=TiposDeCalibracionStr[0:-1]
TiposDeCalibracionStr= TiposDeCalibracionStr+']'


parser = argparse.ArgumentParser(description='Genera varios tipos de mapas usando la cuadricula MTN50 y derivadas. Los mapas los datos mapas RASTER del Instituto Geográfico Nacional, mapas del OpenStreetMap o composiciones de ortofotos basados en PNOA',epilog='2011. Nacho Mas')

parser.add_argument('-t', action='store', dest='tipo_mapa',help='Mapas disponibles:'+TiposDeMapasStr)
parser.add_argument('-c',action='store', dest='calibracion',default='kml',help='Calibración del mapa [txt|imp|KML] para GpsCycleComputer, Compegps o GoogleEarth respectivamente')
parser.add_argument('-gcc',action='store_true', dest='gpscyclecomputer',help='genera el mapa en trozos para GpsCycleComputer')
parser.add_argument('-b',action='store', dest='buscar',help='Busca un mapa en la base de datos por nombre de población')
parser.add_argument('-geoname',action='store', dest='nomgeo',help='Busca nombre de accidente geográfico(sin implemntar todavia)')
parser.add_argument('-e',action='store', dest='escala',help='Escala del mapa.[25 | 50 | 100 | 200 | All]')
parser.add_argument('-fc',action='store', dest='filacolumna',help='fila columna de la cuadricula MTN50',nargs=2,type=int)
parser.add_argument('-hoja',action='store', dest='hoja_mtn50',help='Especificar mapa por el numero de hoja de la cuadricula MTN50',type=int)
parser.add_argument('-png',action='store_true', dest='png',help='Crear imagen png en vez de jpg', default=False)
parser.add_argument('-latlon',action='store',dest='latlon',help='Busca por Latitud y longitud del punto central',nargs=2,type=float)


args = parser.parse_args()

#print args

cuadricula=cuadricula_MNT()

#Busco en la base de datos y devuelvo el resultado
if (args.buscar):
	cuadricula.ign.MTN25_nombre(args.buscar)
	quit()

#Busco en la base de datos y devuelvo el resultado
if (args.nomgeo):
	cuadricula.ign.nomgeo(args.nomgeo)
	quit()

if (args.latlon):
	se=coord(args.latlon[1],args.latlon[0])
	print se.grad()
	(cc,ff)=cuadricula.cuadricula(50,se)	
	cuadricula.ign.MTN50(cc,ff)
	quit()

#defino el tipo de mapa a generar
if args.tipo_mapa in (TiposDeMapas):
	mapa=cuadricula_slippy(args.tipo_mapa)
else:
	print "Tipos de mapas: "+args-tipo_mapa+" no soportado. Disponibles " + TiposDeMapasStr
	quit()

if args.calibracion not in (TiposDeCalibracion):
	print "Tipos de calibracion: "+args.calibracion+" no soportado. Disponibles " + TiposDeCalibracionStr
	quit()

if not (args.filacolumna) and not (args.hoja_mtn50):
	print "Elegir al menos -hoja o -fc. Nunca ambos."
	quit()

if args.png:
	formato="PNG"
	exten=".png"
else:
	formato="JPEG"
	exten=".jpg"

if (args.filacolumna):
	ff=int(args.filacolumna[0])
	cc=int(args.filacolumna[1])

if (args.hoja_mtn50):
	print int(args.hoja_mtn50)
	(cc,ff)=cuadricula.ign.MTN50_N(args.hoja_mtn50)
	args.escala=50
	zoom=15

if not (args.escala):
	print "Es necesario definir la escala del mapa"
	quit()

if (args.escala == '25'):
	zoom=15

if (args.escala == '50'):
	zoom=15
	
if (args.escala == '100'):
	zoom=13

if (args.escala == '200'):
	zoom=13

(se,no) = cuadricula.coord_MNT(int(args.escala),ff,cc)
f=cuadricula.nombre+"."+args.tipo_mapa

if (args.gpscyclecomputer):
	n=4 
	cc0=no
	cc1=se
	c0=coord(0,0)
	c1=coord(0,0)
	ancho=cc1.x-cc0.x
	alto=cc1.y-cc0.y
	xdelta=ancho/n
	ydelta=alto/n
	for i in range(n):
		c0.x=cc0.x+xdelta*(i)
		c1.x=c0.x+xdelta
		for j in range(n):
			c0.y=cc0.y+ydelta*(j)
			c1.y=c0.y+ydelta
			print i,j,c0.x,c0.y,c1.x,c1.y
			im=mapa.get_bbox_lonlat((c0.x,c0.y),(c1.x,c1.y),zoom)
			fi="GPSCYCLE_"+str(i)+"_"+str(j)+"_"+f+exten
			fichero=fi.upper()
			im.save(fichero,formato)
			calibr=calibrador(("GPSCYCLE_"+str(i)+"_"+str(j)+"_"+f).upper(),im.size,(c0,c1))
			calibr.write_txt()
	quit()


im=mapa.get_bbox_lonlat((no.x,no.y),(se.x,se.y),zoom)
im.save(f+exten,formato)
calibr=calibrador(f,im.size,(se,no))


if args.calibracion=='kml':
	calibr.write_kml()
if args.calibracion=='txt':
	calibr.write_txt()
if args.calibracion=='imp':
	calibr.write_imp()





