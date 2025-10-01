# THIS IS NOT EVEN A PROTOTYPE

Despite the name of this project it is not a prototype for the NMDC Field Notes app. This was the result of [Patrick's](https://github.com/pkalita-lbl) technical exploration of [Ionic](https://ionicframework.com/) and [Capacitor](https://capacitorjs.com/). At most this is a proof-of-concept of some technologies that _may_ be used to build the app. 

---

## Development

### Check Node.js version

Capacitor requires Node.js v16 or higher. Since v16 is [EOL](https://nodejs.dev/en/about/releases/), we recommend you use v18 or higher.

You can check your Node.js version with:

```shell
node --version
```

Note: There is an [issue](https://github.com/microbiomedata/nmdc-app-prototype/issues/2) with Node.js version `v20.6.0`. If you are running that Node.js version, we recommend you upgrade to at least `v20.6.1` ([reference](https://github.com/vitejs/vite/issues/14299)).

### Clone the repo

Run

```shell
git clone https://github.com/microbiomedata/nmdc-app-prototype.git
cd nmdc-app-prototype
```

### Install dependencies 

Run

```shell
npm install
```

This also downloads the submission schema as an "out-of-band" dependency and places its files in a directory named `nmdc_submission_schema-7.7.2`.

You also need to have the [Ionic CLI](https://ionicframework.com/docs/cli) installed. It is recommended to install this globally:

```shell
npm install -g @ionic/cli
```

> Alternatively, you can precede all `ionic` commands with `npx` (as in, `$ npx ionic`) to avoid having to install the package globally.

### Environment setup for Capacitor

[Capacitor](https://capacitorjs.com/) is a library which provides access to native device functionality (e.g. location, camera, storage, etc.) to the web application. In order to start using it, review its [Environment Setup](https://capacitorjs.com/docs/getting-started/environment-setup) documentation and make sure you have the necessary dependencies installed.

For example, to build **iOS** apps, you will need (as of the time of this writing): macOS, Node.js, Xcode (v14.1+), Xcode CLI tools, Homebrew, and Cocoapods. To build **Android** apps, you will need (as of the time of this writing): Node.js, Android Studio, and at least one Android SDK installation. To build **web** apps, all you need is Node.js.

### Run the development server

Run

```shell
npm run dev
```

This will start a development server on `localhost:5173`. You can view it in your browser, but we recommend you use your browser's developer tools to [view it in a mobile-sized viewport](https://ionicframework.com/docs/developing/previewing#simulating-a-mobile-viewport). 

### (Optional) Switch UI styles

Ionic includes logic to automatically switch between iOS and Android/Web (i.e. Material) styles based on the browser's user agent. For most browsers, you will see Material styles by default. You can manually override this by adding the `ionic:mode` [query parameter](https://ionicframework.com/docs/developing/tips#changing-mode) to any URL.

For example:

```diff
- http://localhost:5173/
+ http://localhost:5173/?ionic:mode=ios
```

### View on an iOS simulator 

To run on an iOS simulator, first download and install [Xcode](https://developer.apple.com/xcode/) if you haven't already. 

If this is your first time running the simulator _or_ you have added a Capacitor plugin since the last time you ran the simulator run:

```shell
ionic capacitor sync ios
```

Start the simulator with live reloading enabled by running:

```shell
ionic cap run ios --livereload --external
```

This may take a minute or so to start initially. You should see the message `Deploying App.app to <uuid>` written to the console and then the simulator window should open.
