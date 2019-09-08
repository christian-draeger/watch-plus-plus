# watch++
An adjustable clock with date and battery display for the [card10 badge](https://card10.badge.events.ccc.de/).
You'll always find the latest revision at [Hatchery](https://badge.team/projects/watch)

## Features
* Displays time as a seven-segment display
* Displays date including current weekday
* Displays seconds as a bar at the bottom of the screen that become brighter the more seconds of a minute has been passed
* Allows changing the time and date completely via buttons
* Displays the Battery status of your card10-badge

## Controls
* long press button in the lower left corner to switch into edit mode
  * allows to set hour, minute, second, day, month, year
* use upper right button to increment value (+)
* use lower right button to decrement value (-)

## Optional

To run watch++ as the defaut app edit the main.py in the root folder of your card10 badge.
Replace the line 

```
default_app = "apps/analog_clock/__init__.py"
```
with 
```
default_app = "apps/watch/__init__.py"
```

OR

Rename the [__init__.py](__init__.py) to `main.py` and drop it in the root folder of your card10 badge to use the digital clock as default app that is getting startet after your badge has been booted.

OR

set latest version of watch++ as default app by executing:

```
wget -O /Volumes/CARD10/main.py https://raw.githubusercontent.com/christian-draeger/watch-plus-plus/master/__init__.py
```
