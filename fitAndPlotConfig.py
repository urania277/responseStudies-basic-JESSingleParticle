def getPlotDict():
  plotDict={
    "rootFilePath":"",
    "rootFilePaths"   :[
                        #"/home/pekman/TLASteeringFullRun2/output/v12/merged_mc16d_mjj_v12.root"
                        "/home/pekman/TLA/TH3Files/v14/merged_mc16d_mjj_v14.root"
                        #"/home/pekman/TLASteeringFullRun2/output/cut_v2_calibrationSmoothness/scaledAndMerged_cut_v2_hist_TLA_CalibrationSmoothness_MC_HLT_TRUTH_PT_-_grid.root",#MC pT
                        #"/home/pekman/TLASteeringFullRun2/output/aurora_mjj_tlaCut_v5/scaledAndMerged_smooth_aurora_MC.root",#MC mjj
                        #"/home/pekman/TLASteeringFullRun2/output/dirtyData/data_dirty_aurora.root",
                        #"/home/pekman/TLASteeringFullRun2/output/online_over_offline/online_over_offline_data_period_F_aurora.root"
                       ],
    "fitParameters" : {
                      "graphType"             :"response",
                      "slicingAxis"           :"z",
                      "projectionAxis"        :"y",
                      "choosenSlices"         :[[-2.8,2.8]],
                      "projectionRebinWidth"  :1,
                      },
    "plotParameters": {
                      "pt": {
                            "xMin":50,
                            "xMax":4000,
                            "yMin":0.98,
                            "yMax":1.10,
                            "xLabel":  "Offline jet $p_{T}$ [GeV]",
                            "yLabel":  "$p_{T}$ Online/Offline",
                            },
                      "mjj": {
                            "xMin":400,
                            "xMax":2000,
                            #"yMin":0.99,
                            "yMin":0.7,
                            #"yMax":1.01,
                            "yMax":1.1,
                            "xLabel":  "Truth mjj [GeV]",
                            "yLabel":  "$mjj$ Response",
                            }
                      },
    "datasetInfo":    {
                      "Data"  :  {
                                 "legendTitle1": "Small-R jet response at:",
                                 "legendTitle2": ", y*<0.6\n2016 data period F",
                                 },
                      "MC"    :  {
                                 "legendTitle1": "Small-R jet response at:",
                                 "legendTitle2": ", y*<0.6\nmc16d, all $pT$ slices\nAll weights: Applied",
                                 },
                      },
  }
  return plotDict
