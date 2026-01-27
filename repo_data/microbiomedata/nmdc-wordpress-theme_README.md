# nmdc-wordpress-theme

This repository contains the "NMDC" WordPress theme originally built by [Comrade Web Agency](https://comradeweb.com), a development environment for that theme, and instructions for setting up that development environment.

That theme is currently in use on the [NMDC website](https://microbiomedata.org) (`https://microbiomedata.org`).

_Disclaimer: This repository was created by members of the NMDC team (not by the Comrade Web Agency) based upon a backup copy of the development instance of the website. Getting from _there_ to _this repository_—in the absence of documentation—involved some trial-end-error. There may still be some "error" left over._

# Files and folders

- `themes/nmdc/`: The WordPress theme.
   > This is a copy of the `wp-content/themes/nmdc` folder extracted from a September, 2023, backup of the development website hosted on WP Engine.
   * `front/`: Web pages and related assets, some of which are referenced by PHP files in the WordPress theme.
       - `src/`: [Pug](https://pugjs.org/api/getting-started.html), JavaScript, [Sass](https://sass-lang.com/documentation/syntax/#scss), fonts, images, and other files, which are processed and _bundled_ by [webpack](https://webpack.js.org/) (via [gulp](https://gulpjs.com/)).
       - `dist/`: The _bundled_ Javascript, CSS, and other files, some of which are referenced by PHP files in the WordPress theme.
- `dependencies/`: Dependencies of the WordPress theme.
    - `php-related/custom.ini`: A PHP configuration file.
       > This increases the size limit of files that can be uploaded to the website. That increase is necessary because (a) the `advanced-custom-fields-pro.zip` file and (b) the content XML file exported from the production website, each exceed PHP's default file upload size limit of 2 MB.
    - `wordpress-related/mu-plugins/`: So-called "must-use" WordPress plugins.
        - `primary.php`: This file is a copy of the `wp-content/mu-plugins/primary.php` file from the same backup as the WordPress theme.
          > I inferred this dependence through trial and error.
        - `disable-google-analytics.php`: A plugin that disables the "NMDC" theme's function that injects the Google Analytics snippet into HTML pages.
          > This plugin doesn't exist on the production website. We implemented it specifically for our development environment, so we could visit the development instance of the website without affecting our Google Analytics data.
        - `use-mailhog.php`: A plugin that configures WordPress to send emails via [MailHog](https://hub.docker.com/r/mailhog/mailhog/).
          > This plugin doesn't exist on the production website. We implemented it specifically for our development environment, so we could test the submission of the newsletter subscription form, which requires that WordPress be able to send emails.
    - `wordpress-related/plugin-archives/advanced-custom-fields-pro.zip`: The "Advanced Custom Fields PRO" WordPress plugin.
       > I inferred this dependence through trial and error. This file is a zipped copy of the `wp-content/themes/advanced-custom-fields-pro/` folder from same backup as the WordPress theme. It is distinct from the _non-PRO_ version that is in the official WordPress plugin repository.
- `docker-compose.yml`: The specification of a Docker Compose stack you can use to run the website locally for development.
- `README.md`: That's me!

# Setup

## Prerequisites

- You have Docker and Docker Compose installed
- You have an "All content" XML file that was exported from the production website (via "Tools" > "Export" > "All content"); e.g. `nationalmicrobiomedatacollaborative.WordPress.2023-09-20.xml`

## Procedure

1. Spin up the Docker Compose stack.
    ```shell
    docker compose up
    ```
2. Install WordPress.
    1. Visit http://localhost:10001
    1. Select "English" as the language
    1. Fill out the "Information needed" form:
        - Site Title: `site-title`
        - Username: `admin`
        - Password: `admin`
        - Confirm password: Mark the "Confirm use of weak password" checkbox
        - Your email: `admin@example.com`
        - Search engine visibility: Mark the "Discourage search engines..." checkbox
        - Click the "Install WordPress" button
1. Log into the WordPress admin dashboard.
    1. Click "Log In" (after the installation finishes)
    1. Log in using the username and password above
1. Install and activate necessary plugins.
    1. Go to "Plugins" > "Installed Plugins"
    1. Upload, install, and activate the "Advanced Custom Fields PRO" plugin
        1. Click the "Add New" button
        1. Click the "Upload Plugin" button
        1. Upload the `dependencies/wordpress-related/plugin-archives/advanced-custom-fields-pro.zip` file
        1. Click the "Activate Plugin" button
    1. Install and activate the "Contact Form 7" plugin
        1. Click the "Add New" button
        1. Find, install, and activate the "Contact Form 7" plugin
1. Activate the "NMDC" theme.
    1. Go to "Appearance" > "Themes"
    1. On the "NMDC" theme thumbnail, click "Activate"
1. Import the website content.
    1. Go to "Tools" > "Import"
    1. On the "WordPress" row, click "Install Now"
    1. Once installed, click "Run Importer"
    1. On the "Import WordPress" page, click the "Browse..." button and select the "All content" XML file exported from the production website
    1. Click the "Upload File and Import" button
    1. On the "Assign Authors" page:
        1. For each missing author, copy/paste their username into the "...create new user with login name" field
        1. Mark the "Download and import file attachments" checkbox
    1. Wait for the import to finish
        - This can take 3-4 minutes
        - The result page will show the following failure messages:
            ```text
            Failed to import flamingo_inbound_channel Contact Form 7
            Failed to import flamingo_inbound_channel Subscribe
            Failed to import flamingo_inbound_channel Contact
            Failed to import Media "GSP2021 - Survey Poster"
            ```
    1. Click the "Have fun" link to return to the WordPress admin dashboard
1. Customize the "NMDC" theme.
    1. Go to "Appearance" > "Themes"
    1. On the "NMDC" theme thumbnail, click "Customize"
    1. In "Site Identity":
        - Site title: `National Microbiome Data Collaborative`
        - Tagline: `An open and integrative data science ecosystem`
        - Site icon: Click "Select site icon" and, in the Media Library browser that appears, find and select the media item named `cropped-NMDC_Mark-Only.png`
    1. In "Menus" > "View All Locations", in the "Header Menu" dropdown menu, select `Header Menu`
    1. In "Homepage Settings"
        - Set "Your homepage displays" to "a static page"
        - In the "Homepage" menu, select `Home`
    1. Click the "Publish" button
1. Customize the Theme Settings.
    1. Go to "Theme Settings"
        1. Header: 
            - Logotype: Select image named `logo-img.svg`
            - Logotype (Text): Select image named `logo-text.svg`
        1. Footer: 
            - Copyright: `Lawrence Berkeley National Laboratory, all rights reserved.`
            - Footer Links:
                1. `Code of Conduct`: Select the "NMDC Code of Conduct" page and shorten the link text to "Code of Conduct"
                2. `Data Use Policy`: Select the "NMDC Data Use Policy" page and shorten the link text to "Data Use Policy"
                3. `Acknowledgements`: Select the "Acknowledgements" page
        1. Contact information:
            1. Twitter:
                - Select image named `twitter-brands.svg`
                - Social name: `@microbiomedata  #NMDC`
                - URL: `https://twitter.com/microbiomedata`
            2. Instagram:
                - Select image named `instagram-brands.svg`
                - Social name: `@microbiomedata`
                - URL: `https://www.instagram.com/microbiomedata`
            3. YouTube:
                - Select image named `youtube-nmdcblue.svg`
                - Social name: `NMDC YouTube`
                - URL: `https://www.youtube.com/channel/UCyBqKc46NQZ_YgZlKGYegIw/featured`
            4. LinkedIn:
                - Select image named `Untitled-design-1-e1680893436292.png`
                - Social name: `NMDC LinkedIn`
                - URL: `https://www.linkedin.com/company/microbiomedata/`
        1. Other:
            - Google Analytics: (Leave empty)
              > The value that would normally go here is hard-coded in the theme (in `functions/theme-function.php`).
        1. Default image:
            - Default Hero image: Select image named `BlogArticleImage_FullColor.jpg`
            - Default Featured image: Select image named `BlogArticleImage_FullColor.jpg`
1. Customize the Cross Site Blocks.
    1. Go to "Cross Site Blocks"
        1. Subscribe:
            - Title: `Join our vision`
            - Subtitle: `Want more info? Or to be an NMDC Champion? Subscribe to be the first to know about the latest news and developments.`
            - Form ID: Set this to the "post ID" of the "Custom Contact 7" form named "Subscribe"
              > You can get that value by going to "Contact" > "Contact Forms", clicking on "Subscribe" in the table, and looking at the `post={id}` part of the URL. For example, if the URL is `http://localhost:10001/wp-admin/admin.php?page=wpcf7&post=1785&action=edit`, the "post ID" is `1785`. Keep this value handy as you'll need it in a later step.
        1. Form Thank You Message
            - Background: Select image named `thank-bg-1.jpg`
            - Title: `Thank you for your interest`
            - Subtitle: `Please be sure to check your inbox for the latest news, updates, and information.`
            - Logo: Select image named `grey-logo-1.svg`
        1. 404 Page
            - Background: Select image named `hero.jpg`
            - Title: `Oops! 404 error`
            - Subtitle: `Sorry this page can't be found`
1. Update Home Page
    1. Go to "Pages" > "All Pages"
    1. Click "Home". You may need to use the pagination controls or the search box to find it.
    1. In the "Subscribe" section change the "Form Id" to the value used previously in the "Subscribe" Cross Site Block.
    1. In the "Publish" section at the top-right of the page, click the "Update" button.
1. Visit the website at: http://localhost:10001

# Usage

You can visit the **website** at: http://localhost:10001

You can visit the **WordPress admin dashboard** at: http://localhost:10001/wp-admin
> Credentials are defined during the installation of WordPress.

You can visit **MailHog** at: http://localhost:10004

You can visit **Adminer** at: http://localhost:10003
> Credentials are in `docker-compose.yml`.

You can use a local SQL client to access the **MySQL server** at: `mysql://localhost:10002`
> Credentials are in `docker-compose.yml`.

You can run and access a **shell** within the (already-running) `wordpress` container by running:
```shell
docker compose exec wordpress bash
```

You can follow the **logs** of the Docker Compose stack by running:
```shell
docker compose logs --follow

# Or, for the logs of the `wordpress` container only:
docker compose logs --follow wordpress
```

# Tips

### Distributing the WordPress theme

To create a distributable version of this WordPress theme: 

1. Publish a [Release](https://github.com/microbiomedata/nmdc-wordpress-theme/releases) on GitHub.
2. Wait about two minutes for GitHub Actions to attach a file named `nmdc.zip` to that Release.

Here's an explanation of how that works:

> Whenever someone publishes a [Release](https://github.com/microbiomedata/nmdc-wordpress-theme/releases) in this
> project's GitHub repository, the GitHub Actions workflow configured in `.github/workflows/build.yaml` will run.
>
> That workflow will check out the Git tag associated with the newly-published Release, update the WordPress theme's
> version number (in `themes/nmdc/style.css`) to match the name of that Git tag (e.g. `v1.2.3`), compile the WordPress
> theme's frontend assets, compress the WordPress theme's file tree (excluding the `front/node_modules` folder) into a
ZIP file, and attached that ZIP file as an asset to the newly-published Release.

<details>
    <summary>Manual steps (alternative)</summary>

1. Edit the theme's version identifier in `themes/nmdc/style.css` (e.g. change `1.0.0` to `1.0.1`)
2. Refresh the bundled CSS and JavaScript files
    ```shell
    cd themes/nmdc/front && npm install && npm run build && cd -
    ```
3. Create a ZIP file of the theme (excluding the `front/node_modules` folder)
    ```shell
    ./zip-theme.sh
    ```
    > That will generate a file named `nmdc.zip` in the root folder of the repository.
</details>

Once you have the ZIP file, you can upload it to a WordPress installation and activate it there (on a WordPress multisite installation, upload the ZIP file at the Network level, then activate it at the Site level).

### Resetting the database

Drop the `wordpress` database, then recreate it. This can be done via Adminer or a local SQL client.

### Debugging

Here are some WordPress plugins I have found helpful while debugging:

- [Debug Log Manager](https://wordpress.org/plugins/debug-log-manager/) - shows the PHP error log (including stack traces) within the WordPress admin dashboard (adds an exclamation point icon to the admin top bar)
- [PHP Server Configuration](https://wordpress.org/plugins/php-server-configuration/) - shows `phpinfo()` output within the WordPress admin dashboard (adds a menu item to the admin left navigation)
- [What The File](https://wordpress.org/plugins/what-the-file/) - shows which theme template files were used to "build" the current web page (adds a drop-down menu to the admin top bar)

### Editing the `front` folder

The WordPress theme has a folder named `front`. That folder contains web pages and related assets, some of which are referenced by PHP files in the WordPress theme.

Here's how you can make changes to the style rules and JavaScript code used by the web pages in the `front` folder.

1. Go to the `front` folder.
    ```shell
    cd themes/nmdc/front
    ```
1. Install NPM packages.
    ```shell
    npm install
    ```
1. Start a local development server.
    ```shell
    npm run dev
    ```
    > You can access the local development server at: http://localhost:4000
1. Edit the source code within `front/src`.
    > For example:
    > - CSS: In `styles/general/_base.scss`, change the `body` `background-color` from `#fff` to `#f00`, save the file, and see the background color of the homepage turn red. You may have to [hard refresh](https://my.sdsu.edu/guides/clear-cache#h.7t0j2rd77t35) the web page in order to see the change.
    > - JavaScript: In `js/modules/animation.js`, add `alert("Hello");` to the top of the file, save the file, and see an alert appear in the web browser.
1. When done editing the source code, generate a production build (in `front/dist`).
    ```shell
    npm run build
    ```
    > That will make it so the PHP files in the WordPress theme see the changes (the PHP files contain references to `front/dist`).

The Pug and image files in `front/src/pages` are used to generate HTML pages for fast iteration and stakeholder feedback. The Pug files happen to mirror elements that are implemented in PHP, but they are not technically linked in any way.

### Editing `CSS` and `JavaScript`

You can also edit style rules and JavaScript code for parts of the WordPress theme that don't reference the `front/dist` folder.

Here's where you can do each of those things:
- You can add custom style rules to: `style.css`
- You can add custom JavaScript to: `inc/custom.js`

The WordPress theme "loads" (i.e. enqueues the loading of) both of those files within its `functions/styles-and-scripts.php` file.

# Roadmap (tentative)

- Streamline the setup process. For example, write raw SQL queries (e.g. `UPDATE wp_options SET option_value = "National Microbiome Data Collaborative" WHERE option_name = "blogname";`) or use `wp-cli` commands that can take the place of some of the manual GUI steps (e.g. theme configuration). Note that the WordPress Docker image does not include `wp-cli`, but there is a [CLI-only variant](https://hub.docker.com/layers/library/wordpress/cli-php8.2/images/sha256-2c4a8832a4407b69323e8998006ccf09f988852fe8a6aeca8d3560e285785a1d?context=explore) of it available.

# Additional documentation

There is additional documentation in the [`docs/`](./docs/README.md) folder.
