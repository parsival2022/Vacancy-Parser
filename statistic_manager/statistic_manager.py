import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from db_manager.mongo_manager import MongoManager
from parsers.linkedin_parser import LN_KEYWORDS
from parsers.djinni_parser import DJ_KEYWORDS
from parsers.constants import *


class StatisticManager:
    clusters = CLUSTERS

    def __init__(self, db_manager) -> None:
        self.db_manager:MongoManager = db_manager

    def create_pie(self):
        pass

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
                "clusters": self.clusters[cluster_key]["name"]}
            },
            {"$match": {"completed": True}},
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
            title = self.clusters[cluster_key]["name"]
            data[title] = self.get_stats_for_cluster(cluster_key, key)
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
    
    def get_companies_for_clusters(self):
        return self.get_stats_for_clusters("company")
    
    def get_technologies_for_clusters(self):
        filt_res = {}
        other_d = {}
        res = self.get_stats_for_clusters("technologies")
        for cl_k in self.clusters.keys():
            data = {}
            title = self.clusters[cl_k]["name"]
            for k, v in res[title].items():
                if k in self.clusters[cl_k]["technologies"]:
                    data[k] = v
                elif k in OTHER_TECHS:
                    other_d[k] = v
            filt_res[title] = data
        filt_res.update({"other": other_d})
        return filt_res
    
    def generate_pie_chart(self, stats):
        filenames = []
        for k, v in stats.items():
            title = k
            tmp = datetime.now().timestamp()
            v = dict(sorted(v.items()))
            labels = [l for l in v.keys()]
            values = [vl for vl in v.values()]
            fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
            wedges, texts, autotexts = ax.pie(values, wedgeprops=dict(width=0.5), 
                                              startangle=-40, autopct='%1.1f%%', 
                                              pctdistance=0, textprops={"color": "w"})
            bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
            kw = dict(arrowprops=dict(arrowstyle="-"),
                    bbox=bbox_props, zorder=0, va="center")
            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1)/2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                connectionstyle = f"angle,angleA=0,angleB={ang}"
                kw["arrowprops"].update({"connectionstyle": connectionstyle})
                ax.annotate(f"{labels[i]} {autotexts[i].get_text()}", 
                            xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                            horizontalalignment=horizontalalignment, **kw)

            ax.set_title(title)
            filename = f"{title}_{tmp}_piechart.png"
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            filenames.append(filename)
        return filenames
    
    def generate_bar_chart(self, stats): 
        filenames = []
        for k, v in stats.items():
            title = k
            tmp = datetime.now().timestamp()
            labels = [l for l in v.keys()]
            values = [vl for vl in v.values()]
            fig, ax = plt.subplots()
            bars = ax.barh(labels, values)
            ax.bar_label(bars)
            ax.set_xlabel("Number of requirement")
            ax.set_ylabel("Technologie")
            ax.set_title(title)
            filename = f"{title}_{tmp}_piechart.png"
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            filenames.append(filename)
        return filenames
 
  
  


 

