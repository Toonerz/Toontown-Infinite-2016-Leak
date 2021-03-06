from toontown.shtiker import ShtikerPage
from panda3d.core import TextNode, Vec4
from direct.gui.DirectGui import DirectLabel, DirectFrame, DirectButton, DirectScrolledList, DGG
from toontown.toonbase import TTLocalizer
from toontown.building import GroupTrackerGlobals

SUIT_ICON_COLORS = (Vec4(0.863, 0.776, 0.769, 1.0), Vec4(0.749, 0.776, 0.824, 1.0),
                    Vec4(0.749, 0.769, 0.749, 1.0), Vec4(0.843, 0.745, 0.745, 1.0))

                    
class GroupTrackerGroup(DirectButton):
    def __init__(self, parent, leaderId, leaderName, shardName, category, memberIds, memberNames, **kw):
        self.leaderId = leaderId
        self.leaderName = leaderName
        self.shardName = shardName
        self.category = category
        self.memberIds = memberIds
        self.memberNames = memberNames
        self.playerCount = None

        if parent is None:
            parent = aspect2d

        text = TTLocalizer.GroupTrackerCategoryToText[self.category]
        
        optiondefs = (
            ('text', text, None),
            ('text_fg', (0.0, 0.0, 0.0, 1.0), None),
            ('text_align', TextNode.ALeft, None),
            ('text_pos', (0.0, 0.0, 0.0), None),
            ('text_scale', 0.05, None),
            ('relief', None, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(GroupTrackerGroup)
        
        self.playerCount = DirectLabel(parent=self, pos=(0.6, 0, 0), relief=None, text='', text_align=TextNode.ARight, text_scale=0.05, text_fg=(0, 0, 0, 1))
        self.updatePlayerCount()
        
    def destroy(self):
        if hasattr(self, 'playerCount'):
            if self.playerCount:
                self.playerCount.destroy()
                del self.playerCount
        
        DirectButton.destroy(self)
    
    def updatePlayerCount(self):
        maxPlayers = GroupTrackerGlobals.CATEGORY_TO_MAX_PLAYERS[self.category]
        self.playerCount['text'] = (`len(self.memberIds)` + '/' + `maxPlayers`) 
    
    def getLeaderId(self):
        return self.leaderId
        
    def getLeader(self):
        return self.leaderName
    
    def getDistrict(self):
        return self.shardName
    
    def getTitle(self):
        return TTLocalizer.GroupTrackerCategoryToText[self.category]
    
    def getCurrentPlayers(self):
        return len(self.memberIds)
        
    def getCategory(self):
        return self.category
        
    def getMaxPlayers(self):
        return GroupTrackerGlobals.CATEGORY_TO_MAX_PLAYERS[self.category]
        
    def getMemberNames(self):
        return self.memberNames
    
    def getMemberIds(self):
        return self.memberIds


class GroupTrackerPlayer(DirectButton):
    def __init__(self, parent, avId, name, isLeader, **kw):
        self.avId = avId
        self.name = name
        self.isLeader = isLeader
        self.leaderImage = None
        
        if parent is None:
            parent = aspect2d

        text=self.getName()
        
        optiondefs = (
            ('text', text, None),
            ('text_fg', (0.0, 0.0, 0.0, 1.0), None),
            ('text_align', TextNode.ALeft, None),
            ('text_pos', (-0.2, 0.0, 0.0), None),
            ('relief', None, None),
            ('text_scale', 0.05, None),
            ('command', self.loadPlayerDetails, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(GroupTrackerPlayer)
        
        boardingGroupIcons = loader.loadModel('phase_9/models/gui/tt_m_gui_brd_status')
        self.leaderButtonImage = boardingGroupIcons.find('**/tt_t_gui_brd_statusLeader')
        self.leaderImage = DirectButton(parent=self, relief=None, state=DGG.DISABLED, image=(self.leaderButtonImage), image_scale=(0.06, 1.0, 0.06), pos=(-0.26, 0, 0.02), command=None)
        
        self.setLeaderStatus(self.isLeader)
        boardingGroupIcons.removeNode()
    
    def destroy(self):
        if hasattr(self, 'playerCount'):
            if self.leaderImage:
                self.leaderImage.destroy()
                del self.leaderImage
        
        DirectButton.destroy(self)
    
    def setLeaderStatus(self, isLeader):
        self.isLeader = isLeader
        
        if self.isLeader:
            self.leaderImage.show()
        if not self.isLeader:
            self.leaderImage.hide()
    
    def getLeader(self):
        return self.isLeader
    
    def getName(self):
        # Lets cap a length so we dont have too long of names
        name = self.name
        if len(name) > 15:
            name = name[:16] + '...' # Chop the first x characters
        return name
    
    def getId(self):
        return self.avId
        
    def loadPlayerDetails(self):
        # TODO: Load player details based off avId for localAvatar
        pass


class GroupTrackerPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('GroupTrackerPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.groupWidgets = []
        self.playerWidgets = []
        self.images = []                # image nodes: Possible images to apply on groups
        self.scrollList = None          # DirectScrolledList: Holds the GroupTrackerGroup widgets
        self.scrollTitle = None         # DirectLabel: Title of the list that holds the groups
        self.playerList = None          # DirectScrolledList: Holds players when showing a specific group details
        self.playerListTitle = None     # DirectLabel: Title of the playerList
        self.groupInfoTitle = None      # DirectLabel: holds the group detail title to show on the right
        self.groupInfoDistrict = None   # DirectLabel: shows group detail district on the right
        self.statusMessage = None       # DirectLabel: Shows important messages like Loading... or "No boarding groups available"
        self.groupIcon = None           # DirectButton: Icon to associate with the group ex. sellbot icon or cashbot icon depending on group info
        self.wantGroupToggle = None     # DirectButton: Allows the toon to toggle his listing

    def load(self):
        self.listXorigin = -0.02
        self.listFrameSizeX = 0.67
        self.listZorigin = -0.96
        self.listFrameSizeZ = 1.04
        self.arrowButtonScale = 1.3
        self.itemFrameXorigin = -0.237
        self.itemFrameZorigin = 0.365
        self.buttonXstart = self.itemFrameXorigin + 0.293
        self.gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.scrollList = DirectScrolledList(parent=self, 
                                            relief=None, 
                                            pos=(-0.5, 0, 0), 
                                            incButton_image=(self.gui.find('**/FndsLst_ScrollUp'), 
                                                             self.gui.find('**/FndsLst_ScrollDN'),
                                                             self.gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                             self.gui.find('**/FndsLst_ScrollUp')
                                                             ), 
                                            incButton_relief=None, 
                                            incButton_scale=(self.arrowButtonScale, self.arrowButtonScale, -self.arrowButtonScale), 
                                            incButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin - 0.999), 
                                            incButton_image3_color=Vec4(1, 1, 1, 0.2), 
                                            decButton_image=(self.gui.find('**/FndsLst_ScrollUp'), 
                                                             self.gui.find('**/FndsLst_ScrollDN'),
                                                             self.gui.find('**/FndsLst_ScrollUp_Rllvr'), 
                                                             self.gui.find('**/FndsLst_ScrollUp')
                                                             ), 
                                            decButton_relief=None, 
                                            decButton_scale=(self.arrowButtonScale, self.arrowButtonScale, self.arrowButtonScale), 
                                            decButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin + 0.227), 
                                            decButton_image3_color=Vec4(1, 1, 1, 0.2), 
                                            itemFrame_pos=(self.itemFrameXorigin, 0, self.itemFrameZorigin), 
                                            itemFrame_scale=1.0,
                                            itemFrame_relief=DGG.SUNKEN, 
                                            itemFrame_frameSize=(self.listXorigin, self.listXorigin + self.listFrameSizeX,
                                                                 self.listZorigin, self.listZorigin + self.listFrameSizeZ
                                                                 ), 
                                            itemFrame_frameColor=(0.85, 0.95, 1, 1), 
                                            itemFrame_borderWidth=(0.01, 0.01), 
                                            numItemsVisible=15, 
                                            forceHeight=0.065, 
                                            items=self.groupWidgets
                                            )
                                            
        self.scrollTitle = DirectFrame(parent=self.scrollList, 
                                       text=TTLocalizer.GroupTrackerListTitle, 
                                       text_scale=0.06, 
                                       text_align=TextNode.ACenter, 
                                       relief=None,
                                       pos=(self.buttonXstart, 0, self.itemFrameZorigin + 0.127)
                                       )
        
        self.playerList = DirectScrolledList(parent=self, 
                                            relief=None, 
                                            pos=(0.45, 0, 0.1), 
                                            
                                            incButton_image=(self.gui.find('**/FndsLst_ScrollUp'), 
                                                             self.gui.find('**/FndsLst_ScrollDN'),
                                                             self.gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                             self.gui.find('**/FndsLst_ScrollUp')
                                                             ), 
                                            incButton_relief=None, 
                                            incButton_scale=(1.0, 1.0, -1.0), 
                                            incButton_pos=(0, 0, -0.28), 
                                            incButton_image3_color=Vec4(1, 1, 1, 0.05),
                                            
                                            decButton_image=(self.gui.find('**/FndsLst_ScrollUp'), 
                                                             self.gui.find('**/FndsLst_ScrollDN'),
                                                             self.gui.find('**/FndsLst_ScrollUp_Rllvr'), 
                                                             self.gui.find('**/FndsLst_ScrollUp')
                                                             ), 
                                            decButton_relief=None, 
                                            decButton_scale=(1.0, 1.0, 1.0),
                                            decButton_pos=(0.0, 0, 0.04), 
                                            decButton_image3_color=Vec4(1, 1, 1, 0.25), 
                                            
                                            itemFrame_pos=(0, 0, -0.05), 
                                            itemFrame_scale=1.0,
                                            itemFrame_relief=DGG.SUNKEN, 
                                            itemFrame_frameSize=(-0.3, 0.3,  #x
                                                                 -0.2, 0.06),  #z
                                            itemFrame_frameColor=(0.85, 0.95, 1, 1), 
                                            itemFrame_borderWidth=(0.01, 0.01), 
                                            numItemsVisible=4,
                                            forceHeight=0.05, 
                                            items=self.playerWidgets
                                            )
                                            
        self.playerListTitle = DirectFrame(parent=self.playerList, 
                                       text='', 
                                       text_scale=0.05, 
                                       text_align=TextNode.ACenter, 
                                       relief=None,
                                       pos=(0, 0, 0.08)
                                       )
        self.groupInfoTitle = DirectLabel(parent=self, text='', 
                                          text_scale=0.080, text_align=TextNode.ACenter,
                                          text_wordwrap=15, relief=None, pos=(0.45, 0, 0.5))
        self.groupInfoDistrict = DirectLabel(parent=self,
                                     text='',
                                     text_scale=0.050,
                                     text_align=TextNode.ACenter, 
                                     text_wordwrap=15, 
                                     relief=None, 
                                     pos=(0.45, 0, 0.4)
                                     )
        
        self.statusMessage = DirectLabel(parent=self, text='', text_scale=0.060, text_align=TextNode.ACenter, text_wordwrap=5, relief=None, pos=(0.45,0,0.1))
                                     
        # Group Image:
        self.groupIcon = DirectButton(parent=self, relief=None, state=DGG.DISABLED, image=None, image_scale=(0.35, 1, 0.35), image_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(0.45, 10, -0.45), command=self.doNothing)
        
        # Group Toggle:
        self.wantGroupToggle = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.7, 1, 1), text='', text_scale=0.052, text_pos=(0, -0.02), pos=(0.2, 0, -0.65), command=self.toggleWantGroup)
        self.updateWantGroupButton()
        
        
        # Loading possible group icons
        suitIcons = loader.loadModel('phase_3/models/gui/cog_icons')     
        bossbotIcon = suitIcons.find('**/CorpIcon')
        bossbotIcon.setColor(SUIT_ICON_COLORS[0])
        self.images.append(bossbotIcon)
        
        lawbotIcon = suitIcons.find('**/LegalIcon')
        lawbotIcon.setColor(SUIT_ICON_COLORS[1])
        self.images.append(lawbotIcon)
        
        cashbotIcon = suitIcons.find('**/MoneyIcon')
        cashbotIcon.setColor(SUIT_ICON_COLORS[2])
        self.images.append(cashbotIcon)
        
        sellbotIcon = suitIcons.find('**/SalesIcon')
        sellbotIcon.setColor(SUIT_ICON_COLORS[3])
        self.images.append(sellbotIcon)
        
        # Clean up
        self.clearGroupInfo()
        self.statusMessage.hide()
        
        suitIcons.removeNode()
        self.gui.removeNode()
        guiButton.removeNode()

        self.accept('GroupTrackerResponse', self.updatePage)

    def unload(self):
        self.scrollList.destroy()
        self.groupInfoDistrict.destroy()
        self.playerList.destroy()
        self.groupInfoTitle.destroy()
        self.groupIcon.destroy()
        self.wantGroupToggle.destroy()
        for widget in self.playerWidgets:
            widget.destroy()
        for widget in self.groupWidgets:
            widget.destroy()
        self.playerWidgets = []
        
        del self.scrollList
        del self.groupInfoDistrict
        del self.playerList
        del self.groupInfoTitle
        del self.groupIcon
        del self.wantGroupToggle
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        self.setGroups([]) # CLEAR IT ALL
        self.setPlayers()  # CLEAR IT ALL
        if(self.scrollList['items'] == []):
            self.statusMessage['text'] = TTLocalizer.GroupTrackerLoading
            self.statusMessage.show()
        base.cr.globalGroupTracker.requestGroups()
        taskMgr.doMethodLater(3, self.displayNoGroupsTaskHandler, self.uniqueName('timeout'))

    def displayNoGroups(self):
        self.statusMessage['text'] = TTLocalizer.GroupTrackerEmpty
        self.statusMessage.show()
        self.clearGroupInfo()
    
    def displayNoGroupsTaskHandler(self, task):
        self.displayNoGroups()
        return task.done

    def updatePage(self):
        taskMgr.remove(self.uniqueName('timeout'))
        groups = base.cr.globalGroupTracker.getGroupInfo()
        self.setGroups(groups)
        
    def exit(self):
        self.clearGroupInfo()
        ShtikerPage.ShtikerPage.exit(self)
        base.cr.globalGroupTracker.doneRequesting()
    
    def updateGroupInfoEventHandle(self, groupWidget, mouseEvent):
        self.updateGroupInfo(groupWidget)
        
    def updateGroupInfo(self, groupWidget):
        ''' Updates the Right Page of the Group Tracker Page with new Info '''
        self.statusMessage.hide()

        # Update the Player List
        self.setPlayers(groupWidget)
        self.playerList.show()

        # Update the Player List Title
        self.playerListTitle['text'] = ('Players ' + str(groupWidget.getCurrentPlayers()) + '/' + str(groupWidget.getMaxPlayers()) + ':')
        self.playerListTitle.show()

        # Update the District
        self.groupInfoDistrict['text'] = TTLocalizer.BoardingGroupDistrictInformation % { 'district' : groupWidget.getDistrict() }
        self.groupInfoDistrict.show()

        # Update the Title
        self.groupInfoTitle['text'] = groupWidget.getTitle()
        self.groupInfoTitle.show()

        # Update the Image
        self.groupIcon['image'] = self.images[GroupTrackerGlobals.CATEGORY_TO_IMAGE_ID[groupWidget.getCategory()]]
        self.groupIcon['image_scale'] = (0.35, 1, 0.35)
        self.groupIcon.show()

    def clearGroupInfo(self):
        self.playerList.hide()
        self.playerListTitle.hide()
        self.groupInfoDistrict.hide()
        self.groupInfoTitle.hide()
        self.groupIcon.hide()

    def setPlayers(self, groupWidget=None):
        ''' Calls updatePlayerList '''

        # Clear the Widgets that were held in the listings
        for playerWidget in self.playerWidgets:
            playerWidget.destroy()
        self.playerWidgets = []

        # Make a player widget for each player
        # TODO: Edit this stuff when avIds come from players
        if groupWidget:
            leaderId = groupWidget.getLeaderId()
            playerNames = groupWidget.getMemberNames()
            playerIds = groupWidget.getMemberIds()
            for playerName in playerNames:
                playerId = playerIds[playerNames.index(playerName)]
                isLeader = playerId == leaderId
                self.playerWidgets.append(GroupTrackerPlayer(parent=self, avId=playerId, name=playerName, isLeader=isLeader))

        self.updatePlayerList()

    def reconsiderGroupInfo(self, groupWidget):
        ''' If someone is viewing this info and it was updated, we also want to update the info being viewed '''
        if self.playerWidgets is None or self.playerList['items'] == []:
            return # No Info is being viewed at the moment since you cant have an empty group
        
        # We have to update if this group's leader is the leader in the playerlist being viewed right now
        leaderId = groupWidget.getLeaderId()
        
        # Check all the players in the playerList being viewed for the same leader
        for playerWidget in self.playerWidgets:
            if playerWidget.getLeader():
                if leaderId == playerWidget.getId():
                    self.updateGroupInfo(groupWidget)
                    return False
        
        return True
                
    def setGroups(self, groups):
        ''' Calls updateGroupList '''
        
        # Clear our Group Widgets
        for group in self.groupWidgets:
            group.destroy()
        self.groupWidgets = []
        
        wantReconsiderInfo = True
    
        # Create a new group widget for each group
        for group in groups:
            if not group[GroupTrackerGlobals.SHOW] or len(group[GroupTrackerGlobals.MEMBER_IDS]) == 0:
                continue # We are using this to see if this group is dead or if someone doesnt want it up
            leaderId = 0
            for i, g in base.cr.globalGroupTracker.leader2Group.items():
                if g == group:
                    leaderId = i
            if not leaderId:
                continue
                
            leaderName = group[GroupTrackerGlobals.LEADER_NAME]
            shardName = group[GroupTrackerGlobals.SHARD_NAME]
            category = group[GroupTrackerGlobals.CATEGORY]
            memberIds = group[GroupTrackerGlobals.MEMBER_IDS]
            memberNames = group[GroupTrackerGlobals.MEMBER_NAMES]
            
            groupWidget = GroupTrackerGroup(parent=self, leaderId=leaderId, leaderName=leaderName, shardName=shardName, category=category, memberIds=memberIds, memberNames=memberNames)
            groupWidget.bind(DGG.WITHIN, self.updateGroupInfoEventHandle, extraArgs=[groupWidget])
            self.groupWidgets.append(groupWidget)
            if wantReconsiderInfo:
                wantReconsiderInfo = self.reconsiderGroupInfo(groupWidget)
        
        # Edge case where a group that was removed, info might remain on the screen if it didn't exist any more
        if wantReconsiderInfo:
            self.clearGroupInfo()
        
        # There are no groups, hide the information
        if len(self.groupWidgets) == 0:
            self.displayNoGroups()
        self.updateGroupList()

    def updateGroupList(self): 
        self.statusMessage.hide()
        if self.scrollList is None:
            return
            
        # Clear the Group Listing
        for item in self.scrollList['items']:
            if item:
                self.scrollList.removeItem(item, refresh=True)
        self.scrollList['items'] = []
        
        # Re-populate the Group Listing
        for groupWidget in self.groupWidgets:
            self.scrollList.addItem(groupWidget, refresh=True)
        
        if len(self.groupWidgets) == 0:
            self.displayNoGroups()

    def updatePlayerList(self):
        if self.playerList is None:
            return

        # Clear the Player Listing
        for item in self.playerList['items']:
            if item:
                self.playerList.removeItem(item)
        self.playerList['items'] = []

        # Re-Populate the List
        for playerWidget in self.playerWidgets:
            self.playerList.addItem(playerWidget)

    def toggleWantGroup(self):
        if settings.get('grouptracker', False):
            settings['grouptracker'] = False
            base.cr.globalGroupTracker.showMe(False)
        else:
            settings['grouptracker'] = True
            base.cr.globalGroupTracker.showMe(True)
            
        base.localAvatar.wantGroupTracker()
        
        base.localAvatar.wantGroupTracker() # Updates the ai toon so the boarding group AI could know what he wants
        self.updateWantGroupButton()
    
    def updateWantGroupButton(self):
        if settings.get('grouptracker', False):
            self.wantGroupToggle['text'] = 'Hide Me'
        else:
            self.wantGroupToggle['text'] = 'Show Me'
            
    def doNothing(self):
        pass
    
