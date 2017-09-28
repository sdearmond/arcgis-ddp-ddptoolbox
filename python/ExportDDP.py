import arcpy, os, string

try:

    #Read input parameters from script tool
    pageLst = string.split(arcpy.GetParameterAsText(0), ";")
    outPath = arcpy.GetParameterAsText(1)
    outType = arcpy.GetParameterAsText(2)
    convMarkersOpt = arcpy.GetParameterAsText(3)
    overwrite = arcpy.GetParameterAsText(4)

    #This is a function to determine the output path
    def makePath(pageName, fileExt):
        #This cleans the filename of characters that might confuse the operating system
        for i in range(len(pageName)):
            if pageName[i].upper() not in ("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"):
                pageName[i] == "_"
        newPath = os.path.join(outPath, pageName + fileExt)
        if overwrite == "false":
            if os.path.exists(newPath):
                counter = 1
                while os.path.exists(newPath) == True:
                    newPath = os.path.join(outPath, pageName + "_" + str(counter) + fileExt)
                    counter = counter + 1
        return newPath


    #Reference the map and the data driven page object
    mxd = arcpy.mapping.MapDocument("CURRENT")
    ddp = mxd.dataDrivenPages

    #Export pages
    arcpy.AddMessage("   Exporting pages:")
    for myPage in pageLst: #This bit goes through each name in the page list and...

        #This removes quote marks out of the page name
        if myPage[0] == "'" and myPage[-1] == "'":
            myPage = myPage[1:-1]

        arcpy.AddMessage("      " + str(myPage))

        ddp.currentPageID = ddp.getPageIDFromName(myPage)

        if outType == "png":
            PNGpath = makePath(myPage,".png")
            arcpy.mapping.ExportToPNG(mxd, PNGpath, resolution = 300)
        if outType == "eps":
            EPSpath = makePath(myPage,".eps")
            arcpy.mapping.ExportToEPS(mxd, EPSpath, resolution = 600, ps_lang_level = 2, image_compression = "RLE", picture_symbol = "VECTORIZE_BITMAP", convert_markers = convMarkersOpt)
        if outType in ("pdf", "geopdf"):
            PDFpath = makePath(myPage,".pdf")
            arcpy.mapping.ExportToPDF(mxd, PDFpath, image_compression = "DEFLATE", convert_markers = convMarkersOpt, resolution=300)
        if outType == "bmp":
            BMPpath = makePath(myPage,".bmp")
            arcpy.mapping.ExportToBMP(mxd, BMPpath, resolution = 300)

except Exception as e:
    arcpy.AddMessage(e.message)



