import os
from functools import lru_cache
from urllib.parse import urlsplit
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("openproject")
def settings():
    base = os.getenv("OPENPROJECT_URL", "").rstrip("/")
    token = os.getenv("OPENPROJECT_API_KEY", "").strip()
    slug = os.getenv("OPENPROJECT_PROJECT_IDENTIFIER", "").strip()
    if not base or not token or not slug:
        raise ValueError("Missing OPENPROJECT_URL, OPENPROJECT_API_KEY or OPENPROJECT_PROJECT_IDENTIFIER")
    parsed = urlsplit(base)
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("OpenProject URL must be an HTTP(S) origin")
    if parsed.scheme == "http":
        allowed_host = os.getenv("OPENPROJECT_HTTP_ALLOWED_HOST", "").strip()
        if os.getenv("OPENPROJECT_ALLOW_HTTP", "false").lower() != "true" or parsed.hostname != allowed_host or not allowed_host:
            raise ValueError("HTTP requires OPENPROJECT_ALLOW_HTTP=true and exact OPENPROJECT_HTTP_ALLOWED_HOST")
    if not all(c.isascii() and (c.isalnum() or c == "-") for c in slug):
        raise ValueError("Invalid project identifier")
    return base, token, slug

def api(method, path, payload=None, params=None):
    base, token, _ = settings()
    if method not in ("GET", "POST", "PATCH") or not path.startswith("/api/v3/"):
        raise ValueError("Disallowed API call")
    with requests.Session() as session:
        session.trust_env = False
        r = session.request(method, base+path, auth=("apikey", token),
            headers={"Accept":"application/hal+json","Content-Type":"application/json"},
            json=payload, params=params, timeout=(5,20), allow_redirects=False)
    if 300 <= r.status_code < 400:
        raise RuntimeError("Redirect refused: check OpenProject URL")
    if not r.ok:
        raise RuntimeError(f"OpenProject HTTP {r.status_code}; check token, permissions, endpoint, or workflow")
    return r.json()

def rows(data):
    return data.get("_embedded", {}).get("elements", [])

@lru_cache(maxsize=1)
def project():
    slug = settings()[2]
    for page in range(1,21):
        results=rows(api("GET","/api/v3/projects",params={"pageSize":100,"offset":page}))
        for entry in results:
            if entry.get("identifier")==slug:
                result=api("GET",f"/api/v3/projects/{entry['id']}")
                if result.get("identifier")==slug: return result
        if len(results)<100: break
    raise LookupError("Fixed project not found or not visible")

def project_id():
    return int(project()["id"])

def scoped(id):
    item=api("GET",f"/api/v3/work_packages/{int(id)}")
    if item.get("_links",{}).get("project",{}).get("href")!=f"/api/v3/projects/{project_id()}":
        raise PermissionError("Out-of-project operation blocked")
    return item

def summary(item):
    base=settings()[0]
    return {"id":item.get("id"),"subject":item.get("subject"),
            "status":item.get("_links",{}).get("status",{}).get("title"),
            "description":(item.get("description") or {}).get("raw",""),
            "url":f"{base}/work_packages/{item.get('id')}"}

def allow_write():
    if os.getenv("OPENPROJECT_ENABLE_WRITES","false").lower()!="true":
        raise PermissionError("Writes disabled")

@mcp.tool()
def project_options()->dict:
    """Read configured project and available types/statuses."""
    pid=project_id()
    return {"project":{"id":pid,"name":project().get("name"),"identifier":project().get("identifier")},
      "types":[{"id":x["id"],"name":x["name"]} for x in rows(api("GET",f"/api/v3/projects/{pid}/types"))],
      "statuses":[{"id":x["id"],"name":x["name"]} for x in rows(api("GET","/api/v3/statuses"))]}

@mcp.tool()
def list_work_items(limit:int=20)->dict:
    """List work items for configured project only."""
    limit=min(max(int(limit),1),100)
    result=api("GET",f"/api/v3/projects/{project_id()}/work_packages",params={"pageSize":limit})
    return {"total":result.get("total"),"items":[summary(x) for x in rows(result)]}

@mcp.tool()
def get_work_item(work_item_id:int)->dict:
    """Read a work item in the configured project."""
    return summary(scoped(work_item_id))

@mcp.tool()
def create_work_item(subject:str,type_id:int,description:str="",status_id:int=0,apply:bool=False)->dict:
    """Preview or create scoped work item (explicit apply required)."""
    pid=project_id()
    if not subject.strip(): raise ValueError("Subject required")
    types=[x["id"] for x in rows(api("GET",f"/api/v3/projects/{pid}/types"))]
    if type_id not in types: raise ValueError("Invalid project type")
    payload={"subject":subject.strip(),"description":{"format":"markdown","raw":description},
             "_links":{"type":{"href":f"/api/v3/types/{type_id}"}}}
    if status_id:
        statuses=[x["id"] for x in rows(api("GET","/api/v3/statuses"))]
        if status_id not in statuses: raise ValueError("Unknown status")
        payload["_links"]["status"]={"href":f"/api/v3/statuses/{status_id}"}
    if not apply: return {"mode":"preview","project_id":pid,"payload":payload}
    allow_write()
    return {"mode":"created","item":summary(api("POST",f"/api/v3/projects/{pid}/work_packages",payload))}

@mcp.tool()
def update_work_item(work_item_id:int,subject:str="",description:str="",status_id:int=0,apply:bool=False)->dict:
    """Preview or update scoped work item with optimistic locking."""
    item=scoped(work_item_id)
    payload={"lockVersion":item["lockVersion"]}
    if subject.strip(): payload["subject"]=subject.strip()
    if description.strip(): payload["description"]={"format":"markdown","raw":description}
    if status_id:
        statuses=[x["id"] for x in rows(api("GET","/api/v3/statuses"))]
        if status_id not in statuses: raise ValueError("Unknown status")
        payload["_links"]={"status":{"href":f"/api/v3/statuses/{status_id}"}}
    if len(payload)==1: raise ValueError("No changes requested")
    if not apply: return {"mode":"preview","current":summary(item),"changes":payload}
    allow_write()
    return {"mode":"updated","item":summary(api("PATCH",f"/api/v3/work_packages/{work_item_id}",payload))}

if __name__=="__main__":
    mcp.run(transport="stdio")
