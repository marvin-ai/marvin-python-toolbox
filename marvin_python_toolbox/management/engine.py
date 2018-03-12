#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import click
import json
import os
import sys
import time
import os.path
import re
import shutil
import subprocess
import jinja2
import six
from unidecode import unidecode
import multiprocessing
from marvin_python_toolbox.common.profiling import profiling
from marvin_python_toolbox.common.data import MarvinData
from marvin_python_toolbox.common.config import Config
from .._compatibility import iteritems
from .._logging import get_logger


logger = get_logger('management.engine')


@click.group('engine')
def cli():
    pass


@cli.command('engine-dryrun', help='Marvin Dryrun Utility - Run marvin engines in a stadalone way')
@click.option(
    '--action',
    '-a',
    default='all',
    type=click.Choice(['all', 'acquisitor', 'tpreparator', 'trainer', 'evaluator', 'ppreparator', 'predictor', 'feedback']),
    help='Marvin engine action name')
@click.option('--initial-dataset', '-id', help='Initial dataset file path', type=click.Path(exists=True))
@click.option('--dataset', '-d', help='Dataset file path', type=click.Path(exists=True))
@click.option('--model', '-m', help='Engine model file path', type=click.Path(exists=True))
@click.option('--metrics', '-me', help='Engine Metrics file path', type=click.Path(exists=True))
@click.option('--params-file', '-pf', default='engine.params', help='Marvin engine params file path', type=click.Path(exists=True))
@click.option('--messages-file', '-mf', default='engine.messages', help='Marvin engine predictor input messages file path', type=click.Path(exists=True))
@click.option('--feedback-file', '-ff', default='feedback.messages', help='Marvin engine feedback input messages file path', type=click.Path(exists=True))
@click.option('--response', '-r', default=True, is_flag=True, help='If enable, print responses from engine online actions (ppreparator and predictor)')
@click.option('--profiling', default=False, is_flag=True, help='Enable execute method profiling')
@click.option('--spark-conf', '-c', envvar='SPARK_CONF_DIR', type=click.Path(exists=True), help='Spark configuration folder path to be used in this session')
@click.pass_context
def dryrun_cli(ctx, action, params_file, messages_file, feedback_file, initial_dataset, dataset, model, metrics, response, spark_conf, profiling):
    dryrun(ctx, action, params_file, messages_file, feedback_file, initial_dataset, dataset, model, metrics, response, spark_conf, profiling)


def dryrun(ctx, action, params_file, messages_file, feedback_file, initial_dataset, dataset, model, metrics, response, spark_conf, profiling):

    print(chr(27) + "[2J")

    # setting spark configuration directory
    os.environ["SPARK_CONF_DIR"] = spark_conf if spark_conf else os.path.join(os.environ["SPARK_HOME"], "conf")
    os.environ["YARN_CONF_DIR"] = os.environ["SPARK_CONF_DIR"]

    params = read_file(params_file)
    messages_file = read_file(messages_file)
    feedback_file = read_file(feedback_file)

    if action in ['all', 'ppreparator', 'predictor'] and not messages_file:
        print('Please, set the input message to be used by the dry run process. Use --messages-file flag to informe in a json valid form.')
        sys.exit("Stoping process!")

    if action in ['all', 'feedback'] and not feedback_file:
        print('Please, set the feedback input message to be used by the dry run process. Use --feedback-file flag to informe in a json valid form.')
        sys.exit("Stoping process!")

    if action == 'all':
        pipeline = ['acquisitor', 'tpreparator', 'trainer', 'evaluator', 'ppreparator', 'predictor', 'feedback']
    else:
        pipeline = [action]

    _dryrun = MarvinDryRun(ctx=ctx, messages=[messages_file, feedback_file], print_response=response)

    initial_start_time = time.time()

    for step in pipeline:
        _dryrun.execute(clazz=CLAZZES[step], params=params, initial_dataset=initial_dataset, dataset=dataset, model=model, metrics=metrics,
                        profiling_enabled=profiling)

    print("Total Time : {:.2f}s".format(time.time() - initial_start_time))

    print("\n")


