#!/usr/bin/env python
import ROOT
import glob
import math
from python import SelectorTools
from python import UserInput
from python import OutputTools
from python import ConfigureJobs
from python import HistTools
import makeSimpleHtml
import os
import subprocess
import sys
import datetime
import array
from ROOT import vector as Vec
VFloat = Vec('float')
from PlotTools import PlotStyle as Style, pdfViaTex
style = Style()
ROOT.gStyle.SetLineScalePS(1.8)

channels = ["eeee","eemm","mmmm"]
#channels = ["eeee"]
def getComLineArgs():
    parser = UserInput.getDefaultParser()
    parser.add_argument("--lumi", "-l", type=float,
        default=41.5, help="luminosity value (in fb-1)")
    parser.add_argument("--output_file", "-o", type=str,
        default="", help="Output file name")
    parser.add_argument("--test", action='store_true',
        help="Run test job (no background estimate)")
    parser.add_argument("--uwvv", action='store_true',
        help="Use UWVV format ntuples in stead of NanoAOD")
    parser.add_argument("--with_background", action='store_true',
        help="Don't run background selector")
    parser.add_argument("--noHistConfig", action='store_true',
        help="Don't rely on config file to specify hist info")
    parser.add_argument("-j", "--numCores", type=int, default=1,
        help="Number of cores to use (parallelize by dataset)")
    parser.add_argument("--input_tier", type=str,
        default="", help="Selection stage of input files")
    parser.add_argument("--year", type=str,
        default="default", help="Year of Analysis")
    parser.add_argument("-c", "--channels", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["eee","eem","emm","mmm"], help="List of channels"
                        "separated by commas. NOTE: set to Inclusive for NanoAOD")
    parser.add_argument("--scalefactors_file", "-sf", type=str,
        default="", help="ScaleFactors file name")
    parser.add_argument("--leptonSelections", "-ls", type=str,
        default="TightLeptons", help="Either All Loose or Tight")
    parser.add_argument("--output_selection", type=str,
        default="", help="Selection stage of output file "
        "(Same as input if not give)")
    parser.add_argument("-b", "--hist_names", 
                        type=lambda x : [i.strip() for i in x.split(',')],
                        default=["all"], help="List of histograms, "
                        "as defined in ZZ4lRun2DatasetManager, separated "
                        "by commas")
    parser.add_argument("--variable", "-vr", type=str,
        default="all", help="variableName")
    parser.add_argument('--noNorm', action='store_true',
                        help='Leave differential cross sections in abolute normalization rather than normalizing to unity area.')
    parser.add_argument('--plotResponse', action='store_true',
                        help='plot Response Matrices and covariance matrices.')
    parser.add_argument('--plotSystResponse', action='store_true',
                        help='plotResponse Matrices varied up or down with systematics.')
    parser.add_argument('--makeTotals', action='store_true',
                        help='plot total unfolded with uncertainities.')
    parser.add_argument('--noSyst', action='store_true',
                        help='No Systematics calculations.')
    parser.add_argument('--plotDir', type=str, nargs='?',
                        default='/afs/cern.ch/user/u/uhussain/www/ZZFullRun2/PlottingResults/ZZ4l2018/ZZSelectionsTightLeps/ANPlots/ZZ4l2018/RespMat_Moriond2019IDMuSF',
                        help='Directory to put response and covariance plots in')
    parser.add_argument('--unfoldDir', type=str, nargs='?',
                        default='/afs/cern.ch/user/u/uhussain/ZZFullRun2Unfolding',
                        help='Directory to put unfolded histo files in')
    parser.add_argument('--nIter', type=int, nargs='?', default=4,
                        help='Number of iterations for D\'Agostini method')
    return vars(parser.parse_args())

args = getComLineArgs()
manager_path = ConfigureJobs.getManagerPath()
selection = args['selection']
if selection == "":
    selection = "LooseLeptons"
    print "Info: Using BasicZZSelections for hist defintions"
#analysis = "/".join([args['analysis'], selection])
analysis=args['analysis']
_binning = {
    'pt' : [25.*i for i in range(4)] + [100., 150., 200., 300.],
    #'mass' : [100.+100.*i for i in range(12)],
    'mass' : [100.] + [200.+50.*i for i in range(5)] + [500.,600.,800.],
    'massFull' : [80.,100.,120.,130.,150.,180.,200.,240.,300.,400.,1000],
    'eta' : [6,0.,6.],
    'zmass' : [60., 80., 84., 86.] + [87.+i for i in range(10)] + [98., 102., 120.], #[12, 60., 120.],
    'z1mass' : [60., 80., 84., 86.] + [87.+i for i in range(10)] + [98., 102., 120.], #[12, 60., 120.],
    'z2mass' : [60., 75., 83.] + [84.+i for i in range(14)] + [105., 120.],#[12, 60., 120.],
    'z1pt' : [i * 25. for i in range(7)] + [200., 300.],
    'z2pt' : [i * 25. for i in range(7)] + [200., 300.],
    'zpt' : [i * 25. for i in range(7)] + [200., 300.],
    'zHigherPt' : [i * 25. for i in range(7)] + [200., 300.],
    'zLowerPt' : [i * 25. for i in range(7)] + [200., 300.],
    'leppt' : [i * 15. for i in range(11)],
    'l1Pt' : [0.,15.,30.,40.,50.]+[60.+15.*i for i in range(9)]+[195.,225.],#[14,0.,210.],#[15, 0., 150.],
    'dphiz1z2': [0.,1.5,2.0,2.25,2.5,2.75,3.0,3.25],
    'drz1z2': [0.,1.0,2.0,3.0,4.0,5.0,6.0]
    }
units = {
    'pt' : '[GeV]',
    'mass' : '[GeV]',
    'massFull' : '[GeV]',
    'eta' : '',
    'zmass' : '[GeV]',
    'z1mass' : '[GeV]',
    'z2mass' : '[GeV]',
    'zpt' : '[GeV]',
    'z1pt' : '[GeV]',
    'z2pt' : '[GeV]',
    'zHigherPt' : '[GeV]',
    'zLowerPt' : '[GeV]',
    'leppt' : '[GeV]',
    'l1Pt' : '[GeV]',
    'dphiz1z2': '',
    'drz1z2':'',
    }
prettyVars = {
    'pt' : 'p_{T}^{4\\ell}',
    'mass' : 'm_{4\\ell}',
    'massFull' : 'm_{4\\ell}',
    'eta' : '\\eta_{4\\ell}',
    'zmass' : 'm_{Z}',
    'z1mass' : 'm_{Z_{1}}',
    'z2mass' : 'm_{Z_{2}}',
    'z1pt' : 'p_{T}^{Z_{1}}',
    'z2pt' : 'p_{T}^{Z_{2}}',
    'zpt' : 'p_{T}^{Z}',
    'zHigherPt' : 'p_\\text{T}^{\\text{Z}_{\\text{lead}}}',
    'zLowerPt' : 'p_\\text{T}^{\\text{Z}_{\\text{sublead}}}',
    'leppt' : 'p_{T}^{\\ell}',
    'l1Pt' : 'p_\\text{T}^{\\ell_1}', 
    'dphiz1z2': '\\Delta\\phi_{Z_{1},Z_{2}}',
    'drz1z2':'\\Delta\\text{R}_{Z_{1},Z_{2}}}',
    }
