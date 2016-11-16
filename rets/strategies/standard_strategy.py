from rets.configuration import Configuration


class StandardStrategy(object):

    container = {}
    default_components = {
        'parser.login': '\\rets\Parsers\Login\OneFive',
        'parser.object.single': '\PHRETS\Parsers\GetObject\Single',
        'parser.object.multiple': '\PHRETS\Parsers\GetObject\Multiple',
        'parser.search': '\PHRETS\Parsers\Search\OneX',
        'parser.search.recursive': '\PHRETS\Parsers\Search\RecursiveOneX',
        'parser.metadata.system': '\PHRETS\Parsers\GetMetadata\System',
        'parser.metadata.resource': '\PHRETS\Parsers\GetMetadata\Resource',
        'parser.metadata.class': '\PHRETS\Parsers\GetMetadata\ResourceClass',
        'parser.metadata.table': '\PHRETS\Parsers\GetMetadata\Table',
        'parser.metadata.object': '\PHRETS\Parsers\GetMetadata\Object',
        'parser.metadata.lookuptype': '\PHRETS\Parsers\GetMetadata\LookupType',
    }

    def provide(self):
        pass

    def initialize(self, configuration):
        pass