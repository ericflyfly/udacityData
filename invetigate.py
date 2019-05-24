import unicodecsv
from datetime import datetime as dt

#load csv data
def readData(filename):
	with open('./csv/' + filename, 'rb') as f:
		reader = unicodecsv.DictReader(f)
		data = list(reader)
	return data

# print data row by row
def printData(data, startIndex, endIndex):
	if not data or startIndex < 0 or endIndex > len(data):
		return
	print 'Rows of the data: ', getRowsNum(data)
	for i in range(startIndex, endIndex, 1):
		print "Row #", i + 1, " --> ", data[i]

def getRowsNum(data):
	if not data:
		return 0
	return len(data)

def getAllUnique(data, header):
	if not data or header not in data[0]:
		return 0
	res = set()
	for row in data:
		res.add(row[header])
	return res

def replaceCol(data, prevHeader, newHeader):
	if not data or prevHeader not in data[0]:
		return 
	for row in data:
		row[newHeader] = row[prevHeader]
		del row[prevHeader]

def removeTestAcctData(data, testAcct):
	if not data or not testAcct:
		return
	newData = []
	for row in data:
		if row['account_key'] not in testAcct:
			newData.append(row)
	return newData

def within_one_week(join_date, engagement_date):
	time_delta = engagement_date - join_date
	return time_delta.days < 7

def main():
	print '********** Read csv data **********'
	#Load Data and get general information
	enrollments = readData('enrollments.csv')
	printData(enrollments, 0, 5)
	daily_engagement = readData('daily_engagement.csv')
	printData(daily_engagement, 0, 5)
	#daily_engagement_full = readData('daily_engagement_full.csv')
	#printData(daily_engagement_full, 0, 10)
	project_submissions = readData('project_submissions.csv')
	printData(project_submissions, 0, 5)

	### For each of these three tables, find the number of rows in the table and
	### the number of unique students in the table. To find the number of unique
	### students, you might want to create a set of the account keys in each table.

	print '********** Daily enrollments data **********'
	enrollment_num_rows = getRowsNum(enrollments)
	print enrollment_num_rows
	enrollment_account = getAllUnique(enrollments, 'account_key')
	enrollment_num_unique_students = len(enrollment_account)
	print enrollment_num_unique_students

	print '********** Daily engagement data **********'
	engagement_num_rows = getRowsNum(daily_engagement)
	print engagement_num_rows
	replaceCol(daily_engagement, 'acct', 'account_key')
	engagement_account = getAllUnique(daily_engagement, 'account_key')
	engagement_num_unique_students = len(engagement_account)
	print engagement_num_unique_students
	print daily_engagement[0]['account_key']

	print '********** Submission data **********'
	submission_num_rows = getRowsNum(project_submissions)          
	print submission_num_rows
	submission_account = getAllUnique(project_submissions, 'account_key')
	submission_num_unique_students = len(submission_account)
	print submission_num_unique_students

	print '********** Identify suprising data **********'
	### Any enrollment record with no corresponding engagement data ###
	countMissing = 0
	for row in enrollments:
		if row['account_key'] not in engagement_account:
			countMissing += 1
			#print row
	print 'Number ofenrollement record with no corresponding engagement data:  ', countMissing

	### enroll at least a day ###
	countAtLeastaDay = 0
	for row in enrollments:
		if row['account_key'] not in engagement_account and row['days_to_cancel'] != '0':
			countAtLeastaDay += 1
			#print row
	print 'Number ofenrollement record with no corresponding engagement data at least a day:  ', countAtLeastaDay

	### remove testing accounts ###
	#find number of test accounts
	testAcctKey = set() 
	for row in enrollments:
		if row['is_udacity'] == 'True':
			testAcctKey.add(row['account_key'])
	print 'Number of test account:', len(testAcctKey)
	#remove all data related to test accounts
	enrollments_cleaned = removeTestAcctData(enrollments, testAcctKey)
	daily_engagement_cleaned = removeTestAcctData(daily_engagement, testAcctKey)
	project_submissions_cleaned = removeTestAcctData(project_submissions, testAcctKey)
	print '********** Length of cleaned data **********'
	print len(enrollments_cleaned), len(daily_engagement_cleaned), len(project_submissions_cleaned)

	### get paid students ###
	print '********** Get paid_students **********'
	paid_students = {}
	for row in enrollments_cleaned:
		if not row['days_to_cancel'] or int(float(row['days_to_cancel'])) > 7:
			cur_join_date = dt.strptime(row['join_date'], '%Y-%m-%d')
			if row['account_key'] not in paid_students or cur_join_date > paid_students[row['account_key']]:
				paid_students[row['account_key']] = cur_join_date

	print len(paid_students)

	### get engagement record for paid students only ###
	print '********** Get engagement record **********'
	paid_students_engagement = []
	for row in daily_engagement_cleaned:
		if row['account_key'] in paid_students and within_one_week(paid_students[row['account_key']], dt.strptime(row['utc_date'], '%Y-%m-%d')):
			paid_students_engagement.append(row)

	print len(paid_students_engagement)


main()