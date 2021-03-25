import fitAndPlotConfig
import sys
import numpy as np
import scipy as scipy
import matplotlib.pyplot as plt
import mplhep as hep
import os
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline
from scipy.interpolate import splrep
from scipy.interpolate import BSpline

plotDict = fitAndPlotConfig.getPlotDict()

def printFit(pT, Par, nMinNeg, nMaxPos):
    pT0 = Par[ nMaxPos - nMinNeg ];
    
    parLast = ""
    for i in range(nMinNeg,nMaxPos):
        parLast +="-("+str(Par[i-nMinNeg])+"*pow(np.log("+pT0+"),"+str(i-1)+")*"+str(i)+"/"+pT0+")"
    parLast = "("+parLast+")"+"/"+"("+str(nMaxPos)+"*pow(np.log("+pT0+"),"+str(nMaxPos-1)+")/"+pT0+")"
    
    JESfit = ""
    for i in range(nMinNeg,nMaxPos):
        JESfit += "+("+Par[i-nMinNeg]+"*pow(np.log("+pT+"),"+str(i)+")"+")"
    JESfit +="+"+"("+ parLast+")"+"*pow(np.log("+str(pT)+"),"+str(nMaxPos)+")"

def getLabel(TH3NamePlus):
    numerator = TH3NamePlus.split("_-_")[1].split("_")[0].split("-")[0]
    denominator = TH3NamePlus.split("_-_")[1].split("_")[2].split("-")[0]
    if denominator == "":
        denominator = TH3NamePlus.split("_-_")[1].split("_")[2].split("-")[1]
    return(numerator+"$_{p_T}$"+" / "+denominator+"$ _{p_T}$")
    
def getLists():
    import ROOT
    listOfTH3Names=[]
    listOfCalibrationScalesAndYAxes=[]
    listOfDenominatorTypes=[]
    
    inFile = ROOT.TFile.Open(plotDict["rootFilePath"])
    listOfKeys = inFile.GetListOfKeys()
    for key in listOfKeys:
        TH3NamePlus = key.GetName()
        #if TH3NamePlus[0:2] != "h_":
        if TH3NamePlus[0:9] != "scaled_h_":
            continue
        listOfTH3Names.append(TH3NamePlus)
        listOfCalibrationScalesAndYAxes.append((TH3NamePlus.split("_-_")[1].split("_")[2].split("-")[1],TH3NamePlus.split("_-_")[2]))
        listOfDenominatorTypes.append(TH3NamePlus.split("_-_")[1].split("_")[2].split("-")[1])
    inFile.Close()
    listOfTH3Names.reverse()
    return set(listOfCalibrationScalesAndYAxes), set(listOfDenominatorTypes), listOfTH3Names

def resetIterators(counter,lst):
    try:
        return lst[counter]
    except IndexError:
        counter=0
        return lst[counter]

def complexF1JES(x,A,B,C,D,E,F,Z):
    return (A*pow(np.log(x),-2))+(B*pow(np.log(x),-1))+(C*pow(np.log(x),0))+(D*pow(np.log(x),1))+(E*pow(np.log(x),2))+(F*pow(np.log(x),3))+((-(A*pow(np.log(Z),-3)*-2/Z)-(B*pow(np.log(Z),-2)*-1/Z)-(C*pow(np.log(Z),-1)*0/Z)-(D*pow(np.log(Z),0)*1/Z)-(E*pow(np.log(Z),1)*2/Z)-(F*pow(np.log(Z),2)*3/Z))/(4*pow(np.log(Z),3)/Z))*pow(np.log(x),4)
    
def polyLog(x,a4,a3,a2,a1,am1,am2,a0):
    return a4*np.log(x)**4 + a3*np.log(x)**3 + a2*np.log(x)**2 + a1*np.log(x)**1 + a0*np.log(x)**0 + am1*np.log(x)**(-1) + am2*np.log(x)**(-2)

