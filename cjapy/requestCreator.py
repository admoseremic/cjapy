from types import MappingProxyType
from copy import deepcopy
import datetime


class RequestCreator:
    """
    A class to help build a request for CJA API getReport
    """

    template = {
        "globalFilters": [],
        "metricContainer": {
            "metrics": [],
            "metricFilters": [],
        },
        "dimension": "",
        "settings": {
            "countRepeatInstances": True,
            "limit": 20000,
            "page": 0,
            "nonesBehavior": "exclude-nones",
        },
        "statistics": {"functions": ["col-max", "col-min"]},
        "dataId": "",
    }

    def __init__(self, request: dict = None) -> None:
        """
        Instanciate the constructor.
        Arguments:
            request : OPTIONAL : overwrite the template with the definition provided.
        """
        self.__request = deepcopy(request) or deepcopy(self.template)
        self.__metricCount = len(self.__request["metricContainer"]["metrics"])
        self.__metricFilterCount = len(
            self.__request["metricContainer"].get("metricFilters", [])
        )
        self.__globalFiltersCount = len(self.__request["globalFilters"])
        ### Preparing some time statement.
        today = datetime.datetime.now()
        today_date_iso = today.isoformat().split("T")[0]
        ## should give '20XX-XX-XX'
        tomorrow_date_iso = (
            (today + datetime.timedelta(days=1)).isoformat().split("T")[0]
        )
        time_start = "T00:00:00.000"
        time_end = "T23:59:59.999"
        startToday_iso = today_date_iso + time_start
        endToday_iso = today_date_iso + time_end
        startMonth_iso = f"{today_date_iso[:-2]}01{time_start}"
        tomorrow_iso = tomorrow_date_iso + time_start
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        last_day_month = next_month - datetime.timedelta(days=next_month.day)
        last_day_month_date_iso = last_day_month.isoformat().split("T")[0]
        last_day_month_iso = last_day_month_date_iso + time_end
        thirty_days_prior_date_iso = (
            (today - datetime.timedelta(days=30)).isoformat().split("T")[0]
        )
        thirty_days_prior_iso = thirty_days_prior_date_iso + time_start
        seven_days_prior_iso_date = (
            (today - datetime.timedelta(days=7)).isoformat().split("T")[0]
        )
        seven_days_prior_iso = seven_days_prior_iso_date + time_start
        ### assigning predefined dates:
        self.dates = {
            "thisMonth": f"{startMonth_iso}/{last_day_month_iso}",
            "untilToday": f"{startMonth_iso}/{startToday_iso}",
            "todayIncluded": f"{startMonth_iso}/{endToday_iso}",
            "last30daysTillToday": f"{thirty_days_prior_iso}/{startToday_iso}",
            "last30daysTodayIncluded": f"{thirty_days_prior_iso}/{tomorrow_iso}",
            "last7daysTillToday": f"{seven_days_prior_iso}/{startToday_iso}",
            "last7daysTodayIncluded": f"{seven_days_prior_iso}/{endToday_iso}",
        }
        self.today = today

    def addMetric(self, metricId: str = None) -> None:
        """
        Add a metric to the template.
        Arguments:
            metricId : REQUIRED : The metric to add
        """
        if metricId is None:
            raise ValueError("Require a metric ID")
        columnId = self.__metricCount
        addMetric = {"columnId": str(columnId), "id": metricId}
        if columnId == 0:
            addMetric["sort"] = "desc"
        self.__request["metricContainer"]["metrics"].append(addMetric)
        self.__metricCount += 1

    def addMetricFilter(
        self, metricId: str = None, filterId: str = None, metricIndex: int = None
    ) -> None:
        """
        Add a filter to a metric.
        Arguments:
            metricId : REQUIRED : metric where the filter is added
            filterId : REQUIRED : The filter to add.
                when breakdown, use the following format for the value "dimension:::itemId"
            metricIndex : OPTIONAL : If used, set the filter to the metric located on that index.
        """
        if metricId is None:
            raise ValueError("Require a metric ID")
        if filterId is None:
            raise ValueError("Require a filter ID")
        filterIdCount = self.__metricFilterCount
        if filterId.startswith("s") and "@AdobeOrg" in filterId:
            filterType = "segment"
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "segmentId": filterId,
            }
        elif filterId.startswith("20") and "/20" in filterId:
            filterType = "dateRange"
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "dateRange": filterId,
            }
        elif ":::" in filterId:
            filterType = "breakdown"
            dimension, itemId = filterId.split(":::")
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "dimension": dimension,
                "itemId": itemId,
            }
        else:  ### case when it is predefined segments like "All_Visits"
            filterType = "segment"
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "segmentId": filterId,
            }
        if filterIdCount == 0:
            self.__request["metricContainer"]["metricFilters"] = [filter]
        else:
            self.__request["metricContainer"]["metricFilters"].append(filter)
        ### adding filter to the metric
        if metricIndex is None:
            for metric in self.__request["metricContainer"]["metrics"]:
                if metric["id"] == metricId:
                    if "filters" in metric.keys():
                        metric["filters"].append(str(filterIdCount))
                    else:
                        metric["filters"] = [str(filterIdCount)]
        else:
            metric = self.__request["metricContainer"]["metrics"][metricIndex]
            if "filters" in metric.keys():
                metric["filters"].append(str(filterIdCount))
            else:
                metric["filters"] = [str(filterIdCount)]
        ### incrementing the filter counter
        self.__metricFilterCount += 1

    def removeMetricFilter(self, filterId: str = None) -> None:
        """
        remove a filter from a metric
        Arguments:
            filterId : REQUIRED : The filter to add.
                when breakdown, use the following format for the value "dimension:::itemId"
        """
        print("to remove: " + filterId)
        found = False  ## flag
        if filterId is None:
            raise ValueError("Require a filter ID")
        if ":::" in filterId:
            filterId = filterId.split(":::")[1]
        list_index = []
        for metricFilter in self.__request["metricContainer"]["metricFilters"]:
            if filterId in str(metricFilter):
                list_index.append(metricFilter["id"])
                found = True
        ## decrementing the filter counter
        if found:
            for metricFilterId in reversed(list_index):
                del self.__request["metricContainer"]["metricFilters"][
                    int(metricFilterId)
                ]
                for metric in self.__request["metricContainer"]["metrics"]:
                    if metricFilterId in metric.get("filters", []):
                        metric["filters"].remove(metricFilterId)
                        print("remove")
                self.__metricFilterCount -= 1

    def setLimit(self, limit: int = 100) -> None:
        """
        Specific the number of element to retrieve. Default is 10.
        Arguments:
            limit : OPTIONAL : number of elements to return
        """
        self.__request["settings"]["limit"] = limit

    def setRepeatInstance(self, repeat: bool = True) -> None:
        """
        Specify if repeated instances should be counted.
        Arguments:
            repeat : OPTIONAL : True or False (True by default)
        """
        self.__request["settings"]["countRepeatInstances"] = repeat

    def setNoneBehavior(self, returnNones: bool = True) -> None:
        """
        Set the behavior of the None values in that request.
        Arguments:
            returnNones : OPTIONAL : True or False (True by default)
        """
        if returnNones:
            self.__request["settings"]["nonesBehavior"] = "return-nones"
        else:
            self.__request["settings"]["nonesBehavior"] = "exclude-nones"

    def setDimension(self, dimension: str = None) -> None:
        """
        Set the dimension to be used for reporting.
        Arguments:
            dimension : REQUIRED : the dimension to build your report on
        """
        if dimension is None:
            raise ValueError("A dimension must be passed")
        self.__request["dimension"] = dimension

    def setDataViewId(self, dataViewId: str = None) -> None:
        """
        Set the dataView ID to be used for the reporting.
        Arguments:
            dataViewId : REQUIRED : The Data View ID to be passed.
        """
        if dataViewId is None:
            raise ValueError("A dataView ID must be passed")
        self.__request["dataId"] = dataViewId

    def addGlobalFilter(self, filterId: str = None) -> None:
        """
        Add a global filter to the report.
        NOTE : You need to have a dateRange filter at least in the global report.
        Arguments:
            filterId : REQUIRED : The filter to add to the global filter.
                example : ["filterId1","2020-01-01T00:00:00.000/2020-02-01T00:00:00.000"]
        """
        filterIdCount = self.__globalFiltersCount
        if filterId.startswith("s") and "@AdobeOrg" in filterId:
            filterType = "segment"
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "segmentId": filterId,
            }
        elif filterId.startswith("20") and "/20" in filterId:
            filterType = "dateRange"
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "dateRange": filterId,
            }
        elif ":::" in filterId:
            filterType = "breakdown"
            dimension, itemId = filterId.split(":::")
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "dimension": dimension,
                "itemId": itemId,
            }
        else:  ### case when it is predefined segments like "All_Visits"
            filterType = "segment"
            filter = {
                "id": str(filterIdCount),
                "type": filterType,
                "segmentId": filterId,
            }
        ### incrementing the count for globalFilter
        self.__globalFiltersCount += 1
        ### adding to the globalFilter list
        self.__request["globalFilters"].append(filter)

    def to_dict(self):
        """
        Return the request
        """
        return deepcopy(self.__request)