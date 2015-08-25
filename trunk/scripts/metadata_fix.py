#!/usr/bin/python

# This script repairs the ANZMet validation errors and adds in the WMS distribution information to a metadata record
#
# Tags: XPATH, Find and Replace, File Iteration, Folder Creation
# Author: Gavin Jackson
# Date: March 2011

import os
import re
from lxml import etree
from tempfile import mkstemp
from shutil import move
from os import remove, close

#Function to perform a find replace in a file
def replace(file, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(file)
    #Move new file
    move(abs_path, file)

#Directory containing the metadata records to process
base_dir = "/Users/jac24n/Downloads/ANZLite_metadata/xml/"

#Directory where you would like the generated xml to be saved into
out_dir = "/Users/jac24n/Downloads/ANZLite_metadata/output/"

#XPath requires a dictionary of namespaces in order to parse
ns = {'gmd':'http://www.isotc211.org/2005/gmd', 
              'gco':'http://www.isotc211.org/2005/gco',
              'xsi':'http://www.w3.org/2001/XMLSchema-instance', 
              'gml':'http://www.opengis.net/gml',
              'gts':'http://www.isotc211.org/2005/gts', 
              'xlink':'http://www.w3.org/1999/xlink',
              'mcp':'http://bluenet3.antcrc.utas.edu.au/mcp'
              }

#Create output directory (if it doesn't already exist
d = os.path.dirname(out_dir)
if not os.path.exists(d):
    os.makedirs(d)

#Iterate through the folder
listing = os.listdir(base_dir)
for infile in listing:
    #Ignore unix hidden folders
    if (infile.startswith('.')):
        continue
    doc = etree.parse ( base_dir + infile );
    print "processing " + infile
    
    #Make sure we are dealing with the correct data quality element ...
    dt = doc.xpath('/mcp:MD_Metadata/gmd:dataQualityInfo[2]/gmd:DQ_DataQuality/gmd:report', namespaces=ns)
    dq_index = 1
    if (len(dt) == 1):
        dq_index = 2
        
    #PART 1:fix the dates    
    #find out how many elements match
    dt = doc.xpath('/mcp:MD_Metadata/gmd:dataQualityInfo[' + str(dq_index) + ']/gmd:DQ_DataQuality/gmd:report/gmd:DQ_GriddedDataPositionalAccuracy/gmd:dateTime/gco:DateTime', namespaces=ns)

    if (len(dt) == 1):     
        print "updating date in " + infile
        #old text is 2010-03T00:00:00
        #needs to be 2010-03-01T00:00:00
        #todo: regex find/replace operation to add day field
        dt[0].text = dt[0].text.replace('T', '-01T');
          
    else:
        print "WARNING: no dateTime match in " + infile
    
    #PART 2:add the citation attribute
    #example: how to access an attribute using @ syntax
    #  dt = doc.xpath('/mcp:MD_Metadata/gmd:dataQualityInfo[1]/gmd:DQ_DataQuality/gmd:report/gmd:DQ_GriddedDataPositionalAccuracy/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/@gco:nilReason', namespaces=ns)
    dt = doc.xpath('/mcp:MD_Metadata/gmd:dataQualityInfo[' + str(dq_index) + ']/gmd:DQ_DataQuality/gmd:report/gmd:DQ_GriddedDataPositionalAccuracy/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title', namespaces=ns)
    
    if(len(dt) == 1):
        print "  removing attribute"
        del dt[0].attrib['{http://www.isotc211.org/2005/gco}nilReason'];
    else:
        print "WARNING: no nilReason attribute match in " + infile

    #PART 3: add the N/A string
    dt = doc.xpath('/mcp:MD_Metadata/gmd:dataQualityInfo[' + str(dq_index) + ']/gmd:DQ_DataQuality/gmd:report/gmd:DQ_GriddedDataPositionalAccuracy/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces=ns)
    if(len(dt) == 1):
        print "  adding N/A text"
        dt[0].text = "N/A"
    else:
        print "WARNING: no CharacterString element in " + infile

    #PART 4: add date to gmd:CI_Citation
    dt = doc.xpath('/mcp:MD_Metadata/gmd:dataQualityInfo[' + str(dq_index) + ']/gmd:DQ_DataQuality/gmd:report/gmd:DQ_GriddedDataPositionalAccuracy/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date', namespaces=ns)
    if(len(dt) == 1):
        print "  adding date"
        dt[0].text = "2010-03-01"
    else:
        print "WARNING: no Date element in " + infile

    #get uuid of file
    uuid = ''
    dt = doc.xpath('/mcp:MD_Metadata/gmd:fileIdentifier/gco:CharacterString', namespaces=ns)
    if(len(dt) == 1):
        print "file uuid is " + dt[0].text
        uuid = dt[0].text
    else:
        print "WARNING: unable to locate uuid in document"

    #extract layername from metadata filename
    layerName = ''


    #get layer name (from infile)
    m = re.search('(?<=1kmGDMclimateparent_annualclimatestatistics_)\w+', infile)
    print "layerName is " + m.group(0).lower()
    layerName = m.group(0).lower()
    
    #edge cases (where layer names do not match metadata names
    if (layerName.__contains__('dl_p0') or (layerName == 'microgi')):
        #ignore these layers for now
        continue;
    elif (layerName == 'aridi'):
        layerName = 'arid_mean'
    elif (layerName == 'aridx'):
        layerName = 'arid_max'
    elif (layerName == 'aridm'):
        layerName = 'arid_mean'
    elif (layerName.__contains__('wind')):
        layerName = 'Wind_' + layerName

#    I originally tried using DOM manipulation to create the xml below - but it was taking way too long
#    for reference, this is how you create sub elements:
#        dt = doc.xpath('/mcp:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution', namespaces=ns)
#        to = etree.SubElement(dt[0], '{http://www.isotc211.org/2005/gmd}transferOptions')

    #Write out the dom to file
    outFile = open (out_dir + infile , 'w')
    doc.write (outFile)
    outFile.close()

    #Change the status of METValidation
    replace(out_dir + infile, 'METValidation=False', 'METValidation=True');

    #Add WMS distribution XML (ANZMetLite does not seem to support this ...)
    replace(out_dir + infile, '</gmd:MD_Distribution>', """<gmd:transferOptions xmlns:gmx="http://www.isotc211.org/2005/gmx" xmlns:srv="http://www.isotc211.org/2005/srv">
                <gmd:MD_DigitalTransferOptions>
                    <gmd:onLine>
                        <gmd:CI_OnlineResource>
                            <gmd:linkage>
                                <gmd:URL>http://spatial-dev.ala.org.au/geonetwork/srv/en/metadata.show?uuid=ade7be26-a04a-4dd5-894d-7354af083844</gmd:URL>
                            </gmd:linkage>
                            <gmd:protocol>
                                <gco:CharacterString>WWW:LINK-1.0-http--metadata-URL</gco:CharacterString>
                            </gmd:protocol>
                            <gmd:description>
                                <gco:CharacterString>Point of truth URL of this metadata record</gco:CharacterString>
                            </gmd:description>
                        </gmd:CI_OnlineResource>
                    </gmd:onLine>
                    <gmd:onLine>
                        <gmd:CI_OnlineResource>
                            <gmd:linkage>
                                <gmd:URL>http://spatial-dev.ala.org.au/geoserver/wms</gmd:URL>
                            </gmd:linkage>
                            <gmd:protocol>
                                <gco:CharacterString>OGC:WMS-1.1.1-http-get-capabilities</gco:CharacterString>
                            </gmd:protocol>
                            <gmd:name>
                                <gco:CharacterString>adefi</gco:CharacterString>
                            </gmd:name>
                            <gmd:description gco:nilReason="missing">
                                <gco:CharacterString/>
                            </gmd:description>
                            <gmd:function>
                                <gmd:CI_OnLineFunctionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_OnLineFunctionCode" codeListValue=""/>
                            </gmd:function>
                        </gmd:CI_OnlineResource>
                    </gmd:onLine>
                </gmd:MD_DigitalTransferOptions>
            </gmd:transferOptions>
        </gmd:MD_Distribution>""")
    
    #Substitute uuid and layerName
    replace(out_dir + infile, 'ade7be26-a04a-4dd5-894d-7354af083844', uuid);
    replace(out_dir + infile, 'adefi', layerName);

    #only do this once (for testing)  
    #break
