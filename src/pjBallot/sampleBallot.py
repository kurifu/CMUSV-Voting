from __pyjamas__ import JS
from fysom import Fysom
from ballotTree import Race
from pyjamas.ui import KeyboardListener
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.HTML import HTML

contestPosition = 0
candidatePosition = 0
confirm = 0
currObj = ""

contest = HorizontalPanel()
contest.setStyleName('words')
candidate = HorizontalPanel()
candidate.setStyleName('words')
selection = HorizontalPanel()
selection.setStyleName('words')
status = HorizontalPanel()
status.add(HTML('STATUS'))
status.setStyleName('words')

title = HorizontalPanel()
instructions = HorizontalPanel()

#

JS("""
var snd = new Audio();
""")

race = Race('', [], '', '')

def playAudio():
    global currObj
    path = "http://10.0.22.220/" + currObj.audioPath
    print "currObj is", currObj.name, ", path is", path
    JS('''
    snd.src = path;
    snd.play();
    ''')
    

def sendRace(srace):
    global race
    race = srace
    
def getInstruction():
    return race.name

def setContest():
    global candidatePosition
    curcontest = race.selectionList[contestPosition]
    contest.clear()
    contest.add(HTML('<b /> Contest: %s' % curcontest.name))
    candidateList = curcontest.selectionList
    if not curcontest.userSelection:
        candidatePosition = 0
        selection.clear()
        selection.add(HTML('<b /> Selection: -'))
    else:
        candidatePosition = candidateList.index(curcontest.userSelection[-1]) 
        selection.clear()
        selection.add(HTML('<b /> Selection: %s' % curcontest.userSelection[-1].name))
    print "currObj is", currObj
    playAudio()
    
def setConfirm(num):
    confirm += num;
    status.clear()
    if confirm % 2 == 0:
        status.add(HTML('YES'))
        return True
    else:
        status.add(HTML('NO'))
        return False
    
def setCandidate():
    global currObj
    curcontest = race.selectionList[contestPosition]
    candidateName = curcontest.selectionList[candidatePosition].name
    candidate.clear()
    candidate.add(HTML('<b /> Candidate: %s' % candidateName))    
    print "currObj is", currObj
    playAudio()
    

def makeSelection():
    curcontest = race.selectionList[contestPosition]
    curcandidate = curcontest.selectionList[candidatePosition]
    curcontest.userSelection[:] = []
    curcontest.userSelection.append(curcandidate)
    selection.clear()
    selection.add(HTML('<b /> Selection: %s' % curcontest.userSelection[-1].name))
 

def onKeyPress(sender, keycode, modifiers):
    global contestPosition, candidatePosition, fsm, currObj
    
    contestList = race.selectionList
    candidateList = race.selectionList[contestPosition].selectionList
    
    # Contests, only keys allowed are Up/Down to cycle contests, and Enter to select
    if fsm.current == 'contests':
        if keycode == KeyboardListener.KEY_UP:
            contestPosition = (contestPosition+1) if (contestPosition+1<len(contestList)) else 0
            currObj = race.selectionList[contestPosition]
        elif keycode == KeyboardListener.KEY_DOWN:
            contestPosition = len(contestList)-1 if (contestPosition==0) else contestPosition-1
            currObj = race.selectionList[contestPosition]
        elif keycode == KeyboardListener.KEY_ENTER:
            fsm.selectCandidate()
            setCandidate()
            return
        else:
            return
        setContest()
        
    # Candidates; only keys allowed are Left/Right to cycle candidates, and Enter to select
    elif fsm.current == 'candidates':
        if keycode == KeyboardListener.KEY_RIGHT:
            candidatePosition = (candidatePosition+1) if (candidatePosition+1<len(candidateList)) else 0
        elif keycode == KeyboardListener.KEY_LEFT:
            candidatePosition = len(candidateList)-1 if (candidatePosition==0) else candidatePosition-1
        elif keycode == KeyboardListener.KEY_ENTER:
            fsm.reviewCandidates()
        setCandidate()
        
    # Review Candidate Selection: Yes or No, then proceed to end or back up to Candidates
    elif fsm.current == 'review_candidates':
        if keycode == KeyboardListener.KEY_RIGHT:
            setConfirm(1)
        elif keycode == KeyboardListener.KEY_LEFT:
            setConfirm(-1)
        elif keycode == KeyboardListener.KEY_ENTER:
            if confirm % 2 == 0:
                race.selectionList[contestPosition].userSelection.append(candidatePosition)
                makeSelection()
                fsm.doneReview()
            else:
                fsm.reselectCandidates()
    
    # Review Ballot: Yes or No, then proceed to end or back up to Contests
    elif fsm.current == 'review_ballot':
        if keycode == KeyboardListener.KEY_RIGHT:
            setConfirm(1)
        elif keycode == KeyboardListener.KEY_LEFT:
            setConfirm(-1)
        elif keycode == KeyboardListener.KEY_ENTER:
            if confirm % 2 == 0:
                fsm.doneBallot()
            else:
                fsm.reselectContest()

