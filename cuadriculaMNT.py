#!/usr/bin/python
#-*- coding: latin-1 -*-

#import psycopg2 #Para DB en mysql

from pysqlite2 import dbapi2 as sqlite
import sys, os,  pyproj
import pyexiv2
import re



class coord:
     x=float()
     y=float()

     def __init__(self,xx,yy):
	self.x=xx
	self.y=yy
	
     def grados(self,x):
	g=int(x)
	s=(x-g)*3600
	m=int(s/60)
	s=s-m*60
	t=str(g)+"º"+str(abs(m))+"'"+str(abs(s))+"''"
	return t


     def grad(self):
	print "G:"+self.grados(self.x), self.grados(self.y)

     def grados_uiview(self,lat_lon):
        if lat_lon=='lon':
		x=self.x
	        if (x/abs(x)==1):
			flag='E'
		else:
			flag='W' 
                fmtStr="%03u.%02u.%02u%s"
        else:
		x=self.y
	        if (x/abs(x)==1):
			flag='N'
		else:
			flag='S' 
                fmtStr="%02u.%02u.%02u%s"
	g=int(x)
	s=(x-g)*3600
	m=int(s/60)
	s=int((s-m*60)*100)/100
	t=fmtStr % (abs(g),abs(m),abs(s),flag)
        return t 

     def grados_sondemonitor(self,lat_lon):
        if lat_lon=='lon':
		x=self.x
	        if (x/abs(x)==1):
			flag='E'
		else:
			flag='W' 
                fmtStr="%03u,%07.4f,%s"
        else:
		x=self.y
	        if (x/abs(x)==1):
			flag='N'
		else:
			flag='S' 
                fmtStr="%02u,%07.4f,%s"
	g=int(x)
	s=(x-g)*3600
	m=s/60
	t=fmtStr % (abs(g),abs(m),flag)
        return t 



#Conecta con la BD para conseguir los nombres de las cuadriculas
class ign_db:
     conn=None
     mark=None
     nombre=None
     hoja=int
     
     def __init__(self):
	#self.conn=psycopg2.connect('dbname=ign','user=nacho') #para DB en mysql
	self.conn=sqlite.connect('ign.sqlite3')
	self.mark = self.conn.cursor()

     def MTN25(self,cc,ff):
	SQLString="SELECT trim(Nombre_de_la_hoja),mapa,N___de_cuarto,trim(nombre_del_mapa),ign,sge FROM MTN25,MTN50 WHERE mapa=ign AND sge='"+str(cc/2)+"-"+str(ff/2)+"'"
	self.mark.execute(SQLString)
	record=self.mark.fetchall()
	for i in record:
		print "nombre:",i[0]
		print "cuadricula:",int(i[1])
		self.hoja=int(i[1])
		self.nombre="MTN25_HOJA_"+str(int(i[1]))+str(i[2])+"["+str(cc)+"-"+str(ff)+"]("+str(i[0])+")"

     def MTN25_nombre(self,sitio):
	print "Buscando:"+sitio
	SQLString="SELECT trim(Nombre_de_la_hoja),mapa,N___de_cuarto,trim(nombre_del_mapa),ign,sge FROM MTN25,MTN50 WHERE mapa=ign AND Nombre_de_la_hoja like '%"+sitio+"%'"
	self.mark.execute(SQLString)
	record1=self.mark.fetchall()
	for i in record1:
		print ""
		print "nombre hoja MTN50:",i[3]
		print "cuadricula SGE:",i[5]
		print "nombre hoja MTN25:",i[0]
		print "Hoja:",i[1],i[2]


     
     def MTN50(self,cc,ff):
	SQLString="SELECT trim(nombre_del_mapa),ign FROM MTN50 WHERE sge='"+str(cc)+"-"+str(ff)+"'"
	self.mark.execute(SQLString)
	record=self.mark.fetchall()
	for i in record:
		nombre=i[0].encode('utf-8')
		print "nombre:",nombre
		print "Hoja:",int(i[1])
		self.hoja=int(i[1])
		self.nombre="MTN50_HOJA_"+str(int(i[1]))+"["+str(cc)+"-"+str(ff)+"]("+str(nombre).replace(" ","_")+")"
		#self.nombre="MTN50_"+str(nombre)


     def MTN50_N(self,numero):
	self.hoja=numero
	SQLString="SELECT trim(nombre_del_mapa),ign,sge FROM MTN50 WHERE IGN='"+str(numero)+"'"
	self.mark.execute(SQLString)
	record=self.mark.fetchall()
	for i in record:
		nombre=i[0].encode('utf-8')
		print "nombre:",nombre
		print "cuadricula:",int(i[1])
		(kk1,kk2,kk3)=i[2].partition('-')
		ff=int(kk1)
		cc=int(kk3)
		self.nombre="MTN50 HOJA_"+str(int(i[1]))+"["+str(cc)+"-"+str(ff)+"]("+str(nombre).replace(" ","_")+")"
		#self.nombre="MTN50_"+str(nombre)
	return (cc,ff)


     def nomgeo(self,sitio):
	SQLString="SELECT nombre,entidad,hoja25,prov FROM nomgeo WHERE nombre like '%"+sitio+"%'"
	self.mark.execute(SQLString)
	record=self.mark.fetchall()
	for i in record:
		print "nombre:",i[0]
		print "entidad:",i[1]
		print "hoja25:",i[2]
		print "provincia:",i[3]

     def MTN50_nombre(self,sitio):
	print "Buscando:"+sitio
	SQLString="SELECT trim(nombre_del_mapa),ign,sge FROM MTN50 WHERE nombre_del_mapa like '%"+sitio+"%'"
	self.mark.execute(SQLString)
	record=self.mark.fetchall()
	for i in record:
		print "nombre:",i[0]
		print "cuadricula:",int(i[1])
		print "cuadricula SGE:",i[2]




	