# Names of compiled C++ classes to make response matrices fast
# (this is extremely slow in Python because it requires a combination of
# information from multiple trees, which can't be done with TTree::Draw())
responseClassNames = {
    'mass' : {c:'FloatBranchResponseMatrixMaker' for c in channels},
    #'massFull' : {c:'FullSpectrumFloatResponseMatrixMaker' for c in channels},
    'pt' : {c:'FloatBranchResponseMatrixMaker' for c in channels},
    'eta' : {c:'AbsFloatBranchResponseMatrixMaker' for c in channels},
    'z1mass' : {'eeee':'FloatBranchResponseMatrixMaker',
                'mmmm':'FloatBranchResponseMatrixMaker',
                'eemm':'Z1ByMassResponseMatrixMaker',},
    'z2mass' : {'eeee':'FloatBranchResponseMatrixMaker',
                'mmmm':'FloatBranchResponseMatrixMaker',
                'eemm':'Z2ByMassResponseMatrixMaker',},
    'z1pt' : {'eeee':'FloatBranchResponseMatrixMaker',
              'mmmm':'FloatBranchResponseMatrixMaker',
              'eemm':'Z1ByMassResponseMatrixMaker',},
    'z2pt' : {'eeee':'FloatBranchResponseMatrixMaker',
              'mmmm':'FloatBranchResponseMatrixMaker',
              'eemm':'Z2ByMassResponseMatrixMaker',},
    #'zHigherPt' : {c:'Z1ByPtResponseMatrixMaker' for c in channels},
    #'zLowerPt' : {c:'Z2ByPtResponseMatrixMaker' for c in channels},
    'leppt' : {c:'AllLeptonBranchResponseMatrixMaker' for c in channels},
    #'l1Pt' : {c:'LeptonMaxBranchResponseMatrixMaker' for c in channels},
    'zpt' : {c:'BothZsBranchResponseMatrixMaker' for c in channels},
    'zmass' : {c:'BothZsBranchResponseMatrixMaker' for c in channels},
    'dphiz1z2':{c:'ZZAbsDeltaPhiResponseMatrixMaker' for c in channels},
    'drz1z2':{c:'ZZDeltaRResponseMatrixMaker' for c in channels},
    }

# Variable names usable by response maker classes
varNamesForResponseMaker = {
    'mass' : {c:'Mass' for c in channels},
    #'massFull' : {c:'Mass' for c in channels},
    'pt' : {c:'Pt' for c in channels},
    'eta' : {c:'Eta' for c in channels},
    'z1mass' : {'eeee':'e1_e2_Mass','mmmm':'m1_m2_Mass','eemm':'Mass'}, # 4e/4mu just use 1 variable because that's easy
    'z2mass' : {'eeee':'e3_e4_Mass','mmmm':'m3_m4_Mass','eemm':'Mass'}, # for 2e2mu, the response maker class will figure it out
    'z1pt' : {'eeee':'e1_e2_Pt','mmmm':'m1_m2_Pt','eemm':'Pt'}, # 4e/4mu just use 1 variable because that's easy
    'z2pt' : {'eeee':'e3_e4_Pt','mmmm':'m3_m4_Pt','eemm':'Pt'}, # for 2e2mu, the response maker class will figure it out
    'zpt' : {c:'Pt' for c in channels},
    'zmass' : {c:'Mass' for c in channels},
    #'zHigherPt' : {c:'Pt' for c in channels},
    #'zLowerPt' : {c:'Pt' for c in channels},
    'leppt' : {c:'Pt' for c in channels},
    #'l1Pt' : {c:'Pt' for c in channels},
    #'zPt' : {c:'Pt' for c in channels},
    'dphiz1z2': {c:'' for c in channels}, #variable names already set in ResponseMatrix.cxx
    'drz1z2': {c:'' for c in channels},
}

def getLumiTextBox():
    texS = ROOT.TLatex(0.76,0.955, str(args['lumi'])+" fb^{-1} (13 TeV)")
    texS.SetNDC()
    texS.SetTextFont(42)
    texS.SetTextSize(0.030)
    texS.Draw()
    texS1 = ROOT.TLatex(0.11,0.955,"#bf{CMS} #it{Preliminary}")
    texS1.SetNDC()
    texS1.SetTextFont(42)
    texS1.SetTextSize(0.030)
    texS1.Draw()
    return texS,texS1

# list of variables not counting systematic shifts
varList=['Mass','ZZPt','ZPt','LepPt','dPhiZ1Z2','dRZ1Z2']

def generateAnalysisInputs():    
    #dictionary of SF histograms
    hSF = {}
    eLowRecoFile = ROOT.TFile.Open('data/Ele_Reco_LowEt_2018.root')
    hSF['eLowReco'] = eLowRecoFile.Get('EGamma_SF2D').Clone()
    hSF['eLowReco'].SetDirectory(0)
    eLowRecoFile.Close()
    
    eRecoFile = ROOT.TFile.Open('data/Ele_Reco_2018.root')
    hSF['eReco'] = eRecoFile.Get('EGamma_SF2D').Clone()
    hSF['eReco'].SetDirectory(0)
    eRecoFile.Close()
    
    eIdFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2018_NoGap.root')
    hSF['eSel'] = eIdFile.Get('EGamma_SF2D').Clone() 
    hSF['eSel'].SetDirectory(0)
    eIdFile.Close()

    eIdGapFile = ROOT.TFile.Open('data/ElectronSF_Legacy_2018_Gap.root')
    hSF['eSelGap'] = eIdGapFile.Get('EGamma_SF2D').Clone() 
    hSF['eSelGap'].SetDirectory(0)
    eIdGapFile.Close()

    mIdFile = ROOT.TFile.Open('data/final_HZZ_muon_SF_2018_IsBDT_0610.root')
    hSF['m'] = mIdFile.Get('FINAL').Clone()
    hSF['m'].SetDirectory(0)

    hSF['mErr'] = mIdFile.Get('ERROR').Clone()
    hSF['mErr'].SetDirectory(0)
    mIdFile.Close()

    #dictionary of PU weights
    hPU={}
    pileupFile = ROOT.TFile.Open('data/PileupWeights2018/PU_Central.root')
    hPU[''] = pileupFile.Get('pileup')
    hPU[''].SetDirectory(0)
    pileupFile.Close()
    
    pileupFileUp = ROOT.TFile.Open('data/PileupWeights2018/PU_minBiasUP.root')
    hPU['Up'] = pileupFileUp.Get('pileup')
    hPU['Up'].SetDirectory(0)
    pileupFileUp.Close()

    pileupFileDown = ROOT.TFile.Open('data/PileupWeights2018/PU_minBiasDOWN.root')
    hPU['Down'] = pileupFileDown.Get('pileup')
    hPU['Down'].SetDirectory(0)
    pileupFileDown.Close()

    return hSF,hPU