'''
Traverse the list as provided by the 'obj', which can be either of type Race or Contest
'''
def traverselist(obj):
    alist = obj.selectionList
    print('* ' + alist[contestPosition].name + ' highlighted *')

'''
Define State Behaviors
'''
def printstatechange(e):
    print 'event: %s, src: %s, dst: %s' % (e.event, e.src, e.dst)

def onintro(e): 
    print 'hello!'
    
def oncontests(e): 
    candidate.clear()
    status.clear()
    print('\nThe contests are:')
    for i, contest in zip(range(len(race.selectionList)), race.selectionList):
        print('\t' + str(i + 1) + ') ' + contest.name) 
    traverselist(race)
    # initialize our current object, which is the first contest
    currObj = race.selectionList[contestPosition]
    print "current contest is " + currObj.name

# e.pos: the current Contest, which is the position in the race.selectionList
def oncandidates(e):
    currContest = race.selectionList[contestPosition]
    print('\nCurrent race is: ' + currContest.name)
    print('Candidates are:')
    for i, person in zip(range(len(currContest.selectionList)), currContest.selectionList):
        print("\t" + str(i + 1) + ') ' + person.name)
    traverselist(currContest)
    # initialize our current object, which is the first contest
    currObj = currContest.selectionList[contestPosition]
    print "current candidate is " + currObj.name

def onreviewcandidates(e):
    print('\nReview Your Choice for ' + race.selectionList[contestPosition].name + ':')
    candidate = race.selectionList[contestPosition].selectionList[candidatePosition]
    print('\t' + candidate.name)
    setConfirm(0)
    
def oncheckdone(e):
    for i, contest in zip(range(len(race.selectionList)), race.selectionList):
        if len(contest.userSelection) == 0:
            fsm.nextContest()
            return
    fsm.reviewBallot()

def onreviewballot(e):
    print('\nReview your selections:')
    for contest in race.selectionList:
        print(contest.name + ':' + contest.userSelection[0].name)
    setConfirm(0)
    
def ondoneballot(e):
    print('\nVoting complete! Thanks for using this system!')


'''
States and Events
'''
fsm = Fysom({
  'initial': 'intro',
  'events': [
    {'name': 'startVoting', 'src': 'intro', 'dst': 'contests'},
    {'name': 'selectCandidate', 'src': 'contests', 'dst': 'candidates'},
    {'name': 'reviewCandidates', 'src': 'candidates', 'dst': 'review_candidates'},
    {'name': 'reselectCandidates', 'src': 'review_candidates', 'dst': 'candidates'},
    {'name': 'doneReview', 'src': 'review_candidates', 'dst': 'check_done'},
    {'name': 'nextContest', 'src': 'check_done', 'dst': 'contests'},
    {'name': 'otherContest', 'src': 'contests', 'dst': 'contests'}, 
    {'name': 'reviewBallot', 'src': 'check_done', 'dst': 'review_ballot'},
    {'name': 'reselectContest', 'src': 'review_ballot', 'dst': 'contests'}, 
    {'name': 'doneBallot', 'src': 'review_ballot', 'dst': 'done_ballot'},
  ],
    'callbacks': {
     'onintro': onintro,
     'oncontests': oncontests,
     'oncandidates': oncandidates,
     'onreview_candidates': onreviewcandidates,
     'oncheck_done': oncheckdone,
     'onreview_ballot': onreviewballot,
     'ondone_ballot': ondoneballot
    }
})


'''
Assign State Behaviors
'''

#fsm.onchangestate = printstatechange
#fsm.startVoting()
    