def polyLog_first_derivative(x,a4,a3,a2,a1,am1,am2):
    return ( 4*a4*np.log(x)**3 + 3*a3*np.log(x)**2 +2*a2*np.log(x)**1 + a1 - am1*np.log(x)**-2 - 2*am2*np.log(x)**-3 )*x**-1

def polyLog_second_derivative(x,a4,a3,a2,a1,am1,am2):
    return -(4*a4*(np.log(x)-3)*np.log(x)**2)/x**2 - (3*a3*(np.log(x)-2)*np.log(x))/x**2 - (2*a2*(np.log(x)-1))/x**2 - a1/x**2 + 0 + (am1*(np.log(x) + 2))/(x**2*np.log(x)**3) + (2*am2*(np.log(x) + 3))/(x**2*np.log(x)**4)

def autoScale(axis,listOfData):
    listOfMinima=[]
    listOfMaxima=[]
    for currentList in listOfData:
        listOfMinima.append(currentList)
        listOfMaxima.append(currentList)
    minimum=min(listOfMinima)
    maximum=max(listOfMaxima)
    difference=np.abs(minimum-maximum)
    axis.set_ylim(minimum-0.01*difference,maximum-0.95*difference)

def justPlot(pdf,purePath,plot,setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names,currentSlice,printOrPlot):
    pp = plotDict["plotParameters"][plot[1]]
    markers = ["o","^",">","v"]
    colors = ["black","crimson","dodgerblue","darkorange"]#,"forestgreen","violet","darkcyan"]
    DataOrMC = isItDataOrMC()
    #DataOrMC = "Data"
    OnlineOrOffline = isItOnlineOrOffline()
    f, ax = plt.subplots(figsize=(8, 6),sharex=True)
    
    iColors = 0
    iMarkers = 0
    
    denominatorType = plot[0]
    projectionAxisUnit = plot[1]
    #print(listOfTH3Names)

    for TH3Name in listOfTH3Names:
        if(TH3Name.find("_-_"+projectionAxisUnit+"_-_")==-1):
            continue
        print("TH3 Name:",TH3Name)
        inFile = np.load(plotDict["rootFilePath"].split(".root")[0]+"_-_scaled_"+TH3Name+"_-_"+str(currentSlice[0])+":"+str(currentSlice[1])+".npz")
        print(plotDict["rootFilePath"].split(".root")[0]+"_-_"+TH3Name+"_-_"+str(currentSlice[0])+":"+str(currentSlice[1])+".npz")
        x=inFile['x']
        x_error=inFile['xError']
        y=inFile['y']
        y_error=inFile['yError']
        entries=inFile['entries']
        my_label=getLabel(TH3Name)
        ax.errorbar(x, y, yerr=y_error, xerr=x_error,
                    linestyle='None',
                    marker=resetIterators(iMarkers,markers),
                    color=resetIterators(iColors,colors),
                    markersize=2,
                    linewidth=0.5,
                    label=my_label)
                    
        # Legend
        leg = ax.legend(borderpad=0.5, loc=1, ncol=2, frameon=True,facecolor="white",framealpha=1)
        fileName=plotDict["rootFilePath"].split("/")[-1]
        dataType = fileName.split("_")[1]
        numerator = TH3Name.split("_-_")[1].split("_")[0].split("-")[0]
        leg._legend_box.align = "right"
        
        di=plotDict["datasetInfo"]
        if(DataOrMC=="MC"):
            leg.set_title("Online small-R jets: "+"$\eta$ = "+str(currentSlice)+", $y^{*}<0.6$")#+"\nFit range:["+str(round(x[0],0))+", "+str(round(x[-1],0))+"] GeV")
            
        elif(DataOrMC=="Data"):
            ax.set_xlabel(pp["xLabel"], ha='right', x=1.0)
            leg.set_title(di["Data"]["legendTitle1"]+" $\eta$ = "+str(currentSlice)+di["Data"]["legendTitle2"])

        # Apply ATLAS labels and ticks
        plt.sca(ax)
        plt.xticks(rotation=45)
        ax.grid()

        plt.sca(ax)
        plt.xticks(rotation=45)
        ax.set_axisbelow(True)
        ax.set_xticks([300,400,500,600,700,800,900,1000,2000,3000])
                    
        iColors+=1
        iMarkers+=1
        
        ax = plt.gca()
        ax.grid(True)
        ax.set_axisbelow(True)
        
        hep.atlas.text("Internal",ax=ax)
        #for entry in inFile['x']:
        #    print(entry)
        #break
        
    #plt.tight_layout()
    f.subplots_adjust(left=0.1, right=0.95, bottom=0.12, top=0.95)

    # Set limits and labels
    ax.set_xlim(pp["xMin"],pp["xMax"])
    ax.set_ylim(pp["yMin"],pp["yMax"])
    ax.set_ylabel(pp["yLabel"], ha='right', y=1.0)
    ax.set_xscale("log")

    tickList = [1,2,3,4,5,6,7,8,9,
    10,20,30,40,50,60,70,80,90,
    100,200,300,400,500,600,700,800,900,
    1000,2000,3000,4000,5000,6000,7000,8000,9000,
    10000]
    tickLabelList = [1,2,3,4,5,6,7,8,9,
    10,20,30,40,50,60,70,80,90,
    100,200,300,400,500,600,700,800,900,
    1000,2000,3000,4000,5000,6000,7000,8000,9000,
    10000]

    ax.set_xticks(tickList[tickList.index(pp["xMin"]):tickList.index(pp["xMax"])])
    ax.set_xticklabels(tickLabelList[tickLabelList.index(pp["xMin"]):tickLabelList.index(pp["xMax"])])

    if(printOrPlot=="print"):
        pdf.savefig()
        f.savefig(purePath+plotDict["rootFilePath"].split("/")[-1].split(".root")[0]+"_-_"+denominatorType+"_-_"+projectionAxisUnit+"_-_"+str(currentSlice[0])+":"+str(currentSlice[1])+".pdf")
    elif(printOrPlot=="plot"): f.savefig(purePath+plotDict["rootFilePath"].split("/")[-1].split(".root")[0]+"_-_"+denominatorType+"_-_"+projectionAxisUnit+"_-_"+str(currentSlice[0])+":"+str(currentSlice[1])+"_"+".pdf")
    
