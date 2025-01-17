import unicodecsv
from datetime import datetime as dt
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


#load csv data
def read_data(filename):
	with open('./csv/' + filename, 'rb') as f:
		reader = unicodecsv.DictReader(f)
		data = list(reader)
	return data

# print data row by row
def print_data(data, startIndex, endIndex):
	if not data or startIndex < 0 or endIndex > len(data):
		return
	print 'Rows of the data: ', get_row_num(data)
	for i in range(startIndex, endIndex, 1):
		print "Row #", i + 1, " --> ", data[i]

def prase_date(str):
	if str == '':
		return None
	return dt.strptime(str, '%Y-%m-%d')


def prase_maybe_int(str):
	if not str:
		return None 
	return int(str)


def get_row_num(data):
	if not data:
		return 0
	return len(data)

def get_all_unique(data, header):
	if not data or header not in data[0]:
		return 0
	res = set()
	for row in data:
		res.add(row[header])
	return res

def replace_col(data, prevHeader, newHeader):
	if not data or prevHeader not in data[0]:
		return 
	for row in data:
		row[newHeader] = row[prevHeader]
		del row[prevHeader]

def remove_test_acct_data(data, testAcct):
	if not data or not testAcct:
		return
	newData = []
	for row in data:
		if row['account_key'] not in testAcct:
			newData.append(row)
	return newData

def within_one_week(join_date, engagement_date):
	time_delta = engagement_date - join_date
	return time_delta.days < 7 and time_delta.days >= 0

def group_data(data, key_name):
	grouped_data = defaultdict(list)
	for data_point in data:
		account_key = data_point[key_name]
		grouped_data[account_key].append(data_point)
	return grouped_data


def add_has_visited(data):
	for data_point in data:
		if data_point['num_courses_visited'] > 0:
			data_point['has_visited'] = 1
		else:
			data_point['has_visited'] = 0

#get all passing students account key from 
def get_passing_students(project_submissions_cleaned, paid_students, subway_project_lesson_keys):
	passing_students = set()
	for row in project_submissions_cleaned:
		if row['lesson_key'] in subway_project_lesson_keys and row['account_key'] in paid_students:
			if row['assigned_rating'] == 'PASSED' or row['assigned_rating'] == 'DISTINCTION':
				passing_students.add(row['account_key'])
	return passing_students

#get engagement data by their rating
def get_engagement_by_rating(paid_engagement_in_first_week, passing_students):
	non_passing_engagement, passing_engagement = [], []
	for row in paid_engagement_in_first_week:	
		if row['account_key'] in passing_students:
			passing_engagement.append(row)
		else:
			non_passing_engagement.append(row)
	return [passing_engagement, non_passing_engagement]

def describe_data(data, field_name, data_name, need_hist):
	print 'Mean:', np.mean(data)
	print 'Standard deviation:', np.std(data)
	print 'Min:', np.min(data)
	print 'Max:', np.max(data)
	if need_hist:
		plt.hist(data, bins=20)
		plt.xlabel(field_name)
		plt.ylabel('Counts')
		plt.title(data_name + ' ' + field_name)
		plt.show()

		#plot with seaborn
		sns.distplot(data)

	return np.mean(data)

def get_engagement_stat(field_name, acct_data, data_name, need_hist):
	# total minutes visited for each account
	print '********** Stat of', field_name, '**********' 
	total_by_account = {}
	for account_key, engagement_for_student in acct_data.items():
		total = 0
		for engagement_record in engagement_for_student:
			total += engagement_record[field_name]
		total_by_account[account_key] = total

    # get all minutes as a list and print out some stat
	return describe_data(total_by_account.values(), field_name, data_name, need_hist)

