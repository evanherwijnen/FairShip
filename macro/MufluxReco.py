#!/usr/bin/env python
inputFile = 'ship.conical.PGplus-TGeant4.root'
geoFile   = 'geofile_full.conical.PGplus-TGeant4.root'
debug = False

withNoStrawSmearing = None # True   for debugging purposes
nEvents    = 10000
firstEvent = 0
withHists = True
vertexing = True
dy  = None
saveDisk  = False # remove input file
pidProton = False # if true, take truth, if False fake with pion mass
realPR = ''
withT0 = False

import resource
def mem_monitor():
 # Getting virtual memory size 
    pid = os.getpid()
    with open(os.path.join("/proc", str(pid), "status")) as f:
        lines = f.readlines()
    _vmsize = [l for l in lines if l.startswith("VmSize")][0]
    vmsize = int(_vmsize.split()[1])
    #Getting physical memory size  
    pmsize = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print "memory: virtuell = %5.2F MB  physical = %5.2F MB"%(vmsize/1.0E3,pmsize/1.0E3)

import ROOT,os,sys,getopt
import __builtin__ as builtin
import rootUtils as ut
import shipunit as u
import shipRoot_conf

shipRoot_conf.configure()

try:
        opts, args = getopt.getopt(sys.argv[1:], "o:D:FHPu:n:f:g:c:hqv:sl:A:Y:i:",\
           ["ecalDebugDraw","inputFile=","geoFile=","nEvents=","noStrawSmearing","noVertexing","saveDisk","realPR","withT0"])
except getopt.GetoptError:
        # print help information and exit:
        print ' enter --inputFile=  --geoFile= --nEvents=  --firstEvent=,' 
        print ' noStrawSmearing: no smearing of distance to wire, default on' 
        print ' outputfile will have same name with _rec added'   
        sys.exit()
for o, a in opts:
        if o in ("noVertexing"):
            vertexing = False
        if o in ("noStrawSmearing"):
            withNoStrawSmearing = True
        if o in ("--withT0"):
            withT0 = True
        if o in ("-f", "--inputFile"):
            inputFile = a
        if o in ("-g", "--geoFile"):
            geoFile = a
        if o in ("-n", "--nEvents="):
            nEvents = int(a)
        if o in ("-Y"): 
            dy = float(a)
        if o in ("--ecalDebugDraw"):
            EcalDebugDraw = True
        if o in ("--saveDisk"):
            saveDisk = True
	if o in ("--realPR"):
            realPR = "_PR"


# need to figure out which geometry was used
if not dy:
  # try to extract from input file name
  tmp = inputFile.split('.')
  try:
    dy = float( tmp[1]+'.'+tmp[2] )
  except:
    dy = None
print 'configured to process ',nEvents,' events from ' ,inputFile, \
      ' starting with event ',firstEvent, ' with option Yheight = ',dy,' with vertexing',vertexing,' and real pattern reco',realPR=="_PR"
if not inputFile.find('_rec.root') < 0: 
  outFile   = inputFile
  inputFile = outFile.replace('_rec.root','.root') 
else:
  outFile = inputFile.replace('.root','_rec.root') 
# outfile should be in local directory
  tmp = outFile.split('/')
  outFile = tmp[len(tmp)-1]
  if saveDisk: os.system('mv '+inputFile+' '+outFile)
  else :       os.system('cp '+inputFile+' '+outFile)

if not geoFile:
 tmp = inputFile.replace('ship.','geofile_full.')
 geoFile = tmp.replace('_rec','')

fgeo = ROOT.TFile.Open(geoFile)
from ShipGeoConfig import ConfigRegistry
from rootpyPickler import Unpickler
#load Shipgeo dictionary
upkl    = Unpickler(fgeo)
ShipGeo = upkl.load('ShipGeo')
  
