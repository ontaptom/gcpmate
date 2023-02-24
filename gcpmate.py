import os
import re
import sys
import openai
import subprocess

openai.api_key = os.environ.get('OPENAI_API_KEY')


class GCPMate:
    def __init__(self):
        self.current_user = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode('utf-8').strip()
        self.current_project = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode('utf-8').strip()

    def blue_text(self, text):
        return f"\033[94m{text}\033[0m"

    def get_yes_no(self, prompt):
        while True:
            print(f"\n{self.blue_text('Fair warning')}: gcloud may prompts for yes/no confirmation\n\t execution process will respond with yes.\n")
            answer = input(f"Would you like to execute the following {self.blue_text(len(self.commands))} command(s)? [y/N] ").strip().lower()
            if answer in {"y", "yes"}:
                return True
            elif answer in {"", "n", "no"}:
                return False
            else:
                print("Invalid input, please try again.")

    def call_openai_api(self, query, openai_model="code-davinci-002"):
        openai_model = "text-davinci-003"
        try:
            response = openai.Completion.create(
                model=openai_model,
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

    def run(self, query):
        print("Current user logged in with gcloud: " + self.blue_text(self.current_user))
        print("Default project: " + self.blue_text(self.current_project))

        self.call_openai_api(query)

        if len(self.commands) == 0:
            print("I'm sorry. Your question did not return any potential solution including GCLOUD commands.")
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
    if len(sys.argv) != 2:
        print("gcpmate requires one argument with query from the user placed under \"\", for example:\n\n"
              "gcpmate \"create new project called my-superb-new-project\"\n\n")
        sys.exit(1)

    gcpmate = GCPMate()
    gcpmate.run(sys.argv[1])

