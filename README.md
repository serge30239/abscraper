# abscraper

Script will create output folder to save temporary files.
Files will be saved while downloading and in the end combined into one output file.

The script is very verbose to diagnose all possible disruptions:
* Green messages are to feel good about how great everything works
* Yellow warning messages are for when repeated queries return empty result (in most cases that's normal)
* Red error messages are for when some chunk couldn't be downloaded. That will not cayse crash but final output may be missing a few records.