def compare_mean_passing_non_passing(passing_engagement_by_account, non_passing_engagement_by_account, field_name):
	create_histogram = False
	#print '********** mean of passing_engagement ********** '
	passing_total_mins_visited_mean = get_engagement_stat(field_name, passing_engagement_by_account, 'passing_engagement', create_histogram)
	#print 'passing', passing_total_mins_visited_mean
	#print '********** mean of non_passing_engagement ********** '
	non_passing_total_mins_visited_mean = get_engagement_stat(field_name, non_passing_engagement_by_account, 'non_passing_engagement',	create_histogram)
	#print 'non_passing', non_passing_total_mins_visited_mean
	if non_passing_total_mins_visited_mean == 0:
		print 'Error: non_passing_engagement_' + field_name, 'is zero!'
		return 
	print "Passing mean over non_passing mean of", field_name + ':', str((passing_total_mins_visited_mean - non_passing_total_mins_visited_mean) / non_passing_total_mins_visited_mean * 100) + "%"



#!!! may not need this part since compare_mean_passing_non_passing do this and we can use the data in describe_data function!!!

def compute_data_for_hist(passing_engagement_by_account, non_passing_engagement_by_account, field_name):
	res = [[], []]
	for engagement_list in passing_engagement_by_account.values():
		for engagement in engagement_list:
			res[0].append(engagement[field_name])
	for engagement_list in non_passing_engagement_by_account.values():
		for engagement in engagement_list:
			res[1].append(engagement[field_name])
	return res

def create_histogram_pass_non_pass(passing_engagement_by_account, non_passing_engagement_by_account, field_name):
	pass_non_pass_counts = compute_data_for_hist(passing_engagement_by_account, non_passing_engagement_by_account, field_name)
	print('hello there !!!!!!!!!')
	sns.distplot(pass_non_pass_counts[0])
#!!!! end

