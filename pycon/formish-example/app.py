import pkg_resources
from restish import app, templating
from restish.contrib.makorenderer import MakoRenderer

from pycon.resource import Root


def make_renderer():
    """
    Create and return a restish.templating "renderer".
    """
    return MakoRenderer(
            directories=[
                pkg_resources.resource_filename('pycon', 'template')
                ],
            input_encoding='utf-8', output_encoding='utf-8',
            default_filters=['unicode', 'h']
            )


def application(environ, start_response):
    # Add templating config to environ
    renderer = make_renderer()
    environ['restish.templating'] = templating.Templating(renderer)
    return app.RestishApp(Root())(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8080, application)
    server.serve_forever()