CLAZZES = {
    "acquisitor": "AcquisitorAndCleaner",
    "tpreparator": "TrainingPreparator",
    "trainer": "Trainer",
    "evaluator": "MetricsEvaluator",
    "ppreparator": "PredictionPreparator",
    "predictor": "Predictor",
    "feedback": "Feedback"
}


class MarvinDryRun(object):
    def __init__(self, ctx, messages, print_response):
        self.predictor_messages = messages[0]
        self.feedback_messages = messages[1]
        self.pmessages = []
        self.package_name = ctx.obj['package_name']
        self.kwargs = None
        self.print_response = print_response

    def execute(self, clazz, params, initial_dataset, dataset, model, metrics, profiling_enabled=False):
        self.print_start_step(clazz)

        _Step = dynamic_import("{}.{}".format(self.package_name, clazz))

        if not self.kwargs:
            self.kwargs = generate_kwargs(_Step, params, initial_dataset, dataset, model, metrics)

        step = _Step(**self.kwargs)

        def call_online_actions(step, msg, msg_idx):
            def print_message(result):
                try:
                    print(json.dumps(result, indent=4, sort_keys=True))
                except TypeError:
                    print("Unable to serialize the object returned!")

            if self.print_response:
                    print("\nMessage {} :\n".format(msg_idx))
                    print_message(msg)

            if profiling_enabled:
                with profiling(output_path=".profiling", uid=clazz) as prof:
                    result = step.execute(input_message=msg, params=params)

                prof.disable
                print("\nProfile images created in {}\n".format(prof.image_path))

            else:
                result = step.execute(input_message=msg, params=params)

            if self.print_response:
                print("\nResult for Message {} :\n".format(msg_idx))
                print_message(result)

            return result

        if clazz == 'PredictionPreparator':
            for idx, msg in enumerate(self.predictor_messages):
                self.pmessages.append(call_online_actions(step, msg, idx))

        elif clazz == 'Feedback':
            for idx, msg in enumerate(self.feedback_messages):
                self.pmessages.append(call_online_actions(step, msg, idx))

        elif clazz == 'Predictor':

            self.execute("PredictionPreparator", params, initial_dataset, dataset, model, metrics)

            self.pmessages = self.messages if not self.pmessages else self.pmessages

            for idx, msg in enumerate(self.pmessages):
                call_online_actions(step, msg, idx)

        else:
            if profiling_enabled:
                with profiling(output_path=".profiling", uid=clazz) as prof:
                    step.execute(params=params)

                prof.disable

                print("\nProfile images created in {}\n".format(prof.image_path))

            else:
                step.execute(params=params)

        self.print_finish_step()

    def print_finish_step(self):
        print("\n                                               STEP TAKES {:.4f} (seconds) ".format((time.time() - self.start_time)))

    def print_start_step(self, name):
        print("\n------------------------------------------------------------------------------")
        print("MARVIN DRYRUN - STEP [{}]".format(name))
        print("------------------------------------------------------------------------------\n")
        self.start_time = time.time()


def dynamic_import(clazz):
    components = clazz.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def read_file(filename):
    fname = os.path.join("", filename)
    if os.path.exists(fname):

        print("Engine file {} loaded!".format(filename))

        with open(fname, 'r') as fp:
            return json.load(fp)
    else:
        print("Engine file {} doesn't exists...".format(filename))
        return {}


def generate_kwargs(clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None):
    kwargs = {}

    if params:
        kwargs["params"] = params
    if dataset:
        kwargs["dataset"] = clazz.retrieve_obj(dataset)
    if initial_dataset:
        kwargs["initial_dataset"] = clazz.retrieve_obj(initial_dataset)
    if model:
        kwargs["model"] = clazz.retrieve_obj(model)
    if metrics:
        kwargs["metrics"] = clazz.retrieve_obj(metrics)

    kwargs["persistence_mode"] = 'local'
    kwargs["default_root_path"] = os.path.join(os.getenv('MARVIN_DATA_PATH'), '.artifacts')
    kwargs["is_remote_calling"] = True

    return kwargs