#ROOT.gSystem.Load('Utilities/scripts/ResponseMatrixMaker_cxx')
#sigSamples is a dictionary containing sample names and kfactor*cross-section
#sumW is a dictionary with sigsample:sumweights stored
ROOT.gSystem.Load('Utilities/scripts/ResponseMatrixMaker_cxx')
def generateResponseClass(varName, channel,sigSamples,sigSamplesPath,sumW,hPUWt,hSF={}):
    
    className = responseClassNames[varName][channel]

    for h in hSF.values()+hPUWt.values():
        ROOT.SetOwnership(h,False)

    if hSF:
        className = 'SFHist'+className

    #if not hasattr(ROOT,className):
    #        ROOT.gSystem.Load('Utilities/scripts/ResponseMatrixMaker_cxx','kTRUE')
    
    #for example C=<class 'ROOT.BranchValueResponseMatrixMaker<float>'>     
    C = getattr(ROOT, className)
    print("className:",C)
    
    #filelist=["zz4l-powheg"]
    filelist=[str(i) for i in sigSamples.keys()] 
    #improve this by getting this info from ZZDatasetManager just like its done in makeCompositeHists
    #sigConstWeights = {sample : (1.256*35900*1.0835)/sumW
    #                   for sample in ConfigureJobs.getListOfFiles(filelist, selection)}
   
    sigConstWeights = {sample : (sigSamples[sample.split("__")[0]]*1000*args['lumi'])/sumW[sample]
                       for sample in [str(i) for i in sigSamples.keys()] }
    #print "sigConstWeights: ",sigConstWeights
    #print("_binning: ",_binning)
    binning = _binning[varName]
    vBinning = VFloat()
    ROOT.SetOwnership(vBinning,False)
    #print("vBinning: ",vBinning)
    #print("Content of the ROOT vector object: {}".format([x for x in vBinning]))
    #print("binning: ",binning)
    if len(binning) == 3:
        binningTemp = [binning[1] + i * (binning[2] - binning[1])/float(binning[0]) for i in xrange(binning[0]+1)]
        #print("binningTemp: ",binningTemp)
        for b in binningTemp:
            #print("b: ",b)
            vBinning.push_back(b)
    else:
        for b in binning:
            vBinning.push_back(b)

    print("Content of the ROOT vector object: {}".format([x for x in vBinning]))
    #print("vBinning: ",vBinning)
    responseMakers = {}
    #for sample, file_path in sigFileNames.items():
    #for sample in ConfigureJobs.getListOfFiles(filelist,selection):
    for sample in sigSamplesPath.keys():
        if sample=="zz4l-amcatnlo":
            continue
        #print "sample:", sample #expect zz4l-powheg
        #file_path = ConfigureJobs.getInputFilesPath(sample,selection,analysis)
        file_path=sigSamplesPath[sample]
        #print("where are the histos leaking")
        resp = C(channel, varNamesForResponseMaker[varName][channel], vBinning)
        #ROOT.SetOwnership(resp,False)
        file_path=file_path.encode("utf-8")
        #print "file_path: ",file_path
        fileList=glob.glob(file_path)
        #print "type in fileList should be str: ",type(fileList[0])
        for fName in fileList:
            resp.registerFile(fName)
        resp.registerPUWeights(hPUWt[''])
        resp.registerPUWeights(hPUWt['Up'], 'Up')
        resp.registerPUWeights(hPUWt['Down'], 'Down')
        resp.setConstantScale(sigConstWeights[sample])
        if hSF:
            resp.registerElectronSelectionSFHist(hSF['eSel'])
            resp.registerElectronSelectionGapSFHist(hSF['eSelGap'])
            resp.registerElectronLowRecoSFHist(hSF['eLowReco'])
            resp.registerElectronRecoSFHist(hSF['eReco'])
            resp.registerMuonSFHist(hSF['m'])
            resp.registerMuonSFErrorHist(hSF['mErr'])
            #print("scale factors are being added")

        responseMakers[sample] = resp

    altResponseMakers = {}
    for sample in ["zz4l-amcatnlo"]:
        #we only need to make new responseMatrix for zz4l-amcatnlo, ggZZ responseMatrices are already done above. 
        file_path=sigSamplesPath[sample]
        #print("where are the histos leaking")
        resp = C(channel, varNamesForResponseMaker[varName][channel], vBinning)
        #ROOT.SetOwnership(resp,False)
        file_path=file_path.encode("utf-8")
        #print "file_path: ",file_path
        fileList=glob.glob(file_path)
        #print "type in fileList should be str: ",type(fileList[0])
        for fName in fileList:
            resp.registerFile(fName)
        resp.registerPUWeights(hPUWt[''])
        resp.registerPUWeights(hPUWt['Up'], 'Up')
        resp.registerPUWeights(hPUWt['Down'], 'Down')
        resp.setConstantScale(sigConstWeights[sample])
        if hSF:
            resp.registerElectronSelectionSFHist(hSF['eSel'])
            resp.registerElectronSelectionGapSFHist(hSF['eSelGap'])
            resp.registerElectronLowRecoSFHist(hSF['eLowReco'])
            resp.registerElectronRecoSFHist(hSF['eReco'])
            resp.registerMuonSFHist(hSF['m'])
            resp.registerMuonSFErrorHist(hSF['mErr'])
            #print("scale factors are being added")

        altResponseMakers[sample] = resp
        #print "resp: ",resp
        #del resp

    for sample in responseMakers.keys():
        print "sigSamples: " ,sample
    
    for sample in altResponseMakers.keys():
        print "altsigSamples: " ,sample

    for Resp in responseMakers.values()+altResponseMakers.values():
        ROOT.SetOwnership(Resp,False)
    
    return responseMakers,altResponseMakers

