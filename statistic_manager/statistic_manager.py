import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import os
from datetime import datetime, timedelta
from db_manager.mongo_manager import MongoManager
from bot.messages import Messages
from clusters import *


class StatisticManager:
    clusters = CLUSTERS
    pipeline_query_opening = lambda self, cluster_key: [{"$match": {
                                                            "clusters": self.clusters[cluster_key]["name"]}
                                                        },
                                                        {"$match": {"completed": True}}]
    pipeline_query_term = lambda self, time: [{"$addFields": {
                                                "extr_date_converted": {
                                                    "$dateFromString": {
                                                        "dateString": "$extr_date",
                                                        "format": os.getenv("TIMEFORMAT")}
                                                    }
                                            }},
                                            {"$match": {"extr_date_converted": {"$gte": time}}}]
    pipeline_query_for_key = lambda self, key: [{"$unwind": f"${key}"},
                                                {"$group": {
                                                    "_id": f"${key}",  
                                                    "count": { "$sum": 1 }
                                                }},  
                                                {"$sort": { "count": -1 }}]
    pipeline_query_location = lambda self, location: {"$match": {"location": location}}

    def __init__(self, db_manager) -> None:
        self.db_manager:MongoManager = db_manager

    def build_pipeline(self, cluster_key, key, term, location):
        pipeline = []
        pipeline.extend(self.pipeline_query_opening(cluster_key))
        if term:
            time = datetime.now() - timedelta(days=term)
            pipeline.extend(self.pipeline_query_term(time))
        if location:
            pipeline.append(self.pipeline_query_location(location))
        pipeline.extend(self.pipeline_query_for_key(key))
        return pipeline
        
    def normalize_skills(self, skills, limit=10):
        filtered_skills = {key: value for key, value in skills.items() if value >= limit}
        return filtered_skills

    def normalize_technologies(self, techs, cl_name):
        cl_techs = [v["technologies"] for v in self.clusters.values() if v["name"] == cl_name][0]
        filt_data = {k: v for k, v in techs.items() if k in cl_techs}
        filt_other = {k: v for k, v in techs.items() if k in OTHER_TECHS}
        return filt_data, filt_other

    def cluster_count(self, cluster_key):
        res = self.db_manager.count({"clusters": self.clusters[cluster_key]["name"]})
        return res
    
    def count_clusters(self):
        data = {}
        for cluster_key in self.clusters.keys():
            data[cluster_key] = self.cluster_count(cluster_key)
        return data
    
    def get_stats_for_cluster(self, cluster_key, key, title, term=None, location=None, w_key_mode=True):
        data = {}
        cl_title = self.clusters[cluster_key]["name"]
        pipeline = self.build_pipeline(cluster_key, key, term, location)
        res = self.db_manager.aggregate(pipeline) 
        print(res)
        for m_r in [{r["_id"]: r["count"]} for r in res if r["_id"] != NOT_DEFINED]:
            data.update(m_r)
        if key == "technologies":
            normalized_data, other_techs = self.normalize_technologies(data, cl_title)
            print(normalized_data)
            data = normalized_data
        if key == "skills":
            normalized_skills = self.normalize_skills(data, limit=20)
            data = normalized_skills
        t = Messages.generate_title(*title)
        data["graph_title"] = t
        print(data)
        if w_key_mode:
            return {cl_title: data}
        else: 
            return data
    
    def get_stats_for_clusters(self, key, title, term=None, location=None):
        data = {}
        for cl_key in self.clusters.keys():
            title[1] = self.clusters[cl_key]["name"]
            stat = self.get_stats_for_cluster(cl_key, key, title, term=term, location=location)
            data.update(stat)
        return data
    
    def get_stats_chart(self, key, term, location, title, cl_key=None, chart="bar", **kwargs) -> tuple[list[str], dict]:
        if not cl_key:
            stat = self.get_stats_for_clusters(key, title, term=term, location=location)
        else:
            stat = self.get_stats_for_cluster(cl_key, key, title, term=term, location=location)
        filenames = self.generate_pie_chart(stat, **kwargs) if chart == "pie" else self.generate_bar_chart(stat, **kwargs)
        return filenames, stat
    
    def get_comparative_stats_chart(self, query, title, **kwargs):
        results = {}
        term = query.get("term")
        locations = query.get("locations")
        clusters = query.get("clusters")
        options = query.get("options")
        top_res = {}
        for location in locations:
            loc_res = {}
            for cluster_key in clusters:
                cluster_res = {}
                for key in options:
                    key_res = self.get_stats_for_cluster(cluster_key, key, term=term, location=location)
                    cluster_res[key] = key_res
                loc_res[cluster_key] = cluster_res
            top_res[location] = loc_res
        print(top_res)
        filenames = self.generate_comparative_bar_chart(top_res, title, **kwargs)
        return filenames
    
    def generate_pie_chart(self, stats):
        print(stats)
        filenames = []
        for k, v in stats.items():
            title = v.pop("graph_title")
            tmp = datetime.now().timestamp()
            labels = [l for l in v.keys()]
            values = [vl for vl in v.values()]
            total = sum(values)
            legend_labels = [f"{label} ({value / total:.1%})" for label, value in zip(labels, values)]
            explodes = [0.06 for _ in range(len(values))]
            cmap = cm.get_cmap('tab20') 
            colors = cmap(np.linspace(0, 1, len(values)))
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, _ = ax.pie(
                values, 
                startangle=30, 
                explode=explodes,
                colors=colors
            )
            ax.legend(
                wedges, legend_labels, title="Categories", 
                loc="center left", bbox_to_anchor=(-0.5, 0.5), frameon=False
            )
            ax.set_title(title, pad=20, loc='center')
            filename = f"{tmp}_{k}_piechart.png"
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            plt.clf() 
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
            bars = ax.bar(labels, values)
            ax.bar_label(bars)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            filename = f"{title}_{tmp}_barchart.png"
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            filenames.append(filename)
        return filenames
 
  
    def generate_comparative_bar_chart(self, stats:dict, title): 
        width = 0.35
        filenames = []
        tmp = datetime.now().timestamp()
        clusters = stats.keys()
        keys = sorted(set(key for v in stats.values() for key in v.keys()))
        data = {}
        for cl_key in clusters:
            res = []
            for key in keys:
                v = stats[cl_key].get(key) or 0
                res.append(v)
            data[cl_key] = res
        x = np.arange(len(keys))
        fig, ax = plt.subplots()
        for i, item in enumerate(data.items()):
            index = i + 1
            k, v = item
            _x = x - width/2 if index % 2 != 0 else x + width/2
            ax.bar(_x, v, width, label=k)
        # ax.set_xlabel(xlabel)
        # ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(keys)
        ax.legend()
        plt.tight_layout()
        filename = f"{title}_{tmp}_barchart.png"
        plt.savefig(f"charts/{filename}", bbox_inches='tight')
        filenames.append(filename)
        return filenames


 

