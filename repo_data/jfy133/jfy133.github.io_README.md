<a href="https://jekyll-themes.com">
<img src="https://img.shields.io/badge/featured%20on-JT-red.svg" height="20" alt="Jekyll Themes Shield" >
</a>

# James A. Fellows Yates Pesonal Website

> The theme for this wesbite is designed by Xiaoying Riley at [3rd Wave Media](http://themes.3rdwavemedia.com/).
> Visit her [website](http://themes.3rdwavemedia.com/) for more themes.

Checkout the live demo of the original template [here](https://online-cv.webjeda.com).

<table>
  <tr>
    <th>Desktop</th>
    <th>Mobile</th>
  </tr>
  <tr>
    <td>
        <img src="https://online-cv.webjeda.com/assets/images/desktop.png?raw=true" width="600"/>
    </td>
    <td>
        <img src="https://online-cv.webjeda.com/assets/images/mobile.png?raw=true" width="250"/>
    </td>
  </tr>
</table>

## Installation

- [Fork](https://github.com/sharu725/online-cv/fork) the original(!) repository
- Go to settings and set master branch as Github Pages source.
- Your new site should be ready at `https://<username>.github.io/online-cv/`
- Printable version of the site can be found at `https://<username>.github.io/online-cv/print`. Use a third party link https://pdflayer.com/, https://www.web2pdfconvert.com/ etc to get the printable PDF.

Change all the details from one place: `_data/data.yml`

## To preview/edit locally with docker

```sh
docker-compose up
```

_docker-compose.yml_ file is used to create a container that is reachable under http://localhost:4000.
Changes _\_data/data.yml_ will be visible after a while.

### Local machine

- Get the repo into your machine

```bash
git clone https://github.com/sharu725/online-cv.git
```

- Install required ruby gems

```bash
bundle install
```

- Serve the site locally

```bash
bundle exec jekyll serve
```

- Navigate to `http://localhost:4000`

## Skins

There are 6 color schemes available:

| Blue                                                                          | Turquoise                                                                          | Green                                                                          |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| <img src="https://online-cv.webjeda.com/assets/images/blue.jpg" width="300"/> | <img src="https://online-cv.webjeda.com/assets/images/turquoise.jpg" width="300"/> | <img src="https://online-cv.webjeda.com/assets/images/green.jpg" width="300"/> |

| Berry                                                                          | Orange                                                                          | Ceramic                                                                          |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| <img src="https://online-cv.webjeda.com/assets/images/berry.jpg" width="300"/> | <img src="https://online-cv.webjeda.com/assets/images/orange.jpg" width="300"/> | <img src="https://online-cv.webjeda.com/assets/images/ceramic.jpg" width="300"/> |

## Credits (Original Repo)

Thanks to [Nelson Estevão](https://github.com/nelsonmestevao) for all the [contributions](https://github.com/sharu725/online-cv/commits?author=nelsonmestevao).

Thanks to [t-h-e(sfrost)](https://github.com/t-h-e) for all the [contributions](https://github.com/sharu725/online-cv/commits?author=t-h-e).

Check out for more themes: [**Jekyll Themes**](http://jekyll-themes.com).

## Self Instructions

- To add a new section
  - Add new section with your details to `data.yml` with new field names if you want
  - Make a new `_includes` template with section mae
    - easiest is to copy existing similar layouts
    - update section name to file name, and any field names (although may require further css formatting in places)
    - update font-awesome icon atthe top (under section-title `h2`)
  - Add to section type to `index.html`