class MarvinEngineServer(object):
    @classmethod
    def create(self, ctx, action, port, workers, rpc_workers, params, initial_dataset, dataset, model, metrics, pipeline):
        package_name = ctx.obj['package_name']

        def create_object(act):
            clazz = CLAZZES[act]
            _Action = dynamic_import("{}.{}".format(package_name, clazz))
            kwargs = generate_kwargs(_Action, params, initial_dataset, dataset, model, metrics)
            return _Action(**kwargs)

        root_obj = create_object(action)
        previous_object = root_obj

        if pipeline:
            for step in list(reversed(pipeline)):
                previous_object._previous_step = create_object(step)
                previous_object = previous_object._previous_step

        server = root_obj._prepare_remote_server(port=port, workers=workers, rpc_workers=rpc_workers)

        print("Starting GRPC server [{}] for {} Action".format(port, action))
        server.start()

        return server


@cli.command('engine-grpcserver', help='Marvin gRPC engine action server starts')
@click.option(
    '--action',
    '-a',
    default='all',
    type=click.Choice(['all', 'acquisitor', 'tpreparator', 'trainer', 'evaluator', 'predictor', 'feedback']),
    help='Marvin engine action name')
@click.option('--initial-dataset', '-id', help='Initial dataset file path', type=click.Path(exists=True))
@click.option('--dataset', '-d', help='Dataset file path', type=click.Path(exists=True))
@click.option('--model', '-m', help='Engine model file path', type=click.Path(exists=True))
@click.option('--metrics', '-me', help='Engine Metrics file path', type=click.Path(exists=True))
@click.option('--params-file', '-pf', default='engine.params', help='Marvin engine params file path', type=click.Path(exists=True))
@click.option('--metadata-file', '-mf', default='engine.metadata', help='Marvin engine metadata file path', type=click.Path(exists=True))
@click.option('--spark-conf', '-c', envvar='SPARK_CONF_DIR', type=click.Path(exists=True), help='Spark configuration path to be used')
@click.option('--max-workers', '-w', default=multiprocessing.cpu_count(), help='Max number of grpc threads workers per action')
@click.option('--max-rpc-workers', '-rw', default=multiprocessing.cpu_count(), help='Max number of grpc workers per action')
@click.pass_context
def engine_server(ctx, action, params_file, metadata_file, initial_dataset, dataset, model, metrics, spark_conf, max_workers, max_rpc_workers):

    print("Starting server ...")

    # setting spark configuration directory
    os.environ["SPARK_CONF_DIR"] = spark_conf if spark_conf else os.path.join(os.environ["SPARK_HOME"], "conf")
    os.environ["YARN_CONF_DIR"] = os.environ["SPARK_CONF_DIR"]

    params = read_file(params_file)
    metadata = read_file(metadata_file)
    default_actions = {action['name']: action for action in metadata['actions']}

    if action == 'all':
        action = default_actions
    else:
        action = {action: default_actions[action]}

    servers = []
    for action_name in action.keys():
        # initializing server configuration
        engine_server = MarvinEngineServer.create(
            ctx=ctx,
            action=action_name,
            port=action[action_name]["port"],
            workers=max_workers,
            rpc_workers=max_rpc_workers,
            params=params,
            initial_dataset=initial_dataset,
            dataset=dataset,
            model=model,
            metrics=metrics,
            pipeline=action[action_name]["pipeline"]
        )

        servers.append(engine_server)

    try:
        while True:
            time.sleep(100)

    except KeyboardInterrupt:
        print("Terminating server ...")
        for server in servers:
            server.stop(0)


TEMPLATE_BASES = {
    'python-engine': os.path.join(os.path.dirname(__file__), 'templates', 'python-engine')
}

RENAME_DIRS = [
    ('project_package', '{{project.package}}'),
]

IGNORE_DIRS = [
    # Ignore service internal templates
    'templates'
]


_orig_type = type


@cli.command('engine-generateenv', help='Generate a new marvin engine environment and install default requirements.')
@click.argument('engine-path', type=click.Path(exists=True))
def generate_env(engine_path):
    dir_ = os.path.basename(os.path.abspath(engine_path))
    venv_name = _create_virtual_env(dir_, engine_path)
    _call_make_env(venv_name)

    print('\nDone!!!!')
    print('Now to workon in the new engine project use: workon {}'.format(venv_name))


