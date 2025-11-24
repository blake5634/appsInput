import csv
import sys
import datetime as dt
from itertools import combinations

def error(msg):
    print(f'Error: {msg}')
    quit()


#
#  set some configurations
#
ifURL = 'https://facultysearch.interfolio.com/28343/positions/171499'
TESTROW = -1  # <0 = no test printout
SORTING = True  # can be changed in user menu

# define col headers of our working files
outputCols = ['Firstname', 'Lastname', 'Teaching', 'Research', 'WIRC', 'Id','Link', 'Last date', 'Which area','Highest degree school']


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
    def __init__(self, headerCols):
        self.list = []
        self.header = headerCols
        self.len = 0

    def add(self,app):
        self.list.append(app)
        self.len+=1

    def __len__(self):
        return len(self.list)

    def assignRevs(self):
        revlist = ['Blake', 'Amy', 'Baosen', 'Sajjad']
        nrevs = len(revlist)
        combos = list(combinations(revlist,2))
        # print(revlist)
        # print(combos)
        cycle = 3
        p1 = 0
        j = 0
        for app in self.list:
            if (app.crev01 is None) and (app.crev02 is None):
                if j%cycle==0:
                    p1 = (p1+1)%len(combos)
                j += 1
                app.crev01 = combos[p1][0]
                app.crev02 = combos[p1][1]
                print(f'{app.iD:10} {app.crev01} {app.crev02}')
        heads = self.header
        heads.remove('Research')
        heads.remove('Teaching')
        heads.remove('WIRC')
        heads.insert(3,'rev 1')
        heads.insert(4,'rev 1')
        heads.insert(5,'Wscore')
        self.header = heads

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
        self.crev02 = None


    def __repr__(self):
        t = ''
        name = self.lName + ', ' + self.fName
        t += f'{name:25}'
        t += f'{self.iD:9} '
        t += f'{self.appDate:15} '
        t += f'{self.area:20}'
        # t += f'{self.createDate.strftime('%Y-%m-%d'):15}'
        return t

    def genSSRow(self,shType='faculty'):
    # # desired output cols, in order
    # f = ['Firstname', 'Lastname', 'Teaching', 'Research', 'WIRK', 'Id','Link', 'Last date', 'Which area']
        if shType=='faculty':
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
        elif shType=='committee':
            r = [self.fName, self.lName,  self.iD, self.crev01, self.crev02,'', self.url, self.appDate,self.area, self.ins]
            return r
        else:
            error('Unknown SSRow type: ', shType)

def readWorkingFile(inFileName):

    #
    #  read in a working file
    #
    f = open(inFileName, 'r',encoding='utf-8-sig')

    data = csv.reader(f)

    # read the input header
    inputHeaderRow = next(data)
    for i,c in enumerate(inputHeaderRow):
        if (c != outputCols[i]):
            print('input Working file header: ', inputHeaderRow)
            print('               outputCols: ', outputCols)
            error('readWorking: input header mismatch')

    existApps = collection(outputCols)
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
    print('Output Header: ',outputCols)

    # print('Selected Output Columns: ',selectedCols)

    oldcols=[]
    for selHdrCol in selectedCols:
        for i,ht in  enumerate(inputHeaderRow):
            if ht.startswith(selHdrCol):
                oldcols.append(i)

    print('oldcols: ',oldcols)

    applicants = collection(outputCols)

    j = 0
    for row in data:
        fn = row[oldcols[0]]  # oldcols is in 'selectedCols' order
        ln = row[oldcols[1]]
        iD = row[oldcols[2]]
        date = row[oldcols[3]][0:10]
        ar = row[oldcols[4]]
        ins = row[oldcols[5]]  # highest degree school
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

    if TESTROW >= 0:
        print(applicants.apps[TESTROW])
        print('')
        print(applicants.apps[TESTROW].genSSRow())

    return applicants


def mergeCollections(apps1, apps2):
    """Merge two lists of applicant objects, removing duplicates by iD. (thanks Claude)"""
    seen = {app.iD for app in apps1.list}
    return apps1.list + [app for app in apps2.list if app.iD not in seen]

def sortApps(applicants):
    print('Sorting (got here)')
    """Sort applicants by date, then by iD."""
    applicants.list =  sorted(applicants.list, key=lambda app: (dt.datetime.strptime(app.appDate.strip(), '%m/%d/%Y'), app.iD)).copy()
    return applicants

def writeOut(applicants, ofn):
    #
    #  Save new output file (sorted date, then by ID)
    #
    # ofn = 'newsheet.csv'
    if SORTING:
        applicants = sortApps(applicants)

    of = open(ofn, 'w')
    writer = csv.writer(of)

    #write out the header row
    writer.writerow(applicants.header)
    for a in applicants.list:
        row = a.genSSRow()
        writer.writerow(row)
    of.close()

    print(f'Output Saved: {ofn}')


def writeCmteAssign(applicants, ofn):
    #
    #  Save new output file (sorted date, then by ID)
    #
    if SORTING:
        applicants = sortApps(applicants)

    of = open(ofn, 'w')
    writer = csv.writer(of)

    #write out the header row
    writer.writerow(applicants.header)
    for a in applicants.list:
        row = a.genSSRow(shType='committee')  # add reviewer fields
        writer.writerow(row)
    of.close()

    print(f'Committee Assignments Output Saved: {ofn}')

def menu(mdat):
    try:
        x = mdat['labels']
        # x = mdat['meth']
        # x = mdat['style']
        nitems = len(mdat['labels'])
    except:
        error('Bad menu inputs:', mdat)
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
    try:
        j = int(resp)-1
        assert int(j) < nitems
    except:
        error(f'unusable response: {resp}')
    return j, mdat['labels'][j]

#
#
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

    mitems = ['Read, and Convert Download .csv',
              'Read, convert, and MERGE download .csv',
              'Create cmte scores',
              'Set sorting on output save',
              'Clear sorting on output save',
              'Quit']

    mdata = {'labels':mitems, 'state':{'sorting':SORTING}}
    while True:
        j, selcmd = menu(mdata)

        # read in a download csv and produce a shareable sheet
        if j==0:
            # readConvert(sys.argv[1])
            ofn = 'newsheet.csv'
            applicants = readDownload(sys.argv[1])
            writeOut(applicants, ofn)

        # read in a download csv and merge it with an existing shareable sheet
        if selcmd.startswith('Read, convert, and MERGE'):
            # generate collections for new download (newapps) and existing processed data (oldapps)
            newfn = sys.argv[1]
            newapps = readDownload(newfn)
            oldfn = input('Enter existing working csv: ')
            oldapps= readWorkingFile(oldfn.strip())
            updatedAppsList = mergeCollections(newapps, oldapps)  # returns only list
            updatedApps = collection(oldapps.header)
            updatedApps.list = updatedAppsList
            ofn = 'newsheetMerge.csv'
            writeOut(updatedApps, ofn)

        #
        #  Assign cmte members to a collection
        #
        if selcmd.startswith('Create cmte'):
            oldapps = readDownload(sys.argv[1])
            oldapps.assignRevs()
            ofn='CmteRevAssign.csv'
            writeCmteAssign(oldapps, ofn)

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

        if selcmd.upper().startswith('Q'):
            quit()

        x = input('Continue...<enter>')


