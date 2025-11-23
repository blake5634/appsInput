import csv
import sys
import datetime as dt

def error(msg):
    print(f'Error: {msg}')
    quit()

ifURL = 'https://facultysearch.interfolio.com/28343/positions/171499/'
TESTROW = -1  # <0 = no test printout


def help():
    print(f'''

    Log into {ifURL}
    Click "Reports" on left menu.
    On "Position Names": Select 171499.
    Choose "Columns" in upper right.
    Select following columns:
      "Selected": ALL
      "Application":  Initial Submission Date
      "Forms/Research Area:":
                Which Area best describes
                (Main Research Area
                Cross-cutting Area(s))

        ''')


class applicant:
    def __init__(self,fn,ln,iD,aD,ar):
        self.fName = fn
        self.lName = ln
        self.iD = iD
        # self.url = 'https://facultysearch.interfolio.com/28343/positions/171499/applications/' + iD
        self.url = ifURL + iD
        self.appDate = aD
        self.createDate = dt.datetime.today()
        self.area = ar

    def __repr__(self):
        t = ''
        name = self.lName + ', ' + self.fName
        t += f'{name:25}'
        t += f'{self.iD:9} '
        t += f'{self.appDate:15} '
        t += f'{self.area:20}'
        t += f'{self.createDate.strftime('%Y-%m-%d'):15}'
        return t

    def genSSRow(self):
    #
    # # desired output cols, in order
    # outputCols = ['Firstname', 'Lastname', 'Teaching', 'Research', 'WIRK', 'Id','Link', 'Last date', 'Which area']
        r = [self.fName, self.lName,  '', '', '',self.iD, self.url, self.appDate,self.area]
        return r

def readDownload(ifp):

    data = csv.reader(ifp)

    # expected input columns (possibly among others)
    inputHeads = ['Firstname', 'Lastname', 'Last date', 'Which','Id','Position']

    # desired output  order of the input cols we select
    selectedCols = ['Firstname', 'Lastname', 'Id', 'Last date', 'Which area']
    outputCols = ['Firstname', 'Lastname', 'Teaching', 'Research', 'WIRK', 'Id','Link', 'Last date', 'Which area']

    # read the input header
    inputHeaderRow = next(data)

    # print('Input Header: ', inputHeaderRow)
    # print('Output Header: ',outputCols)

    # print('Selected Output Columns: ',selectedCols)

    oldcols=[]
    for oh in selectedCols:
        for i,ht in  enumerate(inputHeaderRow):
            if ht.startswith(oh):
                # outputHeaderRow.append(ht)
                oldcols.append(i)

    # print('oldcols: ',oldcols)

    applicants = []
    j = 0
    for row in data:
        fn = row[oldcols[0]]
        ln = row[oldcols[1]]
        iD = row[oldcols[2]]
        date = row[oldcols[3]][0:10]
        ar = row[oldcols[4]]
        tmp = applicant(fn,ln,iD,date,ar)
        applicants.append(tmp)
        if j==TESTROW:
            print('TestRow: ', row)
            m=0
            for c in row:
                print(f'{m}: {c}')
                m+=1
            print(applicants[-1])
        j+=1


    print(f'parsed and loaded {len(applicants)} applicants')
    ifp.close()

    return applicants, outputCols

def main():
    if not (len(sys.argv) ==2):
        error('need command line arg.')

    if sys.argv[1] == 'help':
        help()
        quit()

    fname = sys.argv[1]
    f = open(fname, 'r',encoding='utf-8-sig')

    applicants, outputCols= readDownload(f)

    if TESTROW > 0:
        print(applicants[TESTROW])
        print('')
        print(applicants[TESTROW].genSSRow())

    #
    #  Generate new output file (sorted date, then by ID)
    #
    ofn = 'newsheet.csv'
    of = open(ofn, 'w')
    writer = csv.writer(of)

    writer.writerow(outputCols )
    for a in applicants:
        row = a.genSSRow()
        writer.writerow(row)
    of.close()

    print(f'Output Saved: {ofn}')

def menu(mdat):
    try:
        x = mdat['labels']
        x = mdat['meth']
        # x = mdat['style']
    except:
        error('Bad menu inputs:', mdat)
    i = 1
    for mi in mdat['labels']:
        print(f'{i:3}: {mi:20}')
        i+=1
if __name__ == '__main__':
    main()

