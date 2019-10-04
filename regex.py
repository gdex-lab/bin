import re
initial_pattern = 'employee_id='
pattern = re.compile(initial_pattern + "([\\d\\w])*")
matches = []

for i, line in enumerate(open('scalyr.txt')):
  for match in re.finditer(pattern, line):
    m =str(match.group()).replace(initial_pattern, '')
    if m not in matches: # make distinct list
      matches.append(m)
      
print(matches)
print("Length of distinct matches: ", len(matches))
