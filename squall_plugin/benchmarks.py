"""CIS Kubernetes Benchmarks"""
import json
import re
import subprocess


class Benchmarks:
    """Benchmarks"""

    def __init__(self) -> None:
        self.config_dir = '/usr/local/bin/squall_plugin/config'
        self.version = 'v1.6.1-10-01-2020'

    def get_version(self) -> str:
        return self.version

    def run(self):
        print("Starting CIS Kubernetes Benchmarks")
        config = self.get_config(f"{self.version}.json")
        for bench in config['benchmarks']:
            result = "Failed"
            try:
                prompt_val = input(f"{bench['prompt']} [{bench['prompt_default']}]")
                reg = re.compile('[a-zA-Z\/0-9\.\-\_]{3,}')
                if prompt_val.strip() == '':
                    prompt_val = bench['prompt_default']
                if reg.match(prompt_val):
                    bench['command'] = bench['command'].replace('[[prompt_val]]', prompt_val)
                else:
                    raise ValueError("The input is invalid.")
            except KeyError:
                pass
            try:
                cmd = bench['command'].split(' ')
                out = subprocess.check_output(cmd).decode('utf-8')

                if '<=' in bench['accept']:
                    if int(out.strip()) <= int(bench['accept'][2:]):
                        result = "Passed"
                elif len(out.split('\n')) > 2:
                    result = "Passed"
                    for line in out.split('\n'):
                        line = line.strip()
                        if line in ['']:
                            continue
                        if line[:5] in ['total']:
                            continue
                        if line[0] == '/' and line[len(line)-1] == ':':
                            continue

                        if bench['accept'] not in line:
                            result = "Failed"

                elif out.strip() == bench['accept']:
                    result = "Passed"
            except subprocess.CalledProcessError:
                result = "Error"

            print(f"{bench['id']} - {bench['desc']} - {result}")

        print("Finished CIS Kubernetes Benchmarks")

    def get_config(self, config: str = None) -> dict:
        if config is None:
            raise ValueError("config is required")
        with open(f"{self.config_dir}/{config}", 'r') as fh:
            config_str = fh.read()

        return json.loads(config_str)