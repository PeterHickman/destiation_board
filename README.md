# destiation_board

The boy likes buses and there exists (for a significant price) destination boards that can show any bus or train departures

So I wrote one for him in Python that accesses data from the local bus company and displays it in the style of a dot matrix departure board

Unless you live in Brighton this is probably not of immediate use

## Notes

1. The font used is [TEXASLED.TTF](https://www.fonts4free.net/texas-led-font.html)
2. `config.yaml` contains the list of stops we are interested in with a display name
3. `fake_touch` in `settings` is used to get pygame working with a touch screen (hides the mouse)
