from flask import Flask, redirect, request

import fnmatch
import itertools
import requests

app = Flask(__name__)


@app.route('/api')
def view_func():
    params = request.args

    if 'repo' in params:
        repo = params.get('repo')
        if not '/' in repo:
            repo = 'inaccel/' + repo

        if 'tag' in params:
            for page in itertools.count(1):
                response = requests.get(
                    'https://api.github.com/repos/{}/releases?page={}&per_page=100'
                    .format(repo, page))

                if response.status_code != 200:
                    return '', response.status_code
                elif response.json():
                    for release in response.json():
                        if fnmatch.fnmatch(release['tag_name'],
                                           params.get('tag')):
                            break
                    else:
                        continue
                    break
                else:
                    return '', 404  # Not Found
        else:
            response = requests.get(
                'https://api.github.com/repos/{}/releases/latest'.format(repo))

            if response.status_code != 200:
                return '', response.status_code
            elif response.json():
                release = response.json()
            else:
                return '', 404  # Not Found

        if 'asset' in params:
            for asset in release['assets']:
                if asset['name'] == params.get('asset'):
                    return redirect(asset['browser_download_url'])
        elif 'zip' in params:
            return redirect(release['zipball_url'])
        elif 'tar' in params:
            return redirect(release['tarball_url'])
        elif release['assets']:
            return redirect(release['assets'][0]['browser_download_url'])

        return '', 404  # Not Found
    else:
        return '', 400  # Bad Request
