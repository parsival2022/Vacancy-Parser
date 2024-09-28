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
    chart_name = "charts"
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
    pipeline_query_for_count = {"$group": {
                                    "_id": None,  
                                    "count": {"$sum": 1}}
                                }
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
        if key:
            pipeline.extend(self.pipeline_query_for_key(key))
        else: 
            pipeline.append(self.pipeline_query_for_count)
        return pipeline
        
    def normalize_skills(self, skills, limit=10):
        filtered_skills = {key: value for key, value in skills.items() if value >= limit}
        return filtered_skills

    def normalize_technologies(self, techs, cl_name):
        cl_techs = [v["technologies"] for v in self.clusters.values() if v["name"] == cl_name][0]
        filt_data = {k: v for k, v in techs.items() if k in cl_techs}
        filt_other = {k: v for k, v in techs.items() if k in OTHER_TECHS}
        return filt_data, filt_other
    
    def get_stats_for_cluster(self, cluster_key, key, title=[], term=None, location=None, w_key_mode=True):
        data = {}
        cl_title = self.clusters[cluster_key]["name"]
        pipeline = self.build_pipeline(cluster_key, key, term, location)
        res = self.db_manager.aggregate(pipeline) 
        for m_r in [{(r["_id"] if r["_id"] else "total"): r["count"]} for r in res if r["_id"] != NOT_DEFINED]:
            data.update(m_r)
        if key == "technologies":
            normalized_data, other_techs = self.normalize_technologies(data, cl_title)
            data = normalized_data
        if key == "skills":
            normalized_skills = self.normalize_skills(data, limit=20)
            data = normalized_skills
        if title:
            t = Messages.generate_title(*title)
            data["graph_title"] = t
        return {cl_title: data} if w_key_mode else data

    def get_stats_for_clusters(self, key, title=[], term=None, location=None):
        data = {}
        for cl_key in self.clusters.keys():
            title[1] = self.clusters[cl_key]["name"]
            stat = self.get_stats_for_cluster(cl_key, key, title=title, term=term, location=location)
            data.update(stat)
        return data
    
    def generate_pie_chart(self, stats):
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
            if not os.path.exists(self.chart_name):
                os.makedirs(self.chart_name)
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
            if not os.path.exists(self.chart_name):
                os.makedirs(self.chart_name)
            plt.savefig(f"charts/{filename}", bbox_inches='tight')
            filenames.append(filename)
        return filenames
 
    def generate_comparative_bar_chart(self, stats:dict, title): 
        filenames = []
        location_keys = []
        cluster_keys = []
        values_to_draw = []
        data = []
        tmp = datetime.now().timestamp()
        for loc_key, loc_obj in stats.items():
            location_keys.append(loc_key)
            for cl_key, cl_obj in loc_obj.items():
                cluster_keys.append(cl_key)
                for lvl_key, lvl_obj in cl_obj.items():
                    values_to_draw.append(lvl_obj)
        if all(not el for el in values_to_draw):
            return None, None
        keys_to_compare = location_keys if len(location_keys) > 1 else cluster_keys
        keys = list(set(key for v in values_to_draw for key in v.keys()))
        for i, comp_key in enumerate(keys_to_compare):
            obj = values_to_draw[i]
            res = {}
            for key in keys:
                v = obj.get(key) or 0
                res[key] = v
            data.append(res)
        x = np.arange(len(keys))
        fig, ax = plt.subplots(figsize=(10, 8))
        num_bars = len(data)
        width = 0.8 / num_bars
        offset = np.linspace(-0.4, 0.4, num_bars, endpoint=False)
        for i, item in enumerate(data):
            label = keys_to_compare[i]
            values = item.values()
            _x = x + offset[i] 
            ax.bar(_x, values, width, label=label)
        ax.set_title(title, pad=20)
        ax.set_xticks(x + offset.mean())
        if len(keys) == 1:
            keys = ["Quantity" for key in keys if key == "None"]
        ax.set_xticklabels(keys, rotation=45, ha="right")
        ax.legend()
        plt.tight_layout(pad=3)
        filename = f"{title}_{tmp}_barchart.png"
        if not os.path.exists(self.chart_name):
            os.makedirs(self.chart_name)
        plt.savefig(f"charts/{filename}", bbox_inches='tight')
        filenames.append(filename)
        return filenames, stats
    
    def get_stats_chart(self, key, term, location, title, cl_key=None, chart="bar", **kwargs) -> tuple[list[str], dict]:
        if not cl_key:
            stat = self.get_stats_for_clusters(key, title=title, term=term, location=location)
        else:
            stat = self.get_stats_for_cluster(cl_key, key, title=title, term=term, location=location)
        filenames = self.generate_pie_chart(stat, **kwargs) if chart == "pie" else self.generate_bar_chart(stat, **kwargs)
        return filenames, stat
    
    def get_comparative_stats_chart(self, query, title, **kwargs):
        term = query.get("term")
        locations = query.get("locations")
        clusters = query.get("clusters")
        options = query.get("options")
        top_res = {}
        for location in locations:
            loc_res = {}
            for cl_key in clusters:
                cl_name = self.clusters.get(cl_key)["name"]
                cluster_res = {}
                for key in options:
                    key_res = self.get_stats_for_cluster(cl_key, key, term=term, location=location, w_key_mode=False)
                    cluster_res[(key.title() if key else "Total")] = key_res
                loc_res[cl_name] = cluster_res
            top_res[location] = loc_res
        print(top_res)
        filenames, stats = self.generate_comparative_bar_chart(top_res, title, **kwargs)
        return filenames, stats




 

