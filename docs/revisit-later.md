# Revisit later

Decisions and ideas deliberately left for a future pass.

## Wind and wave ranges use the upper bound

For a range such as "Wind northwest 15 to 20 knots" or "waves 0.5 to 1 metre", we store only the upper bound (20 knots, 1 metre). It is the safer reading for anyone on the water and fits the existing single-number fields.

The cost is that the display overstates the low end and loses the range. Alternatives to reconsider are the midpoint or separate minimum and maximum values.

## A distinct visual for Light wind

Light wind is valid data with no direction or speed, so it shouldn't look like a normal wind arrow. A dedicated map visual is worth exploring, separately from the bulletin interpretation work.

## Show active Marine warnings

A strong wind warning can be in effect today with nothing on screen, which matters for people on the water. This is a separate follow-up to the bulletin interpretation work, which will make the warning's kind, status, and area available.

## Safer deployment practices

A push to PythonAnywhere deploys and migrates immediately, and data repairs are run by hand afterward. This is acceptable for now, but worth improving.

## Unused bulletin output is kept on purpose

Issue times, conditions, wave phrases, and extended-forecast days aren't displayed or stored as fields today. They are being kept because future features are planned for them, so don't remove them as dead code.

Marine warning entries carry only an issue line in their Bulletin text. The warning's kind, status, and area are in the entry title, for example "STRONG WIND WARNING IN EFFECT, Eastern Lake Superior". Any future warning feature should start from the title.

## Check whether a scrape succeeded

`POST /weather/` now returns `success: false` with a 502 when it can't read the feed, and a 503 when it can't save it. The scheduled job that calls it doesn't check either yet, so a broken scrape goes unnoticed until the site's "Updated" time looks old. Alerting on a failed response, or on several in a row, would catch it early.
