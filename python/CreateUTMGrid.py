#-------------------------------------------------------------------------------
# Name:        CreateMeasuredGrid
# Purpose:     Creates a grid of polylines at a specified interval
#
# Author:      shannon
#
# Created:     19/08/2013
#-------------------------------------------------------------------------------

import arcpy, os

gridInt = long(arcpy.GetParameterAsText(0))
outDir = arcpy.GetParameterAsText(1)

try:

    if arcpy.Exists(os.path.join(outDir, "MeasuredGrid.gdb")):
        arcpy.Delete_management(os.path.join(outDir, "MeasuredGrid.gdb"))

    mxd = arcpy.mapping.MapDocument("CURRENT")
    ddp = mxd.dataDrivenPages

    #Creates a new database to store the grid feature classes
    arcpy.AddMessage("   Creating new file geodatabase...")
    outDB = arcpy.CreateFileGDB_management(outDir, "MeasuredGrid.gdb")

    #Creates a new polyline feature class
    arcpy.AddMessage("   Creating polyline feature class...")
    outFCLines = arcpy.CreateFeatureclass_management(outDB, "GridLines", 'POLYLINE','','','', arcpy.Describe(ddp.indexLayer).spatialReference)
    arcpy.AddField_management(outFCLines,'dir','TEXT','','',10)
    for fld in ['Easting', 'Northing', 'GridInt']:
        arcpy.AddField_management(outFCLines,fld,'LONG')

    #This is a function to determine the grid interval (useful for scale dependancies)
    def getGridInt(myCoord):
        myInt = 0
        if myCoord%(gridInt*8) == 0:
            myInt = gridInt*8
        elif myCoord%(gridInt*4) == 0:
            myInt = gridInt*4
        elif myCoord%(gridInt*2) == 0:
            myInt = gridInt*2
        elif myCoord%gridInt == 0:
            myInt = gridInt
        return myInt

    #Let's make sure that the starting coords are rounded to the nearest specified grid interval
    def rounddown(x):
        return x if x % gridInt == 0 else x - gridInt - x % gridInt
    myExtent = ddp.indexLayer.getExtent()
    startingX = rounddown(myExtent.XMin)
    startingY = rounddown(myExtent.YMin)
    endX = rounddown(myExtent.XMax) + gridInt
    endY = rounddown(myExtent.YMax) + gridInt

    with arcpy.da.InsertCursor(outFCLines, ("SHAPE@", "Easting", "Northing", "dir", "GridInt")) as rows:

        arcpy.AddMessage("   Adding grid lines...")
        #Add the easting lines
        xFrom = startingX
        yFrom = startingY
        xTo = startingX
        yTo = endY + gridInt

        while (xFrom - gridInt) <= myExtent.XMax:
            array = arcpy.Array([arcpy.Point(xFrom, yFrom),arcpy.Point(xTo, yTo)])
            polyline = arcpy.Polyline(array)
            rows.insertRow((polyline,xFrom,0, "E", getGridInt(xFrom)))
            xFrom += gridInt
            xTo += gridInt


        #Add the northing lines
        xFrom = startingX
        yFrom = startingY
        xTo = endX + gridInt
        yTo = startingY

        while (yFrom - gridInt) <= myExtent.YMax:
            array = arcpy.Array([arcpy.Point(xFrom, yFrom),arcpy.Point(xTo, yTo)])
            polyline = arcpy.Polyline(array)
            rows.insertRow((polyline,0,yFrom,"N", getGridInt(yFrom)))
            yFrom += gridInt
            yTo += gridInt


    #Creating the points feature class (we'll use these to make the display coordinate labels around the map frame)
    arcpy.AddMessage("   Creating points feature class...")
    outFCPntsTemp = arcpy.Intersect_analysis([outFCLines, ddp.indexLayer], "in_memory/GridPointsMulti", "ALL", output_type="POINT")
    arcpy.AddMessage(arcpy.GetCount_management(outFCPntsTemp).getOutput(0))
    outFCPnts = arcpy.MultipartToSinglepart_management(outFCPntsTemp,os.path.join(outDir, "MeasuredGrid.gdb", "GridPoints"))
    arcpy.AddMessage(arcpy.GetCount_management(outFCPnts).getOutput(0))
    arcpy.AddField_management(outFCPnts,"PageOrientation","TEXT","",20)
    arcpy.AddXY_management(outFCPnts)


    #Determine top, bottom, left, and right points
    arcpy.AddMessage("   Setting label orientation...")
    pageLst = []
    with arcpy.da.SearchCursor(ddp.indexLayer,ddp.pageNameField.name) as rows:
        for row in rows:
            if row[0] not in pageLst:
                pageLst.append(row[0])


    #This part fill out some fields we'll use for label queries
    for myPage in pageLst:
        dirDict = {"N": ["POINT_X", "Left", "Right"], "E": ["POINT_Y", "Bottom", "Top"]}
        for dir in ['E','N']:
            qryStr = '"' + ddp.pageNameField.name + '" = \'' + str(myPage) + '\' AND "dir" = \'' + dir + '\''
            pntLyr = arcpy.MakeFeatureLayer_management(outFCPnts,"pntLyr",qryStr)
            coordLst = []
            with arcpy.da.SearchCursor(pntLyr, dirDict[dir][0]) as rows:
                for row in rows:
                    if row[0] not in coordLst:
                        coordLst.append(row[0])
            coordLst.sort()
            with arcpy.da.UpdateCursor(pntLyr, ["PageOrientation",dirDict[dir][0]]) as rows:
                for row in rows:
                    if row[1] == coordLst[0]:
                        row[0] = dirDict[dir][1]
                    else:
                        row[0] = dirDict[dir][2]

                    rows.updateRow(row)
    del pntLyr


    arcpy.AddField_management(outFCPnts,"Angle","SHORT")
    calcBlock = """def getAngle(orient):
        orientDict = {"Left": 270, "Right":90, "Top":0, "Bottom":0}
        return orientDict[orient] """
    arcpy.CalculateField_management(outFCPnts,"Angle","getAngle(!PageOrientation!)", "PYTHON", calcBlock)

    arcpy.AddMessage("   Done! You can now add the grid line and points from " + os.path.join(outDir, "MeasuredGrid.gdb") + " to your map.")
    del outDB, outFCLines, outFCPnts
except Exception as e:
    arcpy.AddWarning(e.message)

