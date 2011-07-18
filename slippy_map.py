#!/usr/bin/python
#-*- coding: latin-1 -*-

import math
import sys, os
import Image


class cuadricula_slippy:
	dirbase=None
	imgx = int(256)
	imgy = int(256)
	tipo=None
	debug=1
	
	def __init__(self,tipo="PNOA"):
	#crea la estructura basica de directorios
		self.dirbase=tipo
		self.tipo=tipo
	    	if not os.path.isdir(self.dirbase):
	        	os.mkdir(self.dirbase)
		for z in range(1,19):
        		zoom = "%s" % z
        		if not os.path.isdir(self.dirbase+"/" + zoom):
            			os.mkdir(self.dirbase +"/"+ zoom)
		

	def deg2num(self,lon_deg,lat_deg, zoom):
	#coord to tile num
		lat_rad = lat_deg * math.pi / 180.0
  		n = 2.0 ** zoom
  		xtile = int((lon_deg + 180.0) / 360.0 * n)
  		ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  		return (xtile, ytile)

	def num2deg(self,xtile, ytile, zoom):
	#tile numbers to lon/lat
		n = 2.0 ** zoom
		lon_deg = xtile / n * 360.0 - 180.0
 		lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
		lat_deg = lat_rad * 180.0 / math.pi
		return (lat_deg, lon_deg)

	def num2tile_name(self,xtile, ytile, zoom):
	#calcula el nombre del tile /zoom/x/y.png si no existe el directorio lo crea
       		if not os.path.isdir(self.dirbase+"/" + str(zoom)+"/"+str(xtile)):
       			os.mkdir(self.dirbase +"/"+ str(zoom)+"/"+str(xtile))

		name=self.dirbase+"/"+str(zoom)+"/"+str(xtile)+"/"+str(ytile)+".png"
		return name

	def deg2tile_name(self,lon_deg,lat_deg, zoom):
	#calcula el nombre del tile /zoom/x/y.png  desde las lat/lon
		(xtile,ytile)=self.deg2num( lon_deg,lat_deg, zoom)
		return self.num2tile_name(xtile, ytile, zoom)

	def get_bbox_lonlat(self,(xl,yu),(xr,yd),zoom,recorta=1):
	#crea y ensambla todos los tiles de una bbox lonlat
	#si recorta = 1 le quita la prate sobrante al la imagen
		(xtile1,ytile1)=self.deg2num(xr,yd,zoom)
		(xtile0,ytile0)=self.deg2num(xl,yu,zoom)
		print "BBOX_LONLAT:",(xl,yu),(xr,yd),(xtile0,ytile0),(xtile1,ytile1)
		i=self.get_bbox((xtile0,ytile0),(xtile1,ytile1),zoom)
		if recorta==0:
			return i
		#recorta el sobrante
		return self.recorta(i,(xl,yu),(xr,yd),zoom)

	def recorta(self,im,(xl,yu),(xr,yd),zoom):
		(xtile1,ytile1)=self.deg2num(xr,yd,zoom)
		(xtile0,ytile0)=self.deg2num(xl,yu,zoom)
		print "BBOX_LONLAT:",(xl,yu),(xr,yd),(xtile0,ytile0),(xtile1,ytile1)
		n_x=(xtile1-xtile0)
		n_y=(ytile1-ytile0)
		(y0,x0)=self.num2deg(xtile0,ytile0,zoom)
		(y1,x1)=self.num2deg(xtile0+n_x,ytile0+n_y,zoom)		
		print "RECORTANDO:",(x0,y0),(x1,y1)
		(sizex,sizey)=(n_x*self.imgx,n_y*self.imgy)
		xpix0=int((xl-x0)*sizex/(x1-x0))
		xpix1=int((xr-x0)*sizex/(x1-x0))
		ypix0=int((yu-y0)*sizey/(y1-y0))
		ypix1=int((yd-y0)*sizey/(y1-y0))
		print "RECORTANDO:",xpix0,ypix0,xpix1,ypix1
		return im.crop((xpix0,ypix0,xpix1,ypix1))




	def get_bbox(self,(xtile0,ytile0),(xtile1,ytile1),zoom):
	#crea y ensambla todos los tiles de una bbox
		x_n=xtile1-xtile0+1
		y_n=ytile1-ytile0+1
		print x_n,y_n
		size=(self.imgx*x_n,self.imgy*y_n)
		Im=Image.new("RGB",size,"#FFFFFF")
		for i in range(x_n):
			x0=self.imgx*(i)
			x1=self.imgx*(1+i)
			for j in range(y_n):
				y0=self.imgy*(j)
				y1=self.imgy*(j+1)
				print i,j,zoom,size[0],size[1],x0,y0,x1,y1
				ima=self.get(i+xtile0,j+ytile0,zoom)
				Im.paste(ima,(x0,y0,x1,y1))
		return Im

	def get(self,xtile,ytile,zoom,download=True):
		print "GET",xtile,ytile
	#descarga los titel
		if self.tipo == "MTN-RASTER":
			return self.mtnRaster_get(xtile,ytile,zoom,download)
		if self.tipo == "PNOA-ORTO":
			return self.pnoa_get(xtile,ytile,zoom,download)
		if self.tipo == "OPENSTREETMAP":
			return self.openstreetmap_get(xtile,ytile,zoom,download)

	def avance_descarga(self,count,blocksize,total):
		#retorna el avance de la descarga desde el servidor IDEE
			print "recibidos "+ str(count*blocksize) +" de " +  str(total) + " ("+str(count*blocksize*100/total)+" %)"
	

	def get_from_low_zoom_level(self,(xtile,ytile),zoom):
	#compone una imagen uniendo y redimensionando las del nivel de zoom inferior
		nombre_fichero=self.num2tile_name(xtile,ytile,zoom)
		if os.path.isfile(nombre_fichero):
			print nombre_fichero," YA DESCARGADO"
			try:
				return	Image.open(nombre_fichero)
			except IOError:
				print "fichero no existe"

		else:
			Im=self.paste((2*xtile,2*ytile),(2*xtile+1,2*ytile+1),zoom+1)
					
		Im=Im.resize((self.imgx,self.imgy))
		Im.save(nombre_fichero,"PNG")
		return Im

	def paste(self,(xtile0,ytile0),(xtile1,ytile1),zoom):
	#devuelve una imagen resultado de la unión de tiles
		x_n=xtile1-xtile0+1
		y_n=ytile1-ytile0+1
		size=(self.imgx*x_n,self.imgy*y_n)
		print "PASTE:",x_n,y_n,size,zoom
		print "PASTE:",(xtile0,ytile0),(xtile1,ytile1)
		Im=Image.new("RGB",size,"#FFFFFF")
		for i in range(x_n):
			x0=self.imgx*(i)
			x1=self.imgx*(1+i)
			for j in range(y_n):
				y0=self.imgy*(j)
				y1=self.imgy*(j+1)
				print i,j,zoom,size[0],size[1],x0,y0,x1,y1
				ima=self.get(i+xtile0,j+ytile0,zoom)
				Im.paste(ima,(x0,y0,x1,y1))
		return Im

	def mtnRaster_get(self,xtile,ytile,zoom,download=True):
	#descarga y almacena un tile del servidor PNOA del IDEE
		import urllib
		import socket
		socket.setdefaulttimeout(12)
		size=(self.imgx,self.imgy)
		Im=Image.new("RGB",size,"#FFFFFF")
		urlbase="http://www.idee.es/wms/MTN-Raster/MTN-Raster?"
		urlbase=urlbase+"VERSION=1.1.0&REQUEST=GetMap&SRS=EPSG:4326&LAYERS=mtn_rasterizado&STYLES=&FORMAT=image/png&EXCEPTIONS=INIMAGE"

		nombre_fichero=self.num2tile_name(xtile,ytile,zoom)
		if os.path.isfile(nombre_fichero):
			print nombre_fichero," YA DESCARGADO"
			try:
				Im=Image.open(nombre_fichero)
				(xx,yy)= Im.size
				if self.imgx <> xx or self.imgy <>yy:
				#algo a ido mal. borro el fichero y lo vuelvo a descargar
					print "tamaño erroneo. borrando...",nombre_fichero
					os.remove(nombre_fichero)
					return self.pnoa_get(xtile,ytile,zoom)
				else:
				# todo bien. 
					return	Im
			except IOError:
				print "fichero erroneo. borrando...",nombre_fichero
				os.remove(nombre_fichero)
				if download:
					return self.pnoa_get(xtile,ytile,zoom)
				else:
					return None
		else:
			#zooms nativos 15->MTN50 13 ->MTN200 10->MTN1000				
			if zoom == 15 or zoom==13 or zoom == 10 or zoom == 17:
				#factor=0.95
				factor=1
			if zoom <> 15 and zoom<>13 and zoom <> 10  and zoom <> 17 :
				print "MERGING FROM LOW LEVEL TILES:",zoom+1
				return self.get_from_low_zoom_level((xtile,ytile),zoom)
			nTile=6			
			(lat1,lon0)=self.num2deg(xtile, ytile, zoom)
			(lat0,lon1)=self.num2deg(xtile+nTile, ytile+nTile, zoom)
			BigTileIm=Image.new("RGB",(self.imgx*nTile,self.imgy*nTile),"#FFFFFF")
			urlbase=urlbase+"&WIDTH="+str(self.imgx*factor*nTile)+"&HEIGHT="+str(self.imgy*factor*nTile)
			bbox="&BBOX="+str(lon0)+","+str(lat0)+","+str(lon1)+","+str(lat1)		
			url=urlbase+bbox
			if self.debug:
				grados=lat1-lat0
				print self.imgx*factor/grados
				print "DESCARGANDO:"+nombre_fichero+"\n"+url
			while 1:
				try:		
					f=urllib.urlretrieve(url,"tmp.png",reporthook=self.avance_descarga)[0]
					i=Image.open(f)
					BigTileIm=i.resize((self.imgx*nTile,self.imgy*nTile))
					for k in range(nTile):

							for j in range(nTile):
								nombre_fichero=self.num2tile_name(xtile+k,ytile+j,zoom)
								Im=BigTileIm.crop((k*self.imgx,j*self.imgy,(k+1)*self.imgx,(j+1)*self.imgy))
								Im.save(nombre_fichero,"PNG")
					return Im
					break
				except IOError:
					print "Timeout: Pruebo otra vez"


	def pnoa_get(self,xtile,ytile,zoom,download=True):
	#descarga y almacena un tile del servidor PNOA del IDEE
		import urllib
		import socket
		socket.setdefaulttimeout(12)
		size=(self.imgx,self.imgy)
		Im=Image.new("RGB",size,"#FFFFFF")
		urlbase="http://www.idee.es/wms/PNOA/PNOA?"
		urlbase=urlbase+"VERSION=1.1.0&REQUEST=GetMap&SRS=EPSG:4326&LAYERS=PNOA&STYLES=&FORMAT=image/png&EXCEPTIONS=INIMAGE"

		nombre_fichero=self.num2tile_name(xtile,ytile,zoom)
		if os.path.isfile(nombre_fichero):
			print nombre_fichero," YA DESCARGADO"
			try:
				Im=Image.open(nombre_fichero)
				(xx,yy)= Im.size
				if self.imgx <> xx or self.imgy <>yy:
				#algo a ido mal. borro el fichero y lo vuelvo a descargar
					print "tamaño erroneo. borrando...",nombre_fichero
					os.remove(nombre_fichero)
					return self.pnoa_get(xtile,ytile,zoom)
				else:
				# todo bien. 
					return	Im
			except IOError:
				print "fichero erroneo. borrando...",nombre_fichero
				os.remove(nombre_fichero)
				if download:
					return self.pnoa_get(xtile,ytile,zoom)
				else:
					return None
		else:
			#zooms nativos 15->MTN50 13 ->MTN200 10->MTN1000				
			if  zoom == 17:
				#factor=0.95
				factor=1
			if  zoom <> 17 :
				print "MERGING FROM LOW LEVEL TILES:",zoom+1
				return self.get_from_low_zoom_level((xtile,ytile),zoom)
			nTile=6			
			(lat1,lon0)=self.num2deg(xtile, ytile, zoom)
			(lat0,lon1)=self.num2deg(xtile+nTile, ytile+nTile, zoom)
			BigTileIm=Image.new("RGB",(self.imgx*nTile,self.imgy*nTile),"#FFFFFF")
			urlbase=urlbase+"&WIDTH="+str(self.imgx*factor*nTile)+"&HEIGHT="+str(self.imgy*factor*nTile)
			bbox="&BBOX="+str(lon0)+","+str(lat0)+","+str(lon1)+","+str(lat1)		
			url=urlbase+bbox
			if self.debug:
				grados=lat1-lat0
				print self.imgx*factor/grados
				print "DESCARGANDO:"+nombre_fichero+"\n"+url
			while 1:
				try:		
					f=urllib.urlretrieve(url,"tmp.png",reporthook=self.avance_descarga)[0]
					i=Image.open(f)
					BigTileIm=i.resize((self.imgx*nTile,self.imgy*nTile))
					for k in range(nTile):

							for j in range(nTile):
								nombre_fichero=self.num2tile_name(xtile+k,ytile+j,zoom)
								Im=BigTileIm.crop((k*self.imgx,j*self.imgy,(k+1)*self.imgx,(j+1)*self.imgy))
								Im.save(nombre_fichero,"PNG")
					return Im
					break
				except IOError:
					print "Timeout: Pruebo otra vez"

				
	def openstreetmap_get(self,xtile,ytile,zoom,download=True):
	#no funciona el servidor me manda tiles azules
		import urllib
		import socket
		socket.setdefaulttimeout(10)
		size=(self.imgx,self.imgy)
		Im=Image.new("RGB",size,"#FFFFFF")
		url="http://tah.openstreetmap.org/Tiles/tile/"+str(zoom)+"/"+str(ytile)+"/"+str(xtile)+".png"
		nombre_fichero=self.num2tile_name(xtile,ytile,zoom)
		print url
		while 1:
			try:		
				f=urllib.urlretrieve(url,nombre_fichero,reporthook=self.avance_descarga)[0]
				Im=Image.open(f)
				return Im
				break
			except IOError:
				print "Timeout: Pruebo otra vez"


if __name__ == "__main__":
#	mapa=cuadricula_slippy("OPENSTREETMAP")
	mapa=cuadricula_slippy("PNOA")
	z=14
	lat=40.3333333333
        lon=-3.52083333333
	c=100
	l=100
	print mapa.deg2tile_name(lat,lon,z)
	(xtile,ytile)=mapa.deg2num(lon,lat,z)
	mapa.get(xtile,ytile,z)
	

	for i in range(-c,c,1):
		for j in range(-l,l,1):
			mapa.get(xtile+i,ytile+j,z)

