### Config Options

- `card_stats`: "brief" or "detailed"(as the info window from the browser)
- `deck_names_length`: default is 40, if a string is longer it's split up over multiple lines
- `deck_options`: "brief" or "long"
- `hide_time_column_from_revlog`: "true" or "false"
- `highlight_colors`:   "true" or "false"
- `num_of_revs`:  default is 3,  how many prior reviews should be shown in table for current and prior card
- `optiongroup_names_length`: default is 20,
- `show_deck_names`: "true" or "false"
- `show total cards studied today`: "true" or "false", refers to the whole collection. you can't limit this to the current deck
- `thresholds__ivl_mod_color__lower`:  70,
- `thresholds__ivl_mod_color__upper`:  110,
- `thresholds__lapse_mod_color__lower`:  30, 
- `thresholds__lapse_mod_color__upper`:  70 
- `try_to_show_origvmod_scheduler`:  "true" or "false"

### Meaning of abbreviations used

The add-on uses abbreviations in the sidebar so that the sidebar can be more compact.

On top for the deck options there is:

- "OptGr": Name of the option group
- "Steps": Steps ("New Cards" tab of deck options)
- "LSteps": Steps ("Lapses" tab of deck options)
- "GrIv": Graduating Interval ("New Cards" tab of deck options)
- "EaIv": Easy Interval ("New Cards" tab of deck options)
- "EaBo": Easy Bonus ("Reviews" tab of deck options)
- "IvMo": Interval Modifier ("Reviews" tab of deck options)
- "LpIv": New interval ("Lapses" tab of deck options)

&nbsp;

Then you have "Ivl" for "Interval" and "cid" which stands for "card id". the "card id" stores the
creation time of card in a special format (epoch/unix time in milliseconds).

&nbsp;

The columns in the revision table have the following meaning:

- "Date": the last time you rated the card
- "T" refers to the state of the card: Learned ("Lrn"), Review ("Rev"), Relearned ("ReLn"), Filtered ("Filt"), Defered/Rescheduled ("Resch")
- "R" means how you rated it: "1" means again, "2" means hard, "3" is good, "4" is easy (if you the v2 scheduler)
- "Ivl" is the interval
- "Ease" means the ease(ivlfct) property of the card: It's the approximate amount the interval will grow when you answer a review card with the “Good” button, see https://docs.ankiweb.net/#/stats?id=card-info
