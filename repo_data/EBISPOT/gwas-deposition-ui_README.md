# GWAS Deposition UI

## Description
User interface for submission of GWAS metadata and summary statistics files for use with the [NHGRI-EBI GWAS Catalog](https://www.ebi.ac.uk/gwas). This application is used in conjunction with other components of the GWAS Deposition Application system such as the Template service and GWAS Deposition backend. The application runs within a Kubernetes cluster using Docker.


## Development
This application is developed as a single-page application using ReactJS (https://reactjs.org/) and is bootstrapped from the [Create React App](https://github.com/facebook/create-react-app).


Requirements:
* ReactJS https://reactjs.org/
* Node and npm https://www.npmjs.com/get-npm
    *  Node >= 8.10 and npm >= 5.6

Additional libraries used in the application include:
* React Router https://reactrouter.com/web/guides/quick-start*
* Axios https://github.com/axios/axios
* Material UI https://material-ui.com/
* Material UI Chip Input https://www.npmjs.com/package/material-ui-chip-input
* Material Table https://github.com/mbrn/material-table
* Formik https://formik.org/docs/overview
* Elixir AAP https://aai.ebi.ac.uk/home

These will be installed as node modules.<br>
Run `npm list --depth 0` to see the full list of Node modules used in the application.


### Getting Started
* Install Node and npm (see link above)
* Clone the application from https://github.com/ebispot/gwas-deposition-ui
* Run `npm install` to install the npm modules used by the application 
    * Manually manage any npm install conflicts following instructions from the npm error messages
    * To install a specific version of a NPM module see [NPM: How to Install Specific Version of a Module](https://60devs.com/npm-install-specific-version.html)
* Run `npm start` to launch the application
    * Your browser should automatically open and display the application running on localhost on the specified port found in the package.json file under scripts.start (in this case 8080)
    * NOTE: You MUST be on the EBI VPN to access the web services from the GWAS Deposition Backend Sandbox environment
* Develop new features!
    * NOTE: The application will automatically reload in the browser anytime a file is saved without needing to specifically configure hot reloading.

### Managing the Code base
* The production code is in the branch `master`
* The development code is in the branch `develop`
* The branch `documentation` can be used to add banner text to alert about outages or other information. This branch should be merged into `develop` and be maintained up-to-date with the `develop` branch prior to deploying a new update similar to how the GWAS Search UI `documentation` branch is maintained.

#### Add a new feature or fix a bug
* From you Terminal, switch to the `master` branch as: <br>
    `git checkout master`
* Update your local repo as: <br>
    `git pull origin master`
* Switch to the development branch as: <br>
    `git checkout develop`
* Update the development branch as: <br>
    `git pull origin develop`
* Create a new branch to add the bug or feature as: <br>
    `git checkout -b issREPO-ISSUE-NUMBER_brief_description_of_issue`
* Do the work to fix the issue or add a new feature and commit updates as appropriate
* Push local changes to the remote as: <br>
    `git push origin issREPO-ISSUE-NUMBER_brief_description_of_issue`
* Create a Pull Request to merge the updates in the feature branch into `develop`
* Once the changes are merged into `develop` the Gitlab plan will automatically deploy these changes to the sandbox exvironment where User Acceptance Testing can be done
* When the UAT is completed successfully, the updates in `develop` can be merged into `master`, either through a Pull Request or using `git merge` from your local repo (Remember to update all relevant branches locally before doing the merge)


#### Deploy Updates to Production
The Gitlab plan for the Deposition UI is configured to deploy new tags to the production environment. 
* Create a new tag using `git tag` from your local repo (Remember to update `master` before tagging) or using the GitHub interface to create a tag
* Once the [Gitlab plan](https://gitlab.ebi.ac.uk/gwas/gwas-deposition-ui/-/pipelines) notices the tag, the updates will be deployed to production


## Available Scripts
In the project directory, you can run:

### `npm start`
Runs the app in the development mode.<br>
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br>
You will also see any lint errors in the console.

### `npm test`
Launches the test runner in the interactive watch mode.<br>
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`
Builds the app for production to the `build` folder.<br>
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br>
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`
**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (Webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.


## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).