def main():
	print '********** Read csv data **********'
	#Load Data and get general information
	enrollments = read_data('enrollments.csv')
	print_data(enrollments, 0, 2)
	daily_engagement = read_data('daily_engagement.csv')
	print_data(daily_engagement, 0, 2)
	#daily_engagement_full = read_data('daily_engagement_full.csv')
	#print_data(daily_engagement_full, 0, 10)
	project_submissions = read_data('project_submissions.csv')
	print_data(project_submissions, 0, 2)

	### For each of these three tables, find the number of rows in the table and
	### the number of unique students in the table. To find the number of unique
	### students, you might want to create a set of the account keys in each table.

	print '********** Daily enrollments data **********'
	enrollment_num_rows = get_row_num(enrollments)
	print enrollment_num_rows
	enrollment_account = get_all_unique(enrollments, 'account_key')
	enrollment_num_unique_students = len(enrollment_account)
	print enrollment_num_unique_students

	print '********** Daily engagement data **********'
	engagement_num_rows = get_row_num(daily_engagement)
	print engagement_num_rows
	replace_col(daily_engagement, 'acct', 'account_key')
	engagement_account = get_all_unique(daily_engagement, 'account_key')
	engagement_num_unique_students = len(engagement_account)
	print engagement_num_unique_students
	print daily_engagement[0]['account_key']

	print '********** Submission data **********'
	submission_num_rows = get_row_num(project_submissions)          
	print submission_num_rows
	submission_account = get_all_unique(project_submissions, 'account_key')
	submission_num_unique_students = len(submission_account)
	print submission_num_unique_students

	### Convert string data to the right data type ###
	for row in enrollments:
		row['cancel_date'] = prase_date(row['cancel_date'])
		row['days_to_cancel'] = prase_maybe_int(row['days_to_cancel'])
		row['is_udacity'] = row['is_udacity'] == 'True'
		row['is_canceled'] = row['is_canceled'] == 'True'
		row['join_date'] = prase_date(row['join_date'])

	for row in daily_engagement:
		row['lessons_completed'] = int(float(row['lessons_completed']))
		row['num_courses_visited'] = int(float(row['num_courses_visited']))
		row['projects_completed'] = int(float(row['projects_completed']))
		row['total_minutes_visited'] = float(row['total_minutes_visited'])
		row['utc_date'] = prase_date(row['utc_date'])

	for row in project_submissions:
		row['completion_date'] = prase_date(row['completion_date'])
		row['creation_date'] = prase_date(row['creation_date'])

	print '********** Identify suprising data **********'
	### Any enrollment record with no corresponding engagement data ###
	count_missing = 0
	for row in enrollments:
		if row['account_key'] not in engagement_account:
			count_missing += 1
			#print row
	print 'Number of enrollement record with no corresponding engagement data:  ', count_missing

	### enroll at least a day ###
	count_at_least_one_day = 0
	for row in enrollments:
		if row['account_key'] not in engagement_account and row['days_to_cancel'] != 0:
			count_at_least_one_day += 1
			#print row
	print 'Number of enrollement record with no corresponding engagement data at least a day:  ', count_at_least_one_day

	### remove testing accounts ###
	#find number of test accounts
	test_acct_key = set() 
	for row in enrollments:
		if row['is_udacity']:
			test_acct_key.add(row['account_key'])
	print 'Number of test account:', len(test_acct_key)
	#remove all data related to test accounts
	enrollments_cleaned = remove_test_acct_data(enrollments, test_acct_key)
	daily_engagement_cleaned = remove_test_acct_data(daily_engagement, test_acct_key)
	project_submissions_cleaned = remove_test_acct_data(project_submissions, test_acct_key)
	print '********** Length of cleaned data **********'
	print len(enrollments_cleaned), len(daily_engagement_cleaned), len(project_submissions_cleaned)
	# add a new field to find does the student visited any lesson on that day
	add_has_visited(daily_engagement_cleaned)


	#####################################
	#                 6                 #
	#####################################

	## Create a dictionary named paid_students containing all students who either
	## haven't canceled yet or who remained enrolled for more than 7 days. The keys
	## should be account keys, and the values should be the date the student enrolled.
	print '********** Get paid_students **********'
	paid_students = {}
	for row in enrollments_cleaned:
		if row['days_to_cancel'] == None or row['days_to_cancel'] > 7:
			cur_join_date = row['join_date']
			if row['account_key'] not in paid_students or cur_join_date > paid_students[row['account_key']]:
				paid_students[row['account_key']] = cur_join_date

	print len(paid_students)

	### get engagement record for paid students only ###
	print '********** Get engagement record **********'
	paid_engagement_in_first_week = []
	for row in daily_engagement_cleaned:
		if row['account_key'] in paid_students and within_one_week(paid_students[row['account_key']], row['utc_date']):
			paid_engagement_in_first_week.append(row)

	print len(paid_engagement_in_first_week)

	# print '********** Stat of minutes spent in classroom **********'
	# find all engagement record belong to a sepecific account

	engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')
	"""engagement_by_account = defaultdict(list)
	for row in paid_engagement_in_first_week:
		account_key = row['account_key']
		engagement_by_account[account_key].append(row)"""

	"""# total minutes visited for each account
	total_minutes_by_account = {}
	for account_key, engagement_for_student in engagement_by_account.items():
		total_minutes = 0
		for engagement_record in engagement_for_student:
			total_minutes += engagement_record['total_minutes_visited']
		total_minutes_by_account[account_key] = total_minutes

    # get all minutes as a list and print out some stat
	all_minutes = total_minutes_by_account.values()
	print 'Mean:', np.mean(all_minutes)
	print 'Standard deviation:', np.std(all_minutes)
	print 'Min:', np.min(all_minutes)
	print 'Max:', np.max(all_minutes)"""
	get_engagement_stat('total_minutes_visited', engagement_by_account, 'engagement_by_account', need_hist = False)
	get_engagement_stat('lessons_completed', engagement_by_account, 'engagement_by_account', need_hist = False)
	get_engagement_stat('has_visited', engagement_by_account, 'engagement_by_account', need_hist = False)
	"""
	#Find suprising data --> found the account has cancelled and join again --> fixed in within_one_week function
	#if one user has more than one record, we use the most recent join date instead

	max_minutes = np.max(all_minutes)
	for row in enrollments:
		if row['account_key'] == '108':
			print row

	for acct in total_minutes_by_account.keys():
		if total_minutes_by_account[acct] == max_minutes:
			temp = engagement_by_account[acct]
			for row in temp:
				print row
			break
	"""

	######################################
	#                 11                 #
	######################################

	## Create two lists of engagement data for paid students in the first week.
	## The first list should contain data for students who eventually pass the
	## subway project, and the second list should contain data for students
	## who do not.
	print '********** Get engagement record by student who pass the project and who didn\'t **********'
	subway_project_lesson_keys = ['746169184', '3176718735']
	passing_students = get_passing_students(project_submissions_cleaned, paid_students, subway_project_lesson_keys )
	engagement_by_rating = get_engagement_by_rating(paid_engagement_in_first_week, passing_students)
	passing_engagement, non_passing_engagement = engagement_by_rating[0], engagement_by_rating[1]
	"""for row in paid_engagement_in_first_week:	
		if row['account_key'] in passing_students:
			passing_engagement.append(row)
		else:
			non_passing_engagement.append(row)"""

	print "passing_engagement total:", len(passing_engagement)
	print "non_passing_engagement total:", len(non_passing_engagement)

	non_passing_engagement_by_account = group_data(non_passing_engagement, 'account_key')
	passing_engagement_by_account = group_data(passing_engagement, 'account_key')

	compare_mean_passing_non_passing(passing_engagement_by_account, non_passing_engagement_by_account, 'total_minutes_visited')
	compare_mean_passing_non_passing(passing_engagement_by_account, non_passing_engagement_by_account, 'num_courses_visited')
	compare_mean_passing_non_passing(passing_engagement_by_account, non_passing_engagement_by_account, 'projects_completed')

	#!!! can improve this part later !!!

	#passing and non passing engagements in each month
	#Find how many months are there
	months_pass_non_pass = defaultdict(list)
	for row in paid_engagement_in_first_week:
		months_pass_non_pass[row['utc_date'].month] = [0, 0]

	#Find passing and non passing engagements in each month
	for row in passing_engagement:
		months_pass_non_pass[row['utc_date'].month][0] += 1

	for row in non_passing_engagement:
		months_pass_non_pass[row['utc_date'].month][1] += 1

	print 'Month pass and non pass count <month: [pass_counts, non_pass_counts]>:', months_pass_non_pass

	#Find month that has max people and min people pass and non pass the project
	max_pass = [0, -1]
	max_non_pass = [0, -1]
	min_pass = [0, float("inf")]
	min_non_pass = [0, float("inf")]
	months_precent_pass_over_non_pass = dict()
	for key, value in months_pass_non_pass.items():
		#pass data
		if value[0] > max_pass[1]:
			max_pass[0] = key
			max_pass[1] = value[0]
		if value[0] < min_pass[1]:
			min_pass[0] = key
			min_pass[1] = value[0]
		#non pass data
		if value[1] > max_non_pass[1]:
			max_non_pass[0] = key
			max_non_pass[1] = value[1]
		if value[1] < min_non_pass[1]:
			min_non_pass[0] = key
			min_non_pass[1] = value[1]
		if value[1] != 0:
			months_precent_pass_over_non_pass[key] = (value[0] - value[1]) / float(value[1]) * 100
		else:
			print 'Error: cannot find the precent for', key, 'month since non_passing_students is 0.'

	print 'max_pass [month,count]:', max_pass, 'min_pass [month,count]:', min_pass, 'max_non_pass [month,count]:', max_non_pass, 'min_non_pass [month,count]:', min_non_pass 
	print 'months_precent_pass_over_non_pass <month: precent> :', months_precent_pass_over_non_pass

	#create histogram for various field
	#minutes_spent
	create_histogram_pass_non_pass(passing_engagement_by_account, non_passing_engagement_by_account, 'total_minutes_visited')
	#lessons_completed
	#create_histogram_pass_non_pass(passing_engagement_by_account, non_passing_engagement_by_account, 'lessons_completed')
	#day visited
	#create_histogram_pass_non_pass(passing_engagement_by_account, non_passing_engagement_by_account, )
	#plt.hist(data)
	#plt.show()


main()