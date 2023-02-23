import os
import sys
import openai
import subprocess

openai.api_key = os.environ.get('OPENAI_API_KEY')


class GCPMate:
    def __init__(self):
        self.current_user = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ).stdout.strip()
        self.current_project = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ).stdout.strip()

    def blue_text(self,text):
        return f"\033[94m{text}\033[0m"

    def get_yes_no(self, prompt):
        while True:
            answer = input(f"Proposed solution:\n\t{self.blue_text(prompt)}\nDo you want to execute? [Y/n] ").strip().lower()
            if answer in {"", "y", "yes"}:
                return True
            elif answer in {"n", "no"}:
                return False
            else:
                print("Invalid input, please try again.")

    def call_openai_api(self, query):
        try:
            response = openai.Completion.create(
                model="code-davinci-002",
                prompt=f"# return gcloud cli:\n{query}:###",
                temperature=0,
                max_tokens=550,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["#", "###"]
            )
        except Exception as e:
            print("Error with OpenAI API request: ",e)
            sys.exit(1)
        print(response)
        self.command = response['choices'][0]['text']

    def run(self, query):
        print("Current user logged in with gcloud: " + self.blue_text(self.current_user))
        print("Default project: " + self.blue_text(self.current_project))

        self.call_openai_api(query)

        doit = self.get_yes_no(self.command)
        if not doit:
            # placeholder for exit message
            return

        result = subprocess.run(self.command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not result.stderr:
            print(f"Operation completed. Result:\n\t{self.blue_text(result.stdout)}")
        else:
            print(f"It seems something did not go correctly: {result.stderr}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("gcpmate requires one argument with query from the user placed under \"\", for example:\n\n"
              "gcpmate \"create new project called my-superb-new-project\"\n\n")
        sys.exit(1)

    gcpmate = GCPMate()
    gcpmate.run(sys.argv[1])

