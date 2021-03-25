import ROOT
from array import array
from JES_BalanceFitter import JES_BalanceFitter
import numpy as np
#from atlasplots import atlas_style as astyle

#this helper takes a TH3 and slices it (according to arguments), fits each slice with a gaussian and returns a TGraphErrors of responses or resolutions
    
#graphType = type of graph desired ("res, "relRes", "resp"); inTH3 = input TH3; slicingAxis = axis to bin over; projectionAxis = axis to integrate out; responseAxis = axis with response; sliceBins = bins into which slicingAxis is sliced; rebinningSize = # of bins to combine; outFile = place to save outputs; projectionRebinWidth = how many bins to combine to make each new bin on the projection axis; nSigmaForFit = the fitting range in terms of sample variance

def pretty1DPlot(histFit, responseAxisName, projectionAxisName, slicingAxisName, binWidth, lowerPt, upperPt, currentSlice):
    title = "pT response in pT=["+str(round(lowerPt,2))+","+str(round(upperPt,2))+"] and eta=["+str(currentSlice[0])+","+str(currentSlice[1])+"]"
    
    # Set the ATLAS Style
    #astyle.SetAtlasStyle()
    
    # Construct the canvas
    #c1 = ROOT.TCanvas(title, title, 0, 0, 800, 600)
    
    numerator_scale = responseAxisName.split("_")[0].split("-")[0]
    numerator_type = responseAxisName.split("_")[0].split("-")[1]
    denominator_scale = responseAxisName.split("_")[2].split("-")[0]
    denominator_type = responseAxisName.split("_")[2].split("-")[1]
    extra=""
    
    # Define a distribution
    # Randomly fill the histrogram according to the above distribution
    #histFit.Draw()
    
    # Set axis titles
    histFit.SetTitle(title)
    if(denominator_scale!=""): extra="at "+denominator_scale+"calibration scale"
    xAxisTitle = "Response = "+numerator_type+" jet pT at "+numerator_scale+" calibration scale / "+denominator_type+" jet pT"+extra
    histFit.GetXaxis().SetTitle(xAxisTitle)
    histFit.GetXaxis().SetRangeUser(0,5)
    histFit.GetYaxis().SetTitle("Counts / "+str(round(binWidth,2))+" GeV^{-1}")
    
    # Add the ATLAS Label
    #astyle.ATLASLabel(0.2, 0.87, "Internal")
    
    #ROOT.gStyle.SetOptStat(0);
    #ROOT.gROOT.ForceStyle();
    
    #ROOT.gStyle.SetTitleFontSize(0.8)

    #c1.Update()
    #c1.Write()
    
    histFit.Write()

def getAxisNames(TH3Name):
    return TH3Name.split("_-_")[1], TH3Name.split("_-_")[2], TH3Name.split("_-_")[3]

