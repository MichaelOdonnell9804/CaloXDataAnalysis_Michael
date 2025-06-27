import sys
sys.path.append("CMSPLOTS")  # noqa
import ROOT
from myFunction import DrawHistos
from utils.channel_map import buildDRSBoards, buildFERSBoards, buildTimeReferenceChannels, buildHodoTriggerChannels, buildHodoPosChannels
from utils.utils import number2string
from utils.html_generator import generate_html
from utils.validateMap import DrawFERSBoards, DrawDRSBoards
from runNumber import runNumber

print("Start running script")
ROOT.gROOT.SetBatch(True)

DRSBoards = buildDRSBoards(run=runNumber)
FERSBoards = buildFERSBoards(run=runNumber)
time_reference_channels = buildTimeReferenceChannels(run=runNumber)
hodo_trigger_channels = buildHodoTriggerChannels(run=runNumber)
hodo_pos_channels = buildHodoPosChannels(run=runNumber)


rootdir = f"root/Run{runNumber}/"
outdir = f"plots/Run{runNumber}/"


def makeFERS1DPlots():
    plots = []

    infile_name = f"{rootdir}fers_all_channels_1D.root"
    infile = ROOT.TFile(infile_name, "READ")
    outdir_plots = outdir + "/FERS_1D"
    for _, FERSBoard in FERSBoards.items():
        boardNo = FERSBoard.boardNo
        for iTowerX, iTowerY in FERSBoard.GetListOfTowers():
            sTowerX = number2string(iTowerX)
            sTowerY = number2string(iTowerY)

            hist_C_name = f"hist_FERS_Board{boardNo}_Cer_{sTowerX}_{sTowerY}"
            hist_S_name = f"hist_FERS_Board{boardNo}_Sci_{sTowerX}_{sTowerY}"
            hist_C = infile.Get(hist_C_name)
            hist_S = infile.Get(hist_S_name)
            if not hist_C or not hist_S:
                print(
                    f"Warning: Histograms {hist_C_name} or {hist_S_name} not found in {infile_name}")
                continue

            extraToDraw = ROOT.TPaveText(0.20, 0.65, 0.60, 0.90, "NDC")
            extraToDraw.SetTextAlign(11)
            extraToDraw.SetFillColorAlpha(0, 0)
            extraToDraw.SetBorderSize(0)
            extraToDraw.SetTextFont(42)
            extraToDraw.SetTextSize(0.04)
            extraToDraw.AddText(
                f"Board: {FERSBoard.boardNo}")
            extraToDraw.AddText(f"Tower X: {iTowerX}")
            extraToDraw.AddText(f"Tower Y: {iTowerY}")
            extraToDraw.AddText(
                f"Cer Channel: {FERSBoard.GetChannelByTower(iTowerX, iTowerY, isCer=True).channelNo}")
            extraToDraw.AddText(
                f"Sci Channel: {FERSBoard.GetChannelByTower(iTowerX, iTowerY, isCer=False).channelNo}")

            output_name = f"Energy_Board{boardNo}_iTowerX{sTowerX}_iTowerY{sTowerY}"
            DrawHistos([hist_C, hist_S], ["Cer", "Sci"], 0, 1000, "Energy HG", 1, 1e5, "Counts",
                       output_name,
                       dology=True, drawoptions="HIST", mycolors=[2, 4], addOverflow=True, addUnderflow=True, extraToDraw=extraToDraw,
                       outdir=outdir_plots, runNumber=runNumber)

            plots.append(output_name + ".png")

    output_html = f"html/Run{runNumber}/FERS_1D/index.html"
    generate_html(plots, outdir_plots,
                  output_html=output_html)
    return output_html


