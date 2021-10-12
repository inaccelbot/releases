from flask import Flask, redirect, request

import fnmatch
import requests

app = Flask(__name__)


@app.route('/api')
def view_func():
    params = request.args

    if 'repo' in params:
        repo = params.get('repo')
        if not '/' in repo:
            repo = 'inaccel/' + repo

        release = None
        if 'tag' in params:
            response = requests.get('https://api.github.com/repos/' + repo +
                                    '/releases')

            if response.status_code == 200:
                releases = response.json()

                def latest(releases, tag):
                    for release in releases:
                        if fnmatch.fnmatch(release['tag_name'], tag):
                            return release

                release = latest(releases, params.get('tag'))
        else:
            response = requests.get('https://api.github.com/repos/' + repo +
                                    '/releases/latest')

            if response.status_code == 200:
                release = response.json()

        if release:
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
