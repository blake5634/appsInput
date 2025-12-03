import csv
import sys
import datetime as dt
from itertools import combinations
import numpy as np

def error(msg):
    print(f'Error: {msg}')
    help()
    quit()


#
#  set some configurations
#
ifURL = 'https://facultysearch.interfolio.com/28343/positions/171499'
TESTROW = -1  # <0 = no test printout
SORTING = True  # can be changed in user menu
SCORES_FNAME = 'fac_scores.txt'

# define col headers of our working files
workingFileCols = ['Firstname', 'Lastname', 'Teaching', 'Research', 'WIRC', 'Id','Link', 'Last date', 'Which area','Highest degree school']


assignFileCols = ['Firstname', 'Lastname', 'Id', 'rev 1', 'rev 2', 'Wscore', 'Link', 'Last date', 'Area', 'Highest degree school']

headerTypeDict = {'Assignments':assignFileCols, 'WorkingFile':workingFileCols}

#
#   Begin code
def help():
    print(f'''
    Log into {ifURL}
    Click "Reports" on left menu.
    On "Position Names": Select 171499.
    Choose "Columns" in upper right.
    Select following columns:
      "Selected": ALL
      "Application":  Initial Submission Date
                      Highest Degree Institution
      "Forms/Research Area:":
                Which Area best describes
                (Main Research Area
                Cross-cutting Area(s))
    Download CSV

    then:

    >appsInput.py   [Downloaded csv filename]

        ''')

class collection:
    #
    #  collection is the same for all types but its use dictates the header names (via coltype)
    #
    def __init__(self):
        self.app_list = []

    def add(self,app):
        self.app_list.append(app)

    def __len__(self):
        return len(self.app_list)

    def assignReviewers(self):
        revlist = ['Blake', 'Amy', 'Baosen', 'Sajjad']
        nrevs = len(revlist)
        combos = list(combinations(revlist,2))
        # print(revlist)
        # print(combos)
        cycle = 3
        p1 = np.random.randint(len(combos))  # start at random combo
        j = 0
        for app in self.app_list:
            if (app.crev01 is None) and (app.crev02 is None):
                if j%cycle==0:
                    p1 = (p1+1)%len(combos)
                j += 1
                app.crev01 = combos[p1][0]
                app.crev02 = combos[p1][1]
                print(f'{app.iD:10} {app.crev01} {app.crev02}')

    #
    #  special corrections, exceptions, etc.
    #
    def processExceptionsAndHacks(self):
        for app in self.app_list:
            if app.iD=='6324197': # special end date correction for Charlotte DeVol
                # this candidate applied to wrong position due to our fault.
                app.appDate = '11/13/2025'
        return