# 2D FERS histograms, hg vs lg
def makeFERS2DPlots():
    plots = []
    outdir_plots = outdir + "/FERS_2D"
    infile_name = f"{rootdir}/fers_all_channels_2D.root"
    infile = ROOT.TFile(infile_name, "READ")
    for _, FERSBoard in FERSBoards.items():
        boardNo = FERSBoard.boardNo
        for iTowerX, iTowerY in FERSBoard.GetListOfTowers():
            sTowerX = number2string(iTowerX)
            sTowerY = number2string(iTowerY)
            for var in ["Cer", "Sci"]:
                chan = FERSBoard.GetChannelByTower(
                    iTowerX, iTowerY, isCer=(var == "Cer"))
                hist_name = f"hist_FERS_Board{boardNo}_{var}_{sTowerX}_{sTowerY}_hg_vs_lg"
                hist = infile.Get(hist_name)

                extraToDraw = ROOT.TPaveText(0.20, 0.70, 0.60, 0.90, "NDC")
                extraToDraw.SetTextAlign(11)
                extraToDraw.SetFillColorAlpha(0, 0)
                extraToDraw.SetBorderSize(0)
                extraToDraw.SetTextFont(42)
                extraToDraw.SetTextSize(0.04)
                extraToDraw.AddText(
                    f"Board: {FERSBoard.boardNo}")
                extraToDraw.AddText(f"Tower X: {iTowerX}")
                extraToDraw.AddText(f"Tower Y: {iTowerY}")
                extraToDraw.AddText(f"{var} Channel: {chan.channelNo}")

                output_name = f"FERS_Board{boardNo}_{var}_{sTowerX}_{sTowerY}_hg_vs_lg"
                DrawHistos([hist], f"", 0, 9000, "HG", 0, 1500, "LG",
                           output_name,
                           dology=False, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True, extraToDraw=extraToDraw,
                           outdir=outdir_plots, addOverflow=True, runNumber=runNumber)
                plots.append(output_name + ".png")
    output_html = f"html/Run{runNumber}/FERS_2D/index.html"
    generate_html(plots, outdir_plots, plots_per_row=4,
                  output_html=output_html)
    return output_html


# FERS output vs event
def trackFERSPlots():
    plots = []
    outdir_plots = outdir + "/FERS_vs_Event"
    infile_name = f"{rootdir}/fers_all_channels_2D_vs_event.root"
    infile = ROOT.TFile(infile_name, "READ")
    for _, FERSBoard in FERSBoards.items():
        boardNo = FERSBoard.boardNo
        for iTowerX, iTowerY in FERSBoard.GetListOfTowers():
            sTowerX = number2string(iTowerX)
            sTowerY = number2string(iTowerY)
            for var in ["Cer", "Sci"]:
                chan = FERSBoard.GetChannelByTower(
                    iTowerX, iTowerY, isCer=(var == "Cer"))
                hist_name = f"hist_FERS_Board{boardNo}_{var}_vs_Event_{sTowerX}_{sTowerY}"
                hist = infile.Get(hist_name)

                if not hist:
                    print(
                        f"Warning: Histogram {hist_name} not found in {infile_name}")
                    continue

                extraToDraw = ROOT.TPaveText(0.20, 0.70, 0.60, 0.90, "NDC")
                extraToDraw.SetTextAlign(11)
                extraToDraw.SetFillColorAlpha(0, 0)
                extraToDraw.SetBorderSize(0)
                extraToDraw.SetTextFont(42)
                extraToDraw.SetTextSize(0.04)
                extraToDraw.AddText(
                    f"Board: {FERSBoard.boardNo}")
                extraToDraw.AddText(f"Tower X: {iTowerX}")
                extraToDraw.AddText(f"Tower Y: {iTowerY}")
                extraToDraw.AddText(f"{var} Channel: {chan.channelNo}")

                nEvents = hist.GetXaxis().GetXmax()

                output_name = f"FERS_Board{boardNo}_{var}_{sTowerX}_{sTowerY}_vs_Event"
                DrawHistos([hist], "", 0, nEvents, "Event", 1, 1e5, f"{var} Energy HG",
                           output_name,
                           dology=True, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True,
                           extraToDraw=extraToDraw,
                           outdir=outdir_plots, addOverflow=True, runNumber=runNumber)
                plots.append(output_name + ".png")
    output_html = f"html/Run{runNumber}/FERS_vs_Event/index.html"
    generate_html(plots, outdir_plots, plots_per_row=4,
                  output_html=output_html)
    return output_html