def leftSubPlot(TH3Name, inFile, ax1, pp, currentColor, currentMarker, projectionAxisUnit, currentSlice, denominatorType, DataOrMC, OnlineOrOffline, i):
    plotSingleTH3(TH3Name, inFile, ax1, pp, currentColor, currentMarker, projectionAxisUnit, currentSlice, denominatorType, DataOrMC, OnlineOrOffline, i)

def plotSingleTH3(TH3Name, inFile, ax1, pp, currentColor, currentMarker, projectionAxisUnit, currentSlice, denominatorType, DataOrMC, OnlineOrOffline,i):
    ax1.errorbar(inFile['x'], inFile['y'], yerr=inFile['yError'], xerr=inFile['xError'],
                linestyle='None',
                marker=currentMarker,
                color=currentColor,
                markersize=2,
                linewidth=0.5,
                label=getLabel(TH3Name))

    plotSingleMarker(TH3Name, i, inFile, ax1, currentColor, currentMarker, currentSlice)

    ax1.grid()
    
    # Set limits and labels 1
    ax1.set_xlim(pp["xMin"],pp["xMax"])
    ax1.set_ylim(pp["yMin"],pp["yMax"])
    ax1.set_ylabel(pp["yLabel"], ha='right', y=1.0)
    ax1.set_xscale("log")

    # Legend 1
    leg1 = ax1.legend(borderpad=0.5, frameon=False, loc=2)
    fileName=plotDict["rootFilePath"].split("/")[-1]
    dataType = fileName.split("_")[1]
    numerator = TH3Name.split("_-_")[1].split("_")[0].split("-")[0]
    numeratorType = TH3Name.split("_-_")[1].split("_")[0].split("-")[1]
    leg1._legend_box.align = "left" # Align legend title
    
    di=plotDict["datasetInfo"]

    if(DataOrMC=="MC"):
        ax1.set_xlabel(denominatorType+" $"+projectionAxisUnit+"$ "+"[GeV]", ha='right', x=1.0)
        leg1.set_title(OnlineOrOffline+" MC "+di["MC"]["legendTitle1"]+"\n$\eta$ = "+str(currentSlice)+di["MC"]["legendTitle2"])
        hep.atlas.text("Simulation Internal",ax=ax1)
        
    elif(DataOrMC=="Data"):
        ax1.set_xlabel(pp["xLabel"], ha='right', x=1.0)
        leg1.set_title(OnlineOrOffline+" data "+di["Data"]["legendTitle1"]+"\n$\eta$ = "+str(currentSlice)+di["Data"]["legendTitle2"])
        hep.atlas.text("Internal",ax=ax1)