class applicant:
    def __init__(self,fn,ln,iD,aD,ar,ins,scores=None):
        self.fName = fn
        self.lName = ln
        if scores is not None:
            self.teaching = scores[0]
            self.research = scores[1]
            self.wirc     = scores[2]
        else:
            self.teaching = None
            self.research = None
            self.wirc     = None

        self.iD = iD
        # self.url = 'https://facultysearch.interfolio.com/28343/positions/171499/applications/' + iD
        self.url = ifURL + '/applications/' + iD
        self.appDate = aD
        # self.createDate = dt.datetime.today()
        self.area = ar
        self.ins = ins
        self.crev01 = None
        self.crScore01 = None
        self.crev02 = None
        self.crScore02 = None
        # faculty scores will be e.g.
        #     (name, ResearchScore, TeachingScore, WIRCScore)
        #     [('hannaford', 3.5, 2.5, 4), ('Orsborn', 2.0, 1, 1,5), ... ]
        self.facScores = []

    def addFacScore(name, rsrch, tch, wirc):
        for score in [rsrch,tch,wirc]:
            SCORES = False
            if type(score) != type(3.5) or type(score) != type(3):
                error('faculty score must be a float or int')
            else:
                if score is not None:
                    SCORES = True   # I have seen at least one score
            if not SCORES:
                error('faculty scores are blank for ', name)
        self.facScores.append(name, rsrch, tch, wirc)


    def getAvgFacScores():
        if len(self.facScores) == 0:
            return 0
        n=0
        sum=0
        for rec in self.facScores:
            for s in rec[1:]:
                if s is not None:
                    sum += s
                    n += 1


    def wirc_avg(self):
        n=0
        sum = 0
        if self.crScore01 is not None:
            n += 1
            sum += self.crScore01
        if self.crScore02 is not None:
            n += 1
            sum += self.crScore02
        if n==0:
            return None
        else:
            return sum/n


        if self.crScore is None:
            n=1


    def __repr__(self):
        t = ''
        name = self.lName + ', ' + self.fName
        t += f'{name:25}'
        t += f'{self.iD:9} '
        t += f'{self.appDate:15} '
        t += f'{self.area:20}'
        # t += f'{self.createDate.strftime('%Y-%m-%d'):15}'
        return t

    def genSSRow(self,shType='WorkingFile'):
    # # desired output cols, in order
    # f = ['Firstname', 'Lastname', 'Teaching', 'Research', 'WIRK', 'Id','Link', 'Last date', 'Which area']
        try:
            headerTypeDict[shType]
        except:
            error('genSSRow: invalid header type param:',shType)
        if shType=='WorkingFile':
            s1 = self.teaching
            s2 = self.research
            s3 = self.wirc
            # reviewer scores if present
            if (s1 ) is None:
                s1 = ''
            if (s2 ) is None:
                s2 = ''
            if (s3 ) is None:
                s3 = ''
            r = [self.fName, self.lName,  s1, s2, s3, self.iD, self.url, self.appDate,self.area, self.ins]
            return r
        elif shType=='Assignments':
            r = [self.fName, self.lName,  self.iD, self.crev01, self.crev02,'', self.url, self.appDate,self.area, self.ins]
            return r
        else:
            error('Unknown SSRow type: ', shType)


def readCmteAssgmtsFile(inFileName):
    #
    #  read in a committee review assignments file
    #
    # check the input file
    if 'Ass' not in inFileName:
        error('readCmteAssgmtsFile: filename does not contain "Ass": {inFileName}')

    f = open(inFileName, 'r',encoding='utf-8-sig')

    data = csv.reader(f)

    # read the input header
    inputHeaderRow = next(data)

    existApps = collection()  # make a header just like the Assignments file

    #  cmte assignments header:
    # Firstname, Lastname, Id, rev 1,rev 2, Wscore, Link, Last date, Which area, Highest degree school

    for r in data:
        fn   = r[0]  # cmte ass. header
        ln   = r[1]
        idn  = r[2]
        rev1 = r[3]
        rev2 = r[4]
        wsc = r[5]
        lk  = r[6]
        ad  = r[7]
        ar  = r[8]
        ins = r[9]
        tmp = applicant(fn,ln,idn,ad,ar,ins )
        tmp.crev01 = rev1
        tmp.crev02 = rev2
        existApps.add(tmp)
    return existApps


def readWorkingFile(inFileName):

    if not inFileName.startswith('Working'):
        error('Read Faculty Scores: Command Line arg must be a Working file.')
    #
    #  read in a working file
    #
    f = open(inFileName, 'r',encoding='utf-8-sig')

    data = csv.reader(f)

    # read the input header
    inputHeaderRow = next(data)
    outputCols = headerTypeDict['WorkingFile']
    #
    # for i,c in enumerate(inputHeaderRow):
    #     if (c != outputCols[i]):
    #         print('input Working file header: ', inputHeaderRow)
    #         print('               outputCols: ', outputCols)
    #         error('readWorking: input header mismatch')

    # create collection for the working file apps.
    existApps = collection()
    for r in data:
        fn  = r[0]
        ln  = r[1]
        tch = r[2]
        rsr = r[3]
        wir = r[4]
        idn = r[5]
        lk  = r[6]
        ad  = r[7]
        ar  = r[8]
        ins = r[9]
        tmp = applicant(fn,ln,idn,ad,ar,ins, scores=[tch,rsr,wir])
        existApps.add(tmp)
    return existApps