# 1D histograms for DRS variables
def makeDRS1DPlots():
    plots = []
    infile_name = f"{rootdir}/drs_all_channels_1D.root"
    infile = ROOT.TFile(infile_name, "READ")
    for _, DRSBoard in DRSBoards.items():
        boardNo = DRSBoard.boardNo
        for iTowerX, iTowerY in DRSBoard.GetListOfTowers():
            sTowerX = number2string(iTowerX)
            sTowerY = number2string(iTowerY)

            chan_Cer = DRSBoard.GetChannelByTower(iTowerX, iTowerY, isCer=True)
            chan_Sci = DRSBoard.GetChannelByTower(
                iTowerX, iTowerY, isCer=False)

            hist_C_name = f"hist_DRS_Board{boardNo}_Cer_{sTowerX}_{sTowerY}"
            hist_S_name = f"hist_DRS_Board{boardNo}_Sci_{sTowerX}_{sTowerY}"
            hist_C = infile.Get(hist_C_name)
            hist_S = infile.Get(hist_S_name)
            if not hist_C or not hist_S:
                print(
                    f"Warning: Histograms {hist_C_name} or {hist_S_name} not found in {infile_name}")
                continue

            extraToDraw = ROOT.TPaveText(0.20, 0.65, 0.60, 0.90, "NDC")
            extraToDraw.SetTextAlign(11)
            extraToDraw.SetFillColorAlpha(0, 0)
            extraToDraw.SetBorderSize(0)
            extraToDraw.SetTextFont(42)
            extraToDraw.SetTextSize(0.04)
            extraToDraw.AddText(f"Board: {DRSBoard.boardNo}")
            extraToDraw.AddText(f"iTowerX: {iTowerX}")
            extraToDraw.AddText(f"iTowerY: {iTowerY}")
            extraToDraw.AddText(
                f"Cer Channel: ({chan_Cer.groupNo}, {chan_Cer.channelNo})")
            extraToDraw.AddText(
                f"Sci Channel: ({chan_Sci.groupNo}, {chan_Sci.channelNo})")

            output_name = f"DRS_Variable_Board{boardNo}_iTowerX{sTowerX}_iTowerY{sTowerY}"
            outdir_plots = outdir + "/DRS_1D"
            DrawHistos([hist_C, hist_S], ["Cer", "Sci"], 1400, 2500, "DRS Output", 1, 1e12, "Counts",
                       output_name,
                       dology=True, drawoptions="HIST", mycolors=[2, 4], addOverflow=True, addUnderflow=True, extraToDraw=extraToDraw,
                       legendPos=(0.60, 0.78, 0.90, 0.68),
                       outdir=outdir_plots)
            plots.append(output_name + ".png")

    output_html = f"html/Run{runNumber}/DRS_1D/index.html"
    generate_html(plots, outdir_plots,
                  output_html=output_html)
    return output_html


# DRS vs TS
def makeDRS2DPlots(doSubtractMedian=False):
    suffix = ""
    ymin = -50
    ymax = 50
    if doSubtractMedian:
        suffix = "_subtractMedian"
        ymin = -20
        ymax = 40
    plots = []
    outdir_plots = outdir + "/DRS_vs_TS"
    infile_name = f"{rootdir}/drs_all_channels_2D.root"
    infile = ROOT.TFile(infile_name, "READ")
    for _, DRSBoard in DRSBoards.items():
        boardNo = DRSBoard.boardNo
        for iTowerX, iTowerY in DRSBoard.GetListOfTowers():
            sTowerX = number2string(iTowerX)
            sTowerY = number2string(iTowerY)
            for var in ["Cer", "Sci"]:
                chan = DRSBoard.GetChannelByTower(
                    iTowerX, iTowerY, isCer=(var == "Cer"))
                hist_name = f"hist_DRS_Board{boardNo}_{var}_vs_TS_{sTowerX}_{sTowerY}{suffix}"
                hist = infile.Get(hist_name)
                output_name = f"DRS_{var}_vs_TS_{sTowerX}_{sTowerY}{suffix}"
                plots.append(output_name + ".png")

                if not hist:
                    print(
                        f"Warning: Histogram {hist_name} not found in {infile_name}")
                    continue

                value_mean = hist.GetMean(2)

                extraToDraw = ROOT.TPaveText(0.20, 0.75, 0.60, 0.90, "NDC")
                extraToDraw.SetTextAlign(11)
                extraToDraw.SetFillColorAlpha(0, 0)
                extraToDraw.SetBorderSize(0)
                extraToDraw.SetTextFont(42)
                extraToDraw.SetTextSize(0.04)
                extraToDraw.AddText(
                    f"B: {DRSBoard.boardNo}, G: {chan.groupNo}, C: {chan.channelNo}")
                extraToDraw.AddText(f"iTowerX: {iTowerX}")
                extraToDraw.AddText(f"iTowerY: {iTowerY}")

                DrawHistos([hist], "", 0, 1024, "Time Slice", value_mean + ymin, value_mean + ymax, f"DRS Output",
                           output_name,
                           dology=False, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True,
                           extraToDraw=extraToDraw,
                           outdir=outdir_plots, extraText=var, runNumber=runNumber, addOverflow=True)
    output_html = f"html/Run{runNumber}/DRS_vs_TS{suffix}/index.html"
    generate_html(plots, outdir_plots, plots_per_row=2,
                  output_html=output_html)
    return output_html


