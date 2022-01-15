from flask import Flask, redirect, request

import fnmatch
import itertools
import os
import requests

app = Flask(__name__)

actor = os.getenv('GITHUB_ACTOR')
token = os.getenv('GITHUB_TOKEN')


@app.route('/api')
def view_func():
    args = request.args
    headers = request.headers

    if 'repo' in args:
        repo = args.get('repo')
        if not '/' in repo:
            repo = '{}/{}'.format(actor, repo)

        if repo.startswith('{}/'.format(actor)):
            authorization = 'token {}'.format(token)
        else:
            authorization = None

        if 'tag' in args:
            for page in itertools.count(1):
                response = requests.get(
                    'https://api.github.com/repos/{}/releases?page={}&per_page=100'
                    .format(repo, page),
                    headers={
                        'Authorization':
                        headers.get('Authorization', authorization)
                    })

                if response.status_code != 200:
                    return '', response.status_code
                elif response.json():
                    for release in response.json():
                        if fnmatch.fnmatch(release['tag_name'],
                                           args.get('tag')):
                            break
                    else:
                        continue
                    break
                else:
                    return '', 404  # Not Found
        else:
            response = requests.get(
                'https://api.github.com/repos/{}/releases/latest'.format(repo),
                headers={
                    'Authorization': headers.get('Authorization',
                                                 authorization)
                })

            if response.status_code != 200:
                return '', response.status_code
            elif response.json():
                release = response.json()
            else:
                return '', 404  # Not Found

        if 'asset' in args:
            for asset in release['assets']:
                if asset['name'] == args.get('asset'):
                    return redirect(asset['browser_download_url'])
        elif 'zip' in args:
            return redirect(release['zipball_url'])
        elif 'tar' in args:
            return redirect(release['tarball_url'])
        elif release['assets']:
            return redirect(release['assets'][0]['browser_download_url'])

        return '', 404  # Not Found
    else:
        return '', 400  # Bad Request
