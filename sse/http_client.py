import os
import requests

def http_main(target, settings, args):
    if args.command == 'crawl':
        settings["project"]["name"] = args.project
        if args.include:
            for x in args.include:
                settings["crawl"]["include"].append(x)
        if args.exclude:
            for x in args.exclude:
                settings["crawl"]["exclude"].append(x)
        res = http_crawl(target, args.project, args.dir, settings["crawl"]["include"], settings["crawl"]["exclude"])
        if res and "data" in res and len(res["data"]) > 0:
            for d in res["data"]:
                if d:
                    print(f'{d[0]}: {len(d[1])} chunks')

    elif args.command == 'query':
        res = http_query(target, args.project, args.query, args.limit)
        common_path = os.path.commonprefix([x[0] for x in res["result"]])
        for f in res["result"]:
            file = f[0]
            distance = f[3]
            print(f'    {file.replace(common_path, "")} [distance {distance:.4}]')

def http_crawl(target, project, directory, include_patterns=None, exclude_patterns=None):
    data = {
        'project': project,
        'dir': directory,
        'include': include_patterns if include_patterns else [],
        'exclude': exclude_patterns if exclude_patterns else []
    }
    response = requests.post(f'http://{target}/crawl', json=data)
    return response.json()

def http_query(target, project, query_string, limit=5):
    data = {
        'project': project,
        'query': query_string,
        'limit': limit
    }
    response = requests.post(f'http://{target}/query', json=data)
    return response.json()

def http_health(target):
    try:
        response = requests.get(f'http://{target}/health')
        response.raise_for_status()  # Will raise an exception if the status is not 200
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return False
