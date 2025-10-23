# Baseline Test Run

- Command: ..........................FFFFFFFFFFFFFFFFFEEE
ERROR: Coverage failure: total of 12.14 is less than fail-under=85.00
                                                                                                                         [100%]
============================================================ ERRORS ============================================================
___________________ ERROR at setup of TestWorkflowRunnerIntegration.test_full_workflow_execution_integration ___________________
file /workspace/CLI_RESTART/tests/unit/test_workflow_runner.py, line 267
      def test_full_workflow_execution_integration(self, runner, workflow_file, temp_dir):
E       fixture 'runner' not found
>       available fixtures: _class_scoped_runner, _function_scoped_runner, _module_scoped_runner, _package_scoped_runner, _session_scoped_runner, anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, contract_validator, cov, doctest_namespace, event_loop, event_loop_policy, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mock_adapters, mock_workflow_runner, monkeypatch, no_cover, performance_monitor, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, sample_workflow, temp_dir, test_config, test_data_factory, test_security_framework, test_security_policy, test_service, test_utils, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory, workflow_file, workflow_schema
>       use 'pytest --fixtures [testpath]' for help on them.

/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py:267
_____________________ ERROR at setup of TestWorkflowRunnerPerformance.test_workflow_execution_performance ______________________
file /workspace/CLI_RESTART/tests/unit/test_workflow_runner.py, line 302
      def test_workflow_execution_performance(
E       fixture 'runner' not found
>       available fixtures: _class_scoped_runner, _function_scoped_runner, _module_scoped_runner, _package_scoped_runner, _session_scoped_runner, anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, contract_validator, cov, doctest_namespace, event_loop, event_loop_policy, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mock_adapters, mock_workflow_runner, monkeypatch, no_cover, performance_monitor, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, sample_workflow, temp_dir, test_config, test_data_factory, test_security_framework, test_security_policy, test_service, test_utils, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory, workflow_file, workflow_schema
>       use 'pytest --fixtures [testpath]' for help on them.

/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py:302
_______________________ ERROR at setup of TestWorkflowRunnerPerformance.test_large_workflow_performance ________________________
file /workspace/CLI_RESTART/tests/unit/test_workflow_runner.py, line 332
      def test_large_workflow_performance(
E       fixture 'runner' not found
>       available fixtures: _class_scoped_runner, _function_scoped_runner, _module_scoped_runner, _package_scoped_runner, _session_scoped_runner, anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, contract_validator, cov, doctest_namespace, event_loop, event_loop_policy, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mock_adapters, mock_workflow_runner, monkeypatch, no_cover, performance_monitor, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, sample_workflow, temp_dir, test_config, test_data_factory, test_security_framework, test_security_policy, test_service, test_utils, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory, workflow_file, workflow_schema
>       use 'pytest --fixtures [testpath]' for help on them.

/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py:332
=========================================================== FAILURES ===========================================================
________________________________________ TestWorkflowRunner.test_load_workflow_success _________________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c5bd0>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71f8bd90>
workflow_file = PosixPath('/tmp/tmpmb_gvg8n/test_workflow.yaml')
sample_workflow = {'description': 'Sample workflow for testing', 'inputs': {'files': ['**/*.py'], 'lane': 'test'}, 'name': 'Test Workflow', 'policy': {'max_tokens': 1000, 'prefer_deterministic': True}, ...}

    def test_load_workflow_success(self, runner, workflow_file, sample_workflow):
        """Test successful workflow loading."""
>       result = runner._load_workflow(workflow_file)
                 ^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_load_workflow'

tests/unit/test_workflow_runner.py:34: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
______________________________________ TestWorkflowRunner.test_load_workflow_missing_file ______________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c6210>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71e90e10>, temp_dir = PosixPath('/tmp/tmpmb_gvg8n')

    def test_load_workflow_missing_file(self, runner, temp_dir):
        """Test workflow loading with missing file."""
        missing_file = temp_dir / "missing.yaml"
>       result = runner._load_workflow(missing_file)
                 ^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_load_workflow'

tests/unit/test_workflow_runner.py:44: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
______________________________________ TestWorkflowRunner.test_load_workflow_invalid_yaml ______________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c68d0>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d185d0>, temp_dir = PosixPath('/tmp/tmpmb_gvg8n')

    def test_load_workflow_invalid_yaml(self, runner, temp_dir):
        """Test workflow loading with invalid YAML."""
        invalid_file = temp_dir / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content: [")
    
>       result = runner._load_workflow(invalid_file)
                 ^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_load_workflow'

tests/unit/test_workflow_runner.py:53: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
_______________________________________ TestWorkflowRunner.test_validate_schema_success ________________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c7050>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d245d0>
sample_workflow = {'description': 'Sample workflow for testing', 'inputs': {'files': ['**/*.py'], 'lane': 'test'}, 'name': 'Test Workflow', 'policy': {'max_tokens': 1000, 'prefer_deterministic': True}, ...}
workflow_schema = PosixPath('/tmp/tmpmb_gvg8n/schemas/workflow.schema.json')

    def test_validate_schema_success(self, runner, sample_workflow, workflow_schema):
        """Test successful schema validation."""
>       result = runner._validate_schema(sample_workflow)
                 ^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_validate_schema'

tests/unit/test_workflow_runner.py:58: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
_________________________________ TestWorkflowRunner.test_validate_schema_missing_schema_file __________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c7750>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71fc2110>
sample_workflow = {'description': 'Sample workflow for testing', 'inputs': {'files': ['**/*.py'], 'lane': 'test'}, 'name': 'Test Workflow', 'policy': {'max_tokens': 1000, 'prefer_deterministic': True}, ...}

    def test_validate_schema_missing_schema_file(self, runner, sample_workflow):
        """Test schema validation with missing schema file."""
        # Should pass when schema file doesn't exist
>       result = runner._validate_schema(sample_workflow)
                 ^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_validate_schema'

tests/unit/test_workflow_runner.py:64: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
___________________________________ TestWorkflowRunner.test_validate_schema_invalid_workflow ___________________________________

args = (<test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c7e10>,)
keywargs = {'runner': <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71e87cd0>, 'sample_workflow': {'descrip...*/*.py'], 'lane': 'test'}, 'name': 'Test Workflow', 'policy': {'max_tokens': 1000, 'prefer_deterministic': True}, ...}}

    @wraps(func)
    def patched(*args, **keywargs):
>       with self.decoration_helper(patched,
                                    args,
                                    keywargs) as (newargs, newkeywargs):

/root/.pyenv/versions/3.11.12/lib/python3.11/unittest/mock.py:1375: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/root/.pyenv/versions/3.11.12/lib/python3.11/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/root/.pyenv/versions/3.11.12/lib/python3.11/unittest/mock.py:1357: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/root/.pyenv/versions/3.11.12/lib/python3.11/contextlib.py:517: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/root/.pyenv/versions/3.11.12/lib/python3.11/unittest/mock.py:1446: in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <unittest.mock._patch object at 0x7f2a727bba90>

    def get_original(self):
        target = self.getter()
        name = self.attribute
    
        original = DEFAULT
        local = False
    
        try:
            original = target.__dict__[name]
        except (AttributeError, KeyError):
            original = getattr(target, name, DEFAULT)
        else:
            local = True
    
        if name in _builtins and isinstance(target, ModuleType):
            self.create = True
    
        if not self.create and original is DEFAULT:
>           raise AttributeError(
                "%s does not have the attribute %r" % (target, name)
            )
E           AttributeError: <module 'src.cli_multi_rapid.workflow_runner' from '/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py'> does not have the attribute 'jsonschema'

/root/.pyenv/versions/3.11.12/lib/python3.11/unittest/mock.py:1419: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
_________________________________________ TestWorkflowRunner.test_run_workflow_success _________________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d05d0>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d280d0>
workflow_file = PosixPath('/tmp/tmpmb_gvg8n/test_workflow.yaml')
mock_adapters = {'mock_ai': <tests.conftest.MockAIAdapter object at 0x7f2a71d2b750>, 'mock_deterministic': <tests.conftest.MockDeterministicAdapter object at 0x7f2a71d2aed0>}

    def test_run_workflow_success(self, runner, workflow_file, mock_adapters):
        """Test successful workflow execution."""
        # Mock the router and adapter
        with patch.object(runner, "router") as mock_router:
            mock_router.route_step.return_value = Mock(
                adapter_name="mock_deterministic",
                reasoning="Test routing",
                estimated_tokens=50,
            )
            mock_router.registry.get_adapter.return_value = mock_adapters[
                "mock_deterministic"
            ]
    
            result = runner.run(workflow_file, dry_run=False)
    
>           assert result.success is True
E           assert False is True
E            +  where False = WorkflowResult(success=False, error=None, artifacts=[], tokens_used=0, steps_completed=1, coordination_id=None, execution_time=0.005342, parallel_groups=[]).success

tests/unit/test_workflow_runner.py:93: AssertionError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
_________________________________________ TestWorkflowRunner.test_run_workflow_dry_run _________________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d0d10>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d0fb10>
workflow_file = PosixPath('/tmp/tmpmb_gvg8n/test_workflow.yaml')

    def test_run_workflow_dry_run(self, runner, workflow_file):
        """Test workflow dry run execution."""
        result = runner.run(workflow_file, dry_run=True)
    
>       assert result.success is True
E       assert False is True
E        +  where False = WorkflowResult(success=False, error=None, artifacts=[], tokens_used=0, steps_completed=1, coordination_id=None, execution_time=0.005257, parallel_groups=[]).success

tests/unit/test_workflow_runner.py:101: AssertionError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
____________________________________ TestWorkflowRunner.test_run_workflow_with_token_limit _____________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d1450>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d26c10>
workflow_file = PosixPath('/tmp/tmpmb_gvg8n/test_workflow.yaml')
mock_adapters = {'mock_ai': <tests.conftest.MockAIAdapter object at 0x7f2a71d27290>, 'mock_deterministic': <tests.conftest.MockDeterministicAdapter object at 0x7f2a71d24350>}

    def test_run_workflow_with_token_limit(self, runner, workflow_file, mock_adapters):
        """Test workflow execution with token limit."""
        with patch.object(runner, "router") as mock_router:
            # Mock adapter to return high token usage
            high_token_adapter = Mock()
            high_token_adapter.execute.return_value = AdapterResult(
                success=True,
                tokens_used=1500,  # High token usage
                artifacts=["output.json"],
            )
            high_token_adapter.validate_step.return_value = True
    
            mock_router.route_step.return_value = Mock(
                adapter_name="high_token_adapter",
                reasoning="High token routing",
                estimated_tokens=1500,
            )
            mock_router.registry.get_adapter.return_value = high_token_adapter
    
            result = runner.run(workflow_file, max_tokens=1000)
    
            assert result.success is False
>           assert "Token limit exceeded" in result.error
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           TypeError: argument of type 'NoneType' is not iterable

tests/unit/test_workflow_runner.py:127: TypeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
______________________________________ TestWorkflowRunner.test_run_workflow_missing_file _______________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d1b50>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d4be10>, temp_dir = PosixPath('/tmp/tmpmb_gvg8n')

    def test_run_workflow_missing_file(self, runner, temp_dir):
        """Test workflow execution with missing file."""
        missing_file = temp_dir / "missing.yaml"
    
        result = runner.run(missing_file)
    
        assert result.success is False
>       assert "Failed to load workflow" in result.error
E       AssertionError: assert 'Failed to load workflow' in 'Workflow file not found: /tmp/tmpmb_gvg8n/missing.yaml'
E        +  where 'Workflow file not found: /tmp/tmpmb_gvg8n/missing.yaml' = WorkflowResult(success=False, error='Workflow file not found: /tmp/tmpmb_gvg8n/missing.yaml', artifacts=[], tokens_used=0, steps_completed=0, coordination_id=None, execution_time=0.00011, parallel_groups=[]).error

tests/unit/test_workflow_runner.py:136: AssertionError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
_________________________________________ TestWorkflowRunner.test_execute_step_success _________________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727c5090>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d4b1d0>
mock_adapters = {'mock_ai': <tests.conftest.MockAIAdapter object at 0x7f2a71d38e90>, 'mock_deterministic': <tests.conftest.MockDeterministicAdapter object at 0x7f2a71d3b290>}

    def test_execute_step_success(self, runner, mock_adapters):
        """Test successful step execution."""
        step = {
            "id": "test_step",
            "name": "Test Step",
            "actor": "mock_deterministic",
            "with": {"param": "value"},
        }
    
        with patch.object(runner, "router") as mock_router:
            mock_router.route_step.return_value = Mock(
                adapter_name="mock_deterministic",
                reasoning="Test routing",
                estimated_tokens=0,
            )
            mock_router.registry.get_adapter.return_value = mock_adapters[
                "mock_deterministic"
            ]
    
>           result = runner._execute_step(step)
                     ^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'WorkflowRunner' object has no attribute '_execute_step'

tests/unit/test_workflow_runner.py:157: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
__________________________________ TestWorkflowRunner.test_execute_step_adapter_not_available __________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d1e10>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d0fb10>

    def test_execute_step_adapter_not_available(self, runner):
        """Test step execution with unavailable adapter."""
        step = {"id": "test_step", "name": "Test Step", "actor": "unavailable_adapter"}
    
        with patch.object(runner, "router") as mock_router:
            mock_router.route_step.return_value = Mock(
                adapter_name="unavailable_adapter",
                reasoning="Routing to unavailable adapter",
                estimated_tokens=50,
            )
            mock_router.registry.get_adapter.return_value = None
    
>           result = runner._execute_step(step)
                     ^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'WorkflowRunner' object has no attribute '_execute_step'

tests/unit/test_workflow_runner.py:175: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
___________________________________ TestWorkflowRunner.test_execute_step_validation_failure ____________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d2190>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a7193df10>
mock_adapters = {'mock_ai': <tests.conftest.MockAIAdapter object at 0x7f2a7193f8d0>, 'mock_deterministic': <tests.conftest.MockDeterministicAdapter object at 0x7f2a7193f590>}

    def test_execute_step_validation_failure(self, runner, mock_adapters):
        """Test step execution with validation failure."""
        step = {
            "id": "test_step",
            "name": "Test Step",
            "actor": "mock_deterministic",
            "with": {"invalid": "params"},
        }
    
        # Mock adapter to fail validation
        mock_adapter = Mock()
        mock_adapter.validate_step.return_value = False
    
        with patch.object(runner, "router") as mock_router:
            mock_router.route_step.return_value = Mock(
                adapter_name="mock_deterministic",
                reasoning="Test routing",
                estimated_tokens=0,
            )
            mock_router.registry.get_adapter.return_value = mock_adapter
    
>           result = runner._execute_step(step)
                     ^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'WorkflowRunner' object has no attribute '_execute_step'

tests/unit/test_workflow_runner.py:201: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
___________________________________ TestWorkflowRunner.test_execute_step_execution_exception ___________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d2510>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a718ff490>
mock_adapters = {'mock_ai': <tests.conftest.MockAIAdapter object at 0x7f2a71d9fa50>, 'mock_deterministic': <tests.conftest.MockDeterministicAdapter object at 0x7f2a71d9d6d0>}

    def test_execute_step_execution_exception(self, runner, mock_adapters):
        """Test step execution with adapter exception."""
        step = {"id": "test_step", "name": "Test Step", "actor": "mock_deterministic"}
    
        # Mock adapter to raise exception
        mock_adapter = Mock()
        mock_adapter.validate_step.return_value = True
        mock_adapter.execute.side_effect = Exception("Adapter execution failed")
    
        with patch.object(runner, "router") as mock_router:
            mock_router.route_step.return_value = Mock(
                adapter_name="mock_deterministic",
                reasoning="Test routing",
                estimated_tokens=50,
            )
            mock_router.registry.get_adapter.return_value = mock_adapter
    
>           result = runner._execute_step(step)
                     ^^^^^^^^^^^^^^^^^^^^
E           AttributeError: 'WorkflowRunner' object has no attribute '_execute_step'

tests/unit/test_workflow_runner.py:223: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
______________________________________ TestWorkflowRunner.test_process_template_variables ______________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d28d0>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a72d59c50>
sample_workflow = {'description': 'Sample workflow for testing', 'inputs': {'files': '{{ inputs.files }}', 'lane': '{{ inputs.lane }}'}, 'name': 'Test Workflow', 'policy': {'max_tokens': 1000, 'prefer_deterministic': True}, ...}

    def test_process_template_variables(self, runner, sample_workflow):
        """Test template variable processing."""
        # Add template variables to workflow
        workflow_with_templates = sample_workflow.copy()
        workflow_with_templates["inputs"]["files"] = "{{ inputs.files }}"
        workflow_with_templates["inputs"]["lane"] = "{{ inputs.lane }}"
    
>       result = runner._process_template_variables(
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            workflow_with_templates, files="src/**/*.py", lane="feature/test"
        )
E       AttributeError: 'WorkflowRunner' object has no attribute '_process_template_variables'

tests/unit/test_workflow_runner.py:235: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
___________________________________ TestWorkflowRunner.test_should_execute_step_no_condition ___________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d2f10>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71d4b990>

    def test_should_execute_step_no_condition(self, runner):
        """Test step execution condition with no 'when' clause."""
        step = {"id": "test_step", "name": "Test Step", "actor": "mock_deterministic"}
    
>       result = runner._should_execute_step(step, {})
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_should_execute_step'

tests/unit/test_workflow_runner.py:246: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
__________________________________ TestWorkflowRunner.test_should_execute_step_with_condition __________________________________

self = <test_workflow_runner.TestWorkflowRunner object at 0x7f2a727d3550>
runner = <src.cli_multi_rapid.workflow_runner.WorkflowRunner object at 0x7f2a71dc3cd0>

    def test_should_execute_step_with_condition(self, runner):
        """Test step execution condition with 'when' clause."""
        step = {
            "id": "test_step",
            "name": "Test Step",
            "actor": "mock_deterministic",
            "when": "success(previous_step)",
        }
    
        # Currently always returns True (placeholder implementation)
>       result = runner._should_execute_step(step, {})
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'WorkflowRunner' object has no attribute '_should_execute_step'

tests/unit/test_workflow_runner.py:259: AttributeError
---------------------------------------------------- Captured stdout setup -----------------------------------------------------
Initialized 25 adapters (lazy-loaded via factory)
---------------------------------------------------- Captured stderr setup -----------------------------------------------------
--- Logging error ---
Traceback (most recent call last):
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 335, in is_available
    result = subprocess.run(
             ^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'aider'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/logging/__init__.py", line 1113, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
Call stack:
  File "/root/.pyenv/versions/3.11.12/bin/pytest", line 7, in <module>
    sys.exit(console_main())
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 201, in console_main
    code = main()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/config/__init__.py", line 175, in main
    ret: ExitCode | int = config.hook.pytest_cmdline_main(config=config)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 336, in pytest_cmdline_main
    return wrap_session(config, _main)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 289, in wrap_session
    session.exitstatus = doit(config, session) or 0
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 343, in _main
    config.hook.pytest_runtestloop(session=session)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/main.py", line 367, in pytest_runtestloop
    item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 117, in pytest_runtest_protocol
    runtestprotocol(item, nextitem=nextitem)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 130, in runtestprotocol
    rep = call_and_report(item, "setup", log)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 245, in call_and_report
    call = CallInfo.from_call(
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 344, in from_call
    result: TResult | None = func()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 246, in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 164, in pytest_runtest_setup
    item.session._setupstate.setup(item)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/runner.py", line 514, in setup
    col.setup()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/python.py", line 1674, in setup
    self._request._fillfixtures()
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 719, in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 548, in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 639, in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1127, in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 1195, in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
  File "/root/.pyenv/versions/3.11.12/lib/python3.11/site-packages/_pytest/fixtures.py", line 929, in call_fixture_func
    fixture_result = fixturefunc(**kwargs)
  File "/workspace/CLI_RESTART/tests/unit/test_workflow_runner.py", line 25, in runner
    return WorkflowRunner()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/workflow_runner.py", line 138, in __init__
    self.router = Router()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/router.py", line 106, in __init__
    self.adapters = self.registry.get_available_adapters()
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/adapter_registry.py", line 135, in get_available_adapters
    if adapter and adapter.is_available():
  File "/workspace/CLI_RESTART/src/cli_multi_rapid/adapters/ai_editor.py", line 348, in is_available
    self.logger.warning("Aider command not found in PATH")
Message: 'Aider command not found in PATH'
Arguments: ()
------------------------------------------------------ Captured log setup ------------------------------------------------------
WARNING  adapter.ai_editor:ai_editor.py:348 Aider command not found in PATH
======================================================= warnings summary =======================================================
src/cli_multi_rapid/config/models.py:38
  /workspace/CLI_RESTART/src/cli_multi_rapid/config/models.py:38: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'env'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    url: str | None = Field(None, env=["REDIS_URL"])  # optional; if provided we may ping

src/cli_multi_rapid/config/models.py:44
  /workspace/CLI_RESTART/src/cli_multi_rapid/config/models.py:44: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'env'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    openai_api_key: str | None = Field(None, env=["OPENAI_API_KEY"])  # noqa: S105

src/cli_multi_rapid/config/models.py:45
  /workspace/CLI_RESTART/src/cli_multi_rapid/config/models.py:45: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'env'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    anthropic_api_key: str | None = Field(None, env=["ANTHROPIC_API_KEY"])  # noqa: S105

src/cli_multi_rapid/config/models.py:46
  /workspace/CLI_RESTART/src/cli_multi_rapid/config/models.py:46: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'env'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    google_api_key: str | None = Field(None, env=["GOOGLE_API_KEY", "GEMINI_API_KEY"])  # noqa: S105

src/cli_multi_rapid/config/models.py:49
  /workspace/CLI_RESTART/src/cli_multi_rapid/config/models.py:49: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

tests/unit/test_config_validation.py::test_validation_success
tests/unit/test_config_validation.py::test_validation_failure_on_bad_value
tests/unit/test_config_validation.py::test_env_overrides
  /workspace/CLI_RESTART/src/cli_multi_rapid/config/validation.py:22: PydanticDeprecatedSince20: The `parse_obj` method is deprecated; use `model_validate` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    settings = Settings.parse_obj(merged)

tests/unit/test_workflow_runner.py: 18 warnings
  /workspace/CLI_RESTART/tests/unit/test_workflow_runner.py:25: DeprecationWarning: WorkflowRunner is deprecated. Use core.coordinator.WorkflowCoordinator instead. See migration guide in docs/guides/WORKFLOW-RUNNER-MIGRATION.md
    return WorkflowRunner()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================================================== tests coverage ========================================================
_______________________________________ coverage: platform linux, python 3.11.12-final-0 _______________________________________

Name                                                       Stmts   Miss Branch BrPart   Cover   Missing
-------------------------------------------------------------------------------------------------------
src/cli_multi_rapid/__init__.py                                3      0      0      0 100.00%
src/cli_multi_rapid/adapters/__init__.py                      13      7      2      0  40.00%   30-55
src/cli_multi_rapid/adapters/adapter_registry.py             104     58     38      6  39.44%   45-47, 56-62, 72-85, 105-123, 141-158, 162-166, 175-178, 184, 192->195, 200, 204-219
src/cli_multi_rapid/adapters/ai_analyst.py                   112     78     18      0  26.15%   36-93, 106-136, 157-180, 202-246, 266-305, 322-349, 353, 362-369, 377-391, 395-406, 410-412, 416-427, 464, 473
src/cli_multi_rapid/adapters/ai_editor.py                    173    125     44      2  23.96%   41, 62-120, 134-200, 214, 224-236, 242-256, 262-293, 297-299, 303-313, 317-329, 341-346, 350-355, 359, 369, 393->399, 395-396, 409, 417-461, 465-467
src/cli_multi_rapid/adapters/base_adapter.py                 119     54     14      1  49.62%   24-26, 68, 95-96, 107, 118, 130-138, 150-159, 209-210, 214-215, 219-220, 228-245, 288, 292, 300-303, 307-308, 312-317, 322
src/cli_multi_rapid/adapters/bundle_loader.py                142    122     56      0  10.10%   36-161, 169-170, 182-183, 187-249, 253-299, 303-305
src/cli_multi_rapid/adapters/certificate_generator.py        199    173     72      0   9.59%   36-109, 117-118, 130-134, 138, 149-209, 215-252, 258-282, 288-355, 359-374, 383-424, 428-472, 478-509, 513-515
src/cli_multi_rapid/adapters/code_fixers.py                  147    115     40      1  18.72%   46, 72-79, 92-159, 163-178, 182-191, 195-213, 217-241, 245-268, 274-307, 313-327
src/cli_multi_rapid/adapters/contract_validator.py            73     53     16      0  22.47%   37-133, 141-142, 155-156, 160-162
src/cli_multi_rapid/adapters/cost_estimator.py                31     20      2      0  33.33%   33-34, 47-82
src/cli_multi_rapid/adapters/deepseek_adapter.py             252    211     64      0  13.61%   45, 66-129, 142-209, 224-276, 290-351, 358-373, 377-387, 392, 398-429, 435-457, 461-462, 466-476, 481-487, 498-515, 520-522, 528-601, 605-637, 641
src/cli_multi_rapid/adapters/enhanced_bundle_applier.py      260    229     84      0   9.01%   38-127, 135-136, 149-150, 154-159, 163-203, 209-257, 263-328, 334-365, 372-385, 391-413, 419-463, 469-487, 491-497, 501-508, 512-514
src/cli_multi_rapid/adapters/factory.py                      112     50     28      5  52.14%   86-88, 94-102, 106-107, 111-112, 120-121, 140-141, 145-154, 167-173, 210, 223-234, 238-240, 244-249
src/cli_multi_rapid/adapters/git_ops.py                      385    327    108      0  11.76%   52-214, 222-223, 227-245, 254-260, 264-265, 268-271, 274-275, 278-279, 282, 289-296, 302, 306-365, 371-387, 393-416, 420-460, 464-492, 496-511, 516-552, 558-576, 581-651, 658-705, 710-716, 721-753, 757-758, 771-793, 814-817, 827-828, 832-833, 837-842, 846-849, 853-856, 860-870, 874-875
src/cli_multi_rapid/adapters/github_integration.py           446    385    180      0   9.74%   36-39, 60-106, 110-125, 129, 139-143, 151-227, 238-271, 283-318, 329-350, 361-384, 394-413, 422-442, 451-470, 481-503, 514-536, 540-560, 564-575, 582-600, 606-630, 640-659, 663-684, 702-740, 744-770, 787-815, 821-836, 842-858, 864-880, 886-897, 903-918, 924-940, 944-956, 962-976, 982-991, 995-1001, 1005-1011, 1015-1021, 1027, 1039-1046
src/cli_multi_rapid/adapters/import_resolver.py              207    183     92      0   8.03%   33-128, 136-137, 155-194, 198-208, 218-291, 295-301, 306-372, 376-394, 404-457, 461-491, 497-526, 532-545, 549-551
src/cli_multi_rapid/adapters/pytest_runner.py                153    133     46      0  10.05%   35, 48-165, 171-227, 231-271, 281-313, 323-363
src/cli_multi_rapid/adapters/registry.py                       2      2      0      0   0.00%   8-10
src/cli_multi_rapid/adapters/security_scanner.py             215    184     74      0  10.73%   35-128, 136-137, 149-197, 201-225, 229-236, 240-255, 263-294, 303-336, 340-380, 388-422, 430-458, 466-506, 514-560, 568-597, 605-623, 627-659, 663-676, 680-681
src/cli_multi_rapid/adapters/syntax_validator.py             165    142     42      0  11.11%   34-116, 124-125, 140-187, 191-209, 215-235, 241-258, 264-281, 287-305, 311-322, 328-372, 376-378
src/cli_multi_rapid/adapters/tool_adapter_bridge.py          168    134     66      1  15.81%   31-36, 40, 45-107, 113-130, 141-158, 169-181, 192-206, 217-225, 236-267, 278-287, 297, 306
src/cli_multi_rapid/adapters/type_checker.py                 184    162     56      0   9.17%   33-115, 123-124, 141-142, 146-193, 197-208, 212-268, 275-330, 337-376, 383-428, 435-436
src/cli_multi_rapid/adapters/verifier_adapter.py              71     54     20      0  18.68%   37-122, 129-135
src/cli_multi_rapid/adapters/vscode_diagnostics.py           247    211     98      0  11.59%   75-82, 98-173, 179-212, 218-228, 232-272, 276-337, 341-383, 387-431, 435-438, 451-500, 509-542
src/cli_multi_rapid/benchmarking/__init__.py                   2      2      0      0   0.00%   7-14
src/cli_multi_rapid/benchmarking/performance_profiler.py     157    157     34      0   0.00%   8-404
src/cli_multi_rapid/benchmarking/workflow_optimizer.py       105    105     36      0   0.00%   8-290
src/cli_multi_rapid/cancellation.py                           10     10      0      0   0.00%   8-26
src/cli_multi_rapid/cli.py                                    10     10      0      0   0.00%   1-31
src/cli_multi_rapid/commands/__init__.py                       3      3      0      0   0.00%   5-10
src/cli_multi_rapid/commands/cost_commands.py                196    196     58      0   0.00%   9-412
src/cli_multi_rapid/commands/git_commands.py                  95     95     22      0   0.00%   3-221
src/cli_multi_rapid/commands/pr_commands.py                  153    153     52      0   0.00%   9-371
src/cli_multi_rapid/commands/replay.py                       220    220     74      0   0.00%   3-450
src/cli_multi_rapid/commands/repo_init.py                    168    168     56      0   0.00%   3-345
src/cli_multi_rapid/commands/scripts.py                      209    209     84      0   0.00%   3-353
src/cli_multi_rapid/commands/state.py                        115    115     34      0   0.00%   3-195
src/cli_multi_rapid/commands/verify_commands.py              192    192     74      0   0.00%   9-381
src/cli_multi_rapid/commands/workflow_commands.py            141    141     56      0   0.00%   9-280
src/cli_multi_rapid/config/__init__.py                         5      0      0      0 100.00%
src/cli_multi_rapid/config/coordination.py                    53     53      2      0   0.00%   9-87
src/cli_multi_rapid/config/defaults.py                        59      6      0      0  89.83%   301-309, 322, 336-339
src/cli_multi_rapid/config/github_config.py                  118     99     36      0  12.34%   20-22, 26, 30-36, 40-52, 57-72, 76-102, 106-158, 162, 185-187, 191-197, 201-231, 236-249, 254
src/cli_multi_rapid/config/loader.py                          51      2     20      2  94.37%   43, 76
src/cli_multi_rapid/config/models.py                          41      0      0      0 100.00%
src/cli_multi_rapid/config/settings.py                        71     25     14      0  54.12%   265-267, 276-298, 302, 327-330, 340-345
src/cli_multi_rapid/config/validation.py                      14      0      0      0 100.00%
src/cli_multi_rapid/config/validator.py                      155    124     76      0  13.42%   26-28, 33, 38, 42, 46, 50, 54, 76-77, 86-96, 100-131, 135-162, 169-194, 201-211, 218-225, 233-242, 248-256, 262-286, 293-311, 322-345, 360-361, 374-379, 389-390
src/cli_multi_rapid/contracts/__init__.py                      4      4      0      0   0.00%   3-15
src/cli_multi_rapid/contracts/git_snapshot.py                 26     26      0      0   0.00%   3-43
src/cli_multi_rapid/contracts/models.py                       38     38      0      0   0.00%   1-56
src/cli_multi_rapid/contracts/session_metadata.py             19     19      0      0   0.00%   3-32
src/cli_multi_rapid/coordination/__init__.py                   6      0      0      0 100.00%
src/cli_multi_rapid/coordination/conflict_resolver.py        158    158     60      0   0.00%   9-394
src/cli_multi_rapid/coordination/coordinator.py               41     16     10      0  49.02%   23-26, 37, 41, 45, 56-59, 63-64, 68-73
src/cli_multi_rapid/coordination/deadlock_detector.py         81     14     38     11  72.27%   86, 94->92, 97-99, 102->101, 104->101, 107, 123->122, 147->158, 158->166, 166->173, 168->173, 193-207
src/cli_multi_rapid/coordination/dependency_graph.py          17      1      8      2  88.00%   12, 16->15
src/cli_multi_rapid/coordination/dispatcher.py                15     15      4      0   0.00%   1-19
src/cli_multi_rapid/coordination/file_lock.py                 45     45      8      0   0.00%   1-56
src/cli_multi_rapid/coordination/locks.py                     23     23      4      0   0.00%   1-33
src/cli_multi_rapid/coordination/merge_queue.py              198    198     64      0   0.00%   8-417
src/cli_multi_rapid/coordination/queue.py                     29     29      2      0   0.00%   1-42
src/cli_multi_rapid/coordination/redis_lock.py                24     24      4      0   0.00%   1-32
src/cli_multi_rapid/coordination/registry.py                  37     37     10      0   0.00%   1-55
src/cli_multi_rapid/coordination/security.py                 210    210     86      0   0.00%   8-497
src/cli_multi_rapid/coordination/worker.py                    12     12      0      0   0.00%   1-16
src/cli_multi_rapid/core/__init__.py                           5      0      0      0 100.00%
src/cli_multi_rapid/core/artifact_manager.py                 125     94     36      0  19.25%   64-76, 95-99, 111-114, 118, 122, 134-136, 145-147, 162-184, 196-215, 238-258, 277-281, 290-292, 301, 325-341, 360-373
src/cli_multi_rapid/core/coordinator.py                      122     47     30      8  57.24%   89, 101->114, 110->101, 152-192, 216, 222-227, 232, 235, 238, 253->256, 313-337, 352-372
src/cli_multi_rapid/core/executor.py                          84     46     32      2  36.21%   89, 92-119, 154, 166-174, 193-210, 222-249
src/cli_multi_rapid/core/gate_manager.py                     104     74     18      0  24.59%   74-80, 99-133, 147-177, 192-204, 223-276, 295, 307-310, 319-321, 333-337
src/cli_multi_rapid/cost.py                                   10     10      0      0   0.00%   1-23
src/cli_multi_rapid/cost_tracker.py                          291    221    100      0  17.90%   63-67, 91-93, 121-144, 154-168, 176-213, 217-242, 255-267, 287-335, 342, 356-389, 394-442, 456-498, 504-531, 538-550, 556-585, 591
src/cli_multi_rapid/deterministic_engine.py                   95     67     32      0  22.05%   36-63, 88, 91-118, 134-135, 143-184
src/cli_multi_rapid/domain/__init__.py                         2      0      0      0 100.00%
src/cli_multi_rapid/domain/github_client.py                  200    143     72      0  20.96%   43-44, 95-106, 131-220, 224, 228, 232, 236, 240, 251-254, 263-267, 283-302, 320-335, 347-352, 396-415, 440-451, 476-487, 518-536, 549, 574-584, 602-609, 621
src/cli_multi_rapid/enterprise/__init__.py                     6      0      0      0 100.00%
src/cli_multi_rapid/enterprise/base_service.py               191    146     34      0  20.00%   27-29, 69-104, 108-116, 120-161, 165-260, 265-270, 290-336, 340-344, 348-373, 378-382, 386-392, 396-407, 418, 423, 427-430, 438-443
src/cli_multi_rapid/enterprise/config.py                      60     27     18      0  42.31%   64-77, 82-88, 92-115, 119
src/cli_multi_rapid/enterprise/health_checks.py              144    109     24      0  20.83%   51-54, 58-99, 111-116, 120-121, 125-127, 133-149, 159-169, 173-179, 183-195, 199-224, 228-255, 275-280, 284-291, 295-303
src/cli_multi_rapid/enterprise/metrics.py                    169    138     42      0  14.69%   34-48, 53-72, 78-82, 88-92, 101-110, 119-125, 131-133, 138-155, 166-179, 190-202, 208-214, 220-260, 264-315, 321-326, 330-339, 344-348, 352-358
src/cli_multi_rapid/enterprise/workflow_service.py           139    139     34      0   0.00%   8-285
src/cli_multi_rapid/logging/__init__.py                        5      5      0      0   0.00%   9-16
src/cli_multi_rapid/logging/activity_logger.py                52     52     10      0   0.00%   8-133
src/cli_multi_rapid/logging/conversation_logger.py           129    129     40      0   0.00%   11-397
src/cli_multi_rapid/logging/log_rotation.py                   16     16     10      0   0.00%   3-41
src/cli_multi_rapid/logging/unified_logger.py                150    150     30      0   0.00%   11-469
src/cli_multi_rapid/main.py                                   64     64     12      0   0.00%   9-158
src/cli_multi_rapid/output.py                                 78     78     34      0   0.00%   3-168
src/cli_multi_rapid/resilience/circuit_breaker.py             34      6      8      1  83.33%   25-27, 39-41
src/cli_multi_rapid/roles/__init__.py                          2      0      0      0 100.00%
src/cli_multi_rapid/roles/role_manager.py                     31      0      8      4  89.74%   100->102, 103->105, 111->113, 114->116
src/cli_multi_rapid/router.py                                467    370    220      5  15.14%   66-69, 95-96, 139-140, 150-155, 159-169, 175-200, 207-326, 341-346, 350-355, 359-482, 493-527, 531-547, 559-580, 585-593, 597-614, 618-629, 644, 655, 657->653, 673-695, 707-749, 765-834, 845-850, 855-859, 866-915, 922-930, 938-955
src/cli_multi_rapid/routing/__init__.py                        2      0      0      0 100.00%
src/cli_multi_rapid/routing/simplified_router.py              36      2      8      3  88.64%   47, 59->58, 62
src/cli_multi_rapid/security/__init__.py                       6      0      0      0 100.00%
src/cli_multi_rapid/security/audit.py                        272    227     88      0  12.50%   44-45, 52-55, 59, 62-86, 90-114, 119, 123-149, 158-182, 197-210, 222-224, 242-244, 262, 282, 300-322, 335-379, 385-425, 431-459, 469-507, 514-559, 563-584
src/cli_multi_rapid/security/auth.py                         109     85     28      0  17.52%   17, 26-31, 35-45, 49-60, 64-69, 76-78, 84-98, 102-119, 123-127, 131-138, 142-156, 160-169, 173-181, 185-196
src/cli_multi_rapid/security/framework.py                    223    145     44      0  29.21%   110-134, 140-179, 190-230, 234-283, 287-305, 309-319, 327-365, 371-396, 400-423, 430-457, 461-467, 477-485, 490, 495, 500, 504-523, 527-550, 554
src/cli_multi_rapid/security/rbac.py                          47     29      4      0  35.29%   18-20, 26, 32, 36, 40, 44-47, 52-57, 61-62, 66-67, 71-72, 76, 80, 87, 91, 95-107
src/cli_multi_rapid/setup/__init__.py                          4      4      0      0   0.00%   9-13
src/cli_multi_rapid/setup/platform_setup.py                   93     93     34      0   0.00%   8-420
src/cli_multi_rapid/setup/tool_discovery.py                  166    166     62      0   0.00%   8-411
src/cli_multi_rapid/setup/validation.py                      221    221     66      0   0.00%   8-487
src/cli_multi_rapid/shutdown.py                               35     35      2      0   0.00%   1-48
src/cli_multi_rapid/state/__init__.py                          2      2      0      0   0.00%   3-5
src/cli_multi_rapid/state/state_manager.py                   161    161     50      0   0.00%   10-366
src/cli_multi_rapid/validation/__init__.py                     2      0      0      0 100.00%
src/cli_multi_rapid/validation/contract_validator.py         123     92     40      2  20.25%   20-22, 31-33, 36-43, 57->62, 67, 84-110, 122-136, 158-197, 210-211, 224-225, 252-286, 301-302
src/cli_multi_rapid/verifier.py                              228    200     64      0   9.59%   29-30, 44-66, 72-89, 94-102, 109-125, 132-154, 163-202, 213-246, 261-309, 322-363, 376-415, 426-465, 473-529
src/cli_multi_rapid/workflow_engine.py                       123    123     22      0   0.00%   16-249
src/cli_multi_rapid/workflow_runner.py                       131     47     20      5  58.94%   69, 70->exit, 91-92, 142-146, 175-181, 185-192, 214->218, 235, 242-248, 264-288, 332-335, 355-358, 376-379, 396-405
src/db/__init__.py                                             0      0      0      0 100.00%
src/db/connection.py                                          39     39      6      0   0.00%   1-53
src/db/models.py                                              17     17      0      0   0.00%   1-31
src/gui_terminal/__init__.py                                   2      2      0      0   0.00%   3-7
src/gui_terminal/core/__init__.py                              0      0      0      0 100.00%
src/gui_terminal/core/cost_integration.py                     43     43      6      0   0.00%   1-60
src/gui_terminal/core/event_system.py                         23     23      2      0   0.00%   1-40
src/gui_terminal/core/execution_manager.py                   140    140     26      0   0.00%   7-294
src/gui_terminal/core/logging_config.py                       41     41      4      0   0.00%   1-73
src/gui_terminal/core/platform_integration.py                 50     50     12      0   0.00%   1-79
src/gui_terminal/core/pty_backend.py                         121    121     36      0   0.00%   1-174
src/gui_terminal/core/session_manager.py                      18     18      0      0   0.00%   1-28
src/gui_terminal/core/terminal_widget.py                      88     88     18      0   0.00%   1-109
src/gui_terminal/core/ws_client.py                            29     29      6      0   0.00%   1-45
src/gui_terminal/gui_bridge.py                               130    130      8      0   0.00%   8-252
src/gui_terminal/main.py                                      58     58     10      0   0.00%   1-87
src/gui_terminal/plugins/__init__.py                           2      2      0      0   0.00%   3-5
src/gui_terminal/plugins/manager.py                           55     55     18      0   0.00%   1-67
src/gui_terminal/security/__init__.py                          0      0      0      0 100.00%
src/gui_terminal/security/policy_manager.py                   62     62     22      0   0.00%   1-86
src/gui_terminal/ui/__init__.py                                0      0      0      0 100.00%
src/gui_terminal/ui/artifact_viewer.py                       188    188     34      0   0.00%   8-370
src/gui_terminal/ui/cli_interface.py                         241    241     46      0   0.00%   3-407
src/gui_terminal/ui/cost_dashboard.py                        156    156     18      0   0.00%   8-315
src/gui_terminal/ui/execution_dashboard.py                   185    185     46      0   0.00%   8-310
src/gui_terminal/ui/github_panel.py                          123    123     20      0   0.00%   8-209
src/gui_terminal/ui/main_window.py                             8      8      0      0   0.00%   1-10
src/gui_terminal/ui/main_window_modern.py                    229    229     16      0   0.00%   8-416
src/gui_terminal/ui/status_bar.py                              1      1      0      0   0.00%   1
src/gui_terminal/ui/terminal_view.py                           1      1      0      0   0.00%   1
src/gui_terminal/ui/toolbar.py                                 1      1      0      0   0.00%   1
src/gui_terminal/ui/workflow_browser.py                      167    167     54      0   0.00%   8-297
src/gui_terminal/ui/workflow_config.py                       180    180     42      0   0.00%   8-330
src/notifications/__init__.py                                  5      5      0      0   0.00%   3-9
src/notifications/email.py                                    26     26      0      0   0.00%   3-46
src/notifications/slack.py                                    25     25      2      0   0.00%   3-66
src/notifications/webhook.py                                  20     20      2      0   0.00%   3-34
-------------------------------------------------------------------------------------------------------
TOTAL                                                      14542  12403   4116     61  12.14%
FAIL Required test coverage of 85% not reached. Total coverage: 12.14%
=================================================== short test summary info ====================================================
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_load_workflow_success - AttributeError: 'WorkflowRunner' ...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_load_workflow_missing_file - AttributeError: 'WorkflowRun...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_load_workflow_invalid_yaml - AttributeError: 'WorkflowRun...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_validate_schema_success - AttributeError: 'WorkflowRunner...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_validate_schema_missing_schema_file - AttributeError: 'Wo...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_validate_schema_invalid_workflow - AttributeError: <modul...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_run_workflow_success - assert False is True
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_run_workflow_dry_run - assert False is True
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_run_workflow_with_token_limit - TypeError: argument of ty...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_run_workflow_missing_file - AssertionError: assert 'Faile...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_execute_step_success - AttributeError: 'WorkflowRunner' o...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_execute_step_adapter_not_available - AttributeError: 'Wor...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_execute_step_validation_failure - AttributeError: 'Workfl...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_execute_step_execution_exception - AttributeError: 'Workf...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_process_template_variables - AttributeError: 'WorkflowRun...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_should_execute_step_no_condition - AttributeError: 'Workf...
FAILED tests/unit/test_workflow_runner.py::TestWorkflowRunner::test_should_execute_step_with_condition - AttributeError: 'Wor...
ERROR tests/unit/test_workflow_runner.py::TestWorkflowRunnerIntegration::test_full_workflow_execution_integration
ERROR tests/unit/test_workflow_runner.py::TestWorkflowRunnerPerformance::test_workflow_execution_performance
ERROR tests/unit/test_workflow_runner.py::TestWorkflowRunnerPerformance::test_large_workflow_performance
- Date: Thu Oct 23 12:20:30 UTC 2025
- Result: Fail (workflow runner tests failing due to missing private methods).
- Coverage: 12.14% (fail-under 85%).

See  and  for details.