def readDownload(inFileName):
    #
    #  read in a downloaded file
    #
    f = open(inFileName, 'r',encoding='utf-8-sig')

    data = csv.reader(f)

    # desired output  order of the input cols we select
    selectedCols = ['Firstname', 'Lastname', 'Id', 'Last date', 'Which area', 'Highest degree school']

    # read the input header
    inputHeaderRow = next(data)

    print('Input Header: ', inputHeaderRow)

    # print('Selected Output Columns: ',selectedCols)

    oldcols=[]
    for selHdrCol in selectedCols:
        for i,ht in  enumerate(inputHeaderRow):
            if ht.startswith(selHdrCol):
                oldcols.append(i)

    print('Columns selected from download: ',oldcols)

    applicants = collection()

    j = 0
    for row in data:
        fn = row[oldcols[0]].strip()  # oldcols is in 'selectedCols' order
        ln = row[oldcols[1]].strip()
        iD = row[oldcols[2]].strip()
        date = row[oldcols[3]][0:10]
        ar = row[oldcols[4]].strip()
        ins = row[oldcols[5]].strip()  # highest degree school
        tmp = applicant(fn,ln,iD,date,ar,ins)
        applicants.add(tmp)
        if j==TESTROW:
            print('TestRow: ', row)
            m=0
            for c in row:
                print(f'{m}: {c}')
                m+=1
            print(applicants[-1])
        j+=1


    print(f'parsed and loaded {len(applicants)} applicants')

    f.close()

    applicants.processExceptionsAndHacks()

    if TESTROW >= 0:
        print(applicants.apps[TESTROW])
        print('')
        print(applicants.apps[TESTROW].genSSRow())

    return applicants

#
#   identify new applicants out of a newer download
def selectNewApps(appsNew, appsOld):
    tmp = collection()
    seen = [app.iD for app in appsOld.app_list]
    tmp.app_list = [app for app in appsNew.app_list if app.iD not in seen]
    return tmp


def mergeCollections(apps1, apps2):
    """Merge two lists of applicant objects, removing duplicates by iD. (thanks Claude)"""
    seen = [app.iD for app in apps1.app_list]
    return apps1.app_list + [app for app in apps2.app_list if app.iD not in seen]

def concatenateCollections(apps1,apps2):
    new = collection()
    new.app_list = apps1.app_list + apps2.app_list
    return new

def sortApps(applicants):
    print('Sorting (got here)')
    """Sort applicants by date, then by iD."""
    applicants.app_list =  sorted(applicants.app_list, key=lambda app: (dt.datetime.strptime(app.appDate.strip(), '%m/%d/%Y'), app.iD)).copy()
    return applicants

def writeOut(applicants, headerType, ofn):
    #
    #  Save new output file (sorted date, then by ID)
    #
    # ofn = 'Working_.csv'

    #validate headerType param
    try:
        header = headerTypeDict[headerType]
    except:
        error('Unknown header type for output file: ', headerType)

    if SORTING:
        applicants = sortApps(applicants)

    of = open(ofn, 'w')
    writer = csv.writer(of)

    #write out the header row
    writer.writerow(header)
    for a in applicants.app_list:
        row = a.genSSRow(shType=headerType)
        writer.writerow(row)

    of.close()

    print(f'{headerType} Output Saved: {ofn} (n={len(applicants)})')

#
# def writeCmteAssign(applicants, ofn):
#     #
#     #  Save new output file (sorted date, then by ID)
#     #
#     if SORTING:
#         applicants = sortApps(applicants)
#
#     of = open(ofn, 'w')
#     writer = csv.writer(of)
#
#     #write out the header row
#     writer.writerow(applicants.header)
#     for a in applicants.app_list:
#         row = a.genSSRow(shType='committee')  # add reviewer fields
#         writer.writerow(row)
#     of.close()
#
#     print(f'Committee Assignments Output Saved: {ofn}')

def writeFacScores(coll):
    sfn = SCORES_FNAME
    sfp = open(sfn,'w')
    for app in coll.app_list:
        for (name, res,tch,wirc) in app.facScores:
            row = f'{app.iD} | {name} | {res} | {tch} | {wirc}'
            print(row,file=sfp,end='\n')
    sfp.close()


def readFacScores(coll):
    sfn = SCORES_FNAME
    sfp = open(sfn,'r')
    for row in sfp:
        (scId, name, res,tch,wirc) = row.split('|')
        scId = scId.strip()
        #
        ##   find the app by id
        #          and update the applicant
        for app in coll.app_list:
            # print(f'checking: {scId} {app.iD}')
            if scId == app.iD:
                print(f'match {scId}',name, res, tch, wirc)
                # x = input('continue...')
                app.facScores.append((name, res, tch, wirc))
    sfp.close()
    return coll


