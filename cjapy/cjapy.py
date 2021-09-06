# Created by julien piccini
# email : piccini.julien@gmail.com
import json
from copy import deepcopy
from pathlib import Path
from typing import IO, Union, List
from collections import defaultdict
import time

# Non standard libraries
import pandas as pd

from cjapy import config, connector

JsonOrDataFrameType = Union[pd.DataFrame, dict]
JsonListOrDataFrameType = Union[pd.DataFrame, List[dict]]

class Workspace:
    """
    A class to return data from the getReport method.
    """
    startDate = None,
    endDate = None,
    filters = None

    def __init__(self,responseData:dict)->None:
        """
        Setup the different values from the response of the getReport
        Argument:
            responseData : REQUIRED : data returned & predigested by the getReport method.
        """


class CJA:
    """
    Class that instantiate a connection to a single CJA API connection.
    """

    def __init__(self,config_object: dict = config.config_object, header: dict = config.header)->None:
        """
        Instantiate the class with the information provided.
        """
        self.connector = connector.AdobeRequest(config_object=config_object, header=header)
        self.header = self.connector.header
        self.endpoint = config.endpoints['global']

    def getCurrentUser(self,admin:bool=False,useCache:bool=True)->dict:
        """
        return the current user 
        """
        path = "/aresconfig/users/me"
        params = {'useCache':useCache}
        if admin:
            params['expansion'] = 'admin'
        res = self.connector.getData(self.endpoint + path, params=params)
        return res
    
    def getCalculatedMetrics(self,full:bool=False,
                            inclType:str='all',
                            dataIds:str=None,
                            ownerId:str=None,
                            limit:int=100,
                            filterByIds:str=None,
                            favorite:bool=False,
                            approved:bool=False,
                            output:str="df")->JsonListOrDataFrameType:
        """
        Returns a dataframe or the list of calculated Metrics.
        Arguments:
            full : OPTIONAL : returns all possible attributs if set to True (False by default)
            inclType : OPTIONAL : returns the type selected.Possible options are:
                - all (default)
                - shared
                - templates
                - unauthorized
                - deleted
                - internal
                - curatedItem
            dataIds : OPTIONAL : Filters the result to calculated metrics tied to a specific Data View ID (comma-delimited)
            ownerId : OPTIONAL : Filters the result by specific loginId.
            limit : OPTIONAL : Number of results per request (Default 100)
            filterByIds : OPTIONAL : Filter list to only include calculated metrics in the specified list (comma-delimited),
            favorite : OPTIONAL : If set to true, return only favorties calculated metrics. (default False)
            approved : OPTIONAL : If set to true, returns only approved calculated metrics. (default False)
            output : OPTIONAL : by default returns a "dataframe", can also return the list when set to "raw"
        """
        path = "/calculatedmetrics"
        params = {'limit': limit,"includeType":inclType,'pagination':False,'page':0}
        if full:
            params['expension'] = "dataName,approved,favorite,shares,tags,sharesFullName,usageSummary,usageSummaryWithRelevancyScore,reportSuiteName,siteTitle,ownerFullName,modified,migratedIds,isDeleted,definition,authorization,compatibility,legacyId,internal,dataGroup,categories"
        if dataIds is not None:
            params['dataIds'] = dataIds
        if ownerId is not None:
            params['ownerId'] = ownerId
        if filterByIds is not None:
            params['filterByIds'] = filterByIds
        if favorite:
            params['favorite'] = favorite
        if approved:
            params['approved'] = approved
        res = self.connector.getData(self.endpoint + path, params=params)
        data = res['content']
        lastPage = res.get('lastPage',True)
        while lastPage != True:
            params['page'] += 1
            res = self.connector.getData(self.endpoint + path, params=params)
            data += res['content']
            lastPage = res.get('lastPage',True)
        if output=="df":
            df = pd.DataFrame(data)
            return df
        return res

    def getCalculatedMetricsFunctions(self,output:str='raw')->JsonListOrDataFrameType:
        """
        Returns a list of calculated metrics functions.
        Arguments:
            output : OPTIONAL : default to "raw", can return "dataframe".
        """
        path = "/calculatedmetrics/functions"
        res = self.connector.getData(self.endpoint + path)
        if output=="dataframe":
            df = pd.DataFrame(res)
            return df
        return res
    
    def getCalculatedMetric(self,calcId:str=None,full:bool=True)->dict:
        """
        Return a single calculated metrics based on its ID.
        Arguments:
            calcId : REQUIRED : The calculated metric 
        """
        if calcId is None:
            raise ValueError('Requires a Calculated Metrics ID')
        path = f"/calculatedmetrics/{calcId}"
        params = {'includeHidden':True}
        if full:
            params['expansion'] = "approved,favorite,shares,tags,sharesFullName,usageSummary,usageSummaryWithRelevancyScore,reportSuiteName,siteTitle,ownerFullName,modified,migratedIds,isDeleted,definition,authorization,compatibility,legacyId,internal,dataGroup,categories"
        res = self.connector.getData(self.endpoint+path,params=params)
        return res

    def createCalculatedMetric(self,data:dict=None)->dict:
        """
        Create a calculated metrics based on the dictionary.
        Arguments:
            data : REQUIRED : dictionary that will set the creation.
        """
        if data is None:
            raise ValueError("Require a dictionary to create the calculated metrics")
        path = "/calculatedmetrics"
        res = self.connector.postData(self.endpoint+path,data=data)
        return res
    
    def validateCalculatedMetric(self,data:dict=None)->dict:
        """
        Validate a calculated metrics definition dictionary.
        Arguments:
            data : REQUIRED : dictionary that will set the creation.
        """
        if data is None or type(data) == dict:
            raise ValueError("Require a dictionary to create the calculated metrics")
        path = "/calculatedmetrics/validate"
        res = self.connector.postData(self.endpoint+path,data=data)
        return res

    def deleteCalculateMetrics(self,calcId:str=None)->dict:
        """
        Delete a calculated metrics based on its ID.
        Arguments:
            calcId : REQUIRED : The calculated metrics ID that will be deleted.
        """
        if calcId is None:
            raise ValueError("requires a calculated metrics ID")
        path = f"/calculatedmetrics/{calcId}"
        res = self.connector.deleteData(self.endpoint+path)
        return res
    
    def updateCalculatedMetrics(self,calcId:str=None,data:dict=None)->dict:
        """
        Will overwrite the calculated metrics object with the new object (PUT method)
        Arguments:
            calcId : REQUIRED : The calculated metric ID to be updated
            data : REQUIRED : The dictionary that will overwrite.
        """
        if calcId is None:
            raise ValueError("Require a calculated metrics")
        if data is None or type(data) == dict:
            raise ValueError("Require a dictionary to create the calculated metrics")
        path = f"/calculatedmetrics/{calcId}"
        res = self.connector.putData(self.endpoint+path,data=data)
        return res

    def getShares(self,userId:str=None,inclType:str='sharedTo',limit:int=100,useCache:bool=True)->dict:
        """
        Returns the elements shared.
        Arguments:
            userId : OPTIONAL : User ID to return details for.
            inclType : OPTIONAL : Include additional shares not owned by the user
            limit : OPTIONAL : number of result per request.
            useCache: OPTIONAL : Caching the result (default True)
        """
        params = {'limit':limit,"includeType":inclType,"useCache":useCache}
        path = "/componentmetadata/shares"
        if userId is not None:
            params['userId'] =  userId
        res = self.connector.getData(self.endpoint+path,params=params)
        return res

    def getShare(self,shareId:str=None,useCache:bool=True)->dict:
        """
        Returns a specific share element.
        Arguments:
            shareId : REQUIRED : the element ID.
            useCache : OPTIONAL : If caching the response (True by default)
        """
        params = {"useCache":useCache}
        if shareId is None:
            raise ValueError("Require an ID to retrieve the element")
        path = f"/componentmetadata/shares/{shareId}"
        res = self.connector.getData(self.endpoint+path,params=params)
        return res
    
    def deleteShare(self,shareId:str=None)->dict:
        """
        Delete the shares of an element.
        Arguments:
            shareId : REQUIRED : the element ID to be deleted.
        """
        if shareId is None:
            raise ValueError("Require an ID to retrieve the element")
        path = f"/componentmetadata/shares/{shareId}"
        res = self.connector.deleteData(self.endpoint+path)
        return res
    
    def searchShares(self,data:dict=None,full:bool=False,limit:int=10)->dict:
        """
        Search for multiple shares on component based on the data passed.
        Arguments:
            data : REQUIRED : dictionary specifying the search.
                example: {
                    "componentType": "string",
                    "componentIds": [
                        "string"
                    ],
                    "dataId": "string"
                }
            full : OPTIONAL : add additional data in the results.(Default False)
            limit : OPTIONAL : number of result per page (10 per default)
        """
        path = "/componentmetadata/shares/component/search"
        if data is None:
            raise ValueError("require a dictionary to specify the search.")
        params = {"limit":limit}
        if full:
            params['expansion'] = "sharesFullName"
        res = self.connector.postData(self.endpoint+path,data=data,params=params)
        return res
    
    def updateShares(self,data:list=None,useCache:bool=True)->dict:
        """
        Create one/many shares for one/many components at once. This is a PUT request.
        For each component object in the passed list, the given shares will replace the current set of shares for each component. 
        Arguments:
            data : REQUIRED : list of dictionary containing the component to share.
                Example  [
                    {
                        "componentType": "string",
                        "componentId": "string",
                        "shares": [
                        {
                            "shareToId": 0,
                            "shareToImsId": "string",
                            "shareToType": "string",
                            "accessLevel": "string"
                        }
                        ]
                    }
                ]
            useCache : OPTIONAL : Boolean to use caching. Default is True.
        """
        if data is None or type(data) != list:
            raise ValueError("Require a list of element to share")
        path = "/componentmetadata/shares"
        params = {"useCache":useCache}
        res = self.connector.putData(self.endpoint +path,params=params,data=data)
        return res

    def getTags(self,limit:int=100)->dict:
        """
        Return the tags for the company.
        Arguments:
            limit : OPTIONAL : Number of result per request.
        """
        path = "/componentmetadata/tags"
        params = {"limit":limit}
        res = self.connector.getData(self.endpoint +path,params=params)
        return res
    
    def createTags(self,data:list=None)->dict:
        """
        Create tags for the company, attached to components.
        ARguments:
            data : REQUIRED : list of elements to passed.
                Example [
                    {
                        "id": 0,
                        "name": "string",
                        "description": "string",
                        "components": [
                        null
                        ]
                    }
                ]
        """
        path = "/componentmetadata/tags"
        if data is None and type(data) != list:
            raise ValueError("Require a list of tags to be created")
        res = self.connector.postData(self.endpoint +path,data=data)
        return res
    
    def deleteTags(self,componentIds:str=None,componentType:str=None)->dict:
        """
        Removes all tags from the passed componentIds. 
        Note that currently this is done in a single DB query, so there is a single combined response for the entire operation.
        Arguments:
            componentIds : REQUIRED : comma separated list of component ids to remove tags.
            componentType : REQUIRED : The component type to operate on.
                could be any of the following ; "segment" "dashboard" "bookmark" "calculatedMetric" "project" "dateRange" "metric" "dimension" "virtualReportSuite" "scheduledJob" "alert" "classificationSet" "dataView"
        """
        path = "/componentmetadata/tags"
        if componentIds is None:
            raise ValueError("Require a component ID")
        if componentType is None:
            raise ValueError("Require a component type")
        if componentType not in ["segment","dashboard","bookmark","calculatedMetric","project","dateRange","metric","dimension","virtualReportSuite","scheduledJob","alert","classificationSet","dataView"]:
            raise KeyError("componentType not in the enum")
        params = {componentType: componentType,componentIds: componentIds}
        res = self.connector.deleteData(self.endpoint+path,params=params)
        return res
    
    def getTag(self,tagId:str=None)->dict:
        """
        Return a single tag data by its ID.
        Arguments:
            tagId : REQUIRED : The tag ID to retrieve.
        """
        if tagId is None:
            raise ValueError("Require a tag ID")
        path = f"/componentmetadata/tags/{tagId}"
        res = self.connector.getData(self.endpoint+path)
        return res
    
    def getComponentTags(self,componentId:str=None,componentType:str=None)->dict:
        """
        Return tags for a component based on its ID and type.
        Arguments:
            componentId : REQUIRED : The component ID
            componentType : REQUIRED : The component type.
                could be any of the following ; "segment" "dashboard" "bookmark" "calculatedMetric" "project" "dateRange" "metric" "dimension" "virtualReportSuite" "scheduledJob" "alert" "classificationSet" "dataView"
        """
        if componentId is None:
            raise ValueError("Require a component ID")
        if componentType is None:
            raise ValueError("Require a component type")
        if componentType not in ["segment","dashboard","bookmark","calculatedMetric","project","dateRange","metric","dimension","virtualReportSuite","scheduledJob","alert","classificationSet","dataView"]:
            raise KeyError("componentType not in the enum")
        params = {"componentId": componentId,"componentType": componentType}
        path = "/componentmetadata/tags/search"
        res = self.connector.getData(self.endpoint +path,params=params)
        return res
    
    def updateTags(self,data:list=None)->dict:
        """
        This endpoint allows many tags at once to be created/deleted. PUT method. 
        Any tags passed to this endpoint will become the only tags for that componentId (all other tags will be removed).
        Arguments:
            data : REQUIRED : List of tags and component to be tagged.
                Example [
                            {
                                "componentType": "string",
                                "componentId": "string",
                                "tags": [
                                    {
                                        "id": 0,
                                        "name": "string",
                                        "description": "string",
                                        "components": [
                                        null
                                        ]
                                    }
                                ]
                            }
                        ]
        """
        path = "/componentmetadata/tags/tagitems"
        if data is None or type(data) != list:
            raise ValueError("Require a list of elements to update")
        res = self.connector.putData(self.endpoint + path, data=data)
        return res
    
    def getTopItems(self,dataId:str=None,
                    dimension:str=None,
                    dateRange:str=None,
                    startDate:str=None,
                    endDate:str=None,
                    limit:int=100,
                    searchClause:str=None,
                    searchAnd:str=None,
                    searchOr:str=None,
                    searchNot:str=None,
                    searchPhrase:str=None,
                    remoteLoad:bool=True,
                    xml:bool=False,
                    noneValues:bool=True,
                    **kwargs
                    )->dict:
        """
        Get the top X items (based on paging restriction) for the specified dimension and dataId. Defaults to last 90 days.
        Arguments:
            dataId : REQUIRED : Data Group or Data View to run the report against
            dimension : REQUIRED : Dimension to run the report against. Example: "variables/page"
            dateRange : OPTIONAL : Format: YYYY-MM-DD/YYYY-MM-DD (default 90 days)
            startDate: OPTIONAL : Format: YYYY-MM-DD 
            endDate : OPTIONAL : Format: YYYY-MM-DD
            limit : OPTIONAL : Number of results per request (default 100)
            searchClause : OPTIONAL : General search string; wrap with single quotes. Example: 'PageABC'
            searchAnd : OPTIONAL : Search terms that will be AND-ed together. Space delimited.
            searchOr : OPTIONAL : Search terms that will be OR-ed together. Space delimited.
            searchNot : OPTIONAL : Search terms that will be treated as NOT including. Space delimited.
            searchPhrase : OPTIONAL : A full search phrase that will be searched for.
            remoteLoad : OPTIONAL : tells to load the result in Oberon if possible (default True)
            xml : OPTIONAL : returns the XML for debugging (default False)
            noneValues : OPTIONAL : Controls None values to be included (default True)
        """
        path = "/reports/topItems"
        if dataId is None:
            raise ValueError("Require a data ID")
        if dimension is None:
            raise ValueError("Require a dimension")
        params = {"dataId": dataId, "dimension": dimension,"limit":limit,"allowRemoteLoad":"true","includeOberonXml":False,"lookupNoneValues":True}
        if dateRange is not None:
            params['dateRange'] = dateRange 
        if startDate is not None and endDate is not None:
            params['startDate'] = startDate
            params['endDate'] = endDate
        if searchClause is not None:
            params['search-clause'] = searchClause
        if searchAnd is not None:
            params['searchAnd'] = searchAnd
        if searchOr is not None:
            params['searchOr'] = searchOr
        if searchNot is not None:
            params['searchNot'] = searchNot
        if searchPhrase is not None:
            params['searchPhrase'] = searchPhrase
        if remoteLoad == False:
            params["allowRemoteLoad"]="false"
        if xml:
            params["includeOberonXml"] = True
        if noneValues == False:
            params["lookupNoneValues"] = False
        res = self.connector.getData(self.endpoint+path,params=params)
        return res
    
    def getDimensions(self,dataviewId:str=None,full:bool=False,inclType:str=None,verbose:bool=False)->dict:
        """
        Used to retrieve dimensions for a dataview
        Arguments:
            dataviewId : REQUIRED : the Data View ID to retrieve data from.
            full : OPTIONAL : To add additional elements (default False)
            inclType : OPTIONAL : Possibility to add "hidden" values
        """
        if dataviewId is None:
            raise ValueError("Require a Data View ID")
        path = f"/datagroups/data/{dataviewId}/dimensions"
        params = {}
        if full:
            params['expansion'] = "approved,favorite,tags,usageSummary,usageSummaryWithRelevancyScore,description,sourceFieldId,segmentable,required,hideFromReporting,hidden,includeExcludeSetting,fieldDefinition,bucketingSetting,noValueOptionsSetting,defaultDimensionSort,persistenceSetting,storageId,tableName,dataSetIds,dataSetType,type,schemaPath,hasData,sourceFieldName,schemaType,sourceFieldType,fromGlobalLookup,multiValued,precision"
        if inclType == "hidden":
            params["includeType"] = "hidden"
        res = self.connector.getData(self.endpoint +path,params=params,verbose=verbose)
        return res
    
    def getDimension(self,dataviewId:str=None,dimensionId:str=None,full:bool=True):
        """
        Return a specific dimension based on the dataview ID and dimension ID passed.
        Arguments:
            dataviewId : REQUIRED : the Data View ID to retrieve data from.
            dimensionId : REQUIRED : the dimension ID to return
            full : OPTIONAL : To add additional elements (default True)
        """
        if dataviewId is None:
            raise ValueError("Require a Data View ID")
        if dimensionId is None:
            raise ValueError("Require a Dimension ID")
        path = f"/datagroups/data/{dataviewId}/dimensions/{dimensionId}"
        params = {}
        if full:
            params["expansion"] = "approved,favorite,tags,usageSummary,usageSummaryWithRelevancyScore,description,sourceFieldId,segmentable,required,hideFromReporting,hidden,includeExcludeSetting,fieldDefinition,bucketingSetting,noValueOptionsSetting,defaultDimensionSort,persistenceSetting,storageId,tableName,dataSetIds,dataSetType,type,schemaPath,hasData,sourceFieldName,schemaType,sourceFieldType,fromGlobalLookup,multiValued,precision"
        res = self.connector.getData(self.endpoint +path,params=params)
        return res

    def getMetrics(self,dataviewId:str=None,full:bool=False,inclType:str=None,verbose:bool=False)->dict:
        """
        Used to retrieve metrics for a dataview
        Arguments:
            dataviewId : REQUIRED : the Data View ID to retrieve data from.
            full : OPTIONAL : To add additional elements (default False)
            inclType : OPTIONAL : Possibility to add "hidden" values
        """
        if dataviewId is None:
            raise ValueError("Require a Data View ID")
        path = f"/datagroups/data/{dataviewId}/metrics"
        params = {}
        if full:
            params['expansion'] = "approved,favorite,tags,usageSummary,usageSummaryWithRelevancyScore,description,sourceFieldId,segmentable,required,hideFromReporting,hidden,includeExcludeSetting,fieldDefinition,bucketingSetting,noValueOptionsSetting,defaultDimensionSort,persistenceSetting,storageId,tableName,dataSetIds,dataSetType,type,schemaPath,hasData,sourceFieldName,schemaType,sourceFieldType,fromGlobalLookup,multiValued,precision"
        if inclType == "hidden":
            params["includeType"] = "hidden"
        res = self.connector.getData(self.endpoint +path,params=params,verbose=verbose)
        return res
    
    def getDimension(self,dataviewId:str=None,metricId:str=None,full:bool=True):
        """
        Return a specific metric based on the dataview ID and dimension ID passed.
        Arguments:
            dataviewId : REQUIRED : the Data View ID to retrieve data from.
            metricId : REQUIRED : the metric ID to return
            full : OPTIONAL : To add additional elements (default True)
        """
        if dataviewId is None:
            raise ValueError("Require a Data View ID")
        if metricId is None:
            raise ValueError("Require a Dimension ID")
        path = f"/datagroups/data/{dataviewId}/metrics/{metricId}"
        params = {}
        if full:
            params["expansion"] = "approved,favorite,tags,usageSummary,usageSummaryWithRelevancyScore,description,sourceFieldId,segmentable,required,hideFromReporting,hidden,includeExcludeSetting,fieldDefinition,bucketingSetting,noValueOptionsSetting,defaultDimensionSort,persistenceSetting,storageId,tableName,dataSetIds,dataSetType,type,schemaPath,hasData,sourceFieldName,schemaType,sourceFieldType,fromGlobalLookup,multiValued,precision"
        res = self.connector.getData(self.endpoint +path,params=params)
        return res
    
    def getDataViews(self,
                    limit:int = 100,
                    full:bool=True,
                    output:str="df",
                    parentDataGroupId:str=None,
                    externalIds:str=None,
                    externalParentIds:str=None,
                    includeType:str="all",
                    cached:bool=True,
                    verbose:bool=False,
                    **kwargs
                    )->JsonListOrDataFrameType:
        """
        Returns the Data View configuration.
        Arguments:
            limit : OPTIONAL : number of results per request (default 100)
            full : OPTIONAL : define if all possible information are returned (default True).
            output : OPTIONAL : Type of output selected, either "df" (default) or "raw"
            parentDataGroupId : OPTIONAL : Filters data views by a single parentDataGroupId
            externalIds : OPTIONAL : Comma-delimited list of external ids to limit the response with.
            externalParentIds : OPTIONAL : Comma-delimited list of external parent ids to limit the response with.
            dataViewIds : OPTIONAL : Comma-delimited list of data view ids to limit the response with.
            includeType : OPTIONAL : include additional DataViews not owned by user.(default "all")
            cached : OPTIONAL : return cached results
            verbose : OPTIONAL : add comments in the console.
        """
        path = "/datagroups/dataviews"
        params = {"limit":limit,"includeType": includeType,"cached":cached,"page":0}
        if full:
            params["expansion"] = "name,description,owner,isDeleted,parentDataGroupId,segmentList,currentTimezoneOffset,timezoneDesignator,modified,createdDate,organization,curationEnabled,recentRecordedAccess,sessionDefinition,curatedComponents,externalData,containerNames"
        if parentDataGroupId:
            params["parentDataGroupId"] = parentDataGroupId
        if externalIds:
            params["externalIds"] = externalIds
        if externalParentIds:
            params["externalParentIds"] = externalParentIds
        res = self.connector.getData(self.endpoint+path, params=params,verbose=verbose)
        data = res['content']
        last = res.get('last',True)
        while last != True:
            params["page"] += 1
            res = self.connector.getData(self.endpoint+path, params=params,verbose=verbose)
            data += res['content']
            last = res.get('last',True)
        if output == "df":
            df = pd.DataFrame(data)
            return df
        return data
    
    def getDataView(self,dataViewId:str=None,full:bool=True,save:bool=False)->dict:
        """
        Returns a specific Data View configuration from Configuration ID.
        Arguments:
            dataViewId : REQUIRED : The data view ID to retrieve.
            full : OPTIONAL : getting extra information on the data view
            save : OPTIONAL : save the response in JSON format
        """
        if dataViewId is None:
            raise ValueError('dataViewId is required')
        path = f"/datagroups/dataviews/{dataViewId}"
        params = {}
        if full:
            params["expansion"] = "name,description,owner,isDeleted,parentDataGroupId,segmentList,currentTimezoneOffset,timezoneDesignator,modified,createdDate,organization,curationEnabled,recentRecordedAccess,sessionDefinition,curatedComponents,externalData,containerNames"
        res = self.connector.getData(self.endpoint+path,params=params)
        if save:
            with open(f'{dataViewId}_{int(time.time())}.json',"w") as f:
                f.write(json.dumps(res,indent=4))
        return res
    
    def validateDataView(self, data:Union[dict,IO])->dict:
        """
        Validate the dictionary for the creation of a data view.
        Argument:
            data : REQUIRED : The dictionary or json file that holds the definition for the dataview to be created.
        """
        if data is None:
            raise ValueError("Require information to be passed for data view creation")
        path = "/datagroups/dataviews/validate"
        if '.json' in data:
            with open(data,'r') as f:
                data = json.load(f.read())
        res = self.connector.postData(self.endpoint+path,data=data)
        return res


    def createDataView(self,data:Union[dict,IO]=None,**kwargs)->dict:
        """
        Create and stores the given Data View in the db.
        Arguments:
            data : REQUIRED : The dictionary or json file that holds the definition for the dataview to be created.
        """
        path = "/datagroups/dataviews/"
        if data is None:
            raise ValueError("Require information to be passed for data view creation")
        if '.json' in data:
            with open(data,'r',encoding=kwargs.get('encoding','utf-8')) as f:
                data = json.load(f.read())
        res = self.connector.postData(self.endpoint+path,data=data)
        return res
    
    def deleteDataView(self,dataViewId:str=None)->str:
        """
        Delete a data view by its ID.
        Argument:
            dataViewId : REQUIRED : the data view ID to be deleted
        """
        if dataViewId is None:
            raise ValueError("Require a data view ID")
        path = f"/datagroups/dataviews/{dataViewId}"
        res = self.connector.deleteData(self.endpoint+path)
        return res

    def updateDataView(self, dataViewId:str=None, data:Union[dict,IO]=None,**kwargs)->dict:
        """
        Update the Data View definition (PUT method)
        Arguments:
            dataViewId : REQUIRED : the data view ID to be updated
            data : REQUIRED : The dictionary or JSON file that holds the definition for the dataview to be updated
        possible kwargs:
            encoding : if you pass a JSON file, you can change the encoding to read it.
        """
        if dataViewId is None:
            raise ValueError("Require a Data View ID")
        if data is None:
            raise ValueError("Require data to be passed for the update")
        path = f"/datagroups/dataviews/{dataViewId}"
        if '.json' in data:
            with open(data,'r',encoding=kwargs.get('encoding','utf-8')) as f:
                data = json.load(f.read())
        res = self.connector.putData(self.endpoint+path,data=data)
        return res

    def copyDataView(self,dataViewId:str=None)->dict:
        """
        Copy the setting of a specific data view.
        Arguments:
            dataViewId : REQUIRED : Data View ID to copy the setting on
        """
        if dataViewId is None:
            raise ValueError("Require a data view ID")
        path = f"/datagroups/dataviews/copy/{dataViewId}"
        res = self.connector.putData(self.endpoint+path)
        return res

    def getFilters(self,
                    limit:int=100, 
                    full:bool=False,
                    output:str="df",
                    includeType:str="all",
                    name:str = None,
                    dataIds:str = None,
                    ownerId:str = None,
                    filterByIds:str = None,
                    cached:bool = True,
                    verbose:bool = False,
                    )->JsonListOrDataFrameType:
        """
        Returns a list of filters used in CJA.
        Arguments:
            limit : OPTIONAL : number of result per request (default 100)
            full : OPTIONAL : add additional information to the filters
            output : OPTIONAL : Type of output selected, either "df" (default) or "raw"
            includeType : OPTIONAL : Include additional segments not owned by user.(default all)
                possible values are "shared" "templates" "deleted" "internal"
            name : OPTIONAL : Filter list to only include segments that contains the Name
            dataIds : OPTIONAL : Filter list to only include segments tied to the specified data group ID list (comma-delimited)
            ownerId : OPTIONAL : Filter by a specific owner ID.
            filterByIds : OPTIONAL : Filters by filter ID (comma-separated list)
            cached : OPTIONAL : return cached results
            toBeUsedInRsid : OPTIONAL : The report suite where the segment is intended to be used. This report suite will be used to determine things like compatibility and permissions.
        """
        path = "/filters"
        params = {"limit" : limit,"cached":cached,"includeType":includeType,"page":0}
        if full:
            params["expansion"] = "compatibility,definition,internal,modified,isDeleted,definitionLastModified,createdDate,recentRecordedAccess,performanceScore,owner,dataId,ownerFullName,dataName,sharesFullName,approved,favorite,shares,tags,usageSummary,usageSummaryWithRelevancyScore"
        if name is not None:
            params["name"] = name
        if dataIds is not None:
            params["dataIds"] = dataIds
        if ownerId is not None:
            params["ownerId"] = ownerId
        if filterByIds is not None:
            params["filterByIds"] = filterByIds
        res = self.connector.getData(self.endpoint + path,params=params,verbose=verbose)
        lastPage = res.get('lastPage',True)
        data = res['content']
        while lastPage == False:
            params["page"] += 1
            res = self.connector.getData(self.endpoint + path,params=params,verbose=verbose)
            data += res['content']
            lastPage = res.get('lastPage',True)
        if output == "df":
            df = pd.DataFrame(data)
            return df
        return data

    def getFilter(self,filterId:str=None,full:bool=False,)->dict:
        """
        Returns a single filter definition by its ID.
        Arguments:
            filterId : REQUIRED : ID of the filter
            full : OPTIONAL : Boolean to define additional elements
        """
        if filterId is None:
            raise ValueError("Require a filter ID")
        path = f"/filters/{filterId}"
        params = {}
        if full:
            params["expansion"] = "compatibility,definition,internal,modified,isDeleted,definitionLastModified,createdDate,recentRecordedAccess,performanceScore,owner,dataId,ownerFullName,dataName,sharesFullName,approved,favorite,shares,tags,usageSummary,usageSummaryWithRelevancyScore"
        res = self.connector.getData(self.endpoint+path,params=params)
        return res
    
    def deleteFilter(self,filterId:str=None)->str:
        """
        Delete a filter based on its ID.
        Arguments:
            filterId : REQUIRED : Filter ID to be deleted
        """
        if filterId is None:
            raise ValueError("Require a filter ID")
        path = f"/filters/{filterId}"
        res = self.connector.deleteData(self.endpoint+path)
        return res
    
    def validateFilter(self,data:Union[dict,IO]=None,**kwargs)->dict:
        """
        Validate the syntax for filter creation.
        Arguments:
            data : REQUIRED : Dictionary or JSON file to create a filter
        possible kwargs:
            encoding : if you pass a JSON file, you can change the encoding to read it.
        """
        if data is None:
            raise ValueError("Require some data to validate")
        path = "/filters/validate"
        if '.json' in data:
            with open(data,'r',encoding=kwargs.get('encoding','utf-8')) as f:
                data = json.load(f.read())
        res = self.connector.postData(self.endpoint+path,data=data)
        return res

    def createFilter(self,data:Union[dict,IO]=None,**kwargs)->dict:
        """
        Create a filter.
        Arguments:
            data : REQUIRED : Dictionary or JSON file to create a filter
        possible kwargs:
            encoding : if you pass a JSON file, you can change the encoding to read it.
        """
        if data is None:
            raise ValueError("Require some data to validate")
        path = "/filters"
        if '.json' in data:
            with open(data,'r',encoding=kwargs.get('encoding','utf-8')) as f:
                data = json.load(f.read())
        res = self.connector.postData(self.endpoint+path,data=data)
        return res
    
    def updateFilter(self,filterId:str=None, data:Union[dict,IO]=None,**kwargs)->dict:
        """
        Create a filter.
        Arguments:
            filterId : REQUIRED : Filter ID to be updated
            data : REQUIRED : Dictionary or JSON file to update the filter
        possible kwargs:
            encoding : if you pass a JSON file, you can change the encoding to read it.
        """
        if filterId is None:
            raise ValueError("Require a filter ID")
        if data is None:
            raise ValueError("Require some data to validate")
        path = f"/filters/{filterId}"
        if '.json' in data:
            with open(data,'r',encoding=kwargs.get('encoding','utf-8')) as f:
                data = json.load(f.read())
        res = self.connector.putData(self.endpoint+path,data=data)
        return res
    
    def getReport(self,
                request: Union[dict,IO] = None,
                limit : int = 1000,
                n_results : Union[int,str] = "inf",
                allowRemoteLoad: str = "default",
                useCache:bool = True,
                useResultsCache:bool = False,
                includeOberonXml:bool = False,
                includePredictiveObjects:bool = False,
                returnsNone: bool = True,
                countRepeatInstance:bool = True,
                dataViewId:str = None
            ) -> Workspace:
        """
        Return an instance of Workspace that contains the data requested.
        Argumnents:
            request : REQUIRED : either a dictionary of a JSON file that contains the request information.
            limit : OPTIONAL : number of results per request (default 1000)
            n_results : OPTIONAL : total number of results returns. Use "inf" to return everything (default "inf")
            allowRemoteLoad : OPTIONAL : Controls if Oberon should remote load data. Default behavior is true with fallback to false if remote data does not exist
            useCache : OPTIONAL : Use caching for faster requests (Do not do any report caching)
            useResultsCache : OPTIONAL : Use results caching for faster reporting times (This is a pass through to Oberon which manages the Cache)
            includeOberonXml : OPTIONAL : Controls if Oberon XML should be returned in the response - DEBUG ONLY
            includePredictiveObjects : OPTIONAL : Controls if platform Predictive Objects should be returned in the response. Only available when using Anomaly Detection or Forecasting- DEBUG ONLY
            returnsNone : OPTIONAL: Overwritte the request setting to return None values.
            countRepeatInstance : OPTIONAL: Overwritte the request setting to count repeatInstances values.
            dataViewId : OPTIONAL : Overwrite the data View ID used for report. Only works if the same components are presents. 
        """
        path = "/reports"
        params = {
            "allowRemoteLoad":allowRemoteLoad,
            "useCache":useCache,
            "useResultsCache":useResultsCache,
            "includeOberonXml":includeOberonXml,
            "includePlatformPredictiveObjects":includePredictiveObjects
                }
        if '.json' in request:
            with open(request,'r') as f:
                dataRequest = json.load(f.read())
        elif type(request) == dict:
            dataRequest = request
        else:
            raise ValueError("Require a JSON or Dictionary to request data")
        ### Settings
        dataRequest['settings']['page'] = 0
        dataRequest['settings']['limit'] = limit
        if returnsNone:
            dataRequest['settings']['nonesBehavior'] = "return-nones"
        else:
            dataRequest['settings']['nonesBehavior'] = "exclude-nones"
        if countRepeatInstance:
            dataRequest['settings']['countRepeatInstances'] = True
        else:
            dataRequest['settings']['countRepeatInstances'] = False
        if dataViewId is not None:
            dataRequest["dataId"] = dataViewId
        ### Request data
        res = self.connector.postData(self.endpoint,data=dataRequest,params=params)
        return res
        