_printCounter = 0
#Load the RooUnfold library into ROOT
ROOT.gSystem.Load("RooUnfold/libRooUnfold")
def unfold(varName,chan,responseMakers,altResponseMakers,hSigDic,hAltSigDic,hSigSystDic,hTrueDic,hAltTrueDic,hDataDic,hbkgDic,hbkgMCDic,hbkgMCSystDic,nIter,plotDir=''):
    global _printCounter
    #get responseMakers from the function above- this is the whole game.
    #responseMakers = generateResponseClass(varName, chan,sigSamples,sumW,hSF)

    # outputs
    hUnfolded = {}
    hTruth={}
    hTrueAlt = {}
    hResponseNominal={}
    print "responseMakers: ",responseMakers
    hResponseNominal = {s:resp for s,resp in responseMakers.items()}
    print "hResponseNominal:",hResponseNominal
    
    #Setup() is called here for all signals?
    hResponseSig1 = hResponseNominal["ggZZ4e"].getResponse("pu_Up")
    hResponseSig2 = hResponseNominal["ggZZ4m"].getResponse("pu_Up")
    hResponseSig3 = hResponseNominal["ggZZ4t"].getResponse("pu_Up")
    hResponseSig4 = hResponseNominal["ggZZ2e2tau"].getResponse("pu_Up")
    hResponseSig5 = hResponseNominal["ggZZ2e2mu"].getResponse("pu_Up")
    hResponseSig6 = hResponseNominal["zz4l-powheg"].getResponse("pu_Up")
    #This will pop the powheg response matrix from the hResponseNominal Dictionary
    hResponseNominalTotal = hResponseNominal.pop("zz4l-powheg")
    #print "hRespNominalTotal: ",hResponseNominalTotal
    #This gets us the response matrix as a TH2D for "zz4l-powheg"
    print "This hResponse is full of leaks here"
    hResponse = hResponseNominalTotal.getResponse('nominal')
    hResponse.SetDirectory(0)
    #ROOT.SetOwnership(hResponse,False)
    #print("where are all the leaks") 
    #print "type of hResp: " ,hResponse
    #Now we need to add the rest of the response matrices (MCFMs) to this POHWEG matrix
    #Looping over the values of the dictionary (it doesn't have powheg anymore)
    #print "hResponseNominal after zz-pohwheg:",hResponseNominal
    for response in hResponseNominal.values():
        print "Is the leak here"
        print "response: ",response
        respMat = response.getResponse('nominal')
        #ROOT.SetOwnership(respMat,False)
        hResponse.Add(respMat)
        respMat.SetDirectory(0)
        print "Is the leak where"
        #ROOT.SetOwnership(respMat,False)  
        del respMat
        #respMat.Delete()

    #print ("The leaks happen in this for loop")
    #hResponseNominalTotal = sum(resp for resp in hResponseNominal.values())
    

    #print "type of Total hResp: " ,hResponse
    # But its better to use RooUnfoldResponse here
    #RooUnfoldResponse constructor - create from already-filled histograms
    # "response" gives the response matrix, measured X truth.
    #  "measured" and "truth" give the projections of "response" onto the X-axis and Y-axis respectively,
    #   but with additional entries in "measured" for measurements with no corresponding truth (fakes/background) and
    #    in "truth" for unmeasured events (inefficiency).
    #     "measured" and/or "truth" can be specified as 0 (1D case only) or an empty histograms (no entries) as a shortcut
    #      to indicate, respectively, no fakes and/or no inefficiency.


    ## Give hSig and hTrue in the form of histograms

    varNames={'mass': 'Mass','pt':'ZZPt','zpt':'ZPt','leppt':'LepPt','dphiz1z2':'dPhiZ1Z2','drz1z2':'dRZ1Z2'}
    #varNames={'zmass':'ZMass','mass': 'Mass','pt':'ZZPt','eta':'ZZEta','z1mass':'Z1Mass','z1pt':'Z1Pt','z2mass':'Z2Mass','z2pt':'Z2Pt','zpt':'ZPt','leppt':'LepPt'}

    hSigNominal = hSigDic[chan][varNames[varName]]
    #print "sigHist: ", hSigNominal,", ",hSigNominal.Integral()

    hTrue = hTrueDic[chan]["Gen"+varNames[varName]]
    #histTrue.Scale((1.256*35900*1.0835)/zzSumWeights) 
    hData = hDataDic[chan][varNames[varName]]
    #print "dataHist: ",hData,", ",hData.Integral()
    #Get the background hists - #Get the histName_Fakes_chan histos
    hBkgNominal = hbkgDic[chan][varNames[varName]+"_Fakes"]
    #print "NonPromptHist: ",hBkgNominal,", ",hBkgNominal.Integral()
    hBkgMCNominal = hbkgMCDic[chan][varNames[varName]]
    #print "VVVHist: ",hBkgMCNominal,", ",hBkgMCNominal.Integral()
    #Add the two backgrounds
    hBkgTotal=hBkgNominal.Clone()
    hBkgTotal.Add(hBkgMCNominal)
    #print "TotBkgHist: ",hBkgTotal,", ",hBkgTotal.Integral()

    #No need to rebin certain variables
    #if varNames[varName] not in ['ZZEta']:
        #bins=array.array('d',_binning[varName])
        #Nbins=len(bins)-1 
        #hSigNominal=hSigNominal.Rebin(Nbins,"",bins)
        #hTrue=hTrue.Rebin(Nbins,"",bins)
        #hData=hData.Rebin(Nbins,"",bins)
        #hBkgTotal=hBkgTotal.Rebin(Nbins,"",bins)
    #using the rebin function which takes care of overflow bins
    hSigNominal=rebin(hSigNominal,varName)
    hTrue=rebin(hTrue,varName)
    hData=rebin(hData,varName)
    hBkgTotal=rebin(hBkgTotal,varName)
    
    xaxisSize = hSigNominal.GetXaxis().GetTitleSize()
    yaxisSize = hTrue.GetXaxis().GetTitleSize()
    #print "xaxisSize: ",xaxisSize
    print "trueHist: ",hTrue,", ",hTrue.Integral()
    #print "TotBkgHist after rebinning: ",hBkgTotal,", ",hBkgTotal.Integral()
    hTruth['']=hTrue

    hUnfolded[''], hCov, hResp = getUnfolded(hSigNominal,hBkgTotal,hTruth[''],hResponse,hData, nIter,True)

    #print "hUnfolded['']: ",hUnfolded[''].Integral()
    
    #print("hResp: ",hResp) 
    #del hResponse
    # plot covariance and response
    if plotDir and args['plotResponse']:
        cRes = ROOT.TCanvas("c","canvas")
        if varName == 'massFull':
            cRes.SetLogx()
            cRes.SetLogy()
        draw_opt = "colz text45"
        hResp.GetXaxis().SetTitle('Reco '+prettyVars[varName]+''+units[varName])
        hResp.GetYaxis().SetTitle('True '+prettyVars[varName]+''+units[varName])
        hResp.GetXaxis().SetTitleSize(0.75*xaxisSize)
        hResp.GetYaxis().SetTitleSize(0.75*yaxisSize)
        hResp.Draw(draw_opt)
        texS,texS1=getLumiTextBox()
        #style.setCMSStyle(cRes, '', dataType='  Preliminary', intLumi=35900.)
        #print "plotDir: ",plotDir 
        plotName="response_%s" % (varName)
        output_name="/".join([plotDir,plotName])
        #cRes.Print("%s/response_%s.png" % (plotDir,varName))
        cRes.Print(output_name+".eps")
        cRes.Print(output_name+".png") 
        subprocess.call(["epstopdf", "--outfile=%s" % output_name+".pdf", output_name+".eps"],env={})
        os.remove(output_name+".eps")

        del cRes

        cCov = ROOT.TCanvas("c","canvas")
        if varName == 'massFull':
            cCov.SetLogx()
            cCov.SetLogy()
        draw_opt = "colz text45"
        hCov.Draw(draw_opt)
        texS,texS1=getLumiTextBox()
        covName="covariance_%s" % (varName)
        cov_name="/".join([plotDir,covName])
        cCov.Print(cov_name+".eps")
        cCov.Print(cov_name+".png") 
        subprocess.call(["epstopdf", "--outfile=%s" % cov_name+".pdf", cov_name+".eps"],env={})
        os.remove(cov_name+".eps")
        #style.setCMSStyle(cCov, '', dataType='Preliminary', intLumi=35900.)
        #cCov.Print("%s/covariance_%s.pdf" % (plotDir,varName))
        del cCov
    if not args['noSyst']: 
        # luminosity
        lumiUnc = 0.023
        lumiScale = {'Up':1.+lumiUnc,'Down':1.-lumiUnc}
        for sys, scale in lumiScale.iteritems():
            #print "lumi uncert.",sys
            #print "scale: ",scale
            hSigLumi = hSigNominal * scale
            hSigLumi.SetDirectory(0)

            hBkgLumi = hbkgDic[chan][varNames[varName]+"_Fakes"]
            hBkgLumi.SetDirectory(0)
            hBkgMCLumi = hbkgMCDic[chan][varNames[varName]]
            hBkgMCLumi.SetDirectory(0)
            hBkgMCLumi.Scale(scale)
            hBkgTotalLumi=hBkgLumi.Clone()
            hBkgTotalLumi.Add(hBkgMCLumi)

            hTrueLumiShift = hTruth[''] * scale
            hTrueLumiShift.SetDirectory(0)
            hResponseLumi = hResponse.Clone()
            hResponseLumi.Scale(scale)
            hResponseLumi.SetDirectory(0)
            #print "SigLumiHist: ",hSigLumi,", ",hSigLumi.Integral()
            #print "VVVHist: ",hBkgMCLumi,", ",hBkgMCLumi.Integral()
            #Add the two backgrounds

            hBkgTotalLumi=rebin(hBkgTotalLumi,varName)

            #print "trueHist: ",hTrueLumiShift,", ",hTrueLumiShift.Integral()
            #print "TotBkgHistLumi after rebinning: ",hBkgTotalLumi,", ",hBkgTotalLumi.Integral()

            hUnfolded['lumi_'+sys],hCovLumi,hRespLumi = getUnfolded(hSigLumi,hBkgTotalLumi,hTrueLumiShift,hResponseLumi,hData, nIter,True)

            del hSigLumi
            del hBkgMCLumi
            del hBkgLumi
            del hTrueLumiShift

            #print "hUnfolded['lumi_']: ",hUnfolded['lumi_'+sys].Integral()

            if plotDir and args['plotSystResponse']:
                cResLumi = ROOT.TCanvas("c","canvas",800,800)
                if varName == 'massFull':
                    cRes.SetLogx()
                    cRes.SetLogy()
                draw_opt = "colz text45"
                hRespLumi.GetXaxis().SetTitle('Reco '+prettyVars[varName]+''+units[varName])
                hRespLumi.GetYaxis().SetTitle('True '+prettyVars[varName]+''+units[varName])
                hRespLumi.GetXaxis().SetTitleSize(0.75*xaxisSize)
                hRespLumi.GetYaxis().SetTitleSize(0.75*yaxisSize)
                hRespLumi.Draw(draw_opt)
                style.setCMSStyle(cResLumi, '', dataType='  Preliminary', intLumi=35900.)
                #print "plotDir: ",plotDir
                cResLumi.Print("%s/response_%s_%s.png" % (plotDir,varName,'lumi'+sys))
                cResLumi.Print("%s/response_%s_%s.pdf" % (plotDir,varName,'lumi'+sys))
            
                del cResLumi
        
        hResponsePU = {s:resp for s,resp in responseMakers.items()}
        hRespPUTot = hResponsePU.pop("zz4l-powheg")
        print "No errors in PU chain?"
        # PU reweight uncertainty
        for sys in ['Up','Down']:
            hRespPU = hRespPUTot.getResponse('pu_'+sys)
            hRespPU.SetDirectory(0)
            for resp in hResponsePU.values():
                respMatPU = resp.getResponse('pu_'+sys)
                hRespPU.Add(respMatPU)
                respMatPU.SetDirectory(0)
                del respMatPU
            #print "hSigSystDic: ",hSigSystDic
            hSigPU = hSigSystDic[chan][varNames[varName]+"_CMS_pileup"+sys]
            hSigPU.SetDirectory(0)
            #print 'pu_'+sys 
            #print "sigHist: ", hSigPU,", ",hSigPU.Integral()
            hBkgPU = hbkgDic[chan][varNames[varName]+"_Fakes"]
            hBkgPU.SetDirectory(0)
            #print "NonPromptHist: ",hBkgPU,", ",hBkgPU.Integral()
            hBkgMCPU = hbkgMCSystDic[chan][varNames[varName]+"_CMS_pileup"+sys]
            hBkgMCPU.SetDirectory(0)
            #print "VVVHist: ",hBkgMCPU,", ",hBkgMCPU.Integral()
            hBkgPUTotal=hBkgPU.Clone()
            hBkgPUTotal.Add(hBkgMCPU)
            #print "TotBkgPUHist: ",hBkgPUTotal,", ",hBkgPUTotal.Integral()
            hSigPU=rebin(hSigPU,varName)
            hBkgPUTotal=rebin(hBkgPUTotal,varName)
            #print "TotBkgPUHist after Rebinning: ",hBkgPUTotal,", ",hBkgPUTotal.Integral()
            
            hUnfolded['pu_'+sys] = getUnfolded(hSigPU,
                                                     hBkgPUTotal,
                                                     hTruth[''],
                                                     hRespPU,
                                                     hData, nIter)
            del hSigPU
            del hBkgMCPU
            del hBkgPU
            del hRespPU

        # lepton efficiency uncertainty
        for lep in set(chan):
            hResponseSyst = {s:resp for s,resp in responseMakers.items()}
            hRespSystTot = hResponseSyst.pop("zz4l-powheg")
            print "No errors in systematics chain?"
            for sys in ['Up','Down']:
                hRespSyst = hRespSystTot.getResponse(lep+'Eff_'+sys)
                hRespSyst.SetDirectory(0)
                for response in hResponseSyst.values():
                    respMatSyst = response.getResponse(lep+'Eff_'+sys)
                    hRespSyst.Add(respMatSyst)
                    respMatSyst.SetDirectory(0)
                    del respMatSyst
                #print "hSigSystDic: ",hSigSystDic
                hSigSyst = hSigSystDic[chan][varNames[varName]+"_CMS_eff_"+lep+sys]
                hSigSyst.SetDirectory(0)
                #print lep+'Eff_'+sys 
                #print "sigHist: ", hSigSyst,", ",hSigSyst.Integral()
                hBkgSyst = hbkgDic[chan][varNames[varName]+"_Fakes"]
                hBkgSyst.SetDirectory(0)
                #print "NonPromptHist: ",hBkgSyst,", ",hBkgSyst.Integral()
                hBkgMCSyst = hbkgMCSystDic[chan][varNames[varName]+"_CMS_eff_"+lep+sys]
                hBkgMCSyst.SetDirectory(0)
                #print "VVVHist: ",hBkgMCSyst,", ",hBkgMCSyst.Integral()
                hBkgSystTotal=hBkgSyst.Clone()
                hBkgSystTotal.Add(hBkgMCSyst)
                #print "TotBkgSystHist: ",hBkgSystTotal,", ",hBkgSystTotal.Integral()
                hSigSyst=rebin(hSigSyst,varName)
                hBkgSystTotal=rebin(hBkgSystTotal,varName)
                #print "TotBkgSystHist after Rebinning: ",hBkgSystTotal,", ",hBkgSystTotal.Integral()
                
                hUnfolded[lep+'Eff_'+sys] ,hCovLep,hRespLep = getUnfolded(hSigSyst,
                                                         hBkgSystTotal,
                                                         hTruth[''],
                                                         hRespSyst,
                                                         hData, nIter,True)
                del hSigSyst
                del hBkgMCSyst
                del hBkgSyst
                del hRespSyst

                if plotDir and args['plotSystResponse']:
                    cResSyst = ROOT.TCanvas("c","canvas",1200,1200)
                    if varName == 'massFull':
                        cResSyst.SetLogx()
                        cResSyst.SetLogy()
                    draw_opt = "colz text45"
                    hRespLep.GetXaxis().SetTitle('Reco '+prettyVars[varName]+sys+''+units[varName])
                    hRespLep.GetYaxis().SetTitle('True '+prettyVars[varName]+sys+''+units[varName])
                    hRespLep.GetXaxis().SetTitleSize(0.75*xaxisSize)
                    hRespLep.GetYaxis().SetTitleSize(0.75*yaxisSize)
                    hRespLep.Draw(draw_opt)
                    style.setCMSStyle(cResSyst, '', dataType='  Preliminary', intLumi=35900.)
                    #print "plotDir: ",plotDir
                    cResSyst.Print("%s/response_%s_%s.png" % (plotDir,varName,lep+'Eff_'+sys))
                    cResSyst.Print("%s/response_%s_%s.pdf" % (plotDir,varName,lep+'Eff_'+sys))
                    del cResSyst

    del hResponse 
    
    #Alternative signal zz4l-amcatnlo
    hResponseAltNominal={} 
    print "AltresponseMakers: ",altResponseMakers
    hResponseAltNominal = {s:resp for s,resp in altResponseMakers.items()}
    print "hResponseNominal:",hResponseNominal
    print "hResponseAltNominal:",hResponseAltNominal

    hResponseSig7 = hResponseAltNominal["zz4l-amcatnlo"].getResponse("pu_Up")
    #This will pop the amcnlo response matrix from the hResponseAltNominal Dictionary
    hResponseAltNominalTotal = hResponseAltNominal.pop("zz4l-amcatnlo")

    hAltResponse = hResponseAltNominalTotal.getResponse('nominal')
    hAltResponse.SetDirectory(0)

    for response in hResponseNominal.values():
        print "response: ",response
        respMat = response.getResponse('nominal')
        hAltResponse.Add(respMat)
        respMat.SetDirectory(0)
        del respMat

    hAltSigNominal = hAltSigDic[chan][varNames[varName]]

    hAltTrue = hAltTrueDic[chan]["Gen"+varNames[varName]]

    hAltSigNominal=rebin(hAltSigNominal,varName)
    hAltTrue=rebin(hAltTrue,varName)

    print "AltTrueHist: ",hAltTrue,", ",hAltTrue.Integral()
    
    hTrueAlt['']=hAltTrue

    hUnfolded['generator']  = getUnfolded(hAltSigNominal,hBkgTotal,hTrueAlt[''],hAltResponse,hData, nIter) 

    # make everything local (we'll cache copies)
    for h in hUnfolded.values()+hTruth.values()+hTrueAlt.values():
        ROOT.SetOwnership(h,False)
        print("histos: ",h)
        print ("hTruthOut of Unfold: ",h.Integral())
        #h.SetDirectory(0)
    print "hUnfolded (inside unfold): ",hUnfolded
    print "hTrueAlt (inside unfold): ",hTrueAlt
    return hUnfolded,hTruth,hTrueAlt

