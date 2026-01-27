# GwasCurationUi

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 8.3.21.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change
any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also
use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag
for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out
the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).

# Notes
To run the app locally with the fake API, run `npm run start-fake`.

To run the app locally with the Sandbox API, run `ng serve -c local-sandbox`.

You may want to disable tailwind CSS purge as it sometimes messes up intelliSense, do so by setting `purge.enabled` to false in `tailwind.config.js`.

json-server uses the field `id` as a default, so it won't consider `submissionId` for example querying `/submissions/:submissionId`, instead it will look for a field called `id`. 
A workaround is to add a field `id` to each submission.
