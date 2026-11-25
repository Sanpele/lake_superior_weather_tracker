# Lake Superior Weather Tracker

Tracks Environment Canada's marine forecasts for Lake Superior and shows each region's conditions on a map.

## Language

**Bulletin**:
The title and text of one entry in the marine feed, covering one report type for one area of the lake.
_Avoid_: Summary, entry text

**Conditions**:
What we understood from a Bulletin.
_Avoid_: Parsed summary, parsed data

**Opening wind**:
The first wind a forecast Bulletin states, taken at the top of any stated speed range.
_Avoid_: Current wind, latest wind

**Wind direction**:
The compass direction a wind blows from. A northwest wind moves toward the southeast.
_Avoid_: Wind heading

**Current**:
A Bulletin is current when it appeared in the newest feed we read, whenever it was published. A Bulletin that drops out of the feed is no longer current.
_Avoid_: Latest, today's

**Daily conditions**:
What a region's current Bulletins tell us about its wind, waves, and visibility. Every region has Daily conditions, even when parts of them are Unknown.
_Avoid_: Daily report, weather summary

**Peak wave height**:
The highest wave height a wave Bulletin states anywhere in its forecast period.
_Avoid_: Current waves, wave height

**Light wind**:
A forecast of wind too light to have a stated direction or speed. It is valid data, not missing data.
_Avoid_: Calm, no wind

**Variable wind**:
A forecast of wind with a stated speed but no steady direction.
_Avoid_: Shifting wind, unknown direction

**Marine warning**:
An Environment Canada alert for an area of the lake, with a kind such as strong wind or squall and a Warning status.
_Avoid_: Alert, undefined report

**Warning status**:
Whether a Marine warning is a watch, in effect, or ended.
_Avoid_: Warning state

**Whole-lake**:
The area covering all of Lake Superior, as distinct from the eastern and western regions.
_Avoid_: Undefined region, both regions

**Unknown**:
The result when a Bulletin's text could not be interpreted. It never stands in for a guessed value.
_Avoid_: Default, none
