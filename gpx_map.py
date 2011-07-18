#!/usr/bin/python

import sys, os, Image ,ImageDraw, ImageFont, ImagePath, ImageOps,ImageStat
from cuadriculaMNT import *
import pprint
import xml.dom.minidom
from xml.dom.minidom import Node
from slippy_map import *


class gpx():
	z=15
	minx=9999999999999999
	maxx=-99999999999999999
	miny=999999999999999
	maxy=-99999999999999999
	Xlen=float
	Ylen=float
	puntos=[]
	nombre=None
	def __init__(self,gpxfile):
		self.nombre=gpxfile
		doc = xml.dom.minidom.parse(gpxfile)
 	 	for node in doc.getElementsByTagName("gpx"):
  			traks = node.getElementsByTagName("trk")
  			for trak in traks:
    				traksegs = trak.getElementsByTagName("trkseg")
    				for trakseg in traksegs:
					trakpts= trakseg.getElementsByTagName("trkpt")
					for trakpt in trakpts:
						self.puntos.append((float(trakpt.getAttribute("lat")),float(trakpt.getAttribute("lon"))))
						if float(trakpt.getAttribute("lon")) >= self.maxx:
							self.maxx=float(trakpt.getAttribute("lon"))
						if float(trakpt.getAttribute("lon")) <= self.minx:
							self.minx=float(trakpt.getAttribute("lon"))
						if float(trakpt.getAttribute("lat")) >= self.maxy:
							self.maxy=float(trakpt.getAttribute("lat"))
						if float(trakpt.getAttribute("lat")) <= self.miny:
							self.miny=float(trakpt.getAttribute("lat"))


		self.Xlen=self.maxx-self.minx
		self.Ylen=self.maxy-self.miny
		ax=self.Xlen*0.05
		ay=self.Xlen*0.05

		self.maxx=self.maxx+ax
		self.minx=self.minx-ax
		self.maxy=self.maxy+ay
		self.miny=self.miny-ay
	    	self.mapa=cuadricula_slippy("PNOA")
	
	def resumen(self):
		print "Nombre",self.nombre
		print "Numero de puntos",len(self.puntos)
		print "Max",self.maxx,self.maxy
		print "Min",self.minx,self.miny
		print "Tam:",self.Xlen,self.Ylen

	def pinta(self,strip=True):
		if strip:
			im=self.get_strip_map()
		else:
			im=self.get_mapa()

		(lat1,lon1)=(self.miny,self.maxx)
		(lat0,lon0)=(self.maxy,self.minx)
		im=self.mapa.recorta(im,(self.minx,self.maxy),(self.maxx,self.miny),self.z)
		(ancho,alto)=(lon1-lon0,lat1-lat0)
		(anchoI,altoI)=(float(im.size[0]),float(im.size[1]))
		print "PINTA:",(ancho,alto),(anchoI,altoI)
		def xy((lat,lon)):
			xx=lon-lon0
			yy=lat-lat0
			x=int(anchoI)*xx/ancho
			y=int(altoI)*yy/alto
			#print self.minx,self.miny,lon,lat,xx,yy,x,y
			return (x,y)
		draw=ImageDraw.Draw(im)
		p=ImagePath.Path(map(xy,self.puntos))
		p.compact()
		draw.line(p,width=8,fill='#0000FF')
		return im


	def get_mapa(self):

		(lat1,lon1)=(self.miny,self.maxx)
		(lat0,lon0)=(self.maxy,self.minx)
		(xtile0,ytile0)=self.mapa.deg2num(lon0,lat0,self.z)
		(xtile1,ytile1)=self.mapa.deg2num(lon1,lat1,self.z)
		print (lat0,lon0),(lat1,lon1),	(xtile0,ytile0),	(xtile1,ytile1)
		im=self.mapa.paste((xtile0,ytile0),(xtile1,ytile1),self.z)
		self.size=im.size
		return im
	
	def get_strip_map(self):
		(xtile0,ytile1)=self.mapa.deg2num(self.minx,self.miny,self.z)
		(xtile1,ytile0)=self.mapa.deg2num(self.maxx,self.maxy,self.z)
		imgx=self.mapa.imgx
		imgy=self.mapa.imgy
		x_n=xtile1-xtile0+1
		y_n=ytile1-ytile0+1
		print x_n,y_n
                size=(imgx*x_n,imgy*y_n)
		Im=Image.new("RGB",size,"#ffffff")
		self.size=Im.size		
		nteselas=[]
		margen=1
		for punto in self.puntos:
			(xtile,ytile)=self.mapa.deg2num(punto[1],punto[0],self.z)
			for j in range(-margen,margen+1):
				for k in range(-margen,margen+1):
					nteselas.append((xtile+j,ytile+k))
		
		for i in range(x_n):
			x0=imgx*(i)
			x1=imgx*(1+i)
			for j in range(y_n):
				#print i+xtile0,j+ytile0
				if (i+xtile0,j+ytile0) in nteselas:
					print "teselando"
					y0=imgy*(j)
					y1=imgy*(j+1)
					ima=self.mapa.get(i+xtile0,j+ytile0,self.z)
					Im.paste(ima,(x0,y0,x1,y1))
		return Im

	def save(self,strip=True):
		im=self.pinta(strip)
		im.save(self.nombre+'.jpg', "jpeg")

	def gpscycle(self,strip=True):
		imm=self.pinta(strip)
		L=imm.size[1]
		A=imm.size[0]
		(nx,kk)=divmod(A , 1200)
		(ny,kk)=divmod(L,1200)
		nx=nx+1
		ny=ny+1
		print "gpscycle:",A,L,nx,ny
		se=coord(self.maxx,self.miny)
		no=coord(self.minx,self.maxy)
		#c=calibrador(self.nombre,self.size,(se,no))
		cc0=no
		cc1=se
		c0=coord(0,0)
		c1=coord(0,0)
		ancho=cc1.x-cc0.x
		alto=cc1.y-cc0.y
		xdelta=ancho/nx
		ydelta=alto/ny
		xpix0=0
		ypix0=0
		xpix1=0
		ypix1=0
		pixdeltax=A/nx
		pixdeltay=L/ny
		print ancho,alto,xdelta,ydelta,pixdeltax,pixdeltay
		f=self.nombre
		for i in range(nx):
		  c0.x=cc0.x+xdelta*(i)
		  c1.x=c0.x+xdelta
		  for j in range(ny):
			c0.y=cc0.y+ydelta*(j)
			c1.y=c0.y+ydelta
			xpix0=pixdeltax*(i)
			ypix0=pixdeltay*(j)
			xpix1=pixdeltax*(i+1)
			ypix1=pixdeltay*(j+1)
			print i,j,c0.x,c0.y,c1.x,c1.y
			print xpix0,ypix0,xpix1,ypix1
			im=imm.crop((xpix0,ypix0,xpix1,ypix1))
			stat=ImageStat.Stat(im) 
			print "STAT",stat.stddev,stat.extrema
			if stat.stddev[0] >= 10**-5 or stat.stddev[2] >= 10**-5 or stat.stddev[2] >= 10**-5:
				fichero="GPSCYCLE_"+str(i)+"_"+str(j)+"_"+f+'.jpg'
				im.save(fichero,"jpeg")
				calibr=calibrador(("GPSCYCLE_"+str(i)+"_"+str(j)+"_"+f),im.size,(c0,c1))
				calibr.write_txt()		

if __name__ == '__main__': 
	ruta=gpx(sys.argv[1])
#	ruta.gpscycle(True)
	ruta.pinta(False).show()

	







