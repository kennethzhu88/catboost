#!/usr/bin/env python
#
# Build dynamic library with JNI using user-provided arguments and place it to resources directory
# of Maven package
#
# NOTE: this script must be python2/3 compatible

from __future__ import absolute_import, print_function

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile


@contextlib.contextmanager
def _tempdir(prefix=None):
    tmp_dir = tempfile.mkdtemp(prefix=prefix)
    yield tmp_dir
    # TODO(yazevnul): log error
    shutil.rmtree(tmp_dir, ignore_errors=True)


def _get_platform():
    if sys.platform.startswith('linux'):
        return 'linux'
    return sys.platform


def _get_arcadia_root():
    arcadia_root = None
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    while True:
        if os.path.isfile(os.path.join(path, '.arcadia.root')):
            arcadia_root = path
            break

        if path == os.path.dirname(path):
            break

        path = os.path.dirname(path)

    assert arcadia_root is not None, 'you are probably trying to use this script with repository being checkout not from the root'
    return arcadia_root


def _get_ya_path():
    ya_path = os.path.join(_get_arcadia_root(), 'ya')
    assert os.path.isfile(ya_path), 'no `ya` in arcadia root'
    assert os.access(ya_path, os.X_OK), '`ya` must be executable'
    return ya_path


def _get_package_resources_dir():
    return os.path.join(
        _get_arcadia_root(),
        os.path.join(*'catboost/jvm-packages/catboost4j-prediction/src/main/resources/lib'.split('/')))


def _get_native_lib_dir(relative=None):
    if relative is None:
        relative = _get_arcadia_root()
    return os.path.join(
        relative,
        os.path.join(*'catboost/jvm-packages/catboost4j-prediction/src/native'.split('/')))


def _ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        import errno
        if e.errno != errno.EEXIST:
            raise


def _main():
    ya_path = _get_ya_path()
    resources_dir = _get_package_resources_dir()
    native_lib_dir = _get_native_lib_dir()
    env = os.environ.copy()

    print('building dynamic library with `ya`', file=sys.stderr)
    sys.stderr.flush()

    # TODO(yazevnul): maybe replace `python` with `sys.executable`?
    ya_tool = [ya_path] if _get_platform() != 'win32' else ['python', ya_path]
    with _tempdir(prefix='catboost_build-') as build_output_dir:
        ya_make = ya_tool + ['make'] + sys.argv[1:] + [native_lib_dir, '--output', build_output_dir]
        subprocess.check_call(
            ya_make,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr)

        _ensure_dir_exists(resources_dir)
        native_lib_name = {
            'darwin': 'libcatboost4j-prediction.dylib',
            'win32': 'catboost4j-prediction.dll',
            'linux': 'libcatboost4j-prediction.so',
        }[_get_platform()]

        print('copying dynamic library to resources/lib', file=sys.stderr)
        shutil.copy(
            os.path.join(_get_native_lib_dir(build_output_dir), native_lib_name),
            resources_dir)


if '__main__' == __name__:
    _main()
