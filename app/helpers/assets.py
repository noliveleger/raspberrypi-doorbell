# -*- coding: utf-8 -*-
from flask_assets import Environment


class Assets:
    """
    Assets class.
    """

    @staticmethod
    def register(app):
        """
        Registers all assets declared in the configuration.
        :param app: {Flask.app}
        :return: Webasset environment
        """
        from app.config import config  # Cyc

        assets = Environment(app)
        #assets.cache = "{}/tmp/.webassets-cache".format(app.root_path)

        bundles = config.get('ASSETS')
        for name, bundle in bundles.items():
            assets.register(name, bundle)

        return assets
