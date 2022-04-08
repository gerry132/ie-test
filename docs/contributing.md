## Contributing to the project

The default branch is set to `main`. **This branch should not have pull requests for individual pieces of work.**

When starting a new piece of work, make sure to create your working branch based off the `develop` branch.

To start a new feature first create the new branch you'll be working on.

```bash
git checkout develop
git checkout -b [my-branch]
```

While building the new feature it's recommended to `rebase` your branch on the `develop` branch regularly to pick any changes merged by other developers and fix any conflicts.

```bash
git rebase origin develop
```

When your work is complete you should push your changes to the github repository.

- Go to GITHUB and make a new pull request for your work/branch. Ensure the target branch is set to `develop`
- **Include a link to the ticket you are working on** and add any other information that will assist a developer with the code review.
- Add a label `Develop merge` to the pull request.
- Create the pull request and ask someone to review it.

#### Develop Pull Request

When your work has been code reviewed and is ready for acceptance testing you can merge it.

This will trigger AzurePipelines to start a deployment to staging. When the deployment completes you will receive an email to confirm the deployment.


## Code linting

The github actions will run `flake8` against all python files to check for code quality and formatting.

[.pre-commit-config.yaml](../.pre-commit-config.yaml) Is available for automatic code linting when running `git commit`

To use when making commits on your host machine you must install pre-commit, either create a virtualenv to use with the project or to install globally see instructions at (https://pre-commit.com/#install).

**Pre-commit will not run by default.**

To set it up, run `pre-commit install` on your host machine. Each time you commit changes a report will be generated in the console. If there are issues they will be output in the report.