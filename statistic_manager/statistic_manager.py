from db_manager.mongo_manager import MongoManager
from parsers.linkedin_parser import LN_KEYWORDS
from parsers.djinni_parser import DJ_KEYWORDS
from parsers.constants import *


class StatisticManager:
    clusters = CLUSTERS

    def __init__(self, db_manager) -> None:
        self.db_manager:MongoManager = db_manager

    def cluster_count(self, cluster_key):
        res = self.db_manager.count({"clusters": self.clusters[cluster_key]["name"]})
        return res
    
    def count_clusters(self):
        data = {}
        for cluster_key in self.clusters.keys():
            data[cluster_key] = self.cluster_count(cluster_key)
        return data
    
    def get_stats_for_cluster(self, cluster_key, key):
        data = {}
        pipeline = [  
            {"$match": {
                "clusters": self.clusters[cluster_key]["name"]}},
            {"$unwind": f"${key}"},
            {"$group": {
                    "_id": f"${key}",  
                    "count": { "$sum": 1 }
                    }},  
            {"$sort": { "count": -1 }} 
            ]
        res = self.db_manager.aggregate(pipeline) 
        for m_r in [{("Not defined" if r["_id"] == NOT_DEFINED else r["_id"]): r["count"]} for r in res]:
            data.update(m_r)
        return data
    
    def get_stats_for_clusters(self, key):
        data = {}
        for cluster_key in self.clusters.keys():
            data[cluster_key] = self.get_stats_for_cluster(cluster_key, key)
        return data
    
    def get_sources_for_clusters(self):
        return self.get_stats_for_clusters("source")
    
    def get_skills_for_clusters(self):
        return self.get_stats_for_clusters("skills")

    def get_levels_for_clusters(self):
        return self.get_stats_for_clusters("level")
    
    def get_workplace_for_clusters(self):
        return self.get_stats_for_clusters("workplace_type")
    
    def get_location_for_clusters(self):
        return self.get_stats_for_clusters("location")
    
    def get_technologies_for_clusters(self):
        filt_res = {}
        other_d = {}
        res = self.get_stats_for_clusters("technologies")
        for cl_k in self.clusters.keys():
            data = {}
            for k, v in res[cl_k].items():
                if k in self.clusters[cl_k]["technologies"]:
                    data[k] = v
                elif k in OTHER_TECHS:
                    other_d[k] = v
            filt_res[cl_k] = data
        filt_res.update({"other": other_d})
        return filt_res
    



 
 
  
  


 