#rebin histos and take care of overflow bins
def rebin(hist,varName):
    ROOT.SetOwnership(hist, False)
    #No need to rebin certain variables but still might need overflow check
    if varName not in ['eta']:
        bins=array.array('d',_binning[varName])
        Nbins=len(bins)-1 
        hist=hist.Rebin(Nbins,"",bins)
    else:
        Nbins = hist.GetSize() - 2
    add_overflow = hist.GetBinContent(Nbins) + hist.GetBinContent(Nbins + 1)
    hist.SetBinContent(Nbins, add_overflow)
    return hist

def getUnfolded(hSig, hBkg, hTrue, hResponse, hData, nIter,withRespAndCov=False):
    Response = getattr(ROOT,"RooUnfoldResponse")

    print "TrueBeforeResponse: ", hTrue,", ",hTrue.Integral()
    print "SigBeforeResponse: ", hSig,", ",hSig.Integral()
    response = Response(hSig, hTrue.Clone(), hResponse.Clone()) 
    ROOT.SetOwnership(response,False)
    ROOT.SetOwnership(hData,False)
    #Response matrix as a 2D-histogram: (x,y)=(measured,truth)
    hResp = response.Hresponse()
    #hResp = hResponse
    #print "hResp out of response: ",hResp

    #RooUnfoldIter = getattr(ROOT,"RooUnfoldBayes")

    RooUnfoldInv = getattr(ROOT,"RooUnfoldInvert")

    #RooUnfoldBinbyBin = getattr(ROOT,"RooUnfoldBinByBin")
    try:
        svd = ROOT.TDecompSVD(response.Mresponse())
        sig = svd.GetSig()
        try:
            condition = sig.Max() / max(0., sig.Min())
        except ZeroDivisionError:
            condition = float('inf')
            raise

        print "channel: ",chan
        print "variable: ",varNames[varName]
        print "hResp out of response: ",hResp
        print ''
        print 'condition: {}'.format(condition)
        print ''

    except:
        print "It broke! Printing debug info"
        print "Sig: {}, bkg: {}, true: {}, response: {}".format(hSig.Integral(), hBkg.Integral(), hTrue.Integral(), hResponse.Integral())
        c = ROOT.TCanvas("c1","canvas",800,800)
        hSig.Draw()
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/sig{}.png".format(_printCounter))
        hBkg.draw()
        _style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("bkg{}.png".format(_printCounter))
        hTrue.Draw()
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/true{}.png".format(_printCounter))
        hData.Draw()
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/data{}.png".format(_printCounter))
        draw_opt = "colz text45"
        hResponse.Draw(draw_opt)
        style.setCMSStyle(c, '', dataType='Debug', intLumi=35900.)
        c.Print("DebugPlots/resp{}.png".format(_printCounter))
        c.Print("DebugPlots/resp{}.root".format(_printCounter))
        _printCounter += 1

    print "hData: ", hData.Integral()
    hDataMinusBkg = hData.Clone()
    hDataMinusBkg.Reset()
    print "hBkg: ", hBkg.Integral()
    hDataMinusBkg.Add(hData,1)
    hDataMinusBkg.Add(hBkg,-1)
    #hDataMinusBkg.Add(hBkg,-1)
    #HistTools.zeroNegativeBins(hDataMinusBkg)
    print "DataMinusbkgIntegral: ",hDataMinusBkg, ", ",hDataMinusBkg.Integral()
    #Unfolding using 4 iterations and then stopping
    #if varNames[varName] not in ["Z1Mass","Z2Mass"]:
    #    nIter=8
    #print "No.of iterations: ",nIter
    print "response: ",response

    #Simply inverting the matrix
    unf = RooUnfoldInv(response, hDataMinusBkg)
    
    #unf = RooUnfoldIter(response, hDataMinusBkg, nIter)
    print "unf: ",unf 

    #Unfolds using the method of correction factors
    #unf = RooUnfoldBinbyBin(response, hSig)

    #del hDataMinusBkg
    #This is the unfolded "data" distribution
    hOut = unf.Hreco()
    #ROOT.SetOwnership(hOut,False)
    if not hOut:
        print hOut
        raise ValueError("The unfolded histogram got screwed up somehow!")
    print("hOut: ",hOut,"",hOut.Integral()) 
    #Returns covariance matrices for error calculation of type withError
    #0: Errors are the square root of the bin content
    #1: Errors from the diagonals of the covariance matrix given by the unfolding
    #2: Errors from the covariance matrix given by the unfolding => We use this one for now
    #3: Errors from the covariance matrix from the variation of the results in toy MC tests
    hCov = unf.Ereco(2)
    #hOut.SetDirectory(0)
    #hResp.SetDirectory(0)
    #ROOT.SetOwnership(hCov,False)
    print("hCov: ",hCov) 
    print("where is the crash happening?")
    #return hCov.Clone(),hResp.Clone()
    #return hOut
    if withRespAndCov:
        return hOut,hCov.Clone(),hResp.Clone()
    
    #del hDataMinusBkg
    #print "DataMinusbkgIntegral: ",hDataMinusBkg, ", ",hDataMinusBkg.Integral()
    return hOut