def menu(mdat):
    try:
        x = mdat['labels']
        # x = mdat['meth']
        # x = mdat['style']
        nitems = len(mdat['labels'])
    except:
        error('Bad menu setup inputs:', mdat)
    i = 1
    # print menu header
    #
    statuskeys = mdat['state'].keys()
    for k in statuskeys:
        print(f"{k:10} : {mdat['state'][k]} ",end='')
        print('')
    #
    # print the choices
    #
    for mi in mdat['labels']:
        print(f'{i:3}: {mi:20}')
        i+=1
    resp = input('Select: ')
    if resp == '':
        quit()
    if resp.lower().startswith('he'):
        help()
    try:
        j = int(resp)-1
        assert int(j) < nitems
    except:
        error(f'unusable response: {resp}')
    return j, mdat['labels'][j]


################################################################################3
#
#  Testing
#
#
def run_tests():
    tmitems = ['Test Write Fac scores','Test Read Fac scores', 'Return']

    tmdata = {'labels':tmitems, 'state':{'sorting':SORTING}}

    while True:
        j, selcmd = menu(tmdata)
        if selcmd.startswith('Test Write Fac'):
            tcol = collection()

            #def __init__(self,fn,ln,iD,aD,ar,ins,scores=None):
            app1 = applicant('Robert', 'Wagner',  '0001', '2/10/2022','English Lit', 'Harvard')
            app2 = applicant('Alice', 'Eckhart',  '0002', '3/01/2022','Shakespeare', 'UCLA')
            app3 = applicant('James', 'Chan',     '0003', '2/15/2022','Humor', 'Purdue')
            app4 = applicant('Julie', 'Johnson',  '0004', '2/22/2022','Detective Fic.', 'Michigan')
            tcol.add(app1)
            tcol.add(app2)
            tcol.add(app3)
            tcol.add(app4)

            # a list just for testing.
            testfacscores = [
                ('0001', 'Prof Hobbs', 3.5, 2, 3),
                ('0001','Huang', 2,   2, 2),
                ('0003', 'Scott', 3, 3, 2.5),
                ('0001', 'Scott', 2, 4, 3),
                ('0002', 'Kalman', 2.5, 3.5, 1.5),
                ('0003', 'Kalman', 4.4, 4, 5),
                ('0002', 'Steinmetz', 3.5, 3.5, 3.5)
                ]

            for ts in testfacscores:
                for app in tcol.app_list:
                    # print(f'{ts[0]} =?= {app.iD}')
                    if ts[0]==app.iD:
                        # print('got here: {app.iD}')
                        app.facScores.append(ts[1:])

            writeFacScores(tcol)

            print(f'Faculty scores file written to {SCORES_FNAME}.   Data should be: ')
            for x in testfacscores:
                print(x)
            quit()

        if selcmd.startswith('Test Read Fac'):
            tfp = open(SCORES_FNAME, 'r')
            for line in tfp:
                sc = [s.strip() for s in line.split('|')]
                print(sc)
            quit()

        if selcmd.startswith('Return'):
            return


