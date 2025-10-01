Heroku buildpack: RingoJS
========================

This is a [Heroku buildpack](http://devcenter.heroku.com/articles/buildpack) for [RingoJS](http://ringojs.org/) apps.

Usage
-----

Example usage:

    $ ls
    server.js

    $ heroku create --stack cedar --buildpack https://github.com/jockm/heroku-buildpack-ringojs-jdk7.git
	
	$ git push heroku master

    -----> Heroku receiving push
    -----> Fetching custom build pack... done
    -----> RingoJS app detected
    -----> Installing RingoJS..... done

The buildpack will detect your app as a RingoJS project if it has a file called server.js. If you don't provide a Procfile, the build pack will default to launching your app with `ringo -m . server.js -p $PORT`

***NOTE:*** If you use a different filename for your application, you must still provide a file named `server.js` or you will get the following error message:

> Heroku push rejected, no Cedar-supported app detected

License
---
Copyright 2012 [Jock Murphy](http://jockmurphy.com).
This work is licensed under a Creative Commons Attribution 3.0 Unported License.
