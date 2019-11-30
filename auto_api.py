from flask import Flask, Blueprint, request, jsonify
import inspect
from functools import wraps

# == queue_controller_routes ==
# get initial prices


def instantiate_service(module_name):
    exec(f'global svc; svc = {module_name}(); print(svc)')
    return [func for func in dir(svc) if callable(getattr(svc, func)) and not func.startswith("__")]


class Service:
    """
    I'm service and I know it
    """
    @staticmethod
    def get_demo():
        return '<marquee><h1>' + inspect.currentframe().f_code.co_name + '</marquee>'

    @staticmethod
    def get_a(p1):
        return inspect.currentframe().f_code.co_name + str(p1)

    def get_b(self, pa1, pa2, pa3):
        return inspect.currentframe().f_code.co_name + str([pa1, pa2, pa3])

    def get_c(self):
        return self.__doc__

    def get_post_d(self, par1):
        return inspect.currentframe().f_code.co_name

    def delete_e(self, param1):
        return inspect.currentframe().f_code.co_name


class BuildAPI:
    """
    Returns a decorator that logs the performance metrics of the decorated function
    """

    PARAM_SEPARATOR = '&'

    def __init__(self, fn_names_list, http_methods_list, endpoints_list=None, application_name='Default'):
        endpoints_list = fn_names_list if endpoints_list is None else endpoints_list
        self.service = Service
        self.app = Flask(__name__)
        self.api_routes = Blueprint(application_name, __name__)
        self.fn_names_list = fn_names_list
        self.endpoints_list = endpoints_list
        self.http_methods_list = http_methods_list
        self.var_rule = ''
        self.fn_pointer = None
        self.fn_params = ''
        for index in range(len(endpoints_list) - 1):
            self.index = index
            print("Processing endpoint", endpoints_list[index])
            self.add_endpoint()

    class ArgumentsBucket:
        """
        Will hold the functions necessary for interfacing
        """
        pass

    def parametrize(self):
        """
        Returns a decorator that logs the performance metrics of the decorated function
        """
        print("Received index:", index)

    @staticmethod
    def make_fun(fn_name, fn_params):
        complete_params = ', '.join(fn_params)
        fn_body = ""
        fn_body += "from flask import request\n"
        fn_body += "\n"
        fn_body += "\n"
        fn_body += f"def {fn_name}():\n"
        for param in fn_params:
            fn_body += ("\t" + param + ' = request.args.get("' + param + '")\n')
        fn_body += f"\treturn svc.{fn_name}({complete_params})"
        print(f'=== Creating {fn_name} ===')
        print(fn_body)
        print('==================')
        exec(fn_body)
        return locals()[fn_name]

    def add_endpoint(self):
        index = self.index
        self.fn_name = self.fn_names_list[index]
        self.endpoints = self.endpoints_list[index]
        self.http_methods = self.http_methods_list[index]
        if self.fn_name in dir(self.ArgumentsBucket):
            print("Duplicate definition for function!")
            return

        self.fn_pointer = getattr(self.service, self.fn_name)
        self.fn_params = list(inspect.signature(self.fn_pointer).parameters.keys())
        if 'self' in self.fn_params:
            self.fn_params.remove('self')
        number_of_arguments = len(self.fn_params)
        for i in range(number_of_arguments):
            self.var_rule += '<' + self.fn_params[i] + '>'
            setattr(self.ArgumentsBucket, 'param' + str(i), None)
            if i != number_of_arguments - 1:
                self.var_rule += self.PARAM_SEPARATOR

        proxy_fn = self.make_fun(self.fn_name, self.fn_params)
        setattr(self.ArgumentsBucket, self.fn_name, proxy_fn)
        self.api_routes.route("/" + self.fn_name)(proxy_fn)
        print(' '.join([">>>> Binding:", self.fn_name, "to:", self.endpoints, "through:", str(self.http_methods),
                        "parsing:", str(self.fn_params), "perceived:", str(self.var_rule), "by:", str(proxy_fn)]))

        self.var_rule = ''


if __name__ == "__main__":
    fn_names_list = instantiate_service('Service')

    http_methods_list = []
    instance_list = []
    for index in range(len(fn_names_list)):
        for http_method in ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']:
            if http_method in fn_names_list[index].upper():
                instance_list.append(http_method)
        if not instance_list:
            http_methods_list.append('GET')
        else:
            http_methods_list.append(instance_list)
        instance_list = []
    b_api = BuildAPI(fn_names_list, http_methods_list)


    def create_app(application_name: str):
        """Initialize the core application."""
        app = Flask(application_name, instance_relative_config=False)
        app.url_map.strict_slashes = False
        app.register_blueprint(b_api.api_routes, url_prefix='')

        @app.route('/')
        def root():
            return '</br>'.join([
                '{appName} application running'.format(appName=application_name)])
        root()
        return app

    auto_api = create_app('auto_api')
    print('Recognized Map...')
    print(auto_api.url_map)
    auto_api.run(debug=True, host='0.0.0.0')