def rightSubPlot(i, inFile, ax2, currentSlice, DataOrMC, OnlineOrOffline, TH3Name,pp):
    plotSingleTH1(i, inFile, ax2, currentSlice, DataOrMC, TH3Name)
    plotFit(i, inFile, ax2)
    # Set limits and labels 1
    ax2.set_xlim(0.5,1.5)
    ax2.set_xlabel(pp["yLabel"], ha='right', x=1.0)
    ax2.set_ylabel("Counts", ha='right', y=1.0)
    ax2.ticklabel_format(style='sci',axis='y',scilimits=(0.001,1e10))
        
    # Legend 2
    leg2 = ax2.legend(borderpad=0.5, frameon=False, loc=2)
    fileName=plotDict["rootFilePath"].split("/")[-1]
    dataType = fileName.split("_")[1]
    #print(fileName)
    #numerator = fileName.split("_")[2].split(".")[0]
    numarator = "Truth"
    leg2._legend_box.align = "left" # Align legend title
    
    di=plotDict["datasetInfo"]
    
    thingString = ""
    #for j in range(0,len(inFile['listOfTH1Content'][i][0])):
    #    entries = inFile['listOfTH1Content'][i][0][j]
    #    if entries != 0.0:
    #        #print("\n"+str(int(element))+" entry at: "+str(inFile['listOfTH1Content'][i][1][j]))
    #        thingString=thingString+"\n"+str(int(entries))+" entry with lowEdge: "+str(round(inFile['listOfTH1Content'][i][1][j],6))

    if(DataOrMC=="MC"):
        leg2.set_title(OnlineOrOffline+" MC "+di["MC"]["legendTitle1"]+"\n$\eta$ = "+str(currentSlice)+", "+"$p_T$ = ["+str(inFile['x'][i]-inFile['xError'][i])+", "+str(inFile['x'][i]+inFile['xError'][i])+"] GeV"+thingString)
        hep.atlas.text("Simulation Internal",ax=ax2)
        
    elif(DataOrMC=="Data"):
        leg2.set_title(OnlineOrOffline+" data "+di["MC"]["legendTitle1"]+"\n$\eta$ = "+str(currentSlice)+", "+"$p_T$ = ["+str(inFile['x'][i]-inFile['xError'][i])+", "+str(inFile['x'][i]+inFile['xError'][i])+"] GeV"+thingString)
        hep.atlas.text("Internal",ax=ax2)

def plotFit(i, inFile, ax2):
    p0 = inFile["listOfGaussians"][i][0]
    p1 = inFile["listOfGaussians"][i][1]
    p2 = inFile["listOfGaussians"][i][2]
    fitMin = inFile["listOfGaussians"][i][3]
    fitMax = inFile["listOfGaussians"][i][4]
    Chi2Ndof = inFile["listOfGaussians"][i][5]
    
    x = np.linspace(fitMin, fitMax, 100)
    y= p0*np.exp(-0.5*((x-p1)/p2)**2)
    
    ax2.plot(x,y,label="Fit", color="red")

