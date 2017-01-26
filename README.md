# Stars Reborn #

stars-reborn is a project intended to be a faithful reproduction of Stars! - a
classic 4X (explore, expand, exploit, and exterminate) 16-bit Windows space 
strategy game developed by Jeff Johnson and Jeff McBride circa 1996.  This
project is not endorsed by the original authors or publishers in any way.

The primary tenets this project are:

1.  Create an open game.  This means freely distributable, modifiable, and
    playable (cross-platform, modular, extensible).

    This first goal is in service to the idea that I (Brandon Arrendondo), want 
    people to enjoy this game, learn from it, support it, and keep it alive.

2.  Faithfully reproduce the original game.  This means all of the mechanics of
    the original game must be reverse-engineered (discovered, documented, and
    implemented) and all graphical components recreated.  Anyone familiar with
    the original game should be able to pick up this one and play it without
    missing any feature.
    
3.  Enhance the original game in a respectful and non-intrusive way.  Allow for
    a "Legacy" mode for those who prefer the original, but also allow for some
    of the known bugs and exploits to be fixed, as well as additional add-on
    capability to enhance and fix known micro-management issues.

4.  Stand on the shoulders of giants and acknowledge the contributions of the
    people who have worked hard to make this possible.  This includes previous
    clone efforts, people who have done analysis and documentation of the 
    original game, and anyone who helps in some way to hit the finish line.

This clone is written in Python, with QT (PySide) as a graphics framework.
Much of the data transfer is done in JSON with emphasis on modular components
to allow for future extensions.

Though the original game has simplistic graphics and basic overall game-play,
there are many complexities to it that make it a difficult game to imitate.  As
such, the developers of this clone are always actively seeking feedback and bug 
reports to improve the quality of this clone.

# Requirements #

stars-reborn at the outset is designed to be cross-platform.  The game should
run on any machine that can run:

 * Python 2.7+
 * PySide

# Installation #

TBD.

So far on Ubuntu, I have needed the following packages:

    sudo apt-get install python python-setuptools python-pyside qt4-dev-tools

# Useful Links #

Information about the original game:

    http://en.wikipedia.org/wiki/Stars!

Information about 4X games:

    http://en.wikipedia.org/wiki/4X

The current Stars! wiki:

    http://wiki.starsautohost.org/wiki/Main_Page

The Stars! strategy guide:

    http://stars.arglos.net/articles/ssg/ssg.htm

The Stars! article library:

    http://wiki.starsautohost.org/wiki/Article_Library

The Stars! community forum:

    http://starsautohost.org/sahforum2/
