# GCPMate - Google Cloud Platform Assistant

GCPMate is a tool that helps you manage your Google Cloud Platform (GCP) resources. It uses OpenAI's powerful language models to understand what you want to do, and then generates GCP command-line instructions for you to execute. If you like the proposed outcome, GCPMate can also execute the commands for you!

## Installation

To use GCPMate, you'll need to have Python 3.x and an OpenAI API key. To install GCPMate, simply run:

```bash
pip install gcpmate
```
In current version program expects to find API key in `env` variable `OPENAI_API_KEY`. You can obtain the API key at https://platform.openai.com/account/api-keys. Once ready, you can set up `env` variable by running:

```bash
export OPENAI_API_KEY=<your-api-key>
```

## Usage

To use GCPMate, simply run:

```bash
gcpmate "<your query>"
```

Where `<your query>` is a description of what you want to achieve in GCP.

<img src="./images/list_vms.svg">

GCPMate will use OpenAI's language models to understand your query, and then generate a series of GCP command-line instructions for you to execute. If you like the proposed outcome, GCPMate can also execute the commands for you!

## Examples

Here are some example queries you can use with GCPMate:

```bash
gcpmate "create a new GCP project called my-superb-new-project"
```

```bash
gcpmate "create ubuntu VM called superbvm in us-central1-a in project <xyz>"
```

You can also use GCPMate to ask queries, or paste error messages, or ask to explain a command:

```bash
gcpmate --explain "Why I cannot connect to my VM over ssh?"
```

```bash
gcpmate -e " gcloud compute instances create newvm --project superproject324 --zone us-central1-a --image-family ubuntu-1804-lts --image-project ubuntu-os-cloud"
# this query will return explaination what that command would do.
```
## Options

GCPMate supports several command-line options:
```bash
gcpmate -h  # Show the help message and exit
gcpmate -m <model>  # Specify the OpenAI model to use (default: text-davinci-003)
gcpmate -s  # Skip printing runtime info (gcloud account, project, region, zone, OpenAI model)
gcpmate -e  # Return explanation to given query, which can be command, error message, etc.
```

## Contributing

If you find a bug or have a feature request, please open an issue on the GCPMate GitHub repository: https://github.com/ontaptom/gcpmate

Pull requests are also welcome! If you want to contribute to GCPMate, please fork the repository, create a new branch, and then submit a pull request. Please ensure that your code passes the existing tests and linting rules.

## License

This project is licensed under the terms of the Apache License 2.0. See the `LICENSE` file for more details.