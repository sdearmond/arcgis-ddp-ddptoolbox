# arcgis-ddp-ddptoolbox

This is a toolbox for ESRI ArcMap containing some python tools to make working with data driven pages easier.

Installing the toolbox:

To use these tool, you will need to have ESRI ArcMap version 10.0 or later installed. In ArcMap, open ArcToolbox (Geoprocessing > ArcToolbox). Right-click anywhere in the ArcToolbox window, and choose "Add Toolbox", then navigate to the "DDP_Toolbox.tbx" file to install.


Tools in the toolbox:

1) Export Data Driven Pages
Allows you to export a data driven page set to a series of individual files named by the value in the name field in your data driven pages setup.

2) The Scale-Dependent Measured Grid Toolset contains two tool to facilitate make a measured grid (UTM grid or other projection) that will update with the scale for your data driven pages as appropriate. This toolset contains two tools meant to be run in order. The first updates each "page" feature in your data driven pages index layer to match the data frame extent for that page as it displays exactly. The second uses that index layer to create a series of lines and point to make a nicely formatted measured grid. Further discussion of how to use this toolset is documented here:
http://geobug.net/article/2016/10/12/data-driven-pages-v-utm-grids-multiple-scales