def TH3toTGraphs(graphType, inTH3, slicingAxis, projectionAxis, responseAxis, sliceBins, projectionRebinWidth, outFilePath, nSigmaForFit, fitOptString, TH3Name):
    #quantities to fill TGraphErrors with
    xList, yList, xErrorList, yErrorList, sigmaList, sigmaErrorList, sigmaOverYList, entriesList = array( 'f' ), array( 'f' ), array( 'f' ), array( 'f' ), array( 'f' ), array( 'f' ), array( 'f' ), array( 'f' )
    graphsToReturn = []   
    h3D = inTH3.Clone()
    responseAxisName, projectionAxisName, slicingAxisName = getAxisNames(TH3Name)

    #set JES_BalanceFitter options
    JESBfitter = JES_BalanceFitter(nSigmaForFit)
    JESBfitter.SetGaus()
    JESBfitter.SetFitOpt(fitOptString)
    
    #if outFile exists, we want to save TH3 and the derived TH1s to this file
    if outFilePath:
        saveOutputToFile = True
        outFile = ROOT.TFile.Open(outFilePath+"-TGraph.root", "RECREATE")
        listOfTH1Content=[]
        listOfGaussians=[]
        
    xnBins = h3D.GetXaxis().GetNbins()
    ynBins = h3D.GetYaxis().GetNbins()

    for bin in sliceBins:
        print("Doing bin", bin)

        #Reset the arrays
        del xList[:]
        del yList[:]        
        del xErrorList[:]
        del yErrorList[:]
        del sigmaErrorList[:]
        del sigmaList[:]
        del sigmaOverYList[:]
        del entriesList[:]
             
        #Get the bin which corresponds to the desired slice axis range
        if slicingAxis == "y":
            h3D.GetYaxis().SetRangeUser(bin[0], bin[1]) 
            
        elif slicingAxis == "z":
            h3D.GetZaxis().SetRangeUser(bin[0], bin[1]) 

        if saveOutputToFile:
            outFile.cd()
            h3D.GetZaxis().SetTitle(slicingAxisName)
            h3D.GetYaxis().SetTitle(projectionAxisName)
            h3D.GetXaxis().SetTitle(responseAxisName)
            h3D.Write()
                          
        #Project the 3D histogram with the set y-axis range
        h2D=h3D.Project3D(responseAxis + projectionAxis)
         
        #rebin according to the desired rebinningFactor
        h2D.RebinX(projectionRebinWidth)
        
        #save projected TH3->TH2 to file 
        if saveOutputToFile:
            h3D.GetYaxis().SetTitle(responseAxisName)
            h3D.GetXaxis().SetTitle(projectionAxisName)
            h2D.Write()
                
        currentRebinnedBin = 1; 
        for currentRebinnedBin in range(1, h2D.GetNbinsX()+1):
            
            #name of projection
            projName = "slice"+str(bin[0])+"to"+str(bin[1])+"_projectionBin"+str(h2D.GetXaxis().GetBinLowEdge(currentRebinnedBin))+"to"+str(h2D.GetXaxis().GetBinUpEdge(currentRebinnedBin))
 
            #take projection
            h1D=h2D.ProjectionY(projName, currentRebinnedBin, currentRebinnedBin)
            
            #skip empty bins
            if h1D.GetEntries() == 0:
                #print("empty 1D hist, skipping!")
                continue
            
            #fitting limits
            fitMax = h1D.GetMean() + nSigmaForFit * h1D.GetRMS()
            fitMin = h1D.GetMean() - nSigmaForFit * h1D.GetRMS()
            
            #obtain fit using JES_BalanceFitter and associate it to the TH1           
            JESBfitter.Fit(h1D, fitMin, fitMax)
            #JESBfitter.Fit(h1D, 0, 3)
            fit = JESBfitter.GetFit()
            histFit = JESBfitter.GetHisto()
            Chi2Ndof = JESBfitter.GetChi2Ndof()
            histFit.GetListOfFunctions().Add(fit)
            
            if saveOutputToFile:
                ROOT.gStyle.SetOptStat(0);
                ROOT.gROOT.ForceStyle();
                
                #histFit.SetTitle("p_{T} Range ("+str(round(h2D.GetXaxis().GetBinLowEdge(currentRebinnedBin),2))+", "+str(round(h2D.GetXaxis().GetBinUpEdge(currentRebinnedBin),2))+") GeV. Fit Range: ("+str(round(fitMin,2))+", "+str(round(fitMax,2))+"). Entries: "+str(h1D.GetEntries()))
                #histFit.SetTitle(projectionAxisName+"="+str(round(h2D.GetXaxis().GetBinLowEdge(currentRebinnedBin),2))+", "+str(round(h2D.GetXaxis().GetBinUpEdge(currentRebinnedBin),2))+" Fit Range: ("+str(round(fitMin,2))+", "+str(round(fitMax,2))+"). Entries: "+str(h1D.GetEntries()))
                
                histFit.SetTitle(projectionAxisName+"=["+str(round(h2D.GetXaxis().GetBinLowEdge(currentRebinnedBin),2))+", "+str(round(h2D.GetXaxis().GetBinUpEdge(currentRebinnedBin),2))+"], eta=["+str(bin[0])+", "+str(bin[1])+"], Fit: "+"p0="+str(round(fit.GetParameter(0),6))+", p1="+str(round(fit.GetParameter(1),2))+", p2="+str(round(fit.GetParameter(2),3)))
                
                ROOT.gStyle.SetTitleFontSize(0.8)
                histFit.GetXaxis().SetTitle(responseAxisName)
                binWidth = h2D.GetXaxis().GetBinUpEdge(currentRebinnedBin) - h2D.GetXaxis().GetBinLowEdge(currentRebinnedBin)
                #histFit.GetYaxis().SetTitle("Counts / "+str(round(binWidth,2))+" GeV^{-1}")
                histFit.GetYaxis().SetTitle("Counts / "+str(round(binWidth,2)))
                
                histFit.Write()
                
                listOfGaussians.append([fit.GetParameter(0),fit.GetParameter(1),fit.GetParameter(2), fitMin, fitMax, Chi2Ndof])
                
                #print("\n")
                #for currentBin in range(1,h1D.GetNbinsX()+1):
                #    print(currentBin,round(h1D.GetXaxis().GetBinLowEdge(currentBin),6 ))
                #print(h1D.GetNbinsX(), "Upper edge:",round(h1D.GetXaxis().GetBinUpEdge(h1D.GetNbinsX()),6))
                
                bins=[]
                entries=[]
                binYerr=[]
                #histfit=h1D
                for i in range(1, h1D.GetNbinsX()+1):#Plus one to include last bin, this is simple python syntax
                  specificBinWidth = h1D.GetXaxis().GetBinWidth(i)
                  bins.append(h1D.GetXaxis().GetBinLowEdge(i))
                  entries.append(h1D.GetBinContent(i))
                  binYerr.append(h1D.GetBinError(i))
                bins.append(h1D.GetXaxis().GetBinUpEdge(h1D.GetNbinsX()))# Append the right most edge
                listOfTH1Content.append((entries,bins,binYerr))
                
                #for element in bins:
                #    print(round(element,6))
                
                
                
            #append return graph values
            x = float(h2D.GetXaxis().GetBinCenter(currentRebinnedBin))
            y = float(fit.GetParameter(1))
            xError = float((h2D.GetXaxis().GetBinWidth(currentRebinnedBin)/2.0)) #half bin width
            yError = float(fit.GetParError(1))
            sigma = float(fit.GetParameter(2))
            sigmaError = float(fit.GetParError(2))
            
            try: 
                sigmaOverY = float(fit.GetParameter(2) / float(fit.GetParameter(1)))
            except: 
                sigmaOverY = 0
            
            yList.append(y)
            xList.append(x)
            yErrorList.append(yError)
            xErrorList.append(xError)
            sigmaList.append(sigma)
            sigmaErrorList.append(sigmaError)
            sigmaOverYList.append(sigmaOverY)
            #print(h1D.GetEntries())
            entriesList.append(h1D.GetEntries())
            
        #Create a TGraph from the arrays, this is not necesary
        if graphType == "resolution":
            gr = ROOT.TGraphErrors(len(xList), xList, sigmaList, xErrorList, SigmaErrorList)
        elif graphType == "response":  
            gr = ROOT.TGraphErrors(len(xList), xList, yList, xErrorList, yErrorList)
        elif graphType == "relativeResponse": 
            gr = TGraphErrors( len(xList), xList, sigmaOverYList, xErrorList, SigmaErrorList) #FIXME add error to relative resolution. 
        else: 
            raise Exception("TH3toTGraphs() ERROR: no known graphType provided")
        gr.SetName(graphType+"_slice"+str(bin[0])+"to"+str(bin[1]))
        gr.Write()
        #graphsToReturn.append(gr)
        
        #np.savez(outFilePath.split(".")[0]+"_"+graphType+"_slice"+str(bin[0])+"to"+str(bin[1]),xList, yList, xErrorList, yErrorList, sigmaList, sigmaErrorList, sigmaOverYList)
        np.savez(outFilePath+"_-_"+str(bin[0])+":"+str(bin[1]),
                 x=xList,
                 y=yList,
                 yError=yErrorList,
                 xError=xErrorList,
                 sigma=sigmaList,
                 sigmaError=sigmaErrorList,
                 sigmaOverY=sigmaOverYList,
                 listOfTH1Content=listOfTH1Content,
                 listOfGaussians=listOfGaussians,
                 entries=entriesList)

        #also write to output file if enabled
        #if saveOutputToFile:
        #    gr.Write()
    
    outFile.Close()       
    
    return graphsToReturn