class cuadricula_MNT():
     lat_org=float()
     lon_org=float()
     delta_lat_MNT50=float()
     delta_lon_MNT50=float()
     nombre=None
     ign=ign_db()
     escala=int
     fila=int
     columna=int

     def __init__(self):
	#Coordenadas Origen MNT en ETRS89
	self.lat_org=44.0
        self.lon_org=-9.0-(51.0*60.0+15.0)/3600.0
        self.delta_lat_MNT50=10.0/60.0
        self.delta_lon_MNT50=20.0/60.0
	

     def rejilla_MNT(self,escala):
 	print "HOLA"

     
	
     def coord_MNT(self,escala,cc,ff):
	self.escala=escala
	
	self.nombre="MNT"+str(escala)+"["+str(cc)+"-"+str(ff)+"]"
	se=coord(0,0)
	no=coord(0,0)
        self.fila=ff
	self.columna=cc 
	if escala==50:
		factor=1.0
		self.ign.MTN50(cc,ff)
		self.nombre=self.ign.nombre

	elif escala==25:
		factor=2.0
		self.ign.MTN25(cc,ff)
		self.nombre=self.ign.nombre

	elif escala==10:
		factor=4.0
	elif escala==5:
		factor=8.0
	elif escala==100:
		factor=.5
	elif escala==200:
		factor=.25
	else:
		print 'escala no definida (5,10,25,50,100,200), valor=',escala
		exit()

	nx=3.0*factor
	ny=nx*2.0

	se.x=self.lon_org+float(cc)/nx
	se.y=self.lat_org-float(ff)/ny

	no.x=se.x-self.delta_lon_MNT50/factor
	no.y=se.y+self.delta_lat_MNT50/factor

	if 1==0:
		print 'Cuadricula MNT'+str(escala)+'_'+str(cc)+str(ff)
		print 'origen MNT:',self.lon_org,self.lat_org
		print 'delta'+str(escala)+':',self.delta_lon_MNT50,self.delta_lat_MNT50
		print 'factores,columna,fila:',factor,cc,ff,ny,nx
		print 'nombre',self.nombre
		print 'SE(ETRS89):',se.x,se.y,se.grad()
		print 'NO(ETRS89):',no.x,no.y,no.grad()

	return (se,no)

     def cuadricula(self,escala,cc0):
	if escala==50:
		factor=1.0
	elif escala==25:
		factor=2.0
	elif escala==10:
		factor=4.0
	elif escala==5:
		factor=8.0
	elif escala==100:
		factor=.5
	elif escala==200:
		factor=.25
	else:
		print 'escala no definida (5,10,25,50,100,200), valor=',escala
		exit()

	nx=3.0*factor
	ny=nx*2.0
        cc=int((cc0.x-self.lon_org)*nx)+1
        ff=int((self.lat_org-cc0.y)*ny)+1
        print cc0.x,self.lon_org,self.lat_org,cc0.y
        print nx,ny,cc0.x-self.lon_org,self.lat_org-cc0.y
        print 'escala,fila.columna:',escala,cc,ff
	self.coord_MNT(escala,cc,ff)
	return (cc,ff)

