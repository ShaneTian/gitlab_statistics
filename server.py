#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gitlab
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.debug = True

gitlab_cli = gitlab.Gitlab("http://gitlab.com",
                           private_token="******",
                           timeout=50,
                           api_version="4")

    
def get_gitlab(t1, t2):
    res = []
    projects = gitlab_cli.projects.list(membership=True, all=True)
    for project in projects:
        for branch in project.branches.list():
            commits = project.commits.list(
                all=True,
                query_parameters={
                    "since": t1,
                    "until": t2,
                    "ref_name": branch.name
                }
            )
            for commit in commits:
                com = project.commits.get(commit.id)
                pro={}    
                try:
                    pro["project_name"] = project.path_with_namespace
                    pro["author_name"] = com.author_name
                    pro["branch"] = branch.name
                    pro["additions"] = com.stats["additions"]
                    pro["deletions"] = com.stats["deletions"]
                    pro["commit_num"] = com.stats["total"]                  
                    res.append(pro)
                except:
                    print("error...")
    return res


@app.route("/", methods = ["GET", "POST"])
def data():
    if request.method == "GET":
        return render_template("gitlab.html")
    else:
        ret = {}
        t1 = request.form.get("t1")
        t2 = request.form.get("t2")
        for ele in get_gitlab(t1, t2):
            key = ele["project_name"] + ele["author_name"] + ele["branch"]
            if key not in ret:
                ret[key] = ele
                ret[key]["commit_total"] = 1
            else:
                ret[key]["additions"] += ele["additions"]
                ret[key]["deletions"] += ele["deletions"]
                ret[key]["commit_num"] += ele["commit_num"]
                ret[key]["commit_total"] += 1

        res = []
        for k, v in ret.items():
            v["项目名"] = v.pop("project_name")
            v["开发者"] = v.pop("author_name")
            v["分支"] = v.pop("branch")
            v["添加代码行数"] = v.pop("additions")
            v["删除代码行数"] = v.pop("deletions")
            v["提交总行数"] = v.pop("commit_num")
            v["提交次数"] = v["commit_total"]
            res.append(v)

        return render_template("gitlab.html", msg=res)


if __name__ == "__main__":
    app.run(port="8067")
