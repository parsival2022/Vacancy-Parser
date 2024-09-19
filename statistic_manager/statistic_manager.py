import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta
from db_manager.mongo_manager import MongoManager
from clusters import *


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
    
    def get_stats_for_cluster(self, cluster_key, key, term=10, w_key_mode=True):
        data = {}
        time = datetime.now() - timedelta(days=term)
        pipeline = [  
            {"$match": {
                "clusters": self.clusters[cluster_key]["name"]}
            },
            {"$match": {"completed": True}},
            {"$addFields": {
                "extr_date_converted": {
                    "$dateFromString": {
                        "dateString": "$extr_date",
                        "format": os.getenv("TIMEFORMAT") }
                      }
            }},
            {"$match": {"extr_date_converted": {"$gte": time}}},
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
        if w_key_mode:
            title = self.clusters[cluster_key]["name"]
            return {title: data}
        else: 
            return data
    
    def get_stats_for_clusters(self, key):
        data = {}
        for cluster_key in self.clusters.keys():
            stat = self.get_stats_for_cluster(cluster_key, key)
            data.update(stat)
        return data
    
    def get_stats_chart(self, field, cl_key=None, chart="bar", **kwargs) -> tuple[list[str], dict]:
        if not cl_key:
            stat = self.get_stats_for_clusters(field)
        else:
            stat = self.get_stats_for_cluster(cl_key, field)
        if field == "technologies":
            stat = self.normalize_technologies(stat, incl_other=True if not cl_key else False)
        filenames = self.generate_pie_chart(stat, **kwargs) if chart == "pie" else self.generate_bar_chart(stat, **kwargs)
        return filenames, stat
    
    def normalize_technologies(self, techs, incl_other=True):
        filt_res = {}
        other_techs = {}
        for cl_k in self.clusters.keys():
            try:
                data = {}
                title = self.clusters[cl_k]["name"]
                for k, v in techs[title].items():
                    if k in self.clusters[cl_k]["technologies"]:
                        data[k] = v
                    elif k in OTHER_TECHS:
                        other_techs[k] = v
                filt_res[title] = data
            except KeyError:
                continue
        if incl_other:
            filt_res.update({"Other tecnologies": other_techs})
        return filt_res
    
    def generate_pie_chart(self, stats):
        filenames = []
        for k, v in stats.items():
            title = k
            tmp = datetime.now().timestamp()
            v = dict(sorted(v.items()))
            labels = [l for l in v.keys()]
            values = [vl for vl in v.values()]
            explodes = [0.3 for v in range(len(values))]
            fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
            wedges, texts, autotexts = ax.pie(values, wedgeprops=dict(width=0.5), 
                                              startangle=-40, autopct='%1.1f%%', 
                                              pctdistance=0, textprops={"color": "w"},
                                              labeldistance=3, explode=explodes, radius=3)
            bbox_props = dict(boxstyle="square,pad=0.6", fc="w", ec="k", lw=0.72)
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
            plt.tight_layout(h_pad=5)
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            filenames.append(filename)
        return filenames
    
    def generate_bar_chart(self, stats, x_label="Vacancies", y_label="Values"): 
        filenames = []
        for k, v in stats.items():
            title = k
            tmp = datetime.now().timestamp()
            labels = [l for l in v.keys()]
            values = [vl for vl in v.values()]
            fig, ax = plt.subplots()
            bars = ax.barh(labels, values)
            ax.bar_label(bars)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            filename = f"{title}_{tmp}_barchart.png"
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            filenames.append(filename)
        return filenames
 
  
  


 