def plotSingleTH1(i, inFile, ax2, currentSlice, DataOrMC, TH3Name):
    hep.histplot(inFile['listOfTH1Content'][i][0],inFile['listOfTH1Content'][i][1],yerr=inFile['listOfTH1Content'][i][2], edges=True, label=[getLabel(TH3Name)])
    
def plotSingleMarker(TH3Name, i, inFile, ax1, currentColor, currentMarker, currentSlice):
    ax1.errorbar(inFile['x'][i], inFile['y'][i], yerr=inFile['yError'][i], xerr=inFile['xError'][i],
        linestyle='None',
        marker=currentMarker,
        color="lime",
        markersize=2,
        linewidth=0.5,
        label=getLabel(TH3Name)+" at "+"$\eta$ = "+str(currentSlice)+", "+"$p_T$=["+str(inFile['x'][i]-inFile['xError'][i])+", "+str(inFile['x'][i]+inFile['xError'][i])+"] GeV")

def isItDataOrMC():
    if("MC" or "mc" in plotDict["rootFilePath"].split("/")[-1]): return "MC"
    elif("data" or "Data" or "DATA" in plotDict["rootFilePath"].split("/")[-1]): return "Data"
    else: "Cannot determine if it is Data or MC"
    
def isItOnlineOrOffline():
    if("Online" or "online" in plotDict["rootFilePath"].split("/")[-1]): return "Online"
    elif("Offline" or "offline" in plotDict["rootFilePath"].split("/")[-1]): return "Online"
    else: "Cannot determine if it is Online or Offline"

def justPrint(pdf,purePath,plot,setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names,currentSlice,printOrPlot):
    import ROOT
    
    # The various plotting parameters defined in the config
    pp = plotDict["plotParameters"][plot[1]]

    # Create subplot figure in 800x600 format
    w,h=plt.figaspect(600/1600)
    f, (ax1,ax2) = plt.subplots(1,2,figsize=(w,h))
    
    # Colors, markers and their respective iterators for changing the color of each TH3
    markers = ["o","^",">","v","<"]
    colors = ["black","crimson","dodgerblue","darkorange","forestgreen","violet","darkcyan"]
    iColors = 0
    iMarkers = 0

    #Determine what type of plot this iteration is doing e.g. truth-mjj, Online-pT
    denominatorType = plot[0]
    projectionAxisUnit = plot[1]
    
    # Loop over the list of avaliable TH3s
    for TH3Name in listOfTH3Names:
    
        #Only consider the TH3s relevant to the plot this iteration is doing.
        current_denominatorType=TH3Name.split("_-_")[1].split("_")[2].split("-")[1]
        current_projectionAxisUnit=TH3Name.split("_-_")[2]
        if current_denominatorType != denominatorType or current_projectionAxisUnit != projectionAxisUnit:
            pass
        else:
        
            DataOrMC = isItDataOrMC()
            OnlineOrOffline = isItOnlineOrOffline()
        
            #Load the nupy data which was saved for this specific TH3
            print(TH3Name)
            inFile = np.load(plotDict["rootFilePath"].split(".root")[0]+"_-_"+TH3Name+"_-_"+str(currentSlice[0])+":"+str(currentSlice[1])+".npz",allow_pickle=True)
            
            #Get the current color and marker such that ot loops when the lists end
            currentColor = resetIterators(iColors,colors)
            currentMarker = resetIterators(iMarkers,markers)
            
            #Loop over the data ponts in the sliced and projected TH3. i.e loop over the number of fits/TH1s
            for i in range(0, len(inFile['x'])):
                
                # Plot the sliced and projected TH3 in the left subplot
                leftSubPlot(TH3Name, inFile, ax1, pp, currentColor, currentMarker, projectionAxisUnit, currentSlice, denominatorType, DataOrMC, OnlineOrOffline, i)
                
                # Make a marker for the current data point in the TH3
                #plotSingleMarker(TH3Name, i, inFile, ax1, currentColor, currentMarker)
                
                # Plot the fit and TH1 for this current TH3 data point in the right subplot
                rightSubPlot(i, inFile, ax2, currentSlice, DataOrMC, OnlineOrOffline, TH3Name,pp)
                
                #f.subplots_adjust(left=0.05, right=0.98, wspace=0.2)
                f.subplots_adjust(left=0.08, right=0.98, bottom=0.12, top=0.95)
                
                # Save the current figure in the multipage pdf and clear the axes for the next data point
                pdf.savefig()
                ax1.clear()
                ax2.clear()
                #break
            
            #Increment the color and marker iterators for the new TH3
            iColors+=1
            iMarkers+=1
            
            #plt.close()
            #break