def _generateUncertainties(hDict,norm):

    nominalArea = hDict[''].Integral(0,hDict[''].GetNbinsX()+1)
    hErr = {'Up':{},'Down':{}}
    for sys, h in hDict.iteritems():
        if not sys:
            continue

        he = h.Clone()

        if norm:
            he.Scale(nominalArea/(he.Integral(0,he.GetNbinsX()+1)))

        #Subtract the nominal histogram from the SysUp or Down histogram

        he.Add(hDict[''],-1)
        sysName = sys.replace('_Up','').replace('_Down','')

        if '_Up' in sys:
            hErr['Up'][sysName] = he
        elif '_Down' in sys:
            hErr['Down'][sysName] = he
        else:
            hErr['Up'][sysName] = he
            he2 = he.Clone()
            hErr['Down'][sysName] = he2
    
    return hErr

def _sumUncertainties(errDict,varName):
    if varName == "eta":
        histbins=array.array('d',[0.,1.0,2.0,3.0,4.0,5.0,6.0])
    else:
        histbins=array.array('d',_binning[varName])
    #print "histbins: ",histbins
    hUncUp=ROOT.TH1D("hUncUp","Total Up Uncert.",len(histbins)-1,histbins)
    hUncDn=ROOT.TH1D("hUncDn","Total Dn Uncert.",len(histbins)-1,histbins)
    sysList = errDict['Up'].keys()
    #print "sysList: ",sysList
    #print "hUncUp: ",hUncUp,"",hUncUp.Integral()
    #print "hUncDown: ",hUncDn,"",hUncDn.Integral()
    totUncUp=totUncDn=0.
    UncUpHistos= [errDict['Up'][sys] for sys in sysList]
    UncDnHistos= [errDict['Down'][sys] for sys in sysList]
    LumiUp = errDict['Up']['lumi']
    LumiDn = errDict['Down']['lumi']
    #print "LumiUp: ",LumiUp.Integral()
    #print "LumiDn: ",LumiDn.Integral()
    for i in range(1,hUncUp.GetNbinsX()+1):
        for h1, h2 in zip(UncUpHistos,UncDnHistos):
            #print "histUp: ",h1,"",h1.Integral()
            #print "histDn: ",h2,"",h2.Integral()
            totUncUp += max(h1.GetBinContent(i),h2.GetBinContent(i))**2
            totUncDn += min(h1.GetBinContent(i),h2.GetBinContent(i))**2

        totUncUp = math.sqrt(totUncUp)
        totUncDn = math.sqrt(totUncDn)
        #print "totUncUp: ",totUncUp
        #print "totUncDn: ",totUncDn
        hUncUp.SetBinContent(i,totUncUp)
        hUncDn.SetBinContent(i,totUncDn)
    print("hUncUp: ",hUncUp,"",hUncUp.Integral()) 
    print("hUncDown: ",hUncDn,"",hUncDn.Integral())

    return hUncUp, hUncDn