@cli.command('engine-generate', help='Generate a new marvin engine project and install default requirements.')
@click.option('--name', '-n', prompt='Project name', help='Project name')
@click.option('--description', '-d', prompt='Short description', default='Marvin engine', help='Library short description')
@click.option('--mantainer', '-m', prompt='Mantainer name', default='Marvin AI Community', help='Mantainer name')
@click.option('--email', '-e', prompt='Mantainer email', default='marvin-ai@googlegroups.com', help='Mantainer email')
@click.option('--package', '-p', default='', help='Package name')
@click.option('--dest', '-d', envvar='MARVIN_HOME', type=click.Path(exists=True), help='Root folder path for the creation')
@click.option('--no-env', is_flag=True, default=False, help='Don\'t create the virtual enviroment')
@click.option('--no-git', is_flag=True, default=False, help='Don\'t initialize the git repository')
def generate(name, description, mantainer, email, package, dest, no_env, no_git):
    type_ = 'python-engine'
    type = _orig_type

    # Process package name

    package = _slugify(package or name)

    # Make sure package name starts with "marvin"
    if not package.startswith('marvin'):
        package = 'marvin_{}'.format(package)

    # Remove "lib" prefix from package name
    if type_ == 'lib' and package.endswith('lib'):
        package = package[:-3]
    # Custom strip to remove underscores
    package = package.strip('_')

    # Append project type to services

    if type_ == 'python-engine' and not package.endswith('engine'):
        package = '{}_engine'.format(package)

    # Process directory/virtualenv name

    # Directory name should use '-' instead of '_'
    dir_ = package.replace('_', '-')

    # Remove "marvin" prefix from directory
    if dir_.startswith('marvin'):
        dir_ = dir_[6:]
    dir_ = dir_.strip('-')

    # Append "lib" to directory name if creating a lib
    if type_ == 'lib' and not dir_.endswith('lib'):
        dir_ = '{}-lib'.format(dir_)

    dest = os.path.join(dest, dir_)

    if type_ not in TEMPLATE_BASES:
        print('[ERROR] Could not found template files for "{type}".'.format(type=type_))
        sys.exit(1)

    project = {
        'name': _slugify(name),
        'description': description,
        'package': package,
        'toolbox_version': os.getenv('TOOLBOX_VERSION'),
        'type': type_
    }

    mantainer = {
        'name': mantainer,
        'email': email,
    }

    context = {
        'project': project,
        'mantainer': mantainer,
    }

    _copy_scaffold_structure(TEMPLATE_BASES[type_], dest)
    _copy_processed_files(TEMPLATE_BASES[type_], dest, context)
    _rename_dirs(dest, RENAME_DIRS, context)

    venv_name = None
    if not no_env:
        venv_name = _create_virtual_env(dir_, dest)
        _call_make_env(venv_name)

    if not no_git:
        _call_git_init(dest)

    print('\nDone!!!!')

    if not no_env:
        print('Now to workon in the new engine project use: workon {}'.format(venv_name))


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def _slugify(text, delim='_'):
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return six.u(delim.join(result))


def _copy_scaffold_structure(src, dest):
    os.mkdir(dest)

    for root, dirs, files in os.walk(src):
        for dir_ in dirs:
            dirname = os.path.join(root, dir_)
            dirname = '{dest}{dirname}'.format(dest=dest, dirname=dirname.replace(src, ''))  # get dirname without source path

            os.mkdir(dirname)


def _copy_processed_files(src, dest, context):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(src))

    print('Processing template files...')

    for root, dirs, files in os.walk(src):

        dirname = root.replace(src, '')[1:]  # get dirname without source path
        to_dirname = os.path.join(dest, dirname)

        should_process = not any(root.startswith(dir_) for dir_ in IGNORE_DIRS)

        for file in files:

            # Ignore trash
            if file == '.DS_Store':
                continue

            from_ = os.path.join(dirname, file)
            to_ = os.path.join(to_dirname, file)

            print('Copying "{0}" to "{1}"...'.format(from_, to_))

            if not should_process:
                shutil.copy(os.path.join(src, from_), to_)
            else:
                template = env.get_template(from_)
                output = template.render(**context)

                with open(to_, 'w') as file:
                    file.write(output)