def loopOverTH3(setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names,currentSlice,printOrPlot):
    purePath = "/".join(plotDict["rootFilePath"].split("/")[:-1])+"/"
    for plot in sorted(setOfCalibrationScalesAndYAxes):
        if printOrPlot=="print":
            with PdfPages(purePath+purePath.split("/")[-2]+"-jets_"+"over"+"_"+plot[0]+"-jets"+"_-_"+"function_of_"+plot[1]+".pdf") as pdf:
                justPrint(pdf,purePath,plot,setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names,currentSlice,printOrPlot)
        elif printOrPlot=="plot":
            justPlot(0,purePath,plot,setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names,currentSlice,printOrPlot)

def makePlots(printOrPlot):
    for currentSlice in plotDict["fitParameters"]["choosenSlices"]:
        setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names = getLists()
        loopOverTH3(setOfCalibrationScalesAndYAxes, setOfDenominatorTypes, listOfTH3Names,currentSlice,printOrPlot)

def makeTGraphs():
    inFile = ROOT.TFile.Open(plotDict["rootFilePath"])
    listOfKeys = inFile.GetListOfKeys()
    for key in listOfKeys:
        TH3Name = key.GetName()
        if TH3Name[0:9] != "scaled_h_":
        #if TH3Name[0:2] != "h_":
            continue
        print(TH3Name)
        TGraphOutputPath = plotDict["rootFilePath"].split(".root")[0]+"_-_"+TH3Name
        print("Fitting histogram: ",TGraphOutputPath)
        if inFile.Get(TH3Name).GetEntries()==0.0:
            print("WARNING: TH3 is empty!")
            continue
        
        responseFit_helper.TH3toTGraphs(
                                                                            plotDict["fitParameters"]["graphType"],
                                                                            inFile.Get(TH3Name),
                                                                            plotDict["fitParameters"]["slicingAxis"],
                                                                            plotDict["fitParameters"]["projectionAxis"],
                                                                            "x",
                                                                            plotDict["fitParameters"]["choosenSlices"],
                                                                            plotDict["fitParameters"]["projectionRebinWidth"],
                                                                            TGraphOutputPath,
                                                                            nSigmaForFit,
                                                                            fitOptString,
                                                                            TH3Name)
    inFile.Close()

def getBinning():
    print("hello")

#------------------------------------- MAIN --------------------------------------#
if sys.argv[1] == "fit":
    import ROOT
    import responseFit_helper
    #JES_BalanceFitter configuration
    nSigmaForFit = 1.3 #value taken from DeriveJetScales config settings
    fitOptString = "RESQ" #R = Use the Range specified in the function range; E= Perform better Errors estimation using Minos technique; Q = Quiet mode (minimum printing); S= The result of the fit is returned in the TFitResultPtr
    for path in plotDict["rootFilePaths"]:
        plotDict["rootFilePath"]=path
        makeTGraphs()

elif sys.argv[1] == "plot":
    for path in plotDict["rootFilePaths"]:
        plotDict["rootFilePath"]=path
        makePlots(sys.argv[1])

elif sys.argv[1] == "print":
    for path in plotDict["rootFilePaths"]:
        plotDict["rootFilePath"]=path
        makePlots(sys.argv[1])

elif sys.argv[1] == "binning":
    getBinning()
elif sys.argv[1] == "print_fit":
    printFit("x",["A","B","C","D","E","F","Z"],-2,4)
