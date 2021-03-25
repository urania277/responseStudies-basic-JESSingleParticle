import ROOT
import sys
import os

pathDict={}

def iterate(directory,currentSlice):
    for entry in os.scandir(directory):
        #print(entry.path)
        if entry.path.split(".")[1][0:4]=="3647":
            currentSlice = entry.path.split(".")[1][4:6]
            try:
                if(pathDict[currentSlice]):
                    pass
                else:
                    pathDict[currentSlice]={}
            except KeyError:
                pathDict[currentSlice]={}
        try:
            if entry.path.split("/")[-2]=="data-metadata" and entry.path.split("/")[-1]==("inputFileList_mc16_13TeV.3647"+currentSlice+"_mc16d_p4006.root"):
                #print(currentSlice,"metadata at:",entry.path)
                pathDict[currentSlice]["metadata"]=entry.path
            if entry.path.split("/")[-1].split("_")[0]=="hist-inputFileList":
                #print(currentSlice,"TH3s     at:",entry.path)
                pathDict[currentSlice]["TH3s"]=entry.path
        except IndexError:
            pass
        if os.path.isdir(entry.path):
            iterate(entry.path,currentSlice)
        

def main():
    iterate(str(sys.argv[1]),"")
    print("\nPath dictionary complete\n")
    for slicee in pathDict:
        print("\nJZ",slicee)
        for filee in pathDict[slicee]:
            print(filee,"at:",pathDict[slicee][filee])
    #pathDict["06"]["metadata"]=1
    #print(pathDict)
    for current_slice in pathDict:
        current_metadata_file = ROOT.TFile.Open(pathDict[current_slice]["metadata"])
        current_SumOfWeights = current_metadata_file.Get("MetaData_EventCount").GetBinContent(3)
        print(current_slice,":",current_SumOfWeights)
        current_histogram_file = ROOT.TFile.Open(pathDict[current_slice]["TH3s"],"UPDATE")
        current_histogram_file.cd()
        listOfKeys = current_histogram_file.GetListOfKeys()
        for key in listOfKeys:
            current_histogram_name = key.GetName()
            if current_histogram_name[0]!="h": continue
            current_histogram = current_histogram_file.Get(current_histogram_name)
            current_histogram_clone = current_histogram.Clone()
            current_histogram_clone.Scale(1/current_SumOfWeights)
            current_histogram_clone.SetName("scaled_"+current_histogram_name)
            current_histogram_clone.Write("scaled_"+current_histogram_name,3)

        current_metadata_file.Close()
        current_histogram_file.Close()

    
if __name__ == "__main__":
    main()