def _combineChannelUncertainties(*errDicts):
    hUncTot = {}
    uncList = []
    for errDict in errDicts:
        for sys in ['Up','Down']:
            uncList += errDict[sys].keys()
    uncList = set(uncList)
    print "uncList:",uncList
    for sys in ['Up','Down']:
        hUncTot[sys] = {}
        for unc in uncList:
            if varName == "eta":
                histbins=array.array('d',[0.,1.0,2.0,3.0,4.0,5.0,6.0])
            else:
                histbins=array.array('d',_binning[varName])
            #print "histTot histbins: ",histbins
            histTot=ROOT.TH1D("histTot","Tot Uncert.",len(histbins)-1,histbins)
            ROOT.SetOwnership(histTot,False)
            hUncTot[sys][unc] = histTot
            for errDict in errDicts:
                try:
                    hUncTot[sys][unc].Add(errDict[sys][unc])
                except KeyError:
                    continue

    return hUncTot

def mkdir(plotDir):
    for outdir in [plotDir]:
        try:
            os.makedirs(os.path.expanduser(outdir))
        except OSError as e:
            print e
            pass

plotDir=args['plotDir']
nIterations=args['nIter']

varNames={'mass': 'Mass','pt':'ZZPt','zpt':'ZPt','leppt':'LepPt','dphiz1z2':'dPhiZ1Z2','drz1z2':'dRZ1Z2'}


#Dictionary where signal samples are keys with cross-section*kfactors as values
sigSampleDic=ConfigureJobs.getListOfFilesWithXSec(ConfigureJobs.getListOfEWK())
sigSampleList=[str(i) for i in sigSampleDic.keys()]
print "sigSamples: ",sigSampleList

AltsigSampleDic=ConfigureJobs.getListOfFilesWithXSec(["zz4l-amcatnlo",])
AltsigSampleList=[str(i) for i in AltsigSampleDic.keys()]
print "AltsigSamples: ",AltsigSampleList

#Combine sigSamples
TotSigSampleList = list(set(sigSampleList) | set(AltsigSampleList))
sigSampleDic.update(AltsigSampleDic)
#Replace fOut with fUse once you have run all the data samples and the backgrounds - right now unfolded data looking really big- subtract backgrounds
if args['test']:
    sigSamplesPath={}
    fUse = ROOT.TFile("SystGenFiles/Hists15Oct2019-ZZ4l2018_MVA.root","update")
    fOut=fUse
    for dataset in TotSigSampleList:
        file_path = ConfigureJobs.getInputFilesPath(dataset,selection, analysis)
        #print "file_path:",file_path
        sigSamplesPath[dataset]=file_path

#Sum all data and return a TList of all histograms that are booked. And an empty datSumW dictionary as there are no sumWeights
alldata,dataSumW = HistTools.makeCompositeHists(fOut,"AllData", 
    ConfigureJobs.getListOfFilesWithXSec([args['analysis']+"data"],manager_path), args['lumi'],
    underflow=False, overflow=False)


#all ewkmc/this is also allSignal histos, scaled properly, kind of a repeat of above but with ggZZ added
ewkmc,ewkSumW = HistTools.makeCompositeHists(fOut,"AllEWK", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfEWK(), manager_path), args['lumi'],
    underflow=False, overflow=False)

altSigmc,altSigSumW = HistTools.makeCompositeHists(fOut,"AltSig", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfaltSig(), manager_path), args['lumi'],
    underflow=False, overflow=False)

#Update ewkSumW dictionary with sumWeights value of zz4l-amcatnlo from altSigSumW, the common keys should not be duplicated
ewkSumW.update(altSigSumW)

#all mcbkg that needs to be subtracted
allVVVmc,VVVSumW = HistTools.makeCompositeHists(fOut,"AllVVV", ConfigureJobs.getListOfFilesWithXSec(
    ConfigureJobs.getListOfVVV(), manager_path), args['lumi'],
    underflow=False, overflow=False)

#This is the non-prompt background
ewkcorr = HistTools.getDifference(fOut, "DataEWKCorrected", "AllData", "AllEWK")

print "Signals: ",ewkSumW
#print the sum for a sample (zz4l-powheg)
zzSumWeights = ewkSumW["zz4l-powheg"]  
#print "sumW (zz4l-powheg): ",zzSumWeights

#getHistInDic function also takes care of adding the histograms in eemm+mmee, hence the input here is channels=[eeee,eemm,mmmm]
#dataHists dictionary
hDataDic=OutputTools.getHistsInDic(alldata,varList,channels)

hSigDic=OutputTools.getHistsInDic(ewkmc,varList,channels)

#Alt signals containing zzl4-amcatnlo instead of zz4l-powheg
hAltSigDic=OutputTools.getHistsInDic(altSigmc,varList,channels)

