from urllib.parse import urlparse


class Capabilities(object):

    capabilities = {}

    def add(self, name, uri):
        parse_results = urlparse(uri)
        if parse_results.hostname is None:
            # relative URL given, so build this into an absolute URL
            login_url = self.capabilities.get('Login')
            if not login_url:
                raise ValueError("Cannot automatically determine absolute path for {} given.".format(uri))

            parts = urlparse(login_url)

            new_uri = parts['scheme'] + '://' + parts['netloc'] + ':'
            port = 443 if parts['scheme'] == 'https' else 80
            new_uri += port
            new_uri += uri

            uri = new_uri

        self.capabilities[name] = uri
        return self
