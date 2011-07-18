#!/usr/bin/python
#-*- coding: latin-1 -*-

from optparse import OptionParser
from cuadriculaMNT import *
from slippy_map  import *



usage = "usage: mtn.py [-5|-2] [-g] [-q] [-h]  columna fila"
parser = OptionParser(usage=usage)

parser.add_option("-5", "--50", action="store_true",dest="escala50",default=True,
                  help="Crea mapa MTN 1:50000")
parser.add_option("-2", "--200", action="store_false",dest="escala50",
                  help="Crea mapa MTN 1:200000")
parser.add_option("-i", "--ign", action="store_true",dest="ign",
                  help="Hoja IGN #")
parser.add_option("-t", "--todos", action="store_true",dest="todos",
                  help="Descarga todas las hojas IGN")
parser.add_option("-g", "--gpscycle", action="store_true",dest="gpscycle",default=False,
                  help="Trocea en tiles mas chicos para cargar en GPSCYCLECOMPUTER")
parser.add_option("-n", "--nombre", action="store",dest="nombre_mapa",type="string",
                  help="Busca la fila columna del mapa por el nombre (1:50000")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="operacion silenciosa")
parser.add_option("-p", "--png",
                  action="store_true", dest="png", default=False,
                  help="Crear imagen png en vez de jpg")

parser.add_option("-k", "--kml", action="store_true",dest="calibraKML",
                  help="Crea el fichero KML asociado",default=False)


(options, args) = parser.parse_args()

cuadricula=cuadricula_MNT()
mapa=cuadricula_slippy("MTN-RASTER") ##EL IDEE SOLO DEVUELVE ORTOFOTOS AHORA
#mapa=cuadricula_slippy("ORTO") ##EL IDEE SOLO DEVUELVE ORTOFOTOS AHORA



if options.escala50:
	escala=50
	zoom=15
else:
	#escala=200
	escala=200
	zoom=13


if options.nombre_mapa:
	cuadricula.ign.MTN50_nombre(options.nombre_mapa)
	quit()

if options.png:
	formato="PNG"
	exten=".png"
else:
	formato="JPEG"
	exten=".jpg"

if options.todos:
	for ig in range (1,800):
		escala=50
		(cc,ff)=cuadricula.ign.MTN50_N(ig)
		(se,no) = cuadricula.coord_MNT(escala,ff,cc)
		print "Creando mapa MTN(ign):",cuadricula.nombre
		f=cuadricula.nombre+".pnoa"
		im=mapa.get_bbox_lonlat((no.x,no.y),(se.x,se.y),zoom)
		im.save(f+exten,formato)
		calibr=calibrador(f,im.size,(se,no))
		calibr.write_kml()
	exit()


if options.ign:
	ig=int(args[0])
	escala=50
	(cc,ff)=cuadricula.ign.MTN50_N(ig)
	(se,no) = cuadricula.coord_MNT(escala,ff,cc)
	print "Creando mapa MTN(ign):",cuadricula.nombre

else:
	ff=int(args[0])
	cc=int(args[1])
	(se,no) = cuadricula.coord_MNT(escala,ff,cc)
	print "Creando mapa MTN:",cuadricula.nombre


f=cuadricula.nombre+".pnoa"

if options.gpscycle:
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
calibr.write_kml()




