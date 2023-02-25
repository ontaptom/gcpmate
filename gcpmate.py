import os
import re
import sys
import openai
import subprocess
import argparse
from prettytable import PrettyTable


class GCPMate:
    def __init__(self, openai_model = "text-davinci-003", skip_info = False):
        self.current_user = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode('utf-8').strip()
        self.current_project = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode('utf-8').strip()
        self.default_region = subprocess.run(
            ['gcloud', 'config', 'get-value', 'compute/region'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode('utf-8').strip()
        self.default_region = "(unset)" if self.default_region == "" else self.default_region
        self.default_zone = subprocess.run(
            ['gcloud', 'config', 'get-value', 'compute/zone'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode('utf-8').strip()
        self.default_zone = "(unset)" if self.default_zone == "" else self.default_zone
        self.openai_model = openai_model
        self.skip_info = skip_info

    def blue_text(self, text):
        return f"\033[94m{text}\033[0m"

    def get_yes_no(self, prompt):
        while True:
            print(f"\n{self.blue_text('Fair warning')}: gcloud may prompt for yes/no confirmation.\n\t If so, execution process will respond with yes.\n")
            answer = input(f"Would you like to execute the following {self.blue_text(len(self.commands))} command(s)? [y/N] ").strip().lower()
            if answer in {"y", "yes"}:
                return True
            elif answer in {"", "n", "no"}:
                return False
            else:
                print("Invalid input, please try again.")

    def call_openai_api(self, query):
        try:
            response = openai.Completion.create(
                model=self.openai_model,
                prompt=f"# gcloud cli commands with new line:\n{query}:###",
                temperature=0,
                max_tokens=350,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["#", "###"]
            )
        except Exception as e:
            print("Error with OpenAI API request: ", e)
            sys.exit(1)

        # remove \<new-line> in case if OpenAI returns gcloud in multiple lines
        singleline_commands = response['choices'][0]['text'].replace('\\\n', '')
        # replace multiple spaces with single-space, if any found in the reply:
        singleline_commands = re.sub(' +', ' ', singleline_commands)

        # split multiple commands to a list of commands
        self.commands = [x.strip() for x in re.findall(r'(?:gcloud|gsutil)\b.*?(?:\n|$)', singleline_commands)]

    def print_runtime_info(self):
        table = PrettyTable()
        table.field_names = ["Configuration", "Value"]
        table.add_row(["Active gcloud account", self.blue_text(self.current_user)])
        table.add_row(["Default project", self.blue_text(self.current_project)])
        table.add_row(["Default region", self.blue_text(self.default_region)])
        table.add_row(["Default zone", self.blue_text(self.default_zone)])
        table.add_row(["OpenAI model", self.blue_text(self.openai_model)])
        table.align = "l"
        print(table)

    def run(self, query):
        if not self.skip_info:
            self.print_runtime_info()  
        self.call_openai_api(query)

        if len(self.commands) == 0:
            print("I'm sorry. Your question did not return any potential solution.\n"
                  "You can try rephrasing your question or use a different model by running the "
                  "command with '-m <model_name>' parameter. For more info run 'gcpmate -h'.")
            # finish script at this point
            return

        print(f"The proposed solution consist of {len(self.commands)} command(s):")
        i = 0
        for command in self.commands:
            i += 1
            print(f'\t[{i}] {self.blue_text(command)}')

        doit = self.get_yes_no(self.commands)
        if not doit:
            # placeholder for exit message
            return

        for command in self.commands:
            print(f"---\nExecuting: {self.blue_text(command)}")
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, input='y'.encode())
            if result.stdout:
                # gcloud uses stderr to print prompts, warnings and errors, so also include it in the response
                # https://cloud.google.com/sdk/gcloud#use_of_stdout_and_stderr
                print(f"---\nOperation completed. Result:\n\n{self.blue_text(result.stdout.decode('utf-8'))}\n{self.blue_text(result.stderr.decode('utf-8'))}")
            else:
                # nothing in result.stdout, command most likely failed, print stderr
                print(f"---\nPlease read carefully:\n\n{result.stderr.decode('utf-8')}")


if __name__ == '__main__':
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print("GCPMate uses OpenAI API to assist user with Google Cloud management. To use this tool "
              "please set OPENAI_API_KEY environment variable to your OpenAI API key.\n"
              "You can get your API key from https://platform.openai.com/account/api-keys. "
              "To set the environment variable, run the following command:\n\n"
              "export OPENAI_API_KEY=<your-api-key>\n")
        sys.exit(1)
    openai.api_key = openai_api_key

    parser = argparse.ArgumentParser(description='GCPMate - Google Cloud Platform assistant.\n'
                                     'Describe in query what you wish to achieve, and gcpmate '
                                     '(with a little help from OpenAI) will try to come up with a solution.\n'
                                     'If you like proposed outcome, gcpmate can also '
                                     'handle execution!', add_help=True, 
                                     formatter_class=argparse.RawTextHelpFormatter, 
                                     epilog='Example usage:\n\ngcpmate "create new project called '
                                     'my-superb-new-project"')
    parser.add_argument('query', type=str, help='Query explaining what you wish to achieve in GCP')
    parser.add_argument('-m', '--model', type=str, help='OpenAI model to use for completion. Default: text-davinci-003. '
                        'Also available: code-davinci-002')
    parser.add_argument('-s', '--skip-info', action='store_true', help='Skip printing runtime info (gcloud account, project, region, zone, OpenAI model)')
    args = parser.parse_args()
    skip_info = args.skip_info

    gcpmate = GCPMate(openai_model=args.model, skip_info = skip_info) if args.model else GCPMate(skip_info = skip_info)
    gcpmate.run(sys.argv[1])