#####################################################################
#
#   Main
#
if __name__ == '__main__':

    if not (len(sys.argv) ==2):
        error('need command line arg.')

    if sys.argv[1] == 'help':
        help()
        quit()


    #
    #  set up and run the menu
    #

    mitems = [
              'Read and convert latest download to Working.csv',
              'Update Faculty working file with latest download preserving order',
              'Update the committee assignments',
              'Set sorting on output save',
              'Clear sorting on output save',
              'Read Fac Scores',
              'Disp. Fac Scores',
              'Test Menu',
              'Quit']

    mdata = {'labels':mitems, 'state':{'sorting':SORTING}}


    while True:
        j, selcmd = menu(mdata)

        #
        # read in a download csv, convert it to shareable sheet
        #
        if selcmd.startswith('Read and convert latest download with new sort order'):
            # generate collections for new download (newapps) and existing processed data (oldapps)
            newfn = sys.argv[1]
            latestDownload = readDownload(newfn)

            datestr = dt.datetime.today().strftime("%d-%b-%y")
            ofn = f'Working_-{datestr}.csv'
            writeOut(latestDownload, 'WorkingFile', ofn)


        if selcmd.startswith('Update Faculty work'):
            newfn = sys.argv[1]
            latestDownload = readDownload(newfn)
            oldWorkingfn = input('Enter current faculty working csv file: ')
            oldWorkingApps = readWorkingFile(oldWorkingfn)
            truelyNewApps = selectNewApps(latestDownload, oldWorkingApps)
            updatedWorking = concatenateCollections(oldWorkingApps,truelyNewApps)
            datestr = dt.datetime.today().strftime("%d-%b-%y")
            ofn = f'Working_-{datestr}.csv'
            writeOut(updatedWorking, 'WorkingFile', ofn)


        # #
        # #  Assign cmte members to apps in a collection
        # #
        # if selcmd.startswith('Create cmte'):
        #     appCollect = readDownload(sys.argv[1])
        #     appCollect.assignReviewers()
        #     ofn='CmteRevAssign.csv'
        #     writeOut(appCollect, 'AssignmentsXXX', ofn)

        #
        #  Generate new cmte member assignments as new apps come in
        #
        if selcmd.startswith('Update the committee assignments'):

            # generate collection for new download (newapps)
            newfn = sys.argv[1]
            newappsDL = readDownload(newfn)
            currAppAssignmentsFn = input('Enter Cmte Assignments csv: ').strip()
            oldAppAssignments = readCmteAssgmtsFile(currAppAssignmentsFn)
            truelyNewApps = selectNewApps(newappsDL, oldAppAssignments)
            # print(f'debug: old:{len(oldAppAssignments)} new:{len(newappsDL)}  truenew:{len(truelyNewApps)}')
            # quit()
            truelyNewApps.assignReviewers()

            # append the new assignments onto the old assignments
            latestAssignments = concatenateCollections(oldAppAssignments,truelyNewApps)
            datestr = dt.datetime.today().strftime("%d-%b-%y")
            ofn = f'CmteRevUpdate-{datestr}.csv'
            writeOut(latestAssignments, 'Assignments', ofn)

        #
        #  Fac scores
        #

        # read in the fac score file.
        if selcmd.startswith('Read Fac'):
            newfn = sys.argv[1]  # read in the working applicants file
            currentCol = readWorkingFile(newfn)
            # read in the faculty scores of the apps and merge them into the applicants collection
            currentCol = readFacScores(currentCol)


        #
        #  Fac scores
        #
        def cleanScore(sc):
            ret = []
            for x in sc:
                ret.append(x.strip())
            return ret


        # read in the fac score file.
        if selcmd.startswith('Disp. Fac'):
            csvlines = []
            report = ''
            try:
                x=len(currentCol)
            except:
                error('Display Fac. Score: Read in scores or collection first')
            for app in currentCol.app_list:
                if len(app.facScores) > 0:
                    report += f'{app.iD} - {app.fName} {app.lName}\n'
                    for fs in app.facScores:
                        (reviewer, rsch, tch, wirc) = cleanScore(fs)
                        report += '    ' + str(fs)+'\n'
                        csvline = f'{app.iD}; {app.fName+' '+app.lName}; '
                        csvline += f'{reviewer}; {rsch}; {tch}; {wirc}'
                        csvlines.append(csvline)
                    report += '\n'
            if len(report)<1:
                report = 'No scores found.'
            print(report)
            datestr = dt.datetime.today().strftime("%d-%b-%y")
            ofn = f'FacultyScores-{datestr}.csv'
            ofp = open(ofn,'w')
            for l in csvlines:
                print(l, file=ofp)
            ofp.close()
            print(f'Output file: {ofn}')

        #
        # Set Sorting Option Flag
        #
        if selcmd.startswith('Set'):
            SORTING = True
            print('\nSorting is ENABLED')
            mdata['state']['sorting']=True
        if selcmd.startswith('Clear'):
            SORTING = False
            print('\nSorting is DISABLED')
            mdata['stat']['sorting']=False


        #
        #  Testing menu
        #
        if selcmd.startswith('Test'):
            run_tests()


        if selcmd.upper().startswith('Q'):
            quit()

        x = input('Continue...<enter>')