# DRS mean vs event
def trackDRSPlots():
    plots = []
    infile_name = f"{rootdir}/drs_all_channels_2D_vs_event.root"
    infile = ROOT.TFile(infile_name, "READ")
    outdir_plots = outdir + "/DRS_vs_Event"
    for _, DRSBoard in DRSBoards.items():
        boardNo = DRSBoard.boardNo
        for iTowerX, iTowerY in DRSBoard.GetListOfTowers():
            sTowerX = number2string(iTowerX)
            sTowerY = number2string(iTowerY)
            for var in ["Cer", "Sci"]:
                chan = DRSBoard.GetChannelByTower(
                    iTowerX, iTowerY, isCer=(var == "Cer"))
                hist_name = f"hist_DRS_Board{boardNo}_{var}_vs_Event_{sTowerX}_{sTowerY}"
                hist = infile.Get(hist_name)

                if not hist:
                    print(
                        f"Warning: Histogram {hist_name} not found in {infile_name}")
                    continue

                extraToDraw = ROOT.TPaveText(0.20, 0.70, 0.60, 0.90, "NDC")
                extraToDraw.SetTextAlign(11)
                extraToDraw.SetFillColorAlpha(0, 0)
                extraToDraw.SetBorderSize(0)
                extraToDraw.SetTextFont(42)
                extraToDraw.SetTextSize(0.04)
                extraToDraw.AddText(f"Board: {DRSBoard.boardNo}")
                extraToDraw.AddText(f"iTowerX: {iTowerX}")
                extraToDraw.AddText(f"iTowerY: {iTowerY}")
                extraToDraw.AddText(f"{var} Group: {chan.groupNo}")
                extraToDraw.AddText(f"{var} Channel: {chan.channelNo}")

                nEvents = hist.GetXaxis().GetXmax()

                output_name = f"DRS_Board{boardNo}_{var}_{sTowerX}_{sTowerY}_vs_Event"
                DrawHistos([hist], "", 0, nEvents, "Event", 1400, 2300, f"{var} Mean",
                           output_name,
                           dology=False, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True,
                           extraToDraw=extraToDraw,
                           outdir=outdir_plots, addOverflow=True, runNumber=runNumber)
                plots.append(output_name + ".png")
    output_html = f"html/Run{runNumber}/DRS_vs_Event/index.html"
    generate_html(plots, outdir_plots, plots_per_row=4,
                  output_html=output_html)
    return output_html


# time reference
def compareTimeReferencePlots(doSubtractMedian=False):
    suffix = ""
    ymin = 500
    ymax = 2500
    if doSubtractMedian:
        suffix = "_subtractMedian"
        ymin = -1500
        ymax = 500
    plots = []
    infile_name = f"{rootdir}/time_reference_channels.root"
    infile = ROOT.TFile(infile_name, "READ")
    outdir_plots = outdir + "/TimeReference"
    for chan_name in time_reference_channels:
        hist_name = f"hist_{chan_name}{suffix}"
        hist = infile.Get(hist_name)
        if not hist:
            print(f"Warning: Histogram {hist_name} not found in {infile_name}")
            continue
        extraToDraw = ROOT.TPaveText(0.20, 0.70, 0.60, 0.90, "NDC")
        extraToDraw.SetTextAlign(11)
        extraToDraw.SetFillColorAlpha(0, 0)
        extraToDraw.SetBorderSize(0)
        extraToDraw.SetTextFont(42)
        extraToDraw.SetTextSize(0.04)
        extraToDraw.AddText(f"{chan_name}")
        output_name = f"TimeReference_{chan_name}{suffix}"
        DrawHistos([hist], "", 0, 1024, "Time Slice", ymin, ymax, "Counts",
                   output_name,
                   dology=False, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True,
                   extraToDraw=extraToDraw,
                   outdir=outdir_plots, addOverflow=True, runNumber=runNumber)
        plots.append(output_name + ".png")

    output_html = f"html/Run{runNumber}/TimeReference{suffix}/index.html"
    generate_html(plots, outdir_plots, plots_per_row=2,
                  output_html=output_html)
    return output_html