def _rename_dirs(base, dirs, context):
    for dir_ in dirs:
        dirname, template = dir_
        oldname = os.path.join(base, dirname)

        processed = jinja2.Template(template).render(**context)
        newname = os.path.join(base, processed)

        shutil.move(oldname, newname)

        print('Renaming {0} as {1}'.format(oldname, newname))


def _create_virtual_env(name, dest):
    venv_name = '{}-env'.format(name).replace('_', '-')
    print('Creating virtualenv: {0}...'.format(venv_name))

    command = ['bash', '-c', '. virtualenvwrapper.sh; mkvirtualenv -a {1} {0}; '.format(venv_name, dest)]

    try:
        subprocess.Popen(command, env=os.environ).wait()
    except:
        logger.exception('Could not create the virtualenv!')
        sys.exit(1)

    return venv_name


def _call_make_env(venv_name):
    command = ['bash', '-c', '. virtualenvwrapper.sh; workon {}; make marvin'.format(venv_name)]

    try:
        subprocess.Popen(command, env=os.environ).wait()
    except:
        logger.exception('Could not call make marvin!')
        sys.exit(1)


def _call_git_init(dest):
    command = ['bash', '-c', '/usr/bin/git init {0}'.format(dest)]
    print('Initializing git repository...')
    try:
        subprocess.Popen(command, env=os.environ).wait()
    except OSError:
        print('WARNING: Could not initialize repository!')


@cli.command('engine-httpserver', help='Marvin http api server starts')
@click.option(
    '--action',
    '-a',
    default='all',
    type=click.Choice(['all', 'acquisitor', 'tpreparator', 'trainer', 'evaluator', 'ppreparator', 'predictor', 'feedback']),
    help='Marvin engine action name')
@click.option('--initial-dataset', '-id', help='Initial dataset file path', type=click.Path(exists=True))
@click.option('--dataset', '-d', help='Dataset file path', type=click.Path(exists=True))
@click.option('--model', '-m', help='Engine model file path', type=click.Path(exists=True))
@click.option('--metrics', '-me', help='Engine Metrics file path', type=click.Path(exists=True))
@click.option('--protocol', '-pr', default='', help='Marvin protocol to be loaded during initialization.')
@click.option('--params-file', '-pf', default='engine.params', help='Marvin engine params file path', type=click.Path(exists=True))
@click.option('--spark-conf', '-c', envvar='SPARK_CONF_DIR', type=click.Path(exists=True), help='Spark configuration folder path to be used in this session')
@click.option('--http-host', '-h', default='localhost', help='Engine executor http bind host')
@click.option('--http-port', '-p', default=8000, help='Engine executor http port')
@click.option('--executor-path', '-e', help='Marvin engine executor jar path', type=click.Path(exists=True))
@click.option('--max-workers', '-w', default=multiprocessing.cpu_count(), help='Max number of grpc threads workers per action')
@click.option('--max-rpc-workers', '-rw', default=multiprocessing.cpu_count(), help='Max number of grpc workers per action')
@click.option('--extra-executor-parameters', '-jvm', help='Use to send extra JVM parameters to engine executor process')
@click.pass_context
def engine_httpserver_cli(ctx, action, params_file, initial_dataset, dataset,
                          model, metrics, protocol, spark_conf, http_host, http_port,
                          executor_path, max_workers, max_rpc_workers, extra_executor_parameters):
    engine_httpserver(
        ctx, action, params_file, initial_dataset, dataset,
        model, metrics, protocol, spark_conf, http_host, http_port,
        executor_path, max_workers, max_rpc_workers, extra_executor_parameters
    )


