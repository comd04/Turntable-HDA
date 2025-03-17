import hou
import os
import re

# List of the name recognized by the script.
listName = [
    "_BASE",
    "_COLO",
    "_DIFFR",
    "_METAL",
    "_SPECU",
    "_SPECC",
    "_SPECR",
    "_SPECI",
    "_SPECA",
    "_SPECROT",
    "_TRANSM",
    "_TRANSMC",
    "_TRANSMD",
    "_TRANSMS",
    "_TRANSSC",
    "_TRANSDIS",
    "_TRANSTRA",
    "_SSS",
    "_SSSC",
    "_SSSR",
    "_SSSS",
    "_SSSA",
    "_SHEEN",
    "_SHEENC",
    "_SHEENR",
    "_COAT",
    "_COATC",
    "_COATR",
    "_COATA",
    "_COATROT",
    "_COATI",
    "_COATNORM",
    "_COATAC",
    "_COATAR",
    "_TFT",
    "_TFI",
    "_EMISS",
    "_EMISSC",
    "_OPAC",
    "_TW",
    "_NORM",
    "_TANG",
    "_DISP"
]


# First function, get the path for the turntable node, material node and the location of the textures folder.
def master():

    # Get the turntable node
    turntable = hou.node(".")
    pathTurntable = turntable.path()


    # Get the material node
    topLevelNode = hou.node(pathTurntable + "/textures/asset_MAT")
    pathTopLevelNode = topLevelNode.path()

    # Get textures folder location
    folderLocation = turntable.parm("texturesFolder")
    folderLocation = folderLocation.evalAsString()

    delExistingNode(topLevelNode)
    listFiles(folderLocation, topLevelNode, pathTopLevelNode)


# Delete already existing mtlx node
def delExistingNode(topLevelNode):

    children = topLevelNode.children()
    for child in children:
        if child.type().name() == "mtlximage":
            child.destroy()


# Keep only the .1001 image form each texture with full path
def listFiles(folderLocation, topLevelNode, pathTopLevelNode):

    keepName = []
    keepIndex = []
    extra = ''
    filesList = os.listdir(folderLocation)
    filesList = [i for i in filesList if ('1001' in i)]
    for file in filesList:
        if file.endswith(".rat"):
            filesList.remove(file)
    filesList = [folderLocation + s for s in filesList]
    filesListString = str(filesList)
    for idx in range(len(listName)):
        if listName[idx] in filesListString:
            keepName.append(listName[idx])
            keepIndex.append(idx)

    # If the name of the node created isn't in the same order as the textures file path, change the position of the texture file path
    for idx in range(len(keepName)):
        if keepName[idx] not in filesList[idx]:
            for index in range(len(filesList)):
                if keepName[idx] in filesList[index]:
                    extra = filesList[index]
                    filesList[index] = filesList[idx]
                    filesList[idx] = extra
                    extra = ''

    createNodes(keepName, keepIndex, topLevelNode, pathTopLevelNode, filesList)


# Create the mtlx image 2D nodes from the files list
def createNodes(keepName, keepIndex, topLevelNode, pathTopLevelNode, filesList):
    
    # Run for every node that will be created
    for idx in range(len(keepName)):
        if keepIndex[idx] == 1 or keepIndex[idx] == 5 or keepIndex[idx] == 11 or keepIndex[idx] == 16 or keepIndex[idx] == 20 or keepIndex[idx] == 22 or keepIndex[idx] == 27 or keepIndex[idx] == 30 or keepIndex[idx] == 31 or keepIndex[idx] == 35 or keepIndex[idx] == 38 or keepIndex[idx] == 40 or keepIndex[idx] == 41:
            signatureValue = "color3"
        else:
            signatureValue = "default"
        
        # Give the good signature type
        mtlxImage = topLevelNode.createNode("mtlximage", keepName[idx])
        mtlxImage.parm("signature").set(signatureValue)

        # Connect node to texture coordinate node
        textCoordinateNode = hou.node(pathTopLevelNode + "/mtlxtexcoord1")
        mtlxImage.setInput(3, textCoordinateNode)

        # If this is the normal or opacity or displacement node they have a special connection
        if keepName[idx] == "_NORM":
            normalMapNode = hou.node(pathTopLevelNode + "/normalMap")
            normalMapNode.setInput(0, mtlxImage)
        elif keepName[idx] == "_OPAC":
            opacityNode = hou.node(pathTopLevelNode + "/opacInvert")
            mtlxImage.parm("default_color3r").set(0.95)
            mtlxImage.parm("default_color3g").set(0.95)
            mtlxImage.parm("default_color3b").set(0.95)
            opacityNode.setInput(0, mtlxImage)
        elif keepName[idx] == "_DISP":
            displacementNode = hou.node(pathTopLevelNode + "/mtlxdisplacement")
            displacementNode.setInput(0, mtlxImage)
        else:
            shaderNode = hou.node(pathTopLevelNode + "/mtlxstandard_surface")
            shaderNode.setInput(keepIndex[idx], mtlxImage)

        # Give the texture file path
        fileTextures = mtlxImage.parm("file")
        filesList[idx] = re.sub('.[0-9]{4}.', '.<UDIM>.', filesList[idx])
        fileTextures.set(filesList[idx])


master()