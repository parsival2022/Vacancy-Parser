from db_manager.mongo_manager import MongoManager
from parsers.linkedin_parser import LN_KEYWORDS
from parsers.djinni_parser import DJ_KEYWORDS

PYTHON_CLUSTER = "Python"
JAVA_CLUSTER = "Java"
JS_CLUSTER = "JS"
CPP_CLUSTER = "C++"

LN_PYTHON, LN_JAVA, LN_JS, LN_CPP = LN_KEYWORDS
DJ_PYTHON, DJ_JAVA, DJ_JS, DJ_CPP = DJ_KEYWORDS

class StatisticManager:
    clusters = {
        PYTHON_CLUSTER: {"ln_kw": LN_PYTHON,
                         "dj_kw": DJ_PYTHON},
        JAVA_CLUSTER: {"ln_kw": LN_JAVA,
                       "dj_kw": DJ_JAVA},
        JS_CLUSTER: {"ln_kw": LN_JS,
                     "dj_kw": DJ_JS},
        CPP_CLUSTER: {"ln_kw": LN_CPP,
                      "dj_kw": DJ_CPP}
    }
    def __init__(self, db_manager) -> None:
        self.db_manager:MongoManager = db_manager

    def cluster_count(self, cluster):
        ln_res = self.db_manager.count({"keyword": self.clusters[cluster]["ln_kw"]})
        dj_res = self.db_manager.count({"keyword": self.clusters[cluster]["dj_kw"]})
        return ln_res + dj_res
    
    def count_clusters(self):
        data = {}
        for cluster in self.clusters.keys():
            data[cluster] = self.cluster_count(cluster)
        return data
    
    def get_stats_for_cluster(self, cluster, key):
        pipeline = [  
            {"$match": {
                "keyword": {
                    "$in": [cluster["ln_kw"], cluster["dj_kw"]]
                    }
                }},
            {"$unwind": f"${key}"},
            {"$group": {
                    "_id": f"${key}",  
                    "count": { "$sum": 1 }
                    }},  
            {"$sort": { "count": -1 }} 
            ]
        res = self.db_manager.aggregate(pipeline) 
        return res 
    
    def get_stats_for_clusters(self, key):
        data = {}
        for k, v in self.clusters.items():
            data[k] = self.get_stats_for_cluster(v, key)
        return data
    
    def get_skills_for_clusters(self):
        return self.get_stats_for_clusters("skills")

    def get_levels_for_clusters(self):
        return self.get_stats_for_clusters("level")
    
    def get_workplace_for_clusters(self):
        return self.get_stats_for_clusters("workplace_type")
    
    def get_location_for_clusters(self):
        return self.get_stats_for_clusters("location")


 
 
  
  


 

