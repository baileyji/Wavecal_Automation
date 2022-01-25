import os, errno, sys
from flask_restful import Api, Resource, reqparse
from logging import getLogger
import logging
from .lltf import LLTF


TIMEOUT = 2.0  # timeout for request post
LLTF_CONF_FILE = 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
LLTF_SERVER_PORT = 50001


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    if not path:
        return
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

class MakeFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=0):
        mkdir_p(os.path.dirname(filename))
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


def create_log(name, logfile='', console=True, propagate=False,
               fmt='%(asctime)s %(levelname)s %(message)s (pid=%(process)d)',
               level=logging.DEBUG, stdout=True):

    log = logging.getLogger(name)
    if logfile:
        handler = MakeFileHandler(logfile)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(level)
        log.addHandler(handler)
    else:
        getLogger().debug('not adding file handler to {}'.format(name))

    if console and not len(list(filter(lambda h: type(h) == logging.StreamHandler, log.handlers))):
        handler = logging.StreamHandler(sys.stdout if stdout else sys.stderr)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(level)
        log.addHandler(handler)
    else:
        getLogger().debug('not adding console handler to {}'.format(name))

    log.setLevel(level)
    log.propagate = propagate

    return log



class LLTFAPI(Resource):
    def post(self):
        """
        argument data is sent in a json blob dictionary

        Arguments need to include the command type:
            ie. status', 'move', 'dither', 'stop', 'queryMove', 'queryDither'
        Additional arguments are passed to the function as required
        """
        parser = reqparse.RequestParser()
        choices = ('status', 'set_wave')
        parser.add_argument('command', type=str, required=True, choices=choices,
                            help='Command must be one of: '+', '.join(choices), location='json')
        args = parser.parse_args()
        if args.command == 'status':
            ret = lltf.status()
            return ret, 200
        elif args.command == 'set_wave':
            parser.add_argument('wavelength', type=float, required=True,
                                help='Specify wavelength (nm)', location='json')
            args = parser.parse_args()
            try:
                ret = lltf.set_wave(args.wavelength)
                return ret, 200
            except ValueError as e:
                return str(e), 400
            except Exception as e:
                return str(e), 500


if __name__ == '__main__':
    from flask import Flask

    create_log('LLTFServer', console=True, propagate=False,
               fmt='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    app = Flask(__name__, static_url_path="")
    flasklog = getLogger('werkzeug')
    flasklog.setLevel('ERROR')
    api = Api(app)
    api.add_resource(LLTFAPI, '/lltf', endpoint='lltf')
    lltf = LLTF(LLTF_CONF_FILE)
    app.run(host='0.0.0.0', debug=False, port=LLTF_SERVER_PORT)