# trigger
def compareHodoTriggerPlots(doSubtractMedian=False):
    suffix = ""
    ymin = 500
    ymax = 2500
    if doSubtractMedian:
        suffix = "_subtractMedian"
        ymin = -1500
        ymax = 500
    plots = []
    infile_name = f"{rootdir}/hodo_trigger_channels.root"
    infile = ROOT.TFile(infile_name, "READ")
    outdir_plots = outdir + "/HodoTrigger"
    for chan_name in hodo_trigger_channels:
        hist_name = f"hist_{chan_name}{suffix}"
        hist = infile.Get(hist_name)
        if not hist:
            print(f"Warning: Histogram {hist_name} not found in {infile_name}")
            continue
        extraToDraw = ROOT.TPaveText(0.20, 0.70, 0.60, 0.90, "NDC")
        extraToDraw.SetTextAlign(11)
        extraToDraw.SetFillColorAlpha(0, 0)
        extraToDraw.SetBorderSize(0)
        extraToDraw.SetTextFont(42)
        extraToDraw.SetTextSize(0.04)
        extraToDraw.AddText(f"{chan_name}")
        output_name = f"HodoTrigger_{chan_name}{suffix}"
        DrawHistos([hist], "", 0, 1024, "Time Slice", ymin, ymax, "Counts",
                   output_name,
                   dology=False, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True,
                   extraToDraw=extraToDraw,
                   outdir=outdir_plots, addOverflow=True, runNumber=runNumber)
        plots.append(output_name + ".png")

    output_html = f"html/Run{runNumber}/HodoTrigger{suffix}/index.html"
    generate_html(plots, outdir_plots, plots_per_row=2,
                  output_html=output_html)
    return output_html

# hodo position


def compareHodoPosPlots(doSubtractMedian=False):
    suffix = ""
    ymin = 500
    ymax = 2500
    if doSubtractMedian:
        suffix = "_subtractMedian"
        ymin = -1500
        ymax = 500
    plots = []
    infile_name = f"{rootdir}/hodo_pos_channels.root"
    infile = ROOT.TFile(infile_name, "READ")
    outdir_plots = outdir + "/HodoPos"
    print(f"hodo_pos_channels: {hodo_pos_channels}")
    for board, channels in hodo_pos_channels.items():
        for chan_name in channels:
            hist_name = f"hist_{chan_name}{suffix}"
            hist = infile.Get(hist_name)
            if not hist:
                print(
                    f"Warning: Histogram {hist_name} not found in {infile_name}")
                continue
            extraToDraw = ROOT.TPaveText(0.20, 0.70, 0.60, 0.90, "NDC")
            extraToDraw.SetTextAlign(11)
            extraToDraw.SetFillColorAlpha(0, 0)
            extraToDraw.SetBorderSize(0)
            extraToDraw.SetTextFont(42)
            extraToDraw.SetTextSize(0.04)
            extraToDraw.AddText(f"{chan_name}")
            output_name = f"HodoPos_{chan_name}{suffix}"
            DrawHistos([hist], "", 0, 1024, "Time Slice", ymin, ymax, "Counts",
                       output_name,
                       dology=False, drawoptions="COLZ", doth2=True, zmin=1, zmax=1e4, dologz=True,
                       extraToDraw=extraToDraw,
                       outdir=outdir_plots, addOverflow=True, runNumber=runNumber)
            plots.append(output_name + ".png")

    output_html = f"html/Run{runNumber}/HodoPos{suffix}/index.html"
    generate_html(plots, outdir_plots, plots_per_row=2,
                  output_html=output_html)
    return output_html


if __name__ == "__main__":
    output_htmls = {}

    # validate DRS and FERS boards
    output_htmls["fers mapping"] = DrawFERSBoards(run=runNumber)
    output_htmls["drs mapping"] = DrawDRSBoards(run=runNumber)

    output_htmls["fers 1D"] = makeFERS1DPlots()
    # makeDRS2DPlots()
    output_htmls["drs 2D"] = makeDRS2DPlots(doSubtractMedian=True)

    output_htmls["time reference"] = compareTimeReferencePlots(True)
    output_htmls["hodo trigger"] = compareHodoTriggerPlots(True)
    output_htmls["hodo pos"] = compareHodoPosPlots(True)

    for key, value in output_htmls.items():
        print(f"{key} plots can be viewed at: {value}")

    print("All plots generated successfully.")
