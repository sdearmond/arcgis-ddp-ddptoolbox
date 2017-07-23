#-------------------------------------------------------------------------------
# Name:        Update Viewports to Data Frame Extent
# Purpose:     Updates the shape of a polygon layer used to control data-driven
#              pages. The shape of each feature will be adjusted to a rectangle
#              representing the data frame extent as per the current data-driven
#              page settings.
#
# Author:      shannon
#
# Created:     02/10/2013
# Copyright:   (c) shannon 2013
#-------------------------------------------------------------------------------
import arcpy, os

try:
    mxd = arcpy.mapping.MapDocument("CURRENT")
    ddp = mxd.dataDrivenPages

    #Let's make a backup in case we jack something up royally
    outputPath = os.path.dirname(ddp.indexLayer.dataSource)
    outputName = os.path.basename(ddp.indexLayer.dataSource)
    if "." in outputName:
        outputName = outputName.replace(".","_old.")
    else:
        outputName = outputName + "_old"

    #This bit makes sure the backup filename doesn't already exist
    while os.path.exists(os.path.join(outputPath, outputName)):
        fileCounter = 0
        outputName = outputName.replace("_old","_old" + str(fileCounter))

    backupFC = arcpy.Copy_management(ddp.indexLayer.dataSource, os.path.join(outputPath,outputName))
    arcpy.AddMessage("...Backing up original viewport layer")

    #Add a field to hold the scale
    fldLst = [f.name for f in arcpy.ListFields(ddp.indexLayer.dataSource)]
    if "DDP_Scale" not in fldLst:
        arcpy.AddField_management(ddp.indexLayer, "DDP_Scale", "LONG")

    #For each shape in the viewport feature class...
    counter = 1
    while counter <= ddp.pageCount:
        ddp.currentPageID = counter
        arcpy.AddMessage("...Updating page " + str(ddp.currentPageID))
        ddp.refresh()

        #Grab the extent of the data frame
        curExtent = ddp.dataFrame.extent
        pnt1 = arcpy.Point(curExtent .XMin, curExtent .YMin)
        pnt2 = arcpy.Point(curExtent .XMin, curExtent .YMax)
        pnt3 = arcpy.Point(curExtent .XMax, curExtent .YMax)
        pnt4 = arcpy.Point(curExtent .XMax, curExtent .YMin)
        array = arcpy.Array([pnt1, pnt2, pnt3, pnt4])
        polygon = arcpy.Polygon(array)

        #And the then use it to update the shape
        rows = arcpy.da.UpdateCursor(ddp.indexLayer,["SHAPE@","DDP_Scale"], '"FID" = ' + str(ddp.pageRow.FID))
        # ---> to make this generally useful, you'll have to write something to find the object id field and verify proper syntax to call it based on file type
        for row in rows:
            rows.updateRow([polygon, ddp.dataFrame.scale])
        counter = counter + 1

    arcpy.AddMessage("...Your layer has been updated.")
    arcpy.AddMessage("...I backed up the old one here: " + os.path.join(outputPath,outputName))

    #Cleaning up
    del row
    del rows
    del mxd
    del ddp

except Exception as e:
    arcpy.AddMessage(e.message)