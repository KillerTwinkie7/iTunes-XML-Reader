# iTunes-XML-Reader
Takes an XML file generated from an iTunes library and visualizes some data about it.

Before use, make absolutely sure you're not using the XML file that is currently stored in your iTunes folder. Make a copy before using this program, and the XML itself is modified to make it easier to read from. As such, attempting to move the XML file back into your iTunes library after this program uses it will cause issues.

So, make sure that you back up your iTunes Library XML.

Other than that, take your copied XML and put it in the XML folder. Don't change the name, and run the program. You should get some popups after a bit showing you some of your listening habits.

Eventually, I'd like to incorporate a GUI to select what kinds of things you'd like to see, but we'll see how far that goes.

A natural question has arisen, and that is "What does iTunes count as a 'skip'?". I did some research, and apparently, the skip count is only incremented if you press the next song button within the first 10 seconds of a song, but after the first 2-3 seconds. I will need to do more testing on this myself to see, but that would explain why songs with hundreds of plays only have single digit skips. 
