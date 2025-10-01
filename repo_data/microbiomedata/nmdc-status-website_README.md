# nmdc-status-website

This repository contains static web page(s) the NMDC team uses to display messages during outages and other special events.

It is hosted at: https://status.microbiomedata.org/

## Usage

### Updating the text

Write the text in Markdown format in the file `./message.md`, then reload the web page (i.e. `index.html`). The reloaded web page will show the message in a box below the words, "We'll be right back."

If the `./message.md` file is empty, the web page will show a default message saying all systems are running normally.

### Deployment

GitHub will automatically deploy the latest commit on the `main` branch, to GitHub Pages.

## Design

The website is built upon the [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/) web UI framework.

### Typography

The font was chosen in an attempt to match the [NMDC website](https://microbiomedata.org/).

```css
font-family: Arimo,sans-serif
```

- Arimo is available from Google Fonts: https://fonts.google.com/specimen/Arimo
- Code snippets for using the font: https://thomaspark.co/projects/fontcdn/

### Color palette

The color scheme was chosen in an attempt to match the [NMDC website](https://microbiomedata.org/).

```css
:root {
  --nmdc-white: #ffffff;
  --nmdc-black: #000000;
  --nmdc-blue: #02aae7;
  --nmdc-orange: #ee5338;
  --nmdc-purple: #4f3b80;
  --nmdc-light-gray: #f5f5f5;
  --nmdc-light-blue: #edf9fd;
}
```

In `./index.css`, these colors are defined using CSS [custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties).

## Search engine behavior

The `./robots.txt` file contains the following, which tells all robots (e.g. web crawlers) we **don't** want them to visit any pages of the website. It's up to them to respect that, though.

```txt
User-agent: *
Disallow: /
```

Reference: [robotstxt.org](https://www.robotstxt.org/robotstxt.html)

## Text

The website's text is written in **Markdown** format. I implemented things that way in an attempt to make it easier for team members who are familiar with Markdown—but not with HTML—to update the website.

The website uses a JavaScript library named [Showdown](https://github.com/showdownjs/showdown) to convert that Markdown into HTML. The conversion process happens when the web browser loads the web page.

## Google Analytics

This website currently does **not** use Google Analytics.

## Sources

The following files in this repository were copied from the [NMDC website](https://microbiomedata.org/):

- `./favicon.ico`: https://microbiomedata.org/favicon.ico
- `./img/logo-mark.svg`: https://microbiomedata.org/wp-content/uploads/sites/2/2019/08/logo-img.svg
- `./img/logo-text.svg`: https://microbiomedata.org/wp-content/uploads/sites/2/2019/08/logo-text.svg
- `./img/hero.webp`: This is the result of running https://microbiomedata.org/wp-content/uploads/sites/2/2023/01/XBD201307-03354-194_NMDCHero.jpg through the [Convertio](https://convertio.co/jpg-webp/) JPEG-to-WEBP converter (which decreased its file size by more than half).