class calibrador:
     nombre=None	
     xsize,ysize = (None,None)
     se=coord(0,0)
     no=coord(0,0)		

     def __init__(self,nombre,(xsize,ysize),(se,no)):
	self.nombre=nombre
	self.xsize=xsize
	self.ysize=ysize
	self.se=se
	self.no=no
	
     def write_imp(self):
	c0=coord(0,0)
	c1=coord(0,0)		

       	prj_grs80=pyproj.Proj("+proj=latlon +ellps=GRS80 +towgs84=0,0,0")
       	prj_utm=pyproj.Proj("+proj=utm  +ellps=intl  +nadgrids=./R2008peninsula.gsb") #NO vale para canarias!!!

#       	prj_grs80=pyproj.Proj("+proj=latlong +ellps=GRS80")
#       	prj_utm=pyproj.Proj("+proj=utm +ellps=intl +zone=30")
#       	prj_utm=pyproj.Proj("+proj=utm +ellps=intl +zone=30 +towgs84=-131.0320,-100.2510,-163.3540,-1.2438,-0.0195,-1.1436,9.3900")
       	c0.x,c0.y = pyproj.transform(prj_grs80,prj_utm,self.se.x,self.se.y)
       	c1.x,c1.y = pyproj.transform(prj_grs80,prj_utm,self.no.x,self.no.y)

	if 1==1:
       		print 'imp(GSR80) SE:',self.se.x,self.se.y
       		print 'imp(GSR80) NO:',self.no.x,self.no.y
		print 'imp(utm) SE:',c0.x,c0.y
		print 'imp(utm) NO:',c1.x,c1.y

       	dummy='CompeGPS MAP File\n'
       	dummy=dummy+'<Header>\nVersion=2\nVerCompeGPS=6.0\nProjection=0,UTM,30,N,\nCoordinates=0\n' 
       	dummy=dummy+'Datum=European 1950 (Spain and Portugal)\n</Header>\n'
       	dummy=dummy+'<Map>\nBitmap='+self.nombre+'.jpg\nBitsPerPixel=0\nBitmapWidth='+str(self.xsize)+'\nBitmapHeight='+str(self.ysize)+'\n</Map>\n'
       	dummy=dummy+'<Calibration>\n'
       	dummy=dummy+'P0=0.00000000,0.00000000,30T,'+str(c1.x)+','+str(c1.y)+'\n'
       	dummy=dummy+'P1='+str(self.xsize)+',0.00000000,30T,'+str(c0.x)+','+str(c1.y)+'\n'
       	dummy=dummy+'P1='+str(self.xsize)+','+str(self.ysize)+',30T,'+str(c0.x)+','+str(c0.y)+'\n'
       	dummy=dummy+'P1=0.00000000,'+str(self.ysize)+',30T,'+str(c1.x)+','+str(c0.y)+'\n'
       	dummy=dummy+'</Calibration>\n'
       	f=open(self.nombre+".imp",'w')
       	f.write(dummy)
       	f.close()

     def write_kml(self):
       	dummy= '<?xml version="1.0" encoding="UTF-8"?>'
	dummy=dummy+'<kml xmlns="http://earth.google.com/kml/2.2">'
	dummy=dummy+'<Folder>'
	dummy=dummy+'<name>Mapas 1:50000</name>'
	dummy=dummy+'<description>Mapas de OpenStreet o PNOA. Calibrado segun ellips=GRS80 casi igual al WGR84</description>'
	dummy=dummy+'<GroundOverlay>'
	dummy=dummy+'<name>'+self.nombre+'</name>'
	dummy=dummy+'<description>Superposición sobre el relieve</description>'
	dummy=dummy+'<Icon>'
	dummy=dummy+'<href>'+self.nombre+'.jpg</href>'
	dummy=dummy+'</Icon>'
	dummy=dummy+'<LatLonBox>'
	dummy=dummy+'<north>'+str(self.no.y)+'</north>'
	dummy=dummy+'<south>'+str(self.se.y)+'</south>'
	dummy=dummy+'<east>'+str(self.se.x)+'</east>'
	dummy=dummy+'<west>'+str(self.no.x)+'</west>'
	dummy=dummy+'<rotation>-0.</rotation>'
	dummy=dummy+'</LatLonBox>'
	dummy=dummy+'</GroundOverlay>'
	dummy=dummy+'</Folder>'
	dummy=dummy+'</kml>'
       	f=open(self.nombre+".kml",'w')
       	f.write(dummy)
       	f.close()

     def write_txt(self):
	dummy=''+str(self.se.y)+'\n'#'</south>'
	dummy=dummy+''+str(self.no.x)+'\n'#'</west>'
	dummy=dummy+''+str(self.no.y)+'\n'#'</north>'
	dummy=dummy+''+str(self.se.x)+'\n'#'</east>'
       	f=open(self.nombre+".txt",'w')
       	f.write(dummy)
       	f.close()

     def write_uiview(self):             
	dummy=self.no.grados_uiview('lat')+', '+self.no.grados_uiview('lon')+'\r\n'
	dummy=dummy+self.se.grados_uiview('lat')+', '+self.se.grados_uiview('lon')+'\r\n'
	dummy=dummy+self.nombre
        print dummy
       	f=open(self.nombre+".INF",'w')
       	f.write(dummy)
       	f.close()

     def write_xastir(self):
	dummy='FILENAME '+self.nombre+'.jpg\n'
	dummy=dummy+'#          x          y        lon         lat\n'
	dummy=dummy+'TIEPOINT   1          1    '+str(self.no.x)+'  '+str(self.no.y)+'\n'
	dummy=dummy+'TIEPOINT  '+ str(self.xsize)+'    '+str(self.ysize)+' '+str(self.se.x)+'  '+str(self.se.y)+'\n'
	dummy=dummy+'IMAGESIZE '+str(self.xsize)+'    '+str(self.ysize)
        print dummy
       	f=open(self.nombre+".geo",'w')
       	f.write(dummy)
       	f.close()

     def write_sondemonitor(self):             
	dummy='Point00,xy,0,0,in,deg,'+self.no.grados_sondemonitor('lat')+', '+self.no.grados_sondemonitor('lon')+'\r\n'
	dummy=dummy+'Point01,xy,'+str(self.xsize)+','+str(self.ysize)+',in,deg,'+self.se.grados_sondemonitor('lat')+', '+self.se.grados_sondemonitor('lon')+'\r\n'
	dummy=dummy+'Point02,xy,0,'+str(self.ysize)+',in,deg,'+self.se.grados_sondemonitor('lat')+', '+self.no.grados_sondemonitor('lon')+'\r\n'
	dummy=dummy+'Point03,xy,'+str(self.xsize)+',0,in,deg,'+self.no.grados_sondemonitor('lat')+', '+self.se.grados_sondemonitor('lon')+'\r\n'
        print dummy
       	f=open(self.nombre+".clb",'w')
       	f.write(dummy)
       	f.close()
		
     def write_in_jpeg(self,im):
	import datetime

	image = pyexiv2.Image(im)
    	image.readMetadata()

	image['Exif.Image.ImageDescription'] = self.nombre
	newDateTime = datetime.datetime.today()
	image['Exif.Image.DateTime'] = newDateTime
	image['Exif.GPSInfo.GPSLongitude']=str(self.se.x)
	image.writeMetadata()
 	print image.exifKeys()
	for tag in image.exifKeys():
		print image[tag]

if __name__ == "__main__":
	ign=ign_db()
	ign.MTN50_nombre(sys.argv[1])
#	cuadricula=cuadricula_MNT()
#	se,no = cuadricula.coord_MNT(50,20,19) #Ponton
#	se,no = cuadricula.coord_MNT(50,17,22) #cercedilla
#	se,no = cuadricula.coord_MNT(50,19,22) #madrid
#	calibr=calibrador(cuadricula.nombre,(5570,3740),(se,no))
#	calibr.write_imp()
#	calibr.write_kml()
#	calibr.write_txt()
#	calibr.write_in_jpeg("MTN50 HOJA_432[20-17](Riaza).osm.jpg")