#TrueHists dictionary
#hTrueDic=OutputTools.getHistsInDic(allzzPowheg,["Gen"+s for s in varList],channels)
hTrueDic=OutputTools.getHistsInDic(ewkmc,["Gen"+s for s in varList],channels)

#Alt signals containing zzl4-amcatnlo instead of zz4l-powheg
hAltTrueDic=OutputTools.getHistsInDic(altSigmc,["Gen"+s for s in varList],channels)

#Non-prompt background dictionary
hbkgDic=OutputTools.getHistsInDic(ewkcorr,[s+"_Fakes" for s in varList],channels)
#strange python debug
print "channels: ",channels
if "mmee" in channels:
    channels.remove("mmee")
#VVV background dictionary
hbkgMCDic=OutputTools.getHistsInDic(allVVVmc,varList,channels)
print "hbkgMCDic: ",hbkgMCDic

runVariables=[]
runVariables.append(args['variable'])
print "runVariables: ",runVariables

##Systematic histos
systList=[]
for chan in channels:
    for sys in ["Up","Down"]: 
        for s in runVariables:
            systList.append(varNames[s]+"_CMS_pileup"+sys)
            for lep in set(chan):         
                systList.append(varNames[s]+"_CMS_eff_"+lep+sys)

print systList
hSigSystDic=OutputTools.getHistsInDic(ewkmc,systList,channels)

hbkgMCSystDic=OutputTools.getHistsInDic(allVVVmc,systList,channels)


OutputDirs={}

SFhistos,PUhistos = generateAnalysisInputs()
#So even when selector runs, run the unfolding procedure only on the variables provided.

#Make differential cross sections normalizing to unity area.')
norm = not args['noNorm']
savehists=[]
for varName in runVariables:
    print "varName:", varNames[varName]
    # save unfolded distributions by channel, then systematic
    hUnfolded = {"eeee":{},"eemm":{},"mmmm":{}}
    hTrue = {"eeee":{},"eemm":{},"mmmm":{}}
    hTrueAlt = {"eeee":{},"eemm":{},"mmmm":{}}
    hErr = {}
    hErrTrue = {}
    for chan in channels:
        print "channel: ",chan
        print "hUnfolded: ",hUnfolded
        print "hTrue: ",hTrue
        OutputDir=plotDir+"/"+chan+"/plots"
        if chan not in OutputDirs:
            OutputDirs[chan]=OutputDir
        if not os.path.exists(OutputDir):
            mkdir(OutputDir)
            OutputDirs[chan]=OutputDir
         
        responseMakers,altResponseMakers = generateResponseClass(varName, chan,sigSampleDic,sigSamplesPath,ewkSumW,PUhistos,SFhistos)
        print "hUnfolded in main: ", hUnfolded
        print "hTrue in main: ", hTrue
        print "hTrue in main: ", hTrueAlt
        hUnfolded[chan], hTrue[chan],hTrueAlt[chan] = unfold(varName,chan,responseMakers,altResponseMakers,hSigDic,hAltSigDic,hSigSystDic,hTrueDic,hAltTrueDic,hDataDic,hbkgDic,hbkgMCDic,hbkgMCSystDic,nIterations,OutputDir)
        print("returning unfolded? ",hUnfolded[chan])
        #print("returning truth? ",hTrue[chan])

        if not args['noSyst']: 
            hErr[chan]= _generateUncertainties(hUnfolded[chan],norm)
            print "hErr[",chan,"]: ",hErr[chan]
            (hUncUp, hUncDn) = _sumUncertainties(hErr[chan],varName)
        #hErrTrue[chan] = _generateUncertainties(hTrue[chan],norm)
        #(hTrueUncUp, hTrueUncDn) = _sumUncertainties(hErrTrue[chan],varName)
            #save histograms instead of plotting them
            hUnf = hUnfolded[chan][''].Clone()
            unfName = chan+"_"+varName+"_unf"
            hUnf.SetName(unfName)
            savehists.append(hUnf)
            #hTrue
            hTheo = hTrue[chan][''].Clone()
            truName = chan+"_"+varName+"_true"
            hTheo.SetName(truName)
            savehists.append(hTheo)
            #hTrueAlt
            hTheoAlt = hTrueAlt[chan][''].Clone()
            AltTruName = chan+"_"+varName+"_trueAlt"
            hTheoAlt.SetName(AltTruName)
            savehists.append(hTheoAlt)
            #hUncUp
            UncUp = hUncUp.Clone()
            UncUpName = chan+"_"+varName+"_totUncUp"
            UncUp.SetName(UncUpName)
            savehists.append(UncUp)
            #hUncDn
            UncDn = hUncDn.Clone()
            UncDnName = chan+"_"+varName+"_totUncDown"
            UncDn.SetName(UncDnName)
            savehists.append(UncDn)
    print "savehists: ",savehists
    if args['makeTotals']:
        if "eeee" in channels:
            hTot = hUnfolded["eeee"]['']
            hTrueTot = hTrue["eeee"]['']
            hTrueAltTot = hTrueAlt["eeee"]['']
            #channels.remove("eeee")
        print("channels before adding histos: ",channels)
        for c in ["eemm","mmmm"]:
            hTot.Add(hUnfolded[c][''])
            hTrueTot.Add(hTrue[c][''])
            hTrueAltTot.Add(hTrueAlt[c][''])
        print "hErr.values(): ",hErr.values()
        hErrTot = _combineChannelUncertainties(*hErr.values())
        hTotUncUp, hTotUncDn = _sumUncertainties(hErrTot,varName)
        #Saving Total histograms
        hTotUnf = hTot.Clone()
        TotName = "tot_"+varName+"_unf"
        hTotUnf.SetName(TotName)
        savehists.append(hTotUnf)
        #hTrue
        hTotTrue = hTrueTot.Clone()
        TotTruName = "tot_"+varName+"_true"
        hTotTrue.SetName(TotTruName)
        savehists.append(hTotTrue)
        #hTrueAlt
        hTotTrueAlt = hTrueAltTot.Clone()
        TotAltTruName = "tot_"+varName+"_trueAlt"
        hTotTrueAlt.SetName(TotAltTruName)
        savehists.append(hTotTrueAlt)
        #hUncUp
        TotUncUp = hTotUncUp.Clone()
        TotUncUpName = "tot_"+varName+"_totUncUp"
        TotUncUp.SetName(TotUncUpName)
        savehists.append(TotUncUp)
        #hUncDn
        TotUncDn = hTotUncDn.Clone()
        TotUncDnName = "tot_"+varName+"_totUncDown"
        TotUncDn.SetName(TotUncDnName)
        savehists.append(TotUncDn)
        
for cat in ["eeee","eemm","mmmm"]:   
    #This is where we put all the plots in html format for quick access/debugging
    makeSimpleHtml.writeHTML(os.path.expanduser(OutputDirs[cat].replace("/plots", "")), "2D ResponseMatrices (from MC)")

today = datetime.date.today().strftime("%d%b%Y")
tmpFileName = "PlotRespFull%s-%s.root" % (today, analysis) 
fHistOut = ROOT.TFile.Open(tmpFileName, "update")
#fOut = ROOT.TFile.Open("/".join([outputFolder, outputFile]), "RECREATE")
fHistOut.cd()
for newhists in savehists:
    newhists.Write()
fHistOut.Close()
