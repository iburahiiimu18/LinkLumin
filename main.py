from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import os

app = FastAPI()

# Create the static directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, title: str = Form(...)):
    title_splitted = title.split()
    new_title = "-".join(title_splitted)
    link = f"https://serpapi.com/search.json?engine=google_scholar&q={new_title}"

    params = {
        "q": title,
        "engine": "google_scholar",
        "api_key": "9581bad088e4aac2709eea45342e8eb6b3689c625256cbc321315fef203fd793"
    }

    srch = GoogleSearch(params)
    rlts = srch.get_dict()

    res = rlts["organic_results"]
    research_link = res[0]["link"]
    cited_by_link = res[0]["inline_links"]["cited_by"]["link"]

    response = requests.get(cited_by_link)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.select(".gs_rt a")
    lst = [title.text for title in titles]

    G = nx.Graph()
    G.add_nodes_from(lst)

    for i in range(len(lst)):
        if i != 0:
            G.add_edge(lst[0], lst[i])

    # Adjust node sizes based on text length
    node_sizes = [max(500, len(node) * 100) for node in G.nodes()]

    plt.figure(figsize=(10, 10))
    nx.draw(G, with_labels=True, node_size=node_sizes, font_size=10, node_color='skyblue', font_weight='bold', edge_color='gray')
    plt.savefig("static/graph.png")

    return templates.TemplateResponse("results.html", {"request": request, "research_link": research_link, "cited_by_link": cited_by_link, "titles": lst, "graph": "/static/graph.png"})

# To run the application, use the following command
# uvicorn main:app --reload


"""
Copyright © [2024] Ibrahim Radwan. All rights reserved.
"""
