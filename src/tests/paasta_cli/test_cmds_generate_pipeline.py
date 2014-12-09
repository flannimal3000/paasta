import sys
from StringIO import StringIO
from subprocess import CalledProcessError

from mock import patch
from pytest import raises

from service_deployment_tools.paasta_cli.cmds.generate_pipeline \
    import paasta_generate_pipeline
from service_deployment_tools.paasta_cli.paasta_cli import parse_args
from service_deployment_tools.paasta_cli.utils import NoSuchService


@patch('service_deployment_tools.paasta_cli.cmds.generate_pipeline.guess_service_name')
@patch('sys.stdout', new_callable=StringIO)
def test_generate_pipeline_service_not_found(
        mock_stdout, mock_guess_service_name):
    # paasta generate cannot guess service name and none is provided

    mock_guess_service_name.side_effect = NoSuchService('foo')

    sys.argv = ['./paasta_cli', 'generate-pipeline']
    parsed_args = parse_args()

    with raises(SystemExit) as sys_exit:
        paasta_generate_pipeline(parsed_args)

    output = mock_stdout.getvalue()
    assert sys_exit.value.code == 1
    assert output == 'Service not found\n'


@patch('service_deployment_tools.paasta_cli.cmds.generate_pipeline.guess_service_name')
@patch('service_deployment_tools.paasta_cli.cmds.generate_pipeline.subprocess')
def test_generate_pipeline_subprocess1_fail_no_opt_args(
        mock_subprocess, mock_guess_service_name):
    # paasta generate fails on the first subprocess call, no opt args

    mock_guess_service_name.return_value = 'fake_service'
    mock_subprocess.check_call.side_effect = \
        CalledProcessError(1, 'jenkins cmd 1')

    sys.argv = ['./paasta_cli', 'generate-pipeline']
    parsed_args = parse_args()

    with raises(CalledProcessError):
        paasta_generate_pipeline(parsed_args)


@patch('service_deployment_tools.paasta_cli.cmds.generate_pipeline.guess_service_name')
@patch('service_deployment_tools.paasta_cli.cmds.generate_pipeline.subprocess')
def test_generate_pipeline_subprocess2_fail_with_opt_args(
        mock_subprocess, mock_guess_service_name):
    # paasta generate fails on the second subprocess call, opt args

    mock_guess_service_name.return_value = 'fake_service'
    mock_subprocess.check_call.side_effect = [
        0, CalledProcessError(1, 'jenkins cmd 1')]

    sys.argv = [
        './paasta_cli', 'generate-pipeline', '--service', 'fake_service']
    parsed_args = parse_args()

    with raises(CalledProcessError):
        paasta_generate_pipeline(parsed_args)