h={}
log={}
if withHists:
 ut.bookHist(h,'distu','distance to wire',100,0.,5.)
 ut.bookHist(h,'distv','distance to wire',100,0.,5.)
 ut.bookHist(h,'disty','distance to wire',100,0.,5.)
 ut.bookHist(h,'nmeas','nr measurements',100,0.,50.)
 ut.bookHist(h,'chi2','Chi2/DOF',100,0.,20.)
 ut.bookHist(h,'p-fittedtracks','p of fitted tracks',40,0.,400.)
 ut.bookHist(h,'1/p-fittedtracks','1/p of fitted tracks',120,-0.2,1.) 
 ut.bookHist(h,'ptruth','ptruth',40,0.,400.)
 ut.bookHist(h,'delPOverP','Pfitted/Ptrue-1 vs Ptrue',40,0.,400.,50,-2.0,2.0)
 ut.bookHist(h,'invdelPOverP','1/Pfitted-1/Ptrue)/(1/Ptrue) vs Ptrue',40,0.,400.,50,-2.0,2.0)
 ut.bookProf(h,'deltaPOverP','Pfitted/Ptrue-1 vs Ptrue',40,0.,400.,-10.,10.0)
 ut.bookHist(h,'Pfitted-Pgun','P-fitted vs P-gun',40,0.,400.,50,0.,500.0)
 ut.bookHist(h,'Px/Pzfitted','Px/Pz-fitted',100,-0.04,0.04)
 ut.bookHist(h,'Py/Pzfitted','Py/Pz-fitted',100,-0.04,0.04) 
 ut.bookHist(h,'Px/Pztrue','Px/Pz-true',100,-0.04,0.04)
 ut.bookHist(h,'Py/Pztrue','Py/Pz-true',100,-0.04,0.04) 
 ut.bookHist(h,'Px/Pzfitted-noT4','Px/Pz-fitted only T1,T2,T3 ',100,-0.04,0.04)
 ut.bookHist(h,'Py/Pzfitted-noT4','Py/Pz-fitted only T1,T2,T3',100,-0.04,0.04) 
 ut.bookHist(h,'Px/Pztrue-noT4','Px/Pz-true only T1,T2,T3',100,-0.04,0.04)
 ut.bookHist(h,'Py/Pztrue-noT4','Py/Pz-true only T1,T2,T3',100,-0.04,0.04) 
 ut.bookHist(h,'Px/Pzfitted-Px/Pztruth','Px/Pz-fitted - Px/Pz-true vs P-true',40,0.,400.,100,-0.002,0.002)
 ut.bookHist(h,'Py/Pzfitted-Py/Pztruth','Py/Pz-fitted - Py/Pz-true vs P-true',40,0.,400.,50,-0.02,0.02)
 ut.bookHist(h,'Px/Pzfitted-Px/Pztruth-noT4','Px/Pz-fitted - Px/Pz-true vs P-true (no stereo layers)',40,0.,400.,100,-0.002,0.002)
 ut.bookHist(h,'Py/Pzfitted-Py/Pztruth-noT4','Py/Pz-fitted - Py/Pz-true vs P-true (no stereo layers)',40,0.,400.,50,-0.02,0.02)

 ut.bookHist(h,'p-value','p-value of fit',100,0.,1.)
 ut.bookHist(h,'pt-kick','pt-kick',100,-2.,2.)
 ut.bookHist(h,'nmeas-noT4','nr measurements only T1,T2,T3',100,0.,50.)
 ut.bookHist(h,'chi2-noT4','Chi2/DOF only T1,T2,T3',100,0.,20.)
 ut.bookHist(h,'p-fittedtracks-noT4','p of fitted track only T1,T2,T3',40,0.,400.)
 ut.bookHist(h,'1/p-fittedtracks-noT4','1/p of fitted tracks only T1,T2,T3',120,-0.2,1.) 
 ut.bookHist(h,'ptruth-noT4','ptruth only T1,T2,T3',40,0.,400.)
 ut.bookHist(h,'delPOverP-noT4','Pfitted/Ptrue-1 vs Ptrue only T1,T2,T3',40,0.,400.,50,-2.0,2.0)
 ut.bookHist(h,'invdelPOverP-noT4','1/Pfitted-1/Ptrue)/(1/Ptrue) vs Ptrue only T1,T2,T3',40,0.,400.,50,-2.0,2.0)
 ut.bookProf(h,'deltaPOverP-noT4','Pfitted/Ptrue-1 vs Ptrue only T1,T2,T3',40,0.,400.,-10.,10.0)
 ut.bookHist(h,'Pfitted-Pgun-noT4','P-fitted vs P-gun only T1,T2,T3',40,0.,400.,50,0.,500.0)
 ut.bookHist(h,'p-value-noT4','p-value of fit only T1,T2,T3',100,0.,1.)
 ut.bookHist(h,'hits-T1','x vs y hits in T1',50,-25.,25.,100,-50.,50) 
 ut.bookHist(h,'hits-T2','x vs y hits in T2',50,-25.,25.,100,-50.,50) 
 ut.bookHist(h,'hits-T1x','x vs y hits in T1 x plane',50,-25.,25.,100,-50.,50) 
 ut.bookHist(h,'hits-T1u','x vs y hits in T1 u plane',50,-25.,25.,100,-50.,50)  
 ut.bookHist(h,'hits-T2x','x vs y hits in T2 x plane',50,-25.,25.,100,-50.,50) 
 ut.bookHist(h,'hits-T2v','x vs y hits in T2 v plane',50,-25.,25.,100,-50.,50) 
 ut.bookHist(h,'hits-T3','x vs y hits in T3',200,-100.,100.,160,-80.,80) 
 ut.bookHist(h,'hits-T4','x vs y hits in T4',200,-100.,100.,160,-80.,80)   
 
# -----Create geometry----------------------------------------------

import charmDet_conf
run = ROOT.FairRunSim()
run.SetName("TGeant4")  # Transport engine
run.SetOutputFile("dummy")  # Output file
run.SetUserConfig("g4Config_basic.C") # geant4 transport not used, only needed for creating VMC field
rtdb = run.GetRuntimeDb()
modules = charmDet_conf.configure(run,ShipGeo)
# -----Create geometry----------------------------------------------
run.Init()

#import geomGeant4
#fieldMaker = geomGeant4.addVMCFields('field/GoliathBFieldSetup.txt', False)
#print "!!!!!!!!!!!! printing fields"
#geomGeant4.printVMCFields()



# make global variables
builtin.debug    = debug
builtin.withT0 = withT0
builtin.realPR = realPR

builtin.ShipGeo = ShipGeo
builtin.modules = modules

builtin.withNoStrawSmearing = withNoStrawSmearing
builtin.h    = h
builtin.log  = log
iEvent = 0
builtin.iEvent  = iEvent

# import reco tasks
import MufluxDigiReco
SHiP = MufluxDigiReco.MufluxDigiReco(outFile,fgeo)

nEvents   = min(SHiP.sTree.GetEntries(),nEvents)
# main loop
for iEvent in range(firstEvent, nEvents):
 if iEvent%1000 == 0 or debug: print 'event ',iEvent
 #print 'event =',iEvent
 rc    = SHiP.sTree.GetEvent(iEvent) 
 SHiP.digitize() 
 #print "!!!!!!!!!!!! printing fields"
 SHiP.reconstruct()
 # memory monitoring
 # mem_monitor() 
 
# end loop over events
SHiP.finish()