def engine_httpserver(ctx, action, params_file, initial_dataset, dataset, model, metrics, protocol, spark_conf, http_host,
                      http_port, executor_path, max_workers, max_rpc_workers, extra_executor_parameters):
    logger.info("Starting http and grpc servers ...")

    grpcserver = None
    httpserver = None

    def _params(**kwargs):
        params = []
        if kwargs is not None:
            for key, value in iteritems(kwargs):
                if value is not None:
                    params.append("-{0}".format(str(key)))
                    params.append(str(value))
        return params

    try:
        optional_args = _params(id=initial_dataset, d=dataset, m=model, me=metrics, pf=params_file, c=spark_conf)
        grpcserver = subprocess.Popen(['marvin', 'engine-grpcserver', '-a', action, '-w', str(max_workers), '-rw', str(max_rpc_workers)] + optional_args)

        time.sleep(3)

    except:
        logger.exception("Could not start grpc server!")
        sys.exit(1)

    try:
        if not (executor_path and os.path.exists(executor_path)):
            executor_url = Config.get("executor_url", section="marvin")
            executor_path = MarvinData.download_file(executor_url, force=False)

        command_list = ['java']
        command_list.append('-DmarvinConfig.engineHome={}'.format(ctx.obj['config']['inidir']))
        command_list.append('-DmarvinConfig.ipAddress={}'.format(http_host))
        command_list.append('-DmarvinConfig.port={}'.format(http_port))
        command_list.append('-DmarvinConfig.protocol={}'.format(protocol))

        if extra_executor_parameters:
            command_list.append(extra_executor_parameters)

        command_list.append('-jar')
        command_list.append(executor_path)

        httpserver = subprocess.Popen(command_list)

    except:
        logger.exception("Could not start http server!")
        grpcserver.terminate() if grpcserver else None
        sys.exit(1)

    try:
        while True:
            time.sleep(100)

    except KeyboardInterrupt:
        logger.info("Terminating http and grpc servers...")
        grpcserver.terminate() if grpcserver else None
        httpserver.terminate() if httpserver else None
        logger.info("Http and grpc servers terminated!")
        sys.exit(0)


@cli.command('engine-deploy', help='Engine provisioning and deployment command')
@click.option('--provision', is_flag=True, default=False, help='Forces provisioning')
@click.option('--package', is_flag=True, default=False, help='Creates engine package')
@click.option('--skip-clean', is_flag=True, default=False, help='Skips make clean')
def engine_deploy(provision, package, skip_clean):

    TOOLBOX_VERSION = os.getenv('TOOLBOX_VERSION')

    if provision:
        subprocess.Popen([
            "fab",
            "provision",
        ], env=os.environ).wait()
        subprocess.Popen([
            "fab",
            "deploy:version={version}".format(version=TOOLBOX_VERSION),
        ], env=os.environ).wait()
    elif package:
        subprocess.Popen([
            "fab",
            "package:version={version}".format(version=TOOLBOX_VERSION),
        ], env=os.environ).wait()
    elif skip_clean:
        subprocess.Popen([
            "fab",
            "deploy:version={version},skip_clean=True".format(version=TOOLBOX_VERSION),
        ], env=os.environ).wait()
    else:
        subprocess.Popen([
            "fab",
            "deploy:version={version}".format(version=TOOLBOX_VERSION),
        ], env=os.environ).wait()


@cli.command('engine-httpserver-remote', help='Remote HTTP server control command')
@click.option('--http_host', '-h', default='0.0.0.0', help='Engine executor http bind host')
@click.option('--http_port', '-p', default=8000, help='Engine executor http port')
@click.argument('command', type=click.Choice(['start', 'stop', 'status']))
def engine_httpserver_remote(command, http_host, http_port):
    if command == "start":
        subprocess.Popen([
            "fab",
            "engine_start:{host},{port}".format(host=http_host, port=http_port)
        ], env=os.environ).wait()
    elif command == "stop":
        subprocess.Popen([
            "fab",
            "engine_stop",
        ], env=os.environ).wait()
    elif command == "status":
        subprocess.Popen([
            "fab",
            "engine_status",
        ], env=os.environ).wait()
    else:
        print("Usage: marvin engine-httpserver-remote [ start | stop | status ]")
