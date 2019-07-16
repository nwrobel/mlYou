'''
Version of playstats update script that adds new feature: 
    allows certain playback data to be edited (deleted) based on user's choice through command line 
    prompts and input
'''


# Take the SongPlaybackRecord instances display them in table form to the user, once everything
# has been prepared and we are ready to write the updated tags
print("The following playstat tag updates are ready to write to the audio library - SongPlaybackRecords:")
PrintPlaybackDataTable(songPlaybackRecords)

# continue if we want to make the changes, otherwise we exit
writeChanges = input("Enter the action you wish to take - (w)rite data, (m)odify data, or (q)uit  [w/m/q]: ")

if ((writeChanges == 'q')):
    print("Exiting due to choice of user")
    return

if ((writeChanges == 'm')):
    # display the table again, modified with line numbers so the user can identify what to edit

    # Take the user input
    doneEditing = False
    while(not doneEditing):
        recordNumberToEdit = input("Enter the number of the SongPlaybackRecord you wish to modify")

        # We assume that songPlaybackRecords list has items added to PrettyTable in the order of the list,
        # so we can use that number to access the record we need: TEST THIS
        songPlaybackRecordToEdit = songPlaybackRecords[recordNumberToEdit - 1]

        editAction = input("Enter modification action for this record - (dr)delete record, (dt)delete a playback time")

    if (editAction == 'dr'):
        confirm = input("Are you sure you want to delete record #" + recordNumberToEdit + "? [y/n]")
        if (confirm == 'y'):
            songPlaybackRecords.remove(songPlaybackRecordToEdit)
        elif:
            print("Cancelling action for record #", recordNumberToEdit)

    elif (editAction == 'dt'):
        # Cannot delete a playback time from this playback record if it is the only one for this record
        if (songPlaybackRecordToEdit.playbackTimes == 1):
            print("Cannot delete playback time for record #", recordNumberToEdit, ", it is the only playback for this record")
        else:
            print("Playback times for record #", recordNumberToEdit, ":")
            # Print the playback times, with a number for each
            for index, playbackTime in enumerate(songPlaybackRecords.playbackTimes)
                print(index, " - " , mlu.common.time.FormatTimestampForDisplay(playbackTime))

                playbackToDelete = input("Enter the line number of the playback time you wish to delete")
    
                # FINISH - confirm, then delete

    
   
        







 
      